import csv
from datetime import date
import os

TODAY = date.today()
PAST_DUE_LIMIT = 60
MAX_LATE_BALANCE = 0
MAX_TOTAL_BALANCE = 1000

SAMPLE_FILE_PATH = "C:/Users/bayca/revenue_leak_project/data/pseudo_dental_revenue_leaks.csv"

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

    output_folder = "C:/Users/bayca/revenue_leak_project/output"
    os.makedirs(output_folder, exist_ok=True)

    output_path = f"{output_folder}/{category_type}.csv"

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
def category_summary(report, statement, balance_field):
    # Prints a summary of patients who applied to category into console
    #print(TODAY)
    #print(f"Report Created: C:/Users/bayca/revenue_leak_project/output/{category_type}.csv")
    total_owed = 0
    claim_count = 0

    for patient_id, claims in report.items():
        claim_count += len(claims)

        for claim_id, claim_info in claims.items():
            total_owed += claim_info[balance_field]
    print(f"{statement}: {claim_count} claims | ${total_owed:,.2f}")

    return total_owed
    #print(f"Oldest Balance: {find_oldest_balance(report)} days")
    #print(f"Largest Balance: ${find_largest_balance(report, balance_field):,.2f}")

def total_summary(data):
    print(TODAY)
    print("Revenue Leak Summary")
    print("--------------------")
    unique_claim_count, unique_total_revenue_risk, output_paths = generate_all_reports(data)
    print("--------------------")
    print(f"Total unique claims flagged: {unique_claim_count}")
    print(f"Total unique revenue at risk: ${unique_total_revenue_risk:,.2f}")

    print()
    print("Reports Created:")
    for output_path in output_paths:
        print(f"- {output_path}")


def calculate_unique_claim_exposure(reports):
    seen_claims = set()
    total_exposure = 0
    claim_count = 0

    for report in reports:
        for patient_id, claims in report.items():
            for claim_id, claim_info in claims.items():
                claim_key = (patient_id, claim_id)

                if claim_key not in seen_claims:
                    seen_claims.add(claim_key)
                    total_exposure += claim_info["total_balance"]
                    claim_count += 1

    return claim_count, total_exposure

def add_claim_to_report(report, patient_id, claim_id, claim_info):
    if patient_id not in report:
        report[patient_id] = {}

    report[patient_id][claim_id] = {
        "patient_balance": claim_info["patient_balance"],
        "insurance_balance": claim_info["insurance_balance"],
        "total_balance": claim_info["total_balance"],
        "days_past": claim_info["days_past"],
        "claim_status": claim_info["claim_status"]
    }

### CATEGORY FINDERS ###
### MAKES REPORTS ###
def find_owed_money(patient_data):
    # Generates report that detects if patient has had a balance for over max_due_limit (default: 60) days
    owed_money = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['patient_balance'] > MAX_LATE_BALANCE and claim_info['days_past'] > PAST_DUE_LIMIT and claim_info['claim_status'] == "patient_due":
                add_claim_to_report(owed_money, patient_id, claim_id, claim_info)
    return owed_money

def find_large_balances(patient_data):
    # Generates report that detects extreme total balances over $1,000
    large_balances = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if float(claim_info['total_balance']) > MAX_TOTAL_BALANCE:
                add_claim_to_report(large_balances, patient_id, claim_id, claim_info)
    return large_balances

def find_denied_insurance_claims(patient_data):
    denied_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] in ["denied", "rejected"] and claim_info['insurance_balance'] > 0:
                add_claim_to_report(denied_claims, patient_id, claim_id, claim_info)
    return denied_claims

def find_old_submitted_claims(patient_data):
    # Finds insurance claims that have been submitted for a long period of time and haven't been resolved
    old_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] == "submitted" and claim_info['insurance_balance'] > 0 and claim_info['days_past'] > PAST_DUE_LIMIT:
                add_claim_to_report(old_claims, patient_id, claim_id, claim_info)
    return old_claims

def find_pending_insurance_claims(patient_data):
    # Finds insurance claims that have been pending for over past due limit (60) days
    pending_submitted_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] == "pending_insurance" and claim_info['insurance_balance'] > 0 and claim_info['days_past'] > PAST_DUE_LIMIT:
                add_claim_to_report(pending_submitted_claims, patient_id, claim_id, claim_info)
    return pending_submitted_claims

def find_appealed_claims(patient_data):
    # Finds appealed claims that haven't been resolved with remaining balances
    appealed_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] == "appealed" and claim_info['total_balance'] > 0:
                add_claim_to_report(appealed_claims, patient_id, claim_id, claim_info)
    return appealed_claims


### CATEGORIES LIST ###
REPORT_CATEGORIES = [
    {
        "category_type": "balances_overdue_past_60_days",
        "statement": "Outstanding patient balances overdue 60 days",
        "balance_field": "patient_balance",
        "finder": find_owed_money
    },
    {
        "category_type": "balances_over_1000",
        "statement": "Outstanding total balances over $1,000",
        "balance_field": "total_balance",
        "finder": find_large_balances
    },
    {
        "category_type": "denied_insurance_claims",
        "statement": "Outstanding denied insurance claims",
        "balance_field": "insurance_balance",
        "finder": find_denied_insurance_claims
    },
    {
        "category_type": "old_submitted_claims",
        "statement": "Outstanding old insurance claims",
        "balance_field": "insurance_balance",
        "finder": find_old_submitted_claims
    },
    {
        "category_type": "pending_insurance_claims",
        "statement": "Outstanding pending insurance claims",
        "balance_field": "insurance_balance",
        "finder": find_pending_insurance_claims
    },
    {
        "category_type": "unresolved_appealed_claims",
        "statement": "Outstanding appealed insurance claims",
        "balance_field": "total_balance",
        "finder": find_appealed_claims
    }
]

### MAIN GENERATOR ###
def generate_all_reports(data):
    reports = []
    output_paths = []

    for category in REPORT_CATEGORIES:
        report = category["finder"](data)

        output_path = write_report_to_csv(report, category["category_type"])

        category_summary(
            report,
            category["statement"],
            category["balance_field"]
        )

        reports.append(report)
        output_paths.append(output_path)

    unique_claim_count, unique_total_exposure = calculate_unique_claim_exposure(reports)

    return unique_claim_count, unique_total_exposure, output_paths

if __name__ == '__main__':
    patient_data = read_csv_patient_data(SAMPLE_FILE_PATH)
    total_summary(patient_data)