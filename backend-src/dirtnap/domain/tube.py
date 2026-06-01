from dataclasses import dataclass


@dataclass
class Tube:
    id: int
    barcode: str
    box_id: int | None = None
    core_id: int | None = None
    sample_date: str | None = None
    site_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    sample_type: str | None = None
    description: str | None = None
    volume_ml: float | None = None
    weight_g: float | None = None
    depth_cm: float | None = None
    created_at: str | None = None
    updated_at: str | None = None
