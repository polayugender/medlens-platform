from enum import Enum

class SourceProvenance(str, Enum):
    USER_INPUT = "user_input"
    AI_EXTRACTED = "ai_extracted"
    AI_GENERATED = "ai_generated"

class FlagCategory(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    UNAVAILABLE = "unavailable"
