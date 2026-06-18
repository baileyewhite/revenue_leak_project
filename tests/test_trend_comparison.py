from trend_comparison import generate_report_comparison


def test_generate_report_comparison_counts_new_and_resolved_claims():
    input_report = {
        "P001": {
            "C001": {
                "total_balance": 500.00
            },
            "C002": {
                "total_balance": 300.00
            }
        }
    }

    compare_report = {
        "P001": {
            "C001": {
                "total_balance": 500.00
            },
            "C003": {
                "total_balance": 900.00
            }
        }
    }

    result = generate_report_comparison(
        input_report=input_report,
        compare_report=compare_report,
        compare_path="data/previous.csv"
    )

    assert "Trend Comparison Summary" in result
    assert "New flagged claims in new file: 1" in result
    assert "Resolved claims in new file: 1" in result
    assert "Revenue at risk increased by: $900.00" in result
    assert "Revenue at risk decreased by: $300.00" in result
    assert "Net change in revenue risk exposure: $600.00" in result

def test_generate_report_comparison_when_reports_match():
    input_report = {
        "P001": {
            "C001": {
                "total_balance": 500.00
            }
        }
    }

    compare_report = {
        "P001": {
            "C001": {
                "total_balance": 500.00
            }
        }
    }

    result = generate_report_comparison(
        input_report=input_report,
        compare_report=compare_report,
        compare_path="data/previous.csv"
    )

    assert "New flagged claims in new file: 0" in result
    assert "Resolved claims in new file: 0" in result
    assert "Revenue at risk increased by: $0.00" in result
    assert "Revenue at risk decreased by: $0.00" in result
    assert "Net change in revenue risk exposure: $0.00" in result