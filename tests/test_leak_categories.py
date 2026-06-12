from leak_categories import find_large_balances

def test_find_large_balances_flags_claim_over_1000():
    patient_data = {
        "P001": {
            "C001": {
                "service_date": "2025-01-15",
                "days_past": 100,
                "patient_balance": 100.00,
                "insurance_balance": 950.00,
                "total_balance": 1050.00,
                "claim_status": "submitted",
            }
        }
    }

    result = find_large_balances(patient_data)

    assert "P001" in result
    assert "C001" in result["P001"]

def test_find_large_balances_ignores_claim_under_1000():
    patient_data = {
        "P001": {
            "C001": {
                "service_date": "2025-01-15",
                "days_past": 100,
                "patient_balance": 100.00,
                "insurance_balance": 200.00,
                "total_balance": 300.00,
                "claim_status": "submitted",
            }
        }
    }

    result = find_large_balances(patient_data)

    assert result == {}