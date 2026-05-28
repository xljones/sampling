from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    created_at: Optional[str] = None
