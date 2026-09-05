from enum import Enum

class SourceProvenance(str, Enum):
    USER_INPUT = "user_input"
    AI_EXTRACTED = "ai_extracted"
    AI_GENERATED = "ai_generated"
    CLINICIAN_EDITED = "clinician_edited"

class FlagCategory(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    UNAVAILABLE = "unavailable"
    ABNORMAL_QUALITATIVE = "abnormal_qualitative"
    # RANGE_NOT_PROVIDED aliases to "unavailable" for backwards DB compatibility
    RANGE_NOT_PROVIDED = "unavailable"
