import pytest
from splitter_app.models import Transaction

def test_from_csv_row_valid():
    # TC-M1: valid CSV row round-trip into a Transaction
    row = ["A001", "Lunch", "Adrian", "2025-07-14", "general", "Food & Drinks", "0.5", "12.34"]
    txn = Transaction.from_csv_row(row)
    assert txn.serial_number == "A001"
    assert txn.description == "Lunch"
    assert txn.paid_by == "Adrian"
    assert txn.date == "2025-07-14"
    assert txn.group == "general"
    assert txn.category == "Food & Drinks"
    assert txn.split == pytest.approx(0.5)
    assert txn.amount == pytest.approx(12.34)

def test_to_csv_row_round_trip():
    # TC-M2: ensure to_csv_row matches expected formatting
    txn = Transaction("B002", "Taxi", "Vic", "2025-07-13", "trip", "Travel", 0.3, 45.6)
    row = txn.to_csv_row()
    assert row == ["B002", "Taxi", "Vic", "2025-07-13", "trip", "Travel", "0.3", "45.60"]
