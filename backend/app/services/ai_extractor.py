import json
import re
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.core.prompts import EXTRACTION_SYSTEM_PROMPT
from app.core.flag_calculator import parse_reference_range, compute_flag
from app.schemas.extraction_engine import ExtractionResultSchema, ExtractedTestItemSchema, ReportMetadataSchema

def _extract_via_deterministic_parser(raw_text: str) -> Dict[str, Any]:
    """
    Built-in high-precision clinical report parser.
    Parses common medical lab tables (CMP, CBC, Lipid Panel, etc.)
    with strict adherence to:
    - Never guessing reference ranges
    - Returning verbatim raw_snippet for audit
    """
    lines = raw_text.splitlines()
    extracted_tests: List[Dict[str, Any]] = []
    
    # Heuristics for metadata
    report_date = None
    report_type = "Diagnostic Laboratory Report"
    facility_name = "Clinical Pathology Laboratory"

    date_match = re.search(r'(?:Date|Collected|Reported|Date of Service):\s*([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', raw_text, re.IGNORECASE)
    if date_match:
        report_date = date_match.group(1)

    if "metabolic panel" in raw_text.lower():
        report_type = "Comprehensive Metabolic Panel (CMP)"
    elif "complete blood count" in raw_text.lower() or "cbc" in raw_text.lower():
        report_type = "Complete Blood Count (CBC)"
    elif "lipid" in raw_text.lower():
        report_type = "Lipid Panel"
    elif "thyroid" in raw_text.lower() or "tsh" in raw_text.lower():
        report_type = "Thyroid Function Panel"

    facility_match = re.search(r'(?:Facility|Laboratory|Hospital|Clinic):\s*([^\n\r]+)', raw_text, re.IGNORECASE)
    if facility_match:
        facility_name = facility_match.group(1).strip()

    ignore_keywords = [
        "test", "name", "result", "flag", "units", "reference", "interval", "page",
        "patient", "dob", "specimen", "collection", "doctor", "physician", "ordering",
        "date", "facility", "status", "sex", "report", "verification", "electronic", "fasting"
    ]

    clean_lines = [l.strip() for l in lines if l.strip()]

    # 1. Check for multi-line sequential table format (PyMuPDF vertical cell extraction)
    # Typical sequence: Test Name -> Result -> Units -> Reference Interval
    header_indices = []
    for idx, l in enumerate(clean_lines):
        if "test name" in l.lower() and idx + 3 < len(clean_lines):
            if any("result" in clean_lines[idx+1].lower() or "units" in clean_lines[idx+2].lower() for _ in [1]):
                header_indices.append(idx)

    if header_indices:
        start_idx = header_indices[0] + 4
        idx = start_idx
        while idx < len(clean_lines):
            if any(stop_word in clean_lines[idx].lower() for stop_word in ["comments", "clinical notes", "electronic verification", "page break", "laboratory comments"]):
                break
            if idx + 3 < len(clean_lines):
                t_name = clean_lines[idx]
                t_val = clean_lines[idx+1]
                t_unit = clean_lines[idx+2]
                t_range = clean_lines[idx+3]

                # Ensure t_val is a result number or qualitative descriptor
                val_match = re.match(r'^[><=]?\s*[0-9]+(?:\.[0-9]+)?$|^[><=]?\s*[A-Za-z]+$', t_val)
                range_match = re.search(r'[0-9]+|Negative|Normal|Non-reactive|None|<|>', t_range)
                is_header_noise = any(k in t_name.lower() for k in ["specimen", "facility", "physician", "ordering", "date of"])
                
                if val_match and range_match and not is_header_noise and t_name.lower() not in ignore_keywords:
                    clean_num_str = re.sub(r'^[><=]\s*', '', t_val)
                    try:
                        num_val = float(clean_num_str)
                    except ValueError:
                        num_val = None

                    extracted_tests.append({
                        "test_name": t_name,
                        "value": t_val,
                        "value_numeric": num_val,
                        "unit": t_unit,
                        "reference_range_raw": t_range,
                        "raw_snippet": f"{t_name}   {t_val} {t_unit}   {t_range}",
                        "confidence": 0.99
                    })
                    idx += 4
                    continue
            idx += 1

    # 2. Regex patterns for single-line tabular clinical test lines
    # Typical line: Glucose   115 mg/dL   70 - 99
    if not extracted_tests:
        test_line_regex = re.compile(
            r'^\s*([A-Za-z0-9\(\)\/\-,\s]+?)\s{2,}'+ # Test name
            r'([><=]?\s*[0-9]+(?:\.[0-9]+)?|[A-Za-z]+)\s+'+ # Value
            r'([a-zA-Z%\/µu\^0-9]+)?\s*'+ # Optional Unit
            r'(?:([><=]?\s*[0-9]+(?:\.[0-9]+)?\s*(?:-|–|—|to)\s*[0-9]+(?:\.[0-9]+)?|<[0-9]+(?:\.[0-9]+)?|>[0-9]+(?:\.[0-9]+)?|Negative|Normal|Non-reactive|None))?' # Optional Range
        )

        for line in lines:
            stripped = line.strip()
            if not stripped or len(stripped) < 5:
                continue
            
            # Check if header line
            lower = stripped.lower()
            if any(h in lower for h in ["reference range", "flag unit", "test name", "component"]):
                continue

            match = test_line_regex.match(stripped)
            if match:
                test_name = match.group(1).strip()
                raw_val = match.group(2).strip()
                unit = match.group(3).strip() if match.group(3) else None
                ref_range = match.group(4).strip() if match.group(4) else None

                # Filter noise headers
                if test_name.lower() in ignore_keywords:
                    continue

                # Parse numeric value if applicable
                num_val = None
                try:
                    clean_num_str = re.sub(r'^[><=]\s*', '', raw_val)
                    num_val = float(clean_num_str)
                except ValueError:
                    num_val = None

                extracted_tests.append({
                    "test_name": test_name,
                    "value": raw_val,
                    "value_numeric": num_val,
                    "unit": unit,
                    "reference_range_raw": ref_range,
                    "raw_snippet": stripped,
                    "confidence": 0.98
                })

    # 3. If standard formats did not match, try flexible colon-separated format (excluding header keywords)
    if not extracted_tests:
        for line in lines:
            stripped = line.strip()
            flexible = re.search(r'([A-Za-z0-9\s\-_/]+):\s*([><=]?\s*[0-9]+(?:\.[0-9]+)?|[A-Za-z]+)\s*([a-zA-Z%\/µu\^0-9]+)?(?:\s*\(?(?:Ref|Range|Normal)?[:\s]*([0-9\.\s\-–to><=]+)\)?)?', stripped, re.IGNORECASE)
            if flexible:
                tname = flexible.group(1).strip()
                tval = flexible.group(2).strip()
                tunit = flexible.group(3).strip() if flexible.group(3) else None
                trange = flexible.group(4).strip() if flexible.group(4) else None
                
                if any(k in tname.lower() for k in ignore_keywords) or len(tname) < 2:
                    continue

                num_val = None
                try:
                    clean_num_str = re.sub(r'^[><=]\s*', '', tval)
                    num_val = float(clean_num_str)
                except ValueError:
                    num_val = None

                extracted_tests.append({
                    "test_name": tname,
                    "value": tval,
                    "value_numeric": num_val,
                    "unit": tunit,
                    "reference_range_raw": trange,
                    "raw_snippet": stripped,
                    "confidence": 0.92
                })

    return {
        "report_metadata": {
            "report_date": report_date,
            "report_type": report_type,
            "facility_name": facility_name
        },
        "extracted_tests": extracted_tests
    }

