from dataclasses import dataclass
from typing import Optional


@dataclass
class Tube:
    id: int
    barcode: str
    box_id: Optional[int] = None
    collection_date: Optional[str] = None
    site_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sample_type: Optional[str] = None
    description: Optional[str] = None
    volume_ml: Optional[float] = None
    weight_g: Optional[float] = None
    depth_cm: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
