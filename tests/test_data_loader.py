import pytest
from datetime import date
from data_loader import parse_money, parse_date, map_columns

def test_parse_money_valid():
    result = parse_money("100.00", "patient_balance", 2)
    assert result == 100.00

def test_parse_money_invalid():
    with pytest.raises(ValueError) as error:
        parse_money("abc", "patient_balance", 4)

    assert "Invalid money value" in str(error.value)
    assert "row 4" in str(error.value)

def test_parse_date_valid_date():
    result = parse_date("2025-01-15", 2)

    assert result == date(2025, 1, 15)

def test_parse_date_invalid_date():
    with pytest.raises(ValueError) as error:
        parse_date("not-a-date", 3)

    assert "Invalid date on row 3" in str(error.value)

def test_map_columns_accepts_alternate_headers():
    headers = [
        "Patient ID",
        "claim_number",
        "last_service_date",
        "PATIENT BALANCE",
        "insurance_due",
        "Outstanding_Balance",
        "Status",
    ]

    result = map_columns(headers)

    assert result["patient_id"] == "Patient ID"
    assert result["claim_id"] == "claim_number"
    assert result["service_date"] == "last_service_date"
    assert result["patient_balance"] == "PATIENT BALANCE"

def test_map_columns_missing_required_column():
    headers = [
        "Patient ID",
        "claim_number",
        "last_service_date",
    ]

    with pytest.raises(ValueError) as error:
        map_columns(headers)

    assert "Missing required column" in str(error.value)