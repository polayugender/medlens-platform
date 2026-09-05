from typing import Optional, List
from pydantic import BaseModel, Field

class ReportMetadataSchema(BaseModel):
    report_date: Optional[str] = Field(None, description="Report date in YYYY-MM-DD or as found in document")
    report_type: Optional[str] = Field(None, description="e.g. Comprehensive Metabolic Panel, Lipid Profile")
    facility_name: Optional[str] = Field(None, description="Name of the laboratory or clinic")

class ExtractedTestItemSchema(BaseModel):
    test_name: str = Field(..., description="Standard clinical test name verbatim from document")
    value: str = Field(..., description="Observed result string")
    value_numeric: Optional[float] = Field(None, description="Parsed numeric value, null if qualitative")
    unit: Optional[str] = Field(None, description="Unit of measurement e.g. mg/dL, mmol/L, or null")
    reference_range_raw: Optional[str] = Field(None, description="Reference range explicitly printed in document or null")
    raw_snippet: str = Field(..., description="Verbatim quote from source document for verification and audit")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score of the extraction")

class ExtractionResultSchema(BaseModel):
    report_metadata: ReportMetadataSchema
    extracted_tests: List[ExtractedTestItemSchema]
