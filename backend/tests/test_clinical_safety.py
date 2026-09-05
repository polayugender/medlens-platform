import pytest
from app.core.provenance import SourceProvenance, FlagCategory
from app.core.flag_calculator import (
    parse_reference_range,
    parse_reference_range_with_provenance,
    parse_result_value,
    compute_flag
)
from app.core.phi_sanitizer import sanitize_phi_for_llm
from app.core.safety_guardrails import enforce_clinical_safety_guardrails

def test_zero_hallucination_reference_range():
    """Ensure missing reference ranges are NEVER auto-filled or guessed."""
    # When no reference range exists
    low, high, source_provided = parse_reference_range_with_provenance(None)
    assert low is None and high is None and source_provided is False

    flag = compute_flag(value_numeric=145.0, low=low, high=high, source_provided=source_provided)
    assert flag == FlagCategory.RANGE_NOT_PROVIDED

    # When explicit text says "unavailable" or "not provided"
    low2, high2, source_provided2 = parse_reference_range_with_provenance("range_unavailable")
    assert source_provided2 is False
    flag2 = compute_flag(value_numeric=55.0, low=low2, high=high2, source_provided=source_provided2)
    assert flag2 == FlagCategory.RANGE_NOT_PROVIDED

def test_relational_operators_parsing():
    """Ensure <0.01, >1000, and standard numeric values parse correctly."""
    val_str, num, op = parse_result_value("<0.01")
    assert val_str == "<0.01"
    assert num == 0.01
    assert op == "<"

    val_str2, num2, op2 = parse_result_value("> 1000")
    assert num2 == 1000.0
    assert op2 == ">"

    val_str3, num3, op3 = parse_result_value("145.5")
    assert num3 == 145.5
    assert op3 is None

def test_qualitative_flag_computation():
    """Ensure qualitative findings like Trace, Positive, and Negative flag properly."""
    # Normal qualitative
    flag_neg = compute_flag(value_numeric=None, low=None, high=None, qualitative_value="Negative", source_provided=True)
    assert flag_neg == FlagCategory.NORMAL

    # Abnormal qualitative (Trace, Reactive, Positive) in FHIR mode
    flag_pos = compute_flag(value_numeric=None, low=None, high=None, qualitative_value="Trace", source_provided=True)
    assert flag_pos == FlagCategory.ABNORMAL_QUALITATIVE

    flag_react = compute_flag(value_numeric=None, low=None, high=None, qualitative_value="Reactive", source_provided=True, fhir_mode=True)
    assert flag_react == FlagCategory.ABNORMAL_QUALITATIVE

def test_phi_sanitizer():
    """Ensure all direct Indian and international identifiers are stripped before LLM calls."""
    raw_text = (
        "Patient Name: Eleanor Vance\n"
        "DOB: 1985-04-12\n"
        "ABHA Number: 14-8821-4921-9923\n"
        "Contact: +919876543210\n"
        "Email: eleanor.vance@healthmail.com\n"
        "Glucose: 110 mg/dL (Ref: 70 - 99)\n"
    )

    sanitized, metrics = sanitize_phi_for_llm(raw_text, patient_name="Eleanor Vance")
    
    assert "Eleanor Vance" not in sanitized
    assert "14-8821-4921-9923" not in sanitized
    assert "+919876543210" not in sanitized
    assert "eleanor.vance@healthmail.com" not in sanitized
    assert "[REDACTED_ABHA_ID]" in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert metrics["abha_redacted"] >= 1
    assert metrics["phones_redacted"] >= 1
    assert metrics["emails_redacted"] >= 1

def test_clinical_safety_guardrails():
    """Ensure prohibited diagnostic assertions and dosage commands are blocked and redacted."""
    hallucinated_ai_text = (
        "Based on your HbA1c of 8.2%, you have diabetes mellitus.\n"
        "You should take 500mg Metformin twice daily to control your blood glucose."
    )

    safe_text, triggered, violations = enforce_clinical_safety_guardrails(hallucinated_ai_text)
    
    assert triggered is True
    assert len(violations) >= 2
    # Ensure diagnostic claim is redacted
    assert "you have diabetes mellitus" not in safe_text.lower()
    # Ensure medication dosage is redacted
    assert "take 500mg metformin" not in safe_text.lower()
    assert "[REDACTED: Medication dosage recommendations are strictly prohibited" in safe_text
    # Ensure mandatory clinical disclaimer is appended
    assert "MEDLENS CLINICAL SAFETY NOTICE" in safe_text
