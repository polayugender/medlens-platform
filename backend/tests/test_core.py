import pytest
from app.core.flag_calculator import parse_reference_range, compute_flag
from app.core.provenance import FlagCategory
from app.services.conflict_detector import detect_clinical_inconsistencies

def test_parse_reference_range():
    # Two-sided intervals
    assert parse_reference_range("70 - 99") == (70.0, 99.0)
    assert parse_reference_range("70-99") == (70.0, 99.0)
    assert parse_reference_range("0.5 to 1.2") == (0.5, 1.2)
    assert parse_reference_range("13.5 – 17.5") == (13.5, 17.5) # en-dash

    # One-sided bounds
    assert parse_reference_range("< 200") == (None, 200.0)
    assert parse_reference_range("<= 150") == (None, 150.0)
    assert parse_reference_range("> 40") == (40.0, None)
    assert parse_reference_range(">= 60") == (60.0, None)

    # Missing / unavailable ranges
    assert parse_reference_range(None) == (None, None)
    assert parse_reference_range("") == (None, None)
    assert parse_reference_range("range_unavailable") == (None, None)
    assert parse_reference_range("Not Provided") == (None, None)

def test_compute_flag_deterministic():
    # Two-sided interval (70 - 99)
    assert compute_flag(65.0, 70.0, 99.0) == FlagCategory.LOW
    assert compute_flag(70.0, 70.0, 99.0) == FlagCategory.NORMAL # boundary inclusive
    assert compute_flag(85.0, 70.0, 99.0) == FlagCategory.NORMAL
    assert compute_flag(99.0, 70.0, 99.0) == FlagCategory.NORMAL # boundary inclusive
    assert compute_flag(128.0, 70.0, 99.0) == FlagCategory.HIGH

    # Upper bound only (< 200)
    assert compute_flag(180.0, None, 200.0) == FlagCategory.NORMAL
    assert compute_flag(224.0, None, 200.0) == FlagCategory.HIGH

    # Lower bound only (> 40)
    assert compute_flag(38.0, 40.0, None) == FlagCategory.LOW
    assert compute_flag(55.0, 40.0, None) == FlagCategory.NORMAL

    # Missing range: MUST NEVER GUESS, always UNAVAILABLE
    assert compute_flag(150.0, None, None) == FlagCategory.UNAVAILABLE

    # Qualitative values
    assert compute_flag(None, None, None, qualitative_value="Negative") == FlagCategory.NORMAL
    assert compute_flag(None, None, None, qualitative_value="Non-reactive") == FlagCategory.NORMAL
    assert compute_flag(None, None, None, qualitative_value="Positive") == FlagCategory.HIGH

def test_clinical_conflict_detection():
    intake = {
        "allergies": ["Penicillin", "Sulfa drugs"],
        "medications": [
            {"name": "Amoxicillin", "dosage": "500mg"},
            {"name": "Lisinopril", "dosage": "10mg"}
        ]
    }
    reports = []
    tests = []

    conflicts = detect_clinical_inconsistencies(intake, reports, tests)
    assert len(conflicts) >= 1
    # Ensure allergy alert detected
    allergy_conflicts = [c for c in conflicts if c["category"] == "Allergy Contradiction"]
    assert len(allergy_conflicts) == 1
    assert "Amoxicillin" in allergy_conflicts[0]["title"]
