from config import TODAY, COLUMN_ALIASES
import csv
from datetime import date

def read_csv_patient_data(file_path):
    # Receives a CSV file and outputs patient_data
    patient_data = {}

    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            column_map = map_columns(reader.fieldnames)

            for row_number, row in enumerate(reader, start=2):
                patient_id = row[column_map['patient_id']]
                claim_id = row[column_map['claim_id']]

                service_date = parse_date(row[column_map["service_date"]], row_number)
                days_past = (TODAY - service_date).days

                patient_balance = parse_money(
                        row[column_map["patient_balance"]],
                        "patient_balance",
                        row_number
                    )
                insurance_balance = parse_money(
                        row[column_map["insurance_balance"]],
                        "insurance_balance",
                        row_number
                    )
                total_balance = parse_money(
                        row[column_map["total_balance"]],
                        "total_balance",
                        row_number
                    )
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

    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}")
        return {}

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
            raise ValueError(
                f"Missing required column for: {standard_name}. "
                f"Accepted names are: {possible_names}"
            )

        column_map[standard_name] = actual_column

    return column_map

def parse_date(value, row_number):
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Invalid date on row {row_number}: {value}")

def parse_money(value, field_name, row_number):
    try:
        return float(value)
    except ValueError:
        raise ValueError(
            f"Invalid money value for {field_name} on row {row_number}: {value}"
        )