from datetime import date
from pathlib import Path

TODAY = date.today()
PAST_DUE_LIMIT = 60
MAX_LATE_BALANCE = 0
MAX_TOTAL_BALANCE = 1000

SAMPLE_DATA_FILE = "pseudo_dental_revenue_leaks.csv"
COLUMN_MAPPING_TEST_FILE = "flexible_column_mapping_test.csv"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / SAMPLE_DATA_FILE
OUTPUT_DIR = BASE_DIR / "output"

COLUMN_ALIASES = {
    "patient_id": ["patient_id", "Patient ID", "patient_number", "account_number"],
    "claim_id": ["claim_id", "Claim ID", "claim_number", "encounter_id"],
    "service_date": ["service_date", "last_service_date", "date_of_service", "DOS"],
    "patient_balance": ["patient_balance", "Patient Balance", "amount_due", "patient_due"],
    "insurance_balance": ["insurance_balance", "Insurance Balance", "insurance_due"],
    "total_balance": ["total_balance", "Total Balance", "balance", "outstanding_balance"],
    "claim_status": ["claim_status", "Claim Status", "status"]
}