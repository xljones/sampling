from dataclasses import dataclass


@dataclass
class Core:
    id: int
    barcode: str
    name: str | None = None
    location_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    site_name: str | None = None
    collection_date: str | None = None
    depth_cm: float | None = None
    collector: str | None = None
    sample_type: str | None = None
    owner: str | None = None
    notes: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
