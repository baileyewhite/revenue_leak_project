from data_loader import read_csv_patient_data
from summary import calculate_unique_claim_exposure, generate_all_reports

# 1. Read 2 combined reports: current, & comparing
# 2. Then we have two patient_data dictionaries to compare
# 3. Compare them for a simple test by finding the length difference



def generate_report_comparison(input_report, compare_report, compare_path):
    comparison_lines = []

    def add_line(line=""):
        print(line)
        comparison_lines.append(str(line))

    input_claims = {}
    for patient_id, claims in input_report.items():
        for claim_id, claim_info in claims.items():
            claim_key = (patient_id, claim_id)
            input_claims[claim_key] = claim_info

    compare_claims = {}
    for patient_id, claims in compare_report.items():
        for claim_id, claim_info in claims.items():
            claim_key = (patient_id, claim_id)
            compare_claims[claim_key] = claim_info

    new_claims = []
    risk_increase = 0
    for claim_key, claim_info in compare_claims.items():
        if claim_key not in input_claims:
            new_claims.append(claim_key)
            risk_increase += claim_info['total_balance']

    resolved_claims = []
    risk_decrease = 0
    for claim_key, claim_info in input_claims.items():
        if claim_key not in compare_claims:
            resolved_claims.append(claim_key)
            risk_decrease += claim_info['total_balance']

    net_risk_exposure = risk_increase + risk_decrease

    add_line()
    add_line("Trend Comparison Summary")
    add_line("------------------------")

    if compare_report:
        add_line(f"Compared against previous file: {compare_path}")

    add_line(f"New flagged claims: {len(new_claims)}")
    add_line(f"Resolved claims: {len(resolved_claims)}")
    add_line(f"Revenue at risk increased by: ${risk_increase:,.2f}")
    add_line(f"Revenue at risk decreased by: ${risk_decrease:,.2f}")
    add_line(f"Change in revenue risk exposure: ${net_risk_exposure:,.2f}")
    add_line()

    return comparison_lines
