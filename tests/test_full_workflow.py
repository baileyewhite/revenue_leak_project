import json
from datetime import date
from pathlib import Path

import config
import data_loader
import report_writer
import summary as summary_module

from data_loader import read_csv_patient_data
from summary import total_summary, report_paths_summary
from breakdowns import breakdown_summary
from report_writer import (
    write_executive_summary,
    write_run_metadata,
    write_validation_errors_to_csv,
)


def test_full_workflow_creates_reports_summary_metadata_and_skips_invalid_rows(
    tmp_path,
    monkeypatch
):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    monkeypatch.setattr(config, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(report_writer, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(summary_module, "OUTPUT_DIR", output_dir, raising=False)
    monkeypatch.setattr(data_loader, "OUTPUT_DIR", output_dir, raising=False)

    input_csv = tmp_path / "full_workflow_input.csv"

    input_csv.write_text(
        """patient_id,claim_id,service_date,patient_balance,insurance_balance,total_balance,claim_status,payer,provider,procedure_code_description
P001,C001,2024-01-01,250.00,0.00,250.00,patient_due,Self Pay,Dr. Smith,D0120 Periodic Oral Evaluation
P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Delta Dental,Dr. Patel,D2740 Crown
P003,C003,not-a-date,100.00,0.00,100.00,patient_due,Self Pay,Dr. Lee,D1110 Cleaning
""",
        encoding="utf-8"
    )

    patient_data, validation_errors = read_csv_patient_data(input_csv)

    valid_claims_analyzed = sum(
        len(claims)
        for claims in patient_data.values()
    )

    assert valid_claims_analyzed == 2
    assert len(validation_errors) >= 1

    if validation_errors:
        validation_errors_path = write_validation_errors_to_csv(validation_errors)
        assert validation_errors_path.exists()
        assert validation_errors_path.name == "validation_errors.csv"

    summary_lines, output_paths = total_summary(
        patient_data,
        validation_errors,
        input_path=input_csv
    )

    breakdown_lines = breakdown_summary(patient_data)
    summary_lines.extend(breakdown_lines)

    invalid_rows_skipped = len({
        error["row_number"]
        for error in validation_errors
    })

    metadata = {
        "run_date": str(date.today()),
        "input_file": str(input_csv),
        "comparison_file": None,
        "valid_claims_analyzed": valid_claims_analyzed,
        "invalid_rows_skipped": invalid_rows_skipped,
        "validation_errors": len(validation_errors),
        "identifier_masking_enabled": False,
        "reports_created": len(output_paths) + 2,
    }

    metadata_path = write_run_metadata(metadata)
    output_paths.append(metadata_path)

    report_path_lines = report_paths_summary(output_paths)
    summary_lines.extend(report_path_lines)

    executive_summary_path = write_executive_summary(summary_lines)

    combined_report_path = output_dir / "combined_revenue_leak_report.csv"

    assert executive_summary_path.exists()
    assert metadata_path.exists()
    assert combined_report_path.exists()

    assert any(
        path.name == "denied_insurance_claims.csv"
        for path in output_paths
    )

    assert any(
        path.name == "combined_revenue_leak_report.csv"
        for path in output_paths
    )

    assert any(
        path.name == "run_metadata.json"
        for path in output_paths
    )

    executive_summary_text = executive_summary_path.read_text(encoding="utf-8")

    assert "Revenue Leak Summary" in executive_summary_text
    assert "Total unique claims flagged:" in executive_summary_text
    assert "Breakdown Summary" in executive_summary_text
    assert "Revenue Reports Created" in executive_summary_text
    assert "run_metadata.json" in executive_summary_text

    metadata_text = metadata_path.read_text(encoding="utf-8")
    metadata_data = json.loads(metadata_text)

    assert metadata_data["valid_claims_analyzed"] == 2
    assert metadata_data["invalid_rows_skipped"] >= 1
    assert metadata_data["validation_errors"] >= 1
    assert metadata_data["identifier_masking_enabled"] is False