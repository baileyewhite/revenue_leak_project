from config import TODAY
from leak_categories import REPORT_CATEGORIES
from report_writer import write_report_to_csv, write_combined_report_to_csv

### MAIN GENERATOR ###
def generate_all_reports(data):
    reports = []
    output_paths = []
    reports_by_category = []

    for category in REPORT_CATEGORIES:
        report = category["finder"](data)

        output_path = write_report_to_csv(report, category["category_type"])

        category_summary(
            report,
            category["statement"],
            category["balance_field"]
        )

        reports.append(report)

        reports_by_category.append({
            "category_type": category["category_type"],
            "statement": category["statement"],
            "report": report
        })

        output_paths.append(output_path)

    combined_output_path = write_combined_report_to_csv(reports_by_category)
    output_paths.append(combined_output_path)

    unique_claim_count, unique_total_exposure = calculate_unique_claim_exposure(reports)

    return unique_claim_count, unique_total_exposure, output_paths

def category_summary(report, statement, balance_field):
    # Prints a summary of patients who applied to category into console
    total_owed = 0
    claim_count = 0

    for patient_id, claims in report.items():
        claim_count += len(claims)

        for claim_id, claim_info in claims.items():
            total_owed += claim_info[balance_field]
    if claim_count == 0:
        print(f"No claims found for {statement}")
    print(f"{statement}: {claim_count} claims | ${total_owed:,.2f}")

    return total_owed

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