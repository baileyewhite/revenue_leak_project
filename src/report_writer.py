from config import OUTPUT_DIR
from action_recommendations import get_recommended_action, get_priority_reason
import csv

def write_report_to_csv(report, category_type):
    # Generates a CSV report of the list of patients and their info that applied to category
    headers = [
        "Patient ID",
        "Claim ID",
        "Patient Balance",
        "Insurance Balance",
        "Total Balance",
        "Days Since Service",
        "Claim Status",
        "Risk Level"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{category_type}.csv"

    with open(output_path, 'w', newline='', encoding = "utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for patient_id, claims in report.items():
            for claim_id, claim_info in claims.items():
                writer.writerow({
                    "Patient ID": patient_id,
                    "Claim ID": claim_id,
                    "Patient Balance": claim_info['patient_balance'],
                    "Insurance Balance": claim_info['insurance_balance'],
                    "Total Balance": claim_info['total_balance'],
                    "Days Since Service": claim_info['days_past'],
                    "Claim Status": claim_info['claim_status'],
                    "Risk Level": claim_info['risk_level']
                })
    return output_path

def write_combined_report_to_csv(reports_by_category):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / "combined_revenue_leak_report.csv"

    fieldnames = [
        "category_type",
        "category_statement",
        "patient_id",
        "claim_id",
        "service_date",
        "days_past",
        "patient_balance",
        "insurance_balance",
        "total_balance",
        "claim_status",
        "risk_level",
        "recommended_action",
        "priority_reason"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for category_report in reports_by_category:
            category_type = category_report["category_type"]
            category_statement = category_report["statement"]
            report = category_report["report"]

            for patient_id, claims in report.items():
                for claim_id, claim_info in claims.items():
                    writer.writerow({
                        "category_type": category_type,
                        "category_statement": category_statement,
                        "patient_id": patient_id,
                        "claim_id": claim_id,
                        "service_date": claim_info["service_date"],
                        "days_past": claim_info["days_past"],
                        "patient_balance": claim_info["patient_balance"],
                        "insurance_balance": claim_info["insurance_balance"],
                        "total_balance": claim_info["total_balance"],
                        "claim_status": claim_info["claim_status"],
                        "risk_level": claim_info["risk_level"],
                        "recommended_action": get_recommended_action(category_type, claim_info),
                        "priority_reason": get_priority_reason(category_type, claim_info)
                    })

    return output_path

def write_validation_errors_to_csv(validation_errors):
    headers = [
        "row_number",
        "field_name",
        "value",
        "message",]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"validation_errors.csv"

    with open(output_path, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(validation_errors)

    return output_path

def write_executive_summary(summary_lines):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"executive_summary.txt"

    with open(output_path, 'w', encoding="utf-8") as file:
        for line in summary_lines:
            file.write(line + '\n')

    return output_path