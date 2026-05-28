import os
import sys

os.environ.setdefault("SECRET_KEY", "change-me")
os.environ.setdefault("FLASK_DEBUG", "0")

sys.path.insert(0, os.path.join(os.environ["HOME"], "sampling", "backend-src"))

from wsgi import application  # noqa: E402
