import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(os.environ["HOME"]) / "dirtnap" / ".env")

sys.path.insert(0, os.path.join(os.environ["HOME"], "dirtnap", "backend-src"))

from wsgi import application  # noqa: E402
