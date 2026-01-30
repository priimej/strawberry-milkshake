from dataclasses import dataclass
from typing import Optional

@dataclass
class PointOfInterest:
    id: str
    city: str
    name: str
    lat: float
    lng: float
    author: Optional[str] = None
    category: Optional[str] = None
