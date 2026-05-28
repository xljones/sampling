from dataclasses import dataclass
from typing import Optional
from flask_login import UserMixin


@dataclass
class User(UserMixin):
    id: int
    username: str
    created_at: Optional[str] = None
