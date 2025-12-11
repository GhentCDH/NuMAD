import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent

# load environment variables for development
# in production (docker), env variables are loaded by Docker (.env)
load_dotenv(ROOT / "dev.env")

CSV = ROOT / "data" / "numad-data-20251208.csv"

_db_host = os.getenv("DB_HOST")
_db_name = os.getenv("DB_NAME")
_db_user = os.getenv("DB_USER")
_db_password = os.getenv("DB_PASS")
DB_STRING = f"postgresql://{_db_user}:{_db_password}@{_db_host}:5432/{_db_name}"
