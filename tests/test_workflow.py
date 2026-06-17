import json
import pandas as pd

import config
import report_writer
import summary as summary_module
import workflow

from workflow import run_revenue_leak_analysis


def redirect_output_to_tmp(tmp_path, monkeypatch):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    monkeypatch.setattr(config, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(report_writer, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(summary_module, "OUTPUT_DIR", output_dir, raising=False)
    monkeypatch.setattr(workflow, "OUTPUT_DIR", output_dir)

    return output_dir


def write_test_csv(path, rows):
    header = (
        "patient_id,claim_id,service_date,patient_balance,"
        "insurance_balance,total_balance,claim_status,"
        "payer,provider,procedure_code_description\n"
    )

    path.write_text(
        header + "\n".join(rows) + "\n",
        encoding="utf-8"
    )

    return path


def test_workflow_creates_reports_summary_metadata_and_validation_file(tmp_path, monkeypatch):
    output_dir = redirect_output_to_tmp(tmp_path, monkeypatch)

    input_csv = write_test_csv(
        tmp_path / "test_claims.csv",
        [
            "P001,C001,2024-01-01,250.00,0.00,250.00,patient_due,Self Pay,Provider A,D0120 Periodic Exam",
            "P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Payer A,Provider B,D2740 Crown",
            "P003,C003,2024-02-01,0.00,900.00,900.00,submitted,Payer B,Provider C,D4341 Scaling/Root Planing",
            "P004,C004,not-a-date,100.00,0.00,100.00,patient_due,Self Pay,Provider A,D1110 Cleaning",
        ],
    )

    results = run_revenue_leak_analysis(
        input_path=input_csv,
        compare_path=None,
        mask_identifiers=False,
    )

    assert results["success"] is True
    assert results["message"] == "Analysis complete."

    assert results["executive_summary_path"].exists()
    assert results["combined_report_path"].exists()
    assert results["metadata_path"].exists()

    assert results["validation_errors_path"] is not None
    assert results["validation_errors_path"].exists()

    assert results["total_validation_errors"] >= 1
    assert results["has_compare_file"] is False

    output_file_names = [
        output_path.name
        for output_path in results["output_paths"]
    ]

    assert "combined_revenue_leak_report.csv" in output_file_names
    assert "validation_errors.csv" in output_file_names
    assert "run_metadata.json" in output_file_names

    summary_text = "\n".join(results["summary_lines"])

    assert "Revenue Leak Summary" in summary_text
    assert "Total unique claims flagged:" in summary_text
    assert "Total unique revenue at risk:" in summary_text
    assert "Breakdown Summary" in summary_text
    assert "Revenue Reports Created" in summary_text
    assert "run_metadata.json" in summary_text

    metadata = json.loads(results["metadata_path"].read_text(encoding="utf-8"))

    assert metadata["comparison_file"] is None
    assert metadata["identifier_masking_enabled"] is False
    assert metadata["validation_errors"] >= 1
    assert metadata["invalid_rows_skipped"] >= 1
    assert metadata["reports_created"] >= 1

    assert results["combined_report_path"].parent == output_dir


def test_workflow_with_comparison_adds_trend_summary_and_metadata(tmp_path, monkeypatch):
    redirect_output_to_tmp(tmp_path, monkeypatch)

    input_csv = write_test_csv(
        tmp_path / "input_claims.csv",
        [
            "P001,C001,2024-01-01,500.00,0.00,500.00,patient_due,Self Pay,Provider A,D0120 Periodic Exam",
            "P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Payer A,Provider B,D2740 Crown",
        ],
    )

    compare_csv = write_test_csv(
        tmp_path / "compare_claims.csv",
        [
            "P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Payer A,Provider B,D2740 Crown",
            "P003,C003,2024-02-01,0.00,900.00,900.00,submitted,Payer B,Provider C,D4341 Scaling/Root Planing",
        ],
    )

    results = run_revenue_leak_analysis(
        input_path=input_csv,
        compare_path=compare_csv,
        mask_identifiers=False,
    )

    assert results["success"] is True
    assert results["has_compare_file"] is True

    summary_text = "\n".join(results["summary_lines"])

    assert "Trend Comparison Summary" in summary_text
    assert "New flagged claims" in summary_text
    assert "Resolved claims" in summary_text
    assert "Net change in revenue risk exposure" in summary_text

    metadata = json.loads(results["metadata_path"].read_text(encoding="utf-8"))

    assert metadata["comparison_file"] is not None
    assert metadata["identifier_masking_enabled"] is False


def test_workflow_masks_patient_and_claim_identifiers_in_reports(tmp_path, monkeypatch):
    redirect_output_to_tmp(tmp_path, monkeypatch)

    input_csv = write_test_csv(
        tmp_path / "masking_claims.csv",
        [
            "P001,C001,2024-01-01,500.00,0.00,500.00,patient_due,Self Pay,Provider A,D0120 Periodic Exam",
            "P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Payer A,Provider B,D2740 Crown",
        ],
    )

    results = run_revenue_leak_analysis(
        input_path=input_csv,
        compare_path=None,
        mask_identifiers=True,
    )

    assert results["success"] is True

    combined_text = results["combined_report_path"].read_text(encoding="utf-8")

    assert "P001" not in combined_text
    assert "P002" not in combined_text
    assert "C001" not in combined_text
    assert "C002" not in combined_text

    assert "PATIENT_001" in combined_text
    assert "CLAIM_001" in combined_text

    metadata = json.loads(results["metadata_path"].read_text(encoding="utf-8"))

    assert metadata["identifier_masking_enabled"] is True


def test_workflow_returns_failure_when_no_valid_rows_exist(tmp_path, monkeypatch):
    redirect_output_to_tmp(tmp_path, monkeypatch)

    input_csv = write_test_csv(
        tmp_path / "invalid_claims.csv",
        [
            ",C001,not-a-date,not-money,0.00,250.00,patient_due,Self Pay,Provider A,D0120 Periodic Exam",
            "P002,,bad-date,0.00,bad-money,1200.00,denied,Payer A,Provider B,D2740 Crown",
        ],
    )

    results = run_revenue_leak_analysis(
        input_path=input_csv,
        compare_path=None,
        mask_identifiers=False,
    )

    assert results["success"] is False
    assert results["message"] == "No valid rows found. Reports were not generated."
    assert results["summary_lines"] == []
    assert results["output_paths"] == []
    assert len(results["validation_errors"]) >= 1


def test_workflow_combined_report_contains_expected_worklist_columns(tmp_path, monkeypatch):
    redirect_output_to_tmp(tmp_path, monkeypatch)

    input_csv = write_test_csv(
        tmp_path / "worklist_claims.csv",
        [
            "P001,C001,2024-01-01,500.00,0.00,500.00,patient_due,Self Pay,Provider A,D0120 Periodic Exam",
            "P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Payer A,Provider B,D2740 Crown",
        ],
    )

    results = run_revenue_leak_analysis(
        input_path=input_csv,
        compare_path=None,
        mask_identifiers=False,
    )

    assert results["success"] is True

    combined_df = pd.read_csv(results["combined_report_path"])

    expected_columns = {
        "category_type",
        "category_statement",
        "patient_id",
        "claim_id",
        "provider",
        "payer",
        "service_date",
        "days_past",
        "patient_balance",
        "insurance_balance",
        "total_balance",
        "claim_status",
        "risk_level",
        "recommended_action",
        "priority_reason",
    }

    assert expected_columns.issubset(set(combined_df.columns))
    assert len(combined_df) >= 1