from config import TODAY, BASE_DIR
from leak_categories import REPORT_CATEGORIES
from pathlib import Path
from report_writer import write_report_to_csv, write_combined_report_to_csv, write_validation_errors_to_csv

## HELPER FUNCTIONS ##
def format_relative_path(path):
    path = Path(path)

    try:
        return path.relative_to(BASE_DIR)
    except ValueError:
        return path


def report_paths_summary(output_paths):
    lines = []

    lines.append("")
    lines.append("Revenue Reports Created")
    lines.append("-----------------------")

    for output_path in output_paths:
        relative_path = str(format_relative_path(output_path)).replace("\\", "/")
        lines.append(f"- {relative_path}")

    return lines


def key_takeaways_summary(unique_claim_count, unique_total_revenue_risk):
    lines = []

    lines.append("")
    lines.append("Key Takeaways")
    lines.append("-------------")
    lines.append(f"- {unique_claim_count} unique claims were flagged for follow-up.")
    lines.append(
        f"- ${unique_total_revenue_risk:,.2f} in unique revenue is currently at risk."
    )
    lines.append(
        "- Category totals may overlap because one claim can appear in multiple report categories."
    )
    lines.append(
        "- Review the combined revenue leak report for claim-level recommended actions."
    )

    return lines

### MAIN GENERATOR ###
def generate_all_reports(data):
    reports = []
    output_paths = []
    reports_by_category = []
    category_summary_lines = []

    for category in REPORT_CATEGORIES:
        report = category["finder"](data)

        output_path = write_report_to_csv(report, category["category_type"])

        summary_line = category_summary(
            report,
            category["statement"],
            category["balance_field"]
        )
        category_summary_lines.append(summary_line)
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

    return unique_claim_count, unique_total_exposure, output_paths, category_summary_lines

def category_summary(report, statement, balance_field):
    # Prints a summary of patients who applied to category into console
    total_owed = 0
    claim_count = 0

    risk_counts = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }

    for patient_id, claims in report.items():
        claim_count += len(claims)
        for claim_id, claim_info in claims.items():
            total_owed += claim_info[balance_field]

            if claim_info['risk_level'] == "Low":
                risk_counts['low'] += 1
            if claim_info['risk_level'] == "Medium":
                risk_counts['medium'] += 1
            if claim_info['risk_level'] == "High":
                risk_counts['high'] += 1
            if claim_info['risk_level'] == "Critical":
                risk_counts['critical'] += 1

    risk_summary = format_risk_summary(risk_counts)
    return f"{statement}: {claim_count} claims | ${total_owed:,.2f} | {risk_summary}"

def total_summary(data, validation_errors, input_path=None):
    summary_lines = []

    def add_line(line=""):
        print(line)
        summary_lines.append(str(line))

    add_line(str(TODAY))
    add_line()
    add_line("Revenue Leak Summary")
    add_line("--------------------")
    if input_path:
        relative_input_file = str(format_relative_path(input_path)).replace("\\", "/")
        add_line(f"Input file: {relative_input_file}")
        add_line()

    if validation_errors:
        invalid_rows = len({error["row_number"] for error in validation_errors})
        total_errors = len(validation_errors)

        add_line("*Reports were generated using valid rows only*")
        add_line(f"{invalid_rows} invalid row(s) were skipped.")
        add_line(f"{total_errors} error(s) were found.")
        add_line()

    unique_claim_count, unique_total_revenue_risk, output_paths, category_summary_lines = generate_all_reports(data)

    for line in category_summary_lines:
        add_line(line)

    add_line()
    add_line("Total Exposure")
    add_line("--------------------")
    add_line(f"Total unique claims flagged: {unique_claim_count}")
    add_line(f"Total unique revenue at risk: ${unique_total_revenue_risk:,.2f}")
    add_line()
    add_line("Note: Category totals may overlap because one claim can be flagged in multiple categories. Unique revenue at risk removes duplicate claims.")
    for line in key_takeaways_summary(unique_claim_count, unique_total_revenue_risk):
        add_line(line)
    '''
    add_line("Revenue Reports Created:")

    for output_path in output_paths:
        add_line(f"- {output_path}")
    '''

    return summary_lines, output_paths

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

def format_risk_summary(risk_counts):
    risk_order = ["low", "medium", "high", "critical"]
    parts = []

    for risk_level in risk_order:
        count = risk_counts.get(risk_level, 0)

        if count > 0:
            parts.append(f"{count} {risk_level}")

    if not parts:
        return "Risk: none"

    return "Risk: " + ", ".join(parts)