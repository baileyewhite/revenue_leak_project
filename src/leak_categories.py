from config import MAX_LATE_BALANCE
from rules import merge_rules

def add_claim_to_report(report, patient_id, claim_id, claim_info, rules=None):
    if patient_id not in report:
        report[patient_id] = {}

    copied_claim_info = claim_info.copy()
    copied_claim_info["risk_level"] = risk_level(copied_claim_info, rules)

    report[patient_id][claim_id] = copied_claim_info

def risk_level(claim_info, rules=None):
    rules = merge_rules(rules)

    total_balance = claim_info["total_balance"]
    days_past = claim_info["days_past"]
    claim_status = claim_info["claim_status"]

    if (
            total_balance >= rules["critical_balance_threshold"]
            or days_past >= rules["critical_days_past"]
    ):
        return "critical"

    elif (
            total_balance >= rules["high_balance_threshold"]
            or days_past >= rules["high_days_past"]
            or claim_status in ["denied", "rejected"]
    ):
        return "high"

    elif (
            total_balance >= rules["medium_balance_threshold"]
            or days_past >= rules["medium_days_past"]
    ):
        return "medium"

    else:
        return "low"

### CATEGORY FINDERS ###
### MAKES REPORTS ###
def find_owed_money(patient_data, rules=None):
    # Generates report that detects if patient has had a balance for over max_due_limit (default: 60) days
    rules = merge_rules(rules)
    owed_money = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['patient_balance'] > MAX_LATE_BALANCE and claim_info['days_past'] > rules["patient_overdue_days"] and claim_info['claim_status'] == "patient_due":
                add_claim_to_report(owed_money, patient_id, claim_id, claim_info, rules=rules)
    return owed_money

def find_large_balances(patient_data, rules=None):
    # Generates report that detects extreme total balances over $1,000
    rules = merge_rules(rules)
    large_balances = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if float(claim_info['total_balance']) > rules["large_balance_threshold"]:
                add_claim_to_report(large_balances, patient_id, claim_id, claim_info, rules=rules)
    return large_balances

def find_denied_insurance_claims(patient_data, rules=None):
    rules = merge_rules(rules)
    denied_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] in ["denied", "rejected"] and claim_info['insurance_balance'] > 0:
                add_claim_to_report(denied_claims, patient_id, claim_id, claim_info, rules=rules)
    return denied_claims

def find_old_submitted_claims(patient_data, rules=None):
    # Finds insurance claims that have been submitted for a long period of time and haven't been resolved
    rules = merge_rules(rules)
    old_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] == "submitted" and claim_info['insurance_balance'] > 0 and claim_info['days_past'] > rules["old_submitted_days"]:
                add_claim_to_report(old_claims, patient_id, claim_id, claim_info, rules=rules)
    return old_claims

def find_pending_insurance_claims(patient_data, rules=None):
    # Finds insurance claims that have been pending for over past due limit (60) days
    rules = merge_rules(rules)
    pending_submitted_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] == "pending_insurance" and claim_info['insurance_balance'] > 0 and claim_info['days_past'] > rules["pending_insurance_days"]:
                add_claim_to_report(pending_submitted_claims, patient_id, claim_id, claim_info, rules=rules)
    return pending_submitted_claims

def find_appealed_claims(patient_data, rules=None):
    # Finds appealed claims that haven't been resolved with remaining balances
    rules = merge_rules(rules)
    appealed_claims = {}
    for patient_id, claims in patient_data.items():
        for claim_id, claim_info in claims.items():
            if claim_info['claim_status'] == "appealed" and claim_info['total_balance'] > 0:
                add_claim_to_report(appealed_claims, patient_id, claim_id, claim_info, rules=rules)
    return appealed_claims

### CATEGORIES LIST ###
REPORT_CATEGORIES = [
    {
        "category_type": "balances_overdue_past_60_days",
        "statement": "Outstanding patient balances overdue past {patient_overdue_days} days",
        "balance_field": "patient_balance",
        "finder": find_owed_money
    },
    {
        "category_type": "balances_over_1000",
        "statement": "Outstanding total balances over ${large_balance_threshold}",
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
        "statement": "Outstanding submitted insurance claims older than {old_submitted_days} days",
        "balance_field": "insurance_balance",
        "finder": find_old_submitted_claims
    },
    {
        "category_type": "pending_insurance_claims",
        "statement": "Outstanding pending insurance claims older than {pending_insurance_days} days",
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