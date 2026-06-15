from config import TODAY, REQUIRED_COLUMN_ALIASES, OPTIONAL_COLUMN_ALIASES
import csv
from datetime import date

def read_csv_patient_data(file_path):
    # Receives a CSV file and outputs patient_data
    patient_data = {}
    validation_errors = []

    with open(file_path, 'r', newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        column_map = map_columns(reader.fieldnames)

        for row_number, row in enumerate(reader, start=2):
            row_has_error = False

            patient_id = row[column_map["patient_id"]]
            claim_id = row[column_map["claim_id"]]
            claim_status = row[column_map["claim_status"]]

            if not patient_id.strip():
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "patient_id",
                    "value": patient_id,
                    "message": "Missing patient ID"
                })
                row_has_error = True

            if not claim_id.strip():
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "claim_id",
                    "value": claim_id,
                    "message": "Missing claim ID"
                })
                row_has_error = True

            if not claim_status.strip():
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "claim_status",
                    "value": claim_status,
                    "message": "Missing claim status"
                })
                row_has_error = True

            try:
                service_date = parse_date(row[column_map["service_date"]], row_number)
                days_past = (TODAY - service_date).days
            except ValueError as error:
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "service_date",
                    "value": row[column_map["service_date"]],
                    "message": str(error),
                })
                row_has_error = True

            try:
                patient_balance = parse_money(
                        row[column_map["patient_balance"]],
                        "patient_balance",
                        row_number
                    )
            except ValueError as error:
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "patient_balance",
                    "value": row[column_map["patient_balance"]],
                    "message": str(error),
                })
                row_has_error = True

            try:
                insurance_balance = parse_money(
                        row[column_map["insurance_balance"]],
                        "insurance_balance",
                        row_number
                    )
            except ValueError as error:
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "insurance_balance",
                    "value": row[column_map["insurance_balance"]],
                    "message": str(error),
                })
                row_has_error = True

            try:
                total_balance = parse_money(
                        row[column_map["total_balance"]],
                        "total_balance",
                        row_number
                    )
            except ValueError as error:
                validation_errors.append({
                    "row_number": row_number,
                    "field_name": "total_balance",
                    "value": row[column_map["total_balance"]],
                    "message": str(error),
                })
                row_has_error = True

            payer = ""
            if "payer" in column_map:
                payer = row.get(column_map.get("payer"), "").strip()

            provider = ""
            if "provider" in column_map:
                provider = row.get(column_map.get("provider"), "").strip()

            procedure_code_description = ""
            if "procedure_code_description" in column_map:
                procedure_code_description = row.get(
                    column_map["procedure_code_description"],
                    ""
                ).strip()


            if row_has_error:
                continue

            if patient_id not in patient_data:
                patient_data[patient_id] = {}

            patient_data[patient_id][claim_id] = {
                "service_date": service_date,
                "days_past": days_past,
                "patient_balance": patient_balance,
                "insurance_balance": insurance_balance,
                "total_balance": total_balance,
                "claim_status": claim_status,
                "payer": payer,
                "provider": provider,
                "procedure_code_description": procedure_code_description
            }

    return patient_data, validation_errors

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

    normalized_headers = {
        normalize_header(header): header
        for header in headers
    }

    # Required columns: missing one should stop the program.
    for standard_name, possible_names in REQUIRED_COLUMN_ALIASES.items():
        found_column = None

        for possible_name in possible_names:
            normalized_name = normalize_header(possible_name)

            if normalized_name in normalized_headers:
                found_column = normalized_headers[normalized_name]
                break

        if found_column is None:
            raise ValueError(
                f"Missing required column for: {standard_name}. "
                f"Accepted names are: {possible_names}"
            )

        column_map[standard_name] = found_column

    # Optional columns: include them if found, otherwise skip them.
    for standard_name, possible_names in OPTIONAL_COLUMN_ALIASES.items():
        found_column = None

        for possible_name in possible_names:
            normalized_name = normalize_header(possible_name)

            if normalized_name in normalized_headers:
                found_column = normalized_headers[normalized_name]
                break

        if found_column is not None:
            column_map[standard_name] = found_column

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