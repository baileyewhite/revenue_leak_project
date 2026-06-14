def get_recommended_action(category_type, claim_info):
    '''
    # For later logic
    claim_status = claim_info["claim_status"]
    days_past = claim_info["days_past"]
    total_balance = claim_info["total_balance"]
    '''

    if category_type == "balances_overdue_past_60_days":
        return "Contact patient about overdue balance"

    if category_type == "balances_over_1000":
        return "Prioritize review due to high outstanding balance"

    if category_type == "denied_insurance_claims":
        return "Review denial and prepare correction or appeal"

    if category_type == "old_submitted_claims":
        return "Follow up with payer on aging submitted claim"

    if category_type == "pending_insurance_claims":
        return "Check payer status and confirm next processing step"

    if category_type == "unresolved_appealed_claims":
        return "Review appeal status and follow up with payer"

    return "Review claim for follow-up"

def get_priority_reason(category_type, claim_info):
    # Category_type parameter for later logic
    days_past = claim_info["days_past"]
    total_balance = claim_info["total_balance"]
    claim_status = claim_info["claim_status"]

    return (
        f"Status: {claim_status}; "
        f"{days_past} days past service date; "
        f"${total_balance:,.2f} total balance"
    )