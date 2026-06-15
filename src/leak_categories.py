from config import MAX_LATE_BALANCE, MAX_TOTAL_BALANCE, PAST_DUE_LIMIT

def add_claim_to_report(report, patient_id, claim_id, claim_info):
    if patient_id not in report:
        report[patient_id] = {}

    claim_info_copy = claim_info.copy()

    claim_info_copy['risk_level'] = risk_level(claim_info_copy)

    report[patient_id][claim_id] = claim_info_copy

def risk_level(claim_info):
    total_balance = claim_info['total_balance']
    days_past = claim_info['days_past']
    claim_status = claim_info['claim_status']

    if total_balance >= 2500 or days_past >= 240:
        return "Critical"
    elif total_balance >= 1500 or claim_status in ['denied', 'rejected']:
        return "High"
    elif total_balance >= 750 or days_past >= 90:
        return "Medium"
    else:
        return "Low"

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