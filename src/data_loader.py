from config import TODAY, COLUMN_ALIASES
import csv
from datetime import date

def read_csv_patient_data(file_path):
    # Receives a CSV file and outputs patient_data
    patient_data = {}
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        column_map = map_columns(reader.fieldnames)

        for row in reader:
            patient_id = row[column_map['patient_id']]
            claim_id = row[column_map['claim_id']]


            service_date = date.fromisoformat(row[column_map["service_date"]])
            days_past = (TODAY - service_date).days

            patient_balance = float(row[column_map["patient_balance"]])
            insurance_balance = float(row[column_map["insurance_balance"]])
            total_balance = float(row[column_map["total_balance"]])
            claim_status = row[column_map["claim_status"]]

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

def normalize_header(header):
    return header.strip().lower().replace(" ", "_")

def find_column(headers, possible_names):
    normalized_headers = {}
    for header in headers:
        normalized_headers[normalize_header(header)] = header

    for possible_name in possible_names:
        normalized_name = normalize_header(possible_name)
        if normalized_name in normalized_headers:
            return normalized_headers[normalized_name]

    return None

def map_columns(headers):
    column_map = {}

    for standard_name, possible_names in COLUMN_ALIASES.items():
        actual_column = find_column(headers, possible_names)

        if actual_column is None:
            raise ValueError(f"Missing required column for: {standard_name}")

        column_map[standard_name] = actual_column

    return column_map