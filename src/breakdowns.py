from leak_categories import find_denied_insurance_claims


def generate_breakdown(report_data, group_field, balance_field="total_balance"):
    breakdown = {}

    for patient_id, claims in report_data.items():
        for claim_id, claim_info in claims.items():
            group_value = claim_info.get(group_field)

            if not group_value:
                continue

            if group_value not in breakdown:
                breakdown[group_value] = {
                    "claim_count": 0,
                    "total_balance": 0
                }

            breakdown[group_value]["claim_count"] += 1
            breakdown[group_value]["total_balance"] += claim_info.get(balance_field, 0)

    return breakdown


def find_top_breakdown_item(breakdown):
    if not breakdown:
        return None

    top_name = None
    top_info = None

    for name, info in breakdown.items():
        if top_info is None or info["total_balance"] > top_info["total_balance"]:
            top_name = name
            top_info = info

    return {
        "name": top_name,
        "claim_count": top_info["claim_count"],
        "total_balance": top_info["total_balance"],
    }


def format_top_breakdown_line(label, top_item):
    if top_item is None:
        return f"{label}: No data available"

    return (
        f"{label}: "
        f"{top_item['name']} | "
        f"{top_item['claim_count']} claims | "
        f"${top_item['total_balance']:,.2f}"
    )


def breakdown_summary(report_data):
    breakdown_lines = []

    def add_line(line=""):
        print(line)
        breakdown_lines.append(str(line))

    denied_claims = find_denied_insurance_claims(report_data)

    payer_denied_breakdown = generate_breakdown(
        denied_claims,
        group_field="payer",
        balance_field="insurance_balance"
    )

    provider_breakdown = generate_breakdown(
        report_data,
        group_field="provider",
        balance_field="total_balance"
    )

    procedure_breakdown = generate_breakdown(
        report_data,
        group_field="procedure_code_description",
        balance_field="total_balance"
    )

    top_payer = find_top_breakdown_item(payer_denied_breakdown)
    top_provider = find_top_breakdown_item(provider_breakdown)
    top_procedure = find_top_breakdown_item(procedure_breakdown)

    add_line()
    add_line("Breakdown Summary")
    add_line("-----------------")
    add_line(format_top_breakdown_line("Top payer by denied insurance balance", top_payer))
    add_line(format_top_breakdown_line("Top provider by total revenue at risk", top_provider))
    add_line(format_top_breakdown_line("Top procedure type by total revenue at risk", top_procedure))

    return breakdown_lines