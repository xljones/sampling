from dataclasses import dataclass
from typing import Optional


@dataclass
class Box:
    id: int
    barcode: str
    name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
