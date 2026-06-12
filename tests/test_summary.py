from summary import calculate_unique_claim_exposure

def test_calculate_unique_claim_exposure_does_not_double_count_claims():
    report_1 = {
        "P001": {
            "C001": {"total_balance": 1000.00}
        }
    }

    report_2 = {
        "P001": {
            "C001": {"total_balance": 1000.00}
        }
    }

    claim_count, total_exposure = calculate_unique_claim_exposure([report_1, report_2])

    assert claim_count == 1
    assert total_exposure == 1000.00