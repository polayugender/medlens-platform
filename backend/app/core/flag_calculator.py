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
    if not raw_range or not isinstance(raw_range, str):
        return None, None
    
    clean = raw_range.strip()
    if not clean or clean.lower() in ["unavailable", "n/a", "none", "not provided", "range_unavailable"]:
        return None, None
    
    # Check less-than pattern: e.g. "< 200", "<= 100", "<=150"
    lt_match = re.match(r'^(?:<|<=|less than)\s*([0-9]+(?:\.[0-9]+)?)$', clean, re.IGNORECASE)
    if lt_match:
        try:
            return None, float(lt_match.group(1))
        except ValueError:
            pass

    # Check greater-than pattern: e.g. "> 40", ">= 50", ">50"
    gt_match = re.match(r'^(?:>|>=|greater than)\s*([0-9]+(?:\.[0-9]+)?)$', clean, re.IGNORECASE)
    if gt_match:
        try:
            return float(gt_match.group(1)), None
        except ValueError:
            pass

    # Check range pattern: "low - high" or "low to high"
    range_match = re.match(r'^([0-9]+(?:\.[0-9]+)?)\s*(?:-|–|—|to)\s*([0-9]+(?:\.[0-9]+)?)$', clean, re.IGNORECASE)
    if range_match:
        try:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return low, high
        except ValueError:
            pass

    return None, None

def compute_flag(
    value_numeric: Optional[float],
    low: Optional[float],
    high: Optional[float],
    qualitative_value: Optional[str] = None
) -> FlagCategory:
    """
    Deterministically computes the clinical flag.
    RULE: Only flags if reference range is explicitly known.
    Never hallucinates or estimates.
    """
    # If numeric value is available
    if value_numeric is not None:
        if low is None and high is None:
            return FlagCategory.UNAVAILABLE
        
        # Upper bound only (e.g. < 200)
        if low is None and high is not None:
            if value_numeric > high:
                return FlagCategory.HIGH
            return FlagCategory.NORMAL
        
        # Lower bound only (e.g. > 40)
        if low is not None and high is None:
            if value_numeric < low:
                return FlagCategory.LOW
            return FlagCategory.NORMAL
        
        # Two-sided interval
        if low is not None and high is not None:
            if value_numeric < low:
                return FlagCategory.LOW
            elif value_numeric > high:
                return FlagCategory.HIGH
            else:
                return FlagCategory.NORMAL

    # For qualitative values (e.g. Negative, Normal, Reactive, Detected)
    if qualitative_value:
        norm_val = qualitative_value.strip().lower()
        if norm_val in ["negative", "non-reactive", "normal", "not detected", "none seen"]:
            return FlagCategory.NORMAL
        if norm_val in ["positive", "reactive", "abnormal", "detected"]:
            return FlagCategory.HIGH

    return FlagCategory.UNAVAILABLE
