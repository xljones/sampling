from ._blueprint import bp
from . import tubes, boxes, cores  # noqa: F401 — registers routes on bp

__all__ = ["bp"]
