# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
from datetime import date

TODAY = date.today()
PAST_DUE_LIMIT = 60
MAX_BALANCE = 0

TEST_FILE_PATH = "C:/Users/bayca/revenue_leak_project/data/pseudo_dental_revenue_leaks.csv"

def read_csv_patient_data(file_path):
    patient_data = {}
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for patient in reader:
            patient_data[patient["patient_id"]] = patient

    return patient_data

def find_owed_money(patient_data):
    owed_money = {}
    for patient_id in patient_data:
        service_date = date.fromisoformat(patient_data[patient_id]["service_date"])
        days_past = (TODAY - service_date).days
        patient_balance = float(patient_data[patient_id]["patient_balance"])
        claim_status = patient_data[patient_id]["claim_status"]

        if patient_balance > MAX_BALANCE and days_past > PAST_DUE_LIMIT and claim_status == "patient_due":
            owed_money[patient_id] = {
                "patient_balance": patient_balance,
                "claim_id": patient_data[patient_id]["claim_id"],
                "days_past": days_past,
                "claim_status": claim_status
            }
    return owed_money

def print_report(report):
    for patient_id in report:
        print(f"Patient ID: {patient_id} | Claim ID: {report[patient_id]['claim_id']} | Patient Balance: ${report[patient_id]["patient_balance"]} | Past Due: {report[patient_id]["days_past"]} days")

def print_revenue_info(report):
    total_owed = 0
    for patient_id in report:
        total_owed += report[patient_id]["patient_balance"]

    print(f"Patients with outstanding balances for over 60 days: {len(report)}")
    print(f"Total outstanding balance: ${total_owed:,.2f}")

def write_report_to_csv(report):
    headers = ["Patient ID", "Claim ID", "Patient Balance", "Days Since Service", "Claim Status"]

    with open("C:/Users/bayca/revenue_leak_project/output/dataoutput.csv", 'w', newline='', encoding = "utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for patient_id, patient_info in report.items():
            writer.writerow({
                "Patient ID": patient_id,
                "Claim ID": patient_info['claim_id'],
                "Patient Balance": patient_info['patient_balance'],
                "Days Since Service": patient_info['days_past'],
                "Claim Status": patient_info['claim_status']
            })

def print_summary(report):
    print(TODAY)
    print(f"Report Created: C:/Users/bayca/revenue_leak_project/output/dataoutput.csv")
    print_revenue_info(report)
    print(f"Oldest Balance: {find_oldest_balance(report)} days")
    print(f"Largest Balance: ${find_largest_balance(report):,.2f}")

def find_oldest_balance(report):
    temp = 0
    for patient_id, patient_info in report.items():
        if patient_info['days_past'] > temp:
            temp = patient_info['days_past']
    return temp

def find_largest_balance(report):
    temp = 0
    for patient_id, patient_info in report.items():
        if patient_info['patient_balance'] > temp:
            temp = patient_info['patient_balance']
    return temp

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    report = find_owed_money(read_csv_patient_data(TEST_FILE_PATH))
    write_report_to_csv(report)
    print_summary(report)
    '''
    print(report)

    print_revenue_info(report)
    print_report(report)
    '''