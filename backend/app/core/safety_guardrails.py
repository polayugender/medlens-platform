import re
from typing import Tuple, List

# Diagnostic assertion patterns that violate non-diagnostic AI safety rules
DIAGNOSTIC_CLAIM_PATTERNS = [
    r'\b(?:you have|patient has|patient is suffering from|diagnosed with|confirms a diagnosis of|indicates (?:that )?the patient has)\s+([a-zA-Z\s]{3,30}?)(?:\.|\,|$)',
    r'\b(?:this confirms|this establishes|conclusive evidence of)\s+([a-zA-Z\s]{3,30}?)(?:\.|\,|$)',
    r'\b(?:the diagnosis is|differential diagnosis is confirmed as)\s+([a-zA-Z\s]{3,30}?)(?:\.|\,|$)'
]

# Medication prescription & dosage recommendation patterns that violate clinical safety
DOSAGE_PRESCRIPTION_PATTERNS = [
    r'\b(?:take|prescribe|administer|start taking|increase (?:dosage to|dose to)|decrease (?:dosage to|dose to)|dosage of|dose of)\s+\d+(?:\.\d+)?\s*(?:mg|mcg|ml|g|tablets|capsules|units)\b',
    r'\b(?:should be prescribed|recommended dose is|start patient on)\s+[a-zA-Z0-9\s]{2,25}?\d+\s*(?:mg|mcg|ml|g)\b',
    r'\b(?:prescribe|prescription of)\s+[a-zA-Z0-9\s]{2,25}\b'
]

MANDATORY_CLINICAL_DISCLAIMER = (
    "MEDLENS CLINICAL SAFETY NOTICE: MedLens is an assistive clinical information organization platform "
    "and NOT a diagnostic device. It does not provide medical diagnoses, treatment advice, medication dosages, "
    "or prescription adjustments. All laboratory test results, flags, and health summaries must be reviewed "
    "and interpreted in clinical context by a licensed healthcare practitioner."
)

def enforce_clinical_safety_guardrails(text: str) -> Tuple[str, bool, List[str]]:
    """
    Scans AI-generated text and enforces non-diagnostic & zero-prescription clinical safety rules.
    1. Redacts diagnostic assertions into objective reference-range observations.
    2. Redacts medication dosage and prescription commands.
    3. Injects mandatory clinical disclaimer.
    Returns: (sanitized_text, guardrails_triggered, detected_violations)
    """
    if not text:
        return "", False, []

    violations: List[str] = []
    sanitized = text

    # 1. Check & redact diagnostic assertions
    for pattern in DIAGNOSTIC_CLAIM_PATTERNS:
        matches = re.finditer(pattern, sanitized, re.IGNORECASE)
        for m in matches:
            matched_str = m.group(0)
            violations.append(f"Prohibited diagnostic assertion: '{matched_str.strip()}'")
            sanitized = sanitized.replace(
                matched_str,
                " [OBSERVATION: Laboratory findings show markers outside reference intervals; consult clinician for diagnosis] "
            )

    # 2. Check & redact dosage & prescription commands
    for pattern in DOSAGE_PRESCRIPTION_PATTERNS:
        matches = re.finditer(pattern, sanitized, re.IGNORECASE)
        for m in matches:
            matched_str = m.group(0)
            violations.append(f"Prohibited medication/dosage command: '{matched_str.strip()}'")
            sanitized = sanitized.replace(
                matched_str,
                " [REDACTED: Medication dosage recommendations are strictly prohibited; consult physician] "
            )

    # 3. Ensure mandatory clinical safety disclaimer is present
    if "MEDLENS CLINICAL SAFETY NOTICE" not in sanitized:
        sanitized = f"{sanitized.rstrip()}\n\n---\n**Clinical Safety Advisory**:\n{MANDATORY_CLINICAL_DISCLAIMER}"

    guardrails_triggered = len(violations) > 0
    return sanitized, guardrails_triggered, violations
