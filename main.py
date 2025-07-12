import logging
from pathlib import Path

# Enables logging.
logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]: %(message)s', level=logging.INFO)

# Creates necessary directories
Path("input").mkdir(parents=True, exist_ok=True)
Path("database").mkdir(parents=True, exist_ok=True)
Path("output").mkdir(parents=True, exist_ok=True)

import bot