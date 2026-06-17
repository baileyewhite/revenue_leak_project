import config
import report_writer
import summary as summary_module
import workflow

from workflow import run_revenue_leak_analysis


def test_full_workflow_creates_reports(tmp_path, monkeypatch):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    monkeypatch.setattr(config, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(report_writer, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(summary_module, "OUTPUT_DIR", output_dir, raising=False)
    monkeypatch.setattr(workflow, "OUTPUT_DIR", output_dir)

    input_csv = tmp_path / "test_claims.csv"

    input_csv.write_text(
        """patient_id,claim_id,service_date,patient_balance,insurance_balance,total_balance,claim_status,payer,provider,procedure_code_description
P001,C001,2024-01-01,250.00,0.00,250.00,patient_due,Self Pay,Provider A,D0120 Periodic Exam
P002,C002,2024-01-15,0.00,1200.00,1200.00,denied,Payer A,Provider B,D2740 Crown
P003,C003,2024-02-01,0.00,900.00,900.00,submitted,Payer B,Provider C,D4341 Scaling/Root Planing
P004,C004,not-a-date,100.00,0.00,100.00,patient_due,Self Pay,Provider A,D1110 Cleaning
""",
        encoding="utf-8"
    )

    results = run_revenue_leak_analysis(
        input_path=input_csv,
        compare_path=None,
        mask_identifiers=False,
    )

    assert results["success"] is True
    assert results["executive_summary_path"].exists()
    assert results["combined_report_path"].exists()
    assert results["metadata_path"].exists()
    assert "Revenue Leak Summary" in "\n".join(results["summary_lines"])