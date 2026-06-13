from deidentification import deidentify_patient_data


def test_deidentify_patient_data_masks_patient_and_claim_ids():
    patient_data = {
        "P123": {
            "C456": {
                "service_date": "2025-01-01",
                "days_past": 100,
                "patient_balance": 100.00,
                "insurance_balance": 0.00,
                "total_balance": 100.00,
                "claim_status": "patient_due",
                "risk_level": "Medium"
            }
        }
    }

    result = deidentify_patient_data(patient_data)

    assert "PATIENT_001" in result
    assert "CLAIM_001" in result["PATIENT_001"]
    assert "P123" not in result

def test_deidentify_patient_data_preserves_claim_info():
    patient_data = {
        "P123": {
            "C456": {
                "total_balance": 100.00,
                "claim_status": "patient_due"
            }
        }
    }

    result = deidentify_patient_data(patient_data)

    claim_info = result["PATIENT_001"]["CLAIM_001"]

    assert claim_info["total_balance"] == 100.00
    assert claim_info["claim_status"] == "patient_due"