from datetime import date
from pathlib import Path

TODAY = date.today()
PAST_DUE_LIMIT = 60
MAX_LATE_BALANCE = 0
MAX_TOTAL_BALANCE = 1000

SAMPLE_DATA_FILE = "pseudo_dental_revenue_leaks.csv"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / SAMPLE_DATA_FILE
OUTPUT_DIR = BASE_DIR / "output"