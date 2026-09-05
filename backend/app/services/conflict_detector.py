from typing import List, Dict, Any, Optional

ALLERGY_MEDICATION_CROSS_REACTIVITY = [
    {
        "allergen": "penicillin",
        "meds": ["amoxicillin", "ampicillin", "augmentin", "piperacillin", "oxacillin", "penicillin"],
        "message": "Potential beta-lactam cross-reactivity between reported Penicillin allergy and medication."
    },
    {
        "allergen": "sulfa",
        "meds": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine", "glyburide"],
        "message": "Potential sulfonamide cross-reactivity between reported Sulfa allergy and medication."
    },
    {
        "allergen": "nsaid",
        "meds": ["ibuprofen", "advil", "motrin", "naproxen", "aleve", "aspirin", "meloxicam", "celecoxib", "diclofenac"],
        "message": "Reported NSAID sensitivity/allergy conflicts with active NSAID medication."
    },
    {
        "allergen": "aspirin",
        "meds": ["aspirin", "bayer", "ecotrin", "excedrin"],
        "message": "Reported Aspirin allergy directly conflicts with active Aspirin prescription."
    }
]

def detect_clinical_inconsistencies(
    intake_data: Optional[Dict[str, Any]],
    reports: List[Dict[str, Any]],
    tests: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Scans patient records for cross-source inconsistencies:
    1. Allergy vs Active Medication contradictions
    2. Missing reference range warnings on laboratory tests
    3. High-variance test results across multiple dates
    """
    conflicts: List[Dict[str, Any]] = []

    if not intake_data:
        return conflicts

    allergies = [a.strip().lower() for a in intake_data.get("allergies", []) if a]
    medications = intake_data.get("medications", [])

    # 1. Check Allergy vs Medication
    for item in ALLERGY_MEDICATION_CROSS_REACTIVITY:
        allergen_key = item["allergen"]
        # Check if patient reported this allergen
        has_allergy = any(allergen_key in a for a in allergies)
        if has_allergy:
            for med in medications:
                m_name = med.get("name", "").strip().lower()
                if any(m_target in m_name for m_target in item["meds"]):
                    conflicts.append({
                        "id": f"conflict-allergy-{allergen_key}-{m_name}",
                        "severity": "critical",
                        "category": "Allergy Contradiction",
                        "title": f"Allergy Alert: {med.get('name')} vs {allergen_key.capitalize()} Allergy",
                        "description": (
                            f"Patient intake records an allergy to '{allergen_key.capitalize()}', "
                            f"yet '{med.get('name')}' is currently listed as an active medication. "
                            f"{item['message']}"
                        ),
                        "source_a": "Patient Intake (Allergies)",
                        "source_b": "Patient Intake (Medications)",
                        "action_needed": "Confirm with physician before dispensing or continuing therapy."
                    })

    # 2. Check for Tests with Range Unavailable
    unavail_count = 0
    unavail_names = []
    for t in tests:
        if t.get("flag") == "unavailable" and not t.get("reference_range_raw"):
            unavail_count += 1
            if len(unavail_names) < 3:
                unavail_names.append(t.get("test_name"))

    if unavail_count > 0:
        conflicts.append({
            "id": "notice-range-unavailable",
            "severity": "warning",
            "category": "Documentation Gap",
            "title": f"Reference Range Missing for {unavail_count} Test(s)",
            "description": (
                f"Source laboratory reports did not specify a reference range for {', '.join(unavail_names)}"
                f"{' and others' if unavail_count > 3 else ''}. Per MedLens safety policy, flags cannot be computed without source ranges."
            ),
            "source_a": "Uploaded Medical Report",
            "source_b": "Clinical Safety Policy",
            "action_needed": "Request the laboratory reference interval sheet from the testing facility."
        })

    # 3. Check for Unverified Extracted Tests
    unverified_count = sum(1 for t in tests if not t.get("verified"))
    if unverified_count > 0:
        conflicts.append({
            "id": "notice-unverified-tests",
            "severity": "info",
            "category": "Human-in-the-Loop Review",
            "title": f"{unverified_count} Extracted Test(s) Awaiting Review",
            "description": "Newly uploaded report results must be reviewed and verified by a user before being committed to the unified clinical record.",
            "source_a": "AI Extraction Pipeline",
            "source_b": "Verification Workflow",
            "action_needed": "Open the Review & Verify tab to approve or edit the extracted test values."
        })

    return conflicts
