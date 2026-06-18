DEFAULT_RULES = {
    "patient_overdue_days": 60,
    "large_balance_threshold": 1000.00,
    "old_submitted_days": 60,
    "pending_insurance_days": 60,

    "medium_balance_threshold": 750.00,
    "medium_days_past": 90,
    "high_balance_threshold": 1500.00,
    "high_days_past": 180,
    "critical_balance_threshold": 3000.00,
    "critical_days_past": 240,
}


def merge_rules(rule_overrides=None):
    rules = DEFAULT_RULES.copy()

    if rule_overrides:
        rules.update(rule_overrides)

    return rules