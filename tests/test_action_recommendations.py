from action_recommendations import get_recommended_action, get_priority_reason

def test_get_recommended_action():
    reports_by_category = [
                {
                "category_type": "balances_over_1000",
                "statement": "Outstanding total balances over $1,000",
                "report": "large_balances"
                },
                {
                "category_type": "balances_overdue_past_60_days",
                "statement": "Outstanding patient balances overdue 60 days",
                "report": "find_owed_money"
                }
    ]

    actions = []
    for category_report in reports_by_category:
        category_type = category_report["category_type"]

        actions.append(get_recommended_action(category_type, claim_info=None))

    assert "Contact patient about overdue balance" in actions
    assert "Prioritize review due to high outstanding balance" in actions

def test_get_priority_reason(category_type=0, claim_info=None):
    claim_info = {
        "days_past": 120,
        "total_balance": 1000.00,
        "claim_status": "submitted",
    }

    result = get_priority_reason(category_type=None, claim_info=claim_info)

    assert "submitted" in result
    assert "120 days past service date" in result
    assert "$1,000.00 total balance" in result