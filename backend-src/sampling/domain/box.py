from dataclasses import dataclass


@dataclass
class Box:
    id: int
    barcode: str
    name: str | None = None
    location: str | None = None
    notes: str | None = None
    created_at: str | None = None
