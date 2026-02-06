from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class Extracted(BaseModel, Generic[T]):
    value: Optional[T] = Field(
        default=None,
        description="Extracted value. Use null if missing or unclear."
    )
    evidence: Optional[str] = Field(
        default=None,
        description=(
            "Copy the exact substring from the input that supports the value; "
            "include the larger substring which encapsulates the extracted value."
        )
    )
    confidence: float = Field(
        description=(
            "Confidence score from 0.0 to 1.0. "
            "Use 1.0 for explicit, unambiguous matches; "
            "around 0.5 if inferred but not explicit; "
            "below 0.3 if weak or ambiguous; "
            "use 0.0 when value is missing (we prefer value=None)."
        )
    )

ExtractedInt = Extracted[int]
ExtractedFloat = Extracted[float]
ExtractedBool = Extracted[bool]
ExtractedString = Extracted[str]

class RentalSchema(BaseModel):
    price_monthly: ExtractedInt = Field(description="Monthly rent in CAD. If missing or unclear, value=null.")
    bedrooms: ExtractedInt = Field(description="Number of bedrooms. If missing, value=null.")
    bathrooms: ExtractedFloat = Field(description="Number of bathrooms (e.g., 1, 1.5, 2). If missing, value=null.")
    address: ExtractedString = Field(description="Street/address or area name if present. If missing, value=null.")
    utilities_text: ExtractedString = Field(description="Verbatim utilities info (e.g., 'heat, water, electrical, utilities included'). If missing, value=null.")
