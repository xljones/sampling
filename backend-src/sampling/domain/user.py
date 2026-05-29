from dataclasses import dataclass
from datetime import UTC, datetime

from flask_login import UserMixin


@dataclass
class User(UserMixin):
    id: int
    username: str
    created_at: str | None = None
    is_readonly: bool = False
    expires_at: str | None = None

    @property
    def is_active(self):
        if self.expires_at:
            try:
                return datetime.now(UTC) < datetime.fromisoformat(self.expires_at)
            except ValueError:
                pass
        return True
