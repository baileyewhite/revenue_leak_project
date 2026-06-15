from breakdowns import (
    generate_breakdown,
    find_top_breakdown_item,
    format_top_breakdown_line,
    breakdown_summary,
)


def test_generate_breakdown_groups_claims_and_totals_balance():
    report_data = {
        "P001": {
            "C001": {
                "provider": "Dr. Patel",
                "total_balance": 1000.00,
            },
            "C002": {
                "provider": "Dr. Patel",
                "total_balance": 500.00,
            },
        },
        "P002": {
            "C003": {
                "provider": "Dr. Smith",
                "total_balance": 700.00,
            }
        },
    }

    result = generate_breakdown(
        report_data,
        group_field="provider",
        balance_field="total_balance",
    )

    assert result["Dr. Patel"]["claim_count"] == 2
    assert result["Dr. Patel"]["total_balance"] == 1500.00

    assert result["Dr. Smith"]["claim_count"] == 1
    assert result["Dr. Smith"]["total_balance"] == 700.00


def test_generate_breakdown_skips_missing_group_value():
    report_data = {
        "P001": {
            "C001": {
                "provider": "Dr. Patel",
                "total_balance": 1000.00,
            },
            "C002": {
                "provider": "",
                "total_balance": 500.00,
            },
            "C003": {
                "total_balance": 300.00,
            },
        }
    }

    result = generate_breakdown(
        report_data,
        group_field="provider",
        balance_field="total_balance",
    )

    assert "Dr. Patel" in result
    assert "" not in result
    assert len(result) == 1
    assert result["Dr. Patel"]["claim_count"] == 1
    assert result["Dr. Patel"]["total_balance"] == 1000.00


def test_generate_breakdown_uses_custom_balance_field():
    report_data = {
        "P001": {
            "C001": {
                "payer": "Delta Dental",
                "insurance_balance": 800.00,
                "total_balance": 1000.00,
            },
            "C002": {
                "payer": "Delta Dental",
                "insurance_balance": 400.00,
                "total_balance": 500.00,
            },
        }
    }

    result = generate_breakdown(
        report_data,
        group_field="payer",
        balance_field="insurance_balance",
    )

    assert result["Delta Dental"]["claim_count"] == 2
    assert result["Delta Dental"]["total_balance"] == 1200.00


def test_find_top_breakdown_item_returns_highest_balance():
    breakdown = {
        "Delta Dental": {
            "claim_count": 2,
            "total_balance": 1200.00,
        },
        "United Concordia": {
            "claim_count": 3,
            "total_balance": 3330.00,
        },
    }

    result = find_top_breakdown_item(breakdown)

    assert result == {
        "name": "United Concordia",
        "claim_count": 3,
        "total_balance": 3330.00,
    }


def test_find_top_breakdown_item_returns_none_for_empty_breakdown():
    result = find_top_breakdown_item({})

    assert result is None


def test_format_top_breakdown_line_with_data():
    top_item = {
        "name": "United Concordia",
        "claim_count": 3,
        "total_balance": 3330.00,
    }

    result = format_top_breakdown_line(
        "Top payer by denied insurance balance",
        top_item,
    )

    assert (
        result
        == "Top payer by denied insurance balance: United Concordia | 3 claims | $3,330.00"
    )


def test_format_top_breakdown_line_with_no_data():
    result = format_top_breakdown_line(
        "Top procedure type by total revenue at risk",
        None,
    )

    assert result == "Top procedure type by total revenue at risk: No data available"


def test_breakdown_summary_returns_expected_summary_lines():
    report_data = {
        "P001": {
            "C001": {
                "payer": "United Concordia",
                "provider": "Dr. Patel",
                "procedure_code_description": "D4341 Scaling/Root Planing",
                "claim_status": "denied",
                "days_past": 120,
                "patient_balance": 0.00,
                "insurance_balance": 2000.00,
                "total_balance": 2000.00,
            },
            "C002": {
                "payer": "Delta Dental",
                "provider": "Dr. Smith",
                "procedure_code_description": "D2740 Crown",
                "claim_status": "denied",
                "days_past": 95,
                "patient_balance": 0.00,
                "insurance_balance": 900.00,
                "total_balance": 900.00,
            },
        },
        "P002": {
            "C003": {
                "payer": "MetLife",
                "provider": "Dr. Patel",
                "procedure_code_description": "D4341 Scaling/Root Planing",
                "claim_status": "patient_due",
                "days_past": 150,
                "patient_balance": 1200.00,
                "insurance_balance": 0.00,
                "total_balance": 1200.00,
            }
        },
    }

    result = breakdown_summary(report_data)

    assert "Breakdown Summary" in result
    assert "-----------------" in result

    assert (
        "Top payer by denied insurance balance: "
        "United Concordia | 1 claims | $2,000.00"
    ) in result

    assert (
        "Top provider by total revenue at risk: "
        "Dr. Patel | 2 claims | $3,200.00"
    ) in result

    assert (
        "Top procedure type by total revenue at risk: "
        "D4341 Scaling/Root Planing | 2 claims | $3,200.00"
    ) in result