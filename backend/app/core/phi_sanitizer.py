import re
from typing import Tuple, Dict

# Regex patterns for direct Indian and international Protected Health Information (PHI)
ABHA_PATTERN = re.compile(r'\b\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
INDIAN_PHONE_PATTERN = re.compile(r'(?:\+91[\-\s]?)?[6789]\d{9}\b')
US_PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
DOB_PATTERN = re.compile(r'(?:DOB|Date of Birth|Birth Date):\s*([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', re.IGNORECASE)
NAME_HEADER_PATTERN = re.compile(r'(?:Patient(?:\s+Name)?|Name|Subject):\s*([A-Za-z\s,\.]{3,35})(?=\s{2,}|\n|\r|$)', re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r'\b[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}\b')

def sanitize_phi_for_llm(raw_text: str, patient_name: str = "") -> Tuple[str, Dict[str, int]]:
    """
    De-identifies Protected Health Information (PHI) before dispatching
    clinical report text or prompts to external LLM providers (e.g. Claude).
    
    Order of operations guarantees emails containing patient names are redacted
    as whole entities before individual name token replacement.
    """
    if not raw_text:
        return "", {}

    sanitized = raw_text
    metrics = {
        "names_redacted": 0,
        "abha_redacted": 0,
        "phones_redacted": 0,
        "emails_redacted": 0,
        "dob_redacted": 0
    }

    # 1. Email addresses (scrub first so name-based emails become [REDACTED_EMAIL])
    email_matches = EMAIL_PATTERN.findall(sanitized)
    if email_matches:
        metrics["emails_redacted"] += len(email_matches)
        sanitized = EMAIL_PATTERN.sub('[REDACTED_EMAIL]', sanitized)

    # 2. ABHA IDs & Aadhaar
    abha_matches = ABHA_PATTERN.findall(sanitized)
    if abha_matches:
        metrics["abha_redacted"] += len(abha_matches)
        sanitized = ABHA_PATTERN.sub('[REDACTED_ABHA_ID]', sanitized)

    aadhaar_matches = AADHAAR_PATTERN.findall(sanitized)
    if aadhaar_matches:
        metrics["abha_redacted"] += len(aadhaar_matches)
        sanitized = AADHAAR_PATTERN.sub('[REDACTED_NATIONAL_ID]', sanitized)

    # 3. Phone numbers
    phone_matches = INDIAN_PHONE_PATTERN.findall(sanitized) + US_PHONE_PATTERN.findall(sanitized)
    if phone_matches:
        metrics["phones_redacted"] += len(phone_matches)
        sanitized = INDIAN_PHONE_PATTERN.sub('[REDACTED_PHONE]', sanitized)
        sanitized = US_PHONE_PATTERN.sub('[REDACTED_PHONE]', sanitized)

    # 4. Dates of birth
    dob_matches = DOB_PATTERN.findall(sanitized)
    if dob_matches:
        metrics["dob_redacted"] += len(dob_matches)
        sanitized = DOB_PATTERN.sub('DOB: [REDACTED_DOB]', sanitized)

    # 5. Pattern-based Patient Name headers
    name_matches = NAME_HEADER_PATTERN.findall(sanitized)
    if name_matches:
        metrics["names_redacted"] += len(name_matches)
        sanitized = NAME_HEADER_PATTERN.sub('Patient: [REDACTED_NAME]', sanitized)

    # 6. Explicit patient name scrubbing if supplied
    if patient_name and len(patient_name.strip()) > 2:
        parts = patient_name.strip().split()
        for p in parts:
            if len(p) > 2 and p.lower() not in ["patient", "user", "male", "female"]:
                matches = re.findall(rf'\b{re.escape(p)}\b', sanitized, re.IGNORECASE)
                if matches:
                    metrics["names_redacted"] += len(matches)
                    sanitized = re.sub(rf'\b{re.escape(p)}\b', '[REDACTED_NAME]', sanitized, flags=re.IGNORECASE)

    return sanitized, metrics
