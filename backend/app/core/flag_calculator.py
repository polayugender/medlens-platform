import re
from typing import Optional, Tuple
from app.core.provenance import FlagCategory

def parse_reference_range(raw_range: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """
    Parses a reference range string strictly from the source document.
    Never infers or guesses missing bounds.
    Supports:
      - "70 - 99", "70-99", "70 - 99.5" -> (70.0, 99.0)
      - "< 200", "<= 200", "<200"       -> (None, 200.0)
      - "> 40", ">= 40", ">40"          -> (40.0, None)
      - "0.5 to 1.2"                    -> (0.5, 1.2)
    """
    low, high, _ = parse_reference_range_with_provenance(raw_range)
    return low, high

def parse_reference_range_with_provenance(raw_range: Optional[str]) -> Tuple[Optional[float], Optional[float], bool]:
    """
    Parses reference range and explicitly returns (low, high, source_provided).
    source_provided is TRUE ONLY if explicitly present in source text.
    NEVER hallucinate or impute defaults.
    """
    if not raw_range or not isinstance(raw_range, str):
        return None, None, False
    
    clean = raw_range.strip()
    lower = clean.lower()
    if not clean or lower in ["unavailable", "n/a", "none", "not provided", "range_unavailable", "range_not_provided", "unknown"]:
        return None, None, False
    
    # Check less-than pattern: e.g. "< 200", "<= 100", "<=150"
    lt_match = re.match(r'^(?:<|<=|less than)\s*([0-9]+(?:\.[0-9]+)?)$', clean, re.IGNORECASE)
    if lt_match:
        try:
            return None, float(lt_match.group(1)), True
        except ValueError:
            pass

    # Check greater-than pattern: e.g. "> 40", ">= 50", ">50"
    gt_match = re.match(r'^(?:>|>=|greater than)\s*([0-9]+(?:\.[0-9]+)?)$', clean, re.IGNORECASE)
    if gt_match:
        try:
            return float(gt_match.group(1)), None, True
        except ValueError:
            pass

    # Check range pattern: "low - high" or "low to high"
    range_match = re.match(r'^([0-9]+(?:\.[0-9]+)?)\s*(?:-|–|—|to)\s*([0-9]+(?:\.[0-9]+)?)$', clean, re.IGNORECASE)
    if range_match:
        try:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return low, high, True
        except ValueError:
            pass

    # Non-numeric textual range (e.g. "Negative", "Non-reactive")
    return None, None, True

def parse_result_value(raw_val: Optional[str]) -> Tuple[str, Optional[float], Optional[str]]:
    """
    Parses observed result string into:
    (raw_string, numeric_value, relational_operator)
    e.g.:
      "<0.01" -> ("<0.01", 0.01, "<")
      ">1000" -> (">1000", 1000.0, ">")
      "145"   -> ("145", 145.0, None)
      "Trace" -> ("Trace", None, None)
    """
    if not raw_val or not isinstance(raw_val, str):
        return "", None, None

    clean = raw_val.strip()
    op_match = re.match(r'^([<>]=?|=)\s*([0-9]+(?:\.[0-9]+)?)$', clean)
    if op_match:
        op = op_match.group(1)
        try:
            num = float(op_match.group(2))
            return clean, num, op
        except ValueError:
            pass

    # Pure numeric
    plain_match = re.match(r'^([0-9]+(?:\.[0-9]+)?)$', clean)
    if plain_match:
        try:
            return clean, float(plain_match.group(1)), None
        except ValueError:
            pass

    # Qualitative (Trace, Positive, etc.)
    return clean, None, None

def compute_flag(
    value_numeric: Optional[float],
    low: Optional[float],
    high: Optional[float],
    qualitative_value: Optional[str] = None,
    source_provided: bool = True,
    operator: Optional[str] = None,
    fhir_mode: bool = False
) -> FlagCategory:
    """
    Deterministically computes the clinical lab flag.
    NON-NEGOTIABLE SAFETY RULE:
    If source document did not explicitly provide a reference range,
    strictly return FlagCategory.RANGE_NOT_PROVIDED (or UNAVAILABLE). Never hallucinate!
    """
    if not source_provided:
        return FlagCategory.RANGE_NOT_PROVIDED

    # 1. Qualitative value checks
    if qualitative_value:
        norm_val = qualitative_value.strip().lower()
        normal_qualifiers = ["negative", "non-reactive", "normal", "not detected", "none seen", "absent", "clear"]
        abnormal_qualifiers = ["positive", "reactive", "abnormal", "detected", "trace", "present", "elevated"]

        if norm_val in normal_qualifiers:
            return FlagCategory.NORMAL
        if norm_val in abnormal_qualifiers:
            if fhir_mode or norm_val in ["trace", "present", "elevated"]:
                return FlagCategory.ABNORMAL_QUALITATIVE
            return FlagCategory.HIGH

    # If both bounds are missing and no explicit range was parsed
    if low is None and high is None:
        return FlagCategory.RANGE_NOT_PROVIDED

    # 2. Numeric with relational operators (<0.01, >1000)
    if value_numeric is not None:
        if operator in [">", ">="]:
            if high is not None and value_numeric >= high:
                return FlagCategory.HIGH
            return FlagCategory.NORMAL

        if operator in ["<", "<="]:
            if low is not None and value_numeric <= low:
                return FlagCategory.LOW
            return FlagCategory.NORMAL

        # Standard numeric bounds
        if low is None and high is not None:
            if value_numeric > high:
                return FlagCategory.HIGH
            return FlagCategory.NORMAL

        if low is not None and high is None:
            if value_numeric < low:
                return FlagCategory.LOW
            return FlagCategory.NORMAL

        if low is not None and high is not None:
            if value_numeric < low:
                return FlagCategory.LOW
            elif value_numeric > high:
                return FlagCategory.HIGH
            else:
                return FlagCategory.NORMAL

    return FlagCategory.RANGE_NOT_PROVIDED
