from config import TODAY
import csv
from datetime import date

def read_csv_patient_data(file_path):
    # Receives a CSV file and outputs patient_data
    patient_data = {}
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            patient_id = row['patient_id']
            claim_id = row['claim_id']


            service_date = date.fromisoformat(row["service_date"])
            days_past = (TODAY - service_date).days

            patient_balance = float(row["patient_balance"])
            insurance_balance = float(row["insurance_balance"])
            total_balance = float(row["total_balance"])
            claim_status = row["claim_status"]

            if patient_id not in patient_data:
                patient_data[patient_id] = {}

            patient_data[patient_id][claim_id] = {
                "service_date": service_date,
                "days_past": days_past,
                "patient_balance": patient_balance,
                "insurance_balance": insurance_balance,
                "total_balance": total_balance,
                "claim_status": claim_status
            }

    return patient_data