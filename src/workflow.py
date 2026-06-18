from datetime import date

from config import BASE_DIR, OUTPUT_DIR
from data_loader import read_csv_patient_data
from path_utils import resolve_input_csv_path
from rules import merge_rules
from summary import (
    total_summary,
    report_paths_summary,
    format_relative_path,
)
from breakdowns import breakdown_summary
from trend_comparison import generate_report_comparison
from deidentification import deidentify_patient_data
from report_writer import (
    write_executive_summary,
    write_run_metadata,
    write_validation_errors_to_csv,
)


def get_summary_value(summary_lines, prefix):
    for line in summary_lines:
        if line.startswith(prefix):
            return line.replace(prefix, "").strip()

    return "N/A"


def count_claims(patient_data):
    return sum(
        len(claims)
        for claims in patient_data.values()
    )


def count_invalid_rows(validation_errors):
    return len({
        error["row_number"]
        for error in validation_errors
        if "row_number" in error
    })


def normalize_path(path):
    if path is None:
        return None

    return resolve_input_csv_path(path)


def build_run_metadata(
    input_path,
    compare_path,
    patient_data,
    validation_errors,
    compare_validation_errors,
    mask_identifiers,
    output_paths,
    rules
):
    all_validation_errors = validation_errors + compare_validation_errors

    return {
        "run_date": str(date.today()),
        "input_file": str(format_relative_path(input_path)).replace("\\", "/"),
        "comparison_file": (
            str(format_relative_path(compare_path)).replace("\\", "/")
            if compare_path
            else None
        ),
        "valid_claims_analyzed": count_claims(patient_data),
        "invalid_rows_skipped": count_invalid_rows(all_validation_errors),
        "validation_errors": len(all_validation_errors),
        "identifier_masking_enabled": mask_identifiers,
        "rules_used": rules,
        "reports_created": len(output_paths) + 2,
    }


def run_revenue_leak_analysis(
    input_path,
    compare_path=None,
    mask_identifiers=False,
    rules=None
):
    rules = merge_rules(rules)

    input_path = normalize_path(input_path)
    compare_path = normalize_path(compare_path)

    patient_data, validation_errors = read_csv_patient_data(input_path)

    compare_validation_errors = []
    comparison_lines = []

    if compare_path:
        compare_data, compare_validation_errors = read_csv_patient_data(compare_path)

        comparison_lines = generate_report_comparison(
            input_report=patient_data,
            compare_report=compare_data,
            compare_path=compare_path,
        )

    if not patient_data:
        return {
            "success": False,
            "message": "No valid rows found. Reports were not generated.",
            "summary_lines": [],
            "output_paths": [],
            "validation_errors": validation_errors,
            "compare_validation_errors": compare_validation_errors,
            "comparison_lines": comparison_lines,
        }

    if mask_identifiers:
        patient_data = deidentify_patient_data(patient_data)

    summary_lines, output_paths = total_summary(
        patient_data,
        validation_errors,
        input_path=input_path,
        rules=rules
    )

    breakdown_lines = breakdown_summary(patient_data)
    summary_lines.extend(breakdown_lines)

    if comparison_lines:
        summary_lines.extend(comparison_lines)

    all_validation_errors = validation_errors + compare_validation_errors

    validation_errors_path = None

    if all_validation_errors:
        validation_errors_path = write_validation_errors_to_csv(all_validation_errors)
        output_paths.append(validation_errors_path)

    metadata = build_run_metadata(
        input_path=input_path,
        compare_path=compare_path,
        patient_data=patient_data,
        validation_errors=validation_errors,
        compare_validation_errors=compare_validation_errors,
        mask_identifiers=mask_identifiers,
        output_paths=output_paths,
        rules=rules
    )

    metadata_path = write_run_metadata(metadata)
    output_paths.append(metadata_path)

    report_path_lines = report_paths_summary(output_paths)
    summary_lines.extend(report_path_lines)

    executive_summary_path = write_executive_summary(summary_lines)

    total_claims_flagged = get_summary_value(
        summary_lines,
        "Total unique claims flagged:",
    )

    total_revenue_at_risk = get_summary_value(
        summary_lines,
        "Total unique revenue at risk:",
    )

    return {
        "success": True,
        "message": "Analysis complete.",
        "summary_lines": summary_lines,
        "output_paths": output_paths,
        "validation_errors": validation_errors,
        "compare_validation_errors": compare_validation_errors,
        "all_validation_errors": all_validation_errors,
        "comparison_lines": comparison_lines,
        "executive_summary_path": executive_summary_path,
        "metadata_path": metadata_path,
        "validation_errors_path": validation_errors_path,
        "combined_report_path": OUTPUT_DIR / "combined_revenue_leak_report.csv",
        "total_claims_flagged": total_claims_flagged,
        "total_revenue_at_risk": total_revenue_at_risk,
        "total_validation_errors": len(all_validation_errors),
        "has_compare_file": compare_path is not None,
        "metadata": metadata,
    }