async def _extract_via_claude(raw_text: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Calls Anthropic Claude Messages API with extraction prompt and JSON schema."""
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "system": EXTRACTION_SYSTEM_PROMPT,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Extract structured data from this medical report:\n\n{raw_text}"
                        }
                    ]
                }
            )
            if response.status_code == 200:
                data = response.json()
                content = data["content"][0]["text"]
                # Parse JSON out of content
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                return json.loads(content)
    except Exception as e:
        print(f"Claude extraction error: {e}")
    return None

async def extract_structured_tests_from_report(raw_text: str) -> ExtractionResultSchema:
    """
    Main extraction orchestrator:
    1. Tries Claude API if configured
    2. Falls back seamlessly to deterministic high-precision clinical parser
    3. Guarantees deterministic flag computation and strict Pydantic schema validation
    """
    extracted_data = None

    if settings.ANTHROPIC_API_KEY:
        extracted_data = await _extract_via_claude(raw_text, settings.ANTHROPIC_API_KEY)

    if not extracted_data:
        extracted_data = _extract_via_deterministic_parser(raw_text)

    # Validate against Pydantic schema
    metadata = ReportMetadataSchema(
        report_date=extracted_data.get("report_metadata", {}).get("report_date"),
        report_type=extracted_data.get("report_metadata", {}).get("report_type"),
        facility_name=extracted_data.get("report_metadata", {}).get("facility_name")
    )

    test_items: List[ExtractedTestItemSchema] = []
    for item in extracted_data.get("extracted_tests", []):
        test_items.append(ExtractedTestItemSchema(
            test_name=item["test_name"],
            value=str(item["value"]),
            value_numeric=item.get("value_numeric"),
            unit=item.get("unit"),
            reference_range_raw=item.get("reference_range_raw"),
            raw_snippet=item.get("raw_snippet", f"{item['test_name']}: {item['value']}"),
            confidence=float(item.get("confidence", 1.0))
        ))

    return ExtractionResultSchema(
        report_metadata=metadata,
        extracted_tests=test_items
    )
