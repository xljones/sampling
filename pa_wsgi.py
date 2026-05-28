import os
import sys

sys.path.insert(0, os.path.join(os.environ["HOME"], "sampling", "backend-src"))

from wsgi import application  # noqa: E402
