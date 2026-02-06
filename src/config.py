from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ConfidenceThresholds:
    warn: float = 0.6
    error: float = 0.3
    
@dataclass(frozen=True)
class PricePolicy:
    min_price: int = 300

    base_max: int = 1700
    per_bed_max: int = 1000

    cap_max: int = 9000         
    unknown_max: int = 9000     

    def max_for_bedrooms(self, beds: Optional[int]) -> int:
        if beds is None:
            return self.unknown_max
        b = max(0, beds)
        return min(self.cap_max, self.base_max + self.per_bed_max * b)

@dataclass(frozen=True)
class BedroomsRange:
    min: int = 0
    max: int = 10

@dataclass(frozen=True)
class BathroomsRange:
    min: int = 1
    max: int = 10