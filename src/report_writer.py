from config import OUTPUT_DIR
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
        "Claim Status"]

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
                    "Claim Status": claim_info['claim_status']
                })
    return output_path