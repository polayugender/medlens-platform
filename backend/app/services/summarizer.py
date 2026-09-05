import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.core.prompts import SUMMARY_SYSTEM_PROMPT
from app.core.provenance import FlagCategory

def _generate_deterministic_clinical_summary(
    patient_data: Dict[str, Any],
    intake_data: Optional[Dict[str, Any]],
    verified_tests: List[Dict[str, Any]]
) -> str:
    """
    Deterministically synthesizes a plain-language summary strictly following
    the MedLens clinical safety contract (no diagnosis, no treatments, facts only).
    """
    sections: List[str] = []

    # Header / Context
    name = patient_data.get("name", "Patient")
    sections.append(f"### Record Overview for {name}\n")
    sections.append(
        "This is an organized overview synthesizing your self-reported health background with verified diagnostic laboratory reports on file.\n"
    )

    # 1. Patient Intake Context (User-Reported)
    if intake_data:
        sections.append("#### Self-Reported Health Profile (Source: Patient Intake)")
        age = intake_data.get("age")
        sex = intake_data.get("sex")
        sections.append(f"- **Demographics**: {age} years old, {sex}")

        symptoms = intake_data.get("symptoms", [])
        if symptoms:
            sections.append(f"- **Reported Symptoms**: {', '.join(symptoms)}")
        else:
            sections.append("- **Reported Symptoms**: None currently reported")

        conditions = intake_data.get("existing_conditions", [])
        if conditions:
            sections.append(f"- **Existing Diagnoses On File**: {', '.join(conditions)}")

        allergies = intake_data.get("allergies", [])
        if allergies:
            sections.append(f"- **Known Allergies**: {', '.join(allergies)}")
        else:
            sections.append("- **Known Allergies**: No known drug/food allergies recorded")

        meds = intake_data.get("medications", [])
        if meds:
            med_strs = [f"{m.get('name')} ({m.get('dosage', 'dose unstated')}, {m.get('frequency', '')})" for m in meds]
            sections.append(f"- **Current Active Medications**: {'; '.join(med_strs)}")
        sections.append("")

    # 2. Verified Laboratory Results (AI-Extracted & Clinician-Confirmed)
    sections.append("#### Laboratory Findings & Reference Range Observations (Source: Verified Reports)")
    if not verified_tests:
        sections.append("No verified diagnostic laboratory tests are currently linked to this record.\n")
    else:
        # Group tests into High, Low, Normal, and Range Unavailable
        high_tests = [t for t in verified_tests if t.get("flag") == FlagCategory.HIGH.value]
        low_tests = [t for t in verified_tests if t.get("flag") == FlagCategory.LOW.value]
        normal_tests = [t for t in verified_tests if t.get("flag") == FlagCategory.NORMAL.value]
        unavail_tests = [t for t in verified_tests if t.get("flag") == FlagCategory.UNAVAILABLE.value]

        if high_tests:
            sections.append("**Values Above Documented Reference Range:**")
            for t in high_tests:
                unit_str = f" {t['unit']}" if t.get("unit") else ""
                ref_str = f" (Reported reference range: {t['reference_range_raw']})" if t.get("reference_range_raw") else ""
                sections.append(f"- **{t['test_name']}**: {t['value']}{unit_str}{ref_str} — above the stated laboratory reference range.")
            sections.append("")

        if low_tests:
            sections.append("**Values Below Documented Reference Range:**")
            for t in low_tests:
                unit_str = f" {t['unit']}" if t.get("unit") else ""
                ref_str = f" (Reported reference range: {t['reference_range_raw']})" if t.get("reference_range_raw") else ""
                sections.append(f"- **{t['test_name']}**: {t['value']}{unit_str}{ref_str} — below the stated laboratory reference range.")
            sections.append("")

        if normal_tests:
            sections.append(f"**Within Documented Reference Range ({len(normal_tests)} markers):**")
            marker_names = [f"{t['test_name']} ({t['value']}{' ' + t['unit'] if t.get('unit') else ''})" for t in normal_tests]
            sections.append(f"- {', '.join(marker_names)}")
            sections.append("")

        if unavail_tests:
            sections.append("**Markers Without Provided Reference Range On Document:**")
            for t in unavail_tests:
                unit_str = f" {t['unit']}" if t.get("unit") else ""
                sections.append(f"- **{t['test_name']}**: {t['value']}{unit_str} — the uploaded laboratory document did not specify a reference interval.")
            sections.append("")

    # 3. Advisory Note (Guardrail)
    sections.append("---")
    sections.append(
        "**Clinical Consultation Reminder**: These findings are an objective transcription of your source documents. "
        "Laboratory values must always be evaluated in the full context of your clinical examination, medical history, and clinical signs. "
        "Please bring this organized summary to your healthcare practitioner for evaluation."
    )

    return "\n".join(sections)

async def _generate_claude_summary(prompt_payload: str, api_key: str) -> Optional[str]:
    """Generates clinical summary via Claude API with strict non-diagnostic system prompt."""
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
                    "max_tokens": 2048,
                    "system": SUMMARY_SYSTEM_PROMPT,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Summarize this patient record following all guardrails:\n\n{prompt_payload}"
                        }
                    ]
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
    except Exception as e:
        print(f"Claude summary error: {e}")
    return None

async def generate_patient_summary(
    patient_data: Dict[str, Any],
    intake_data: Optional[Dict[str, Any]],
    verified_tests: List[Dict[str, Any]]
) -> str:
    """
    Orchestrates the generation of the plain-language clinical summary.
    Enforces non-diagnostic guardrails and provenance clarity.
    """
    prompt_payload = f"""
    PATIENT DEMOGRAPHICS:
    Name: {patient_data.get('name')}
    DOB: {patient_data.get('dob')}
    Sex: {patient_data.get('sex')}

    INTAKE HEALTH PROFILE (Source: Patient Input):
    {intake_data}

    VERIFIED LABORATORY RESULTS (Source: Verified Medical Reports):
    {verified_tests}
    """

    if settings.ANTHROPIC_API_KEY:
        claude_summary = await _generate_claude_summary(prompt_payload, settings.ANTHROPIC_API_KEY)
        if claude_summary:
            return claude_summary

    # Fallback to deterministic clinical narrative generator
    return _generate_deterministic_clinical_summary(patient_data, intake_data, verified_tests)
