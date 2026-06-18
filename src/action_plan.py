import csv
from pathlib import Path


RISK_SCORE = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def get_row_priority(row):
    risk_level = str(row.get("risk_level", "")).lower()

    return (
        RISK_SCORE.get(risk_level, 0),
        to_float(row.get("total_balance")),
        to_int(row.get("days_past")),
    )


def build_unique_action_rows(combined_report_path):
    combined_report_path = Path(combined_report_path)

    if not combined_report_path.exists():
        return []

    with open(combined_report_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    unique_claims = {}

    for row in rows:
        claim_key = (
            row.get("patient_id", ""),
            row.get("claim_id", ""),
        )

        if claim_key not in unique_claims:
            unique_claims[claim_key] = row
        else:
            current_row = unique_claims[claim_key]

            if get_row_priority(row) > get_row_priority(current_row):
                unique_claims[claim_key] = row

    sorted_rows = sorted(
        unique_claims.values(),
        key=get_row_priority,
        reverse=True,
    )

    return sorted_rows


def generate_action_plan(combined_report_path, top_n=5):
    action_rows = build_unique_action_rows(combined_report_path)

    lines = []
    lines.append("")
    lines.append("Recommended Action Plan")
    lines.append("-----------------------")

    if not action_rows:
        lines.append("- No claim-level follow-up actions were generated.")
        return lines

    risk_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    action_counts = {}

    def claim_word(count):
        return "claim" if count == 1 else "claims"

    for row in action_rows:
        risk_level = str(row.get("risk_level", "")).lower()
        recommended_action = row.get("recommended_action", "Review claim")

        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

        action_counts[recommended_action] = action_counts.get(recommended_action, 0) + 1

    critical_count = risk_counts["critical"]
    high_count = risk_counts["high"]
    medium_count = risk_counts["medium"]
    low_count = risk_counts["low"]

    lines.append(
        f"- Worklist contains {len(action_rows)} unique flagged {claim_word(len(action_rows))}: "
        f"{critical_count} critical, {high_count} high, {medium_count} medium, and {low_count} low."
    )

    top_priority_rows = action_rows[:top_n]

    lines.append(
        f"- Start with the top {len(top_priority_rows)} priority "
        f"{claim_word(len(top_priority_rows))} listed below."
    )

    if action_counts:
        top_action = max(action_counts, key=action_counts.get)
        lines.append(f"- Most common recommended action: {top_action}.")

    largest_claim = max(
        action_rows,
        key=lambda row: to_float(row.get("total_balance")),
    )

    lines.append(
        "- Largest single claim at risk: "
        f"{largest_claim.get('claim_id', 'Unknown claim')} | "
        f"${to_float(largest_claim.get('total_balance')):,.2f} | "
        f"{to_int(largest_claim.get('days_past'))} days past service."
    )

    lines.append("")
    lines.append(f"Top {top_n} Priority Claims")
    lines.append("---------------------")

    for row in action_rows[:top_n]:
        risk_level = str(row.get("risk_level", "unknown")).title()
        claim_id = row.get("claim_id", "Unknown claim")
        payer = row.get("payer", "Unknown payer")
        total_balance = to_float(row.get("total_balance"))
        days_past = to_int(row.get("days_past"))
        recommended_action = row.get("recommended_action", "Review claim")

        lines.append(
            f"- {risk_level} | Claim {claim_id} | {payer} | "
            f"${total_balance:,.2f} | {days_past} days | {recommended_action}"
        )

    return lines