import csv
import os
import pytest
from splitter_app.models import Transaction
from splitter_app.persistence import CSVRepository

def test_load_all_nonexistent(tmp_path):
    # TC-P1: loading when CSV does not exist returns empty list
    repo = CSVRepository(str(tmp_path / "txns.csv"))
    assert repo.load_all() == []

def test_save_and_load(tmp_path):
    # TC-P2: save one transaction and reload it
    path = tmp_path / "txns.csv"
    repo = CSVRepository(str(path))
    txn = Transaction("C001", "Coffee", "Vic", "2025-07-14", "general", "Food & Drinks", 0.5, 5.0)
    repo.save(txn)
    loaded = repo.load_all()
    assert len(loaded) == 1
    assert loaded[0] == txn

def test_legacy_format_parsing(tmp_path):
    # TC-P3: handle legacy CSV with split label "(1/2 each)"
    path = tmp_path / "txns.csv"
    row = ["A003", "Dinner", "Adrian", "trip", "2025-07-12", "30.00", "Food & Drinks", "Even (1/2 each)"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    repo = CSVRepository(str(path))
    loaded = repo.load_all()
    assert len(loaded) == 1
    txn = loaded[0]
    assert txn.serial_number == "A003"
    assert txn.split == pytest.approx(0.5)
    assert txn.amount == pytest.approx(30.0)

def test_delete_removes_serial(tmp_path):
    # TC-P4: delete one entry, ensure only the other remains
    path = tmp_path / "txns.csv"
    repo = CSVRepository(str(path))
    txn1 = Transaction("D001", "Movie", "Adrian", "2025-07-10", "general", "Other", 1.0, 12.0)
    txn2 = Transaction("D002", "Snack", "Vic",    "2025-07-11", "general", "Food & Drinks", 0.5, 6.0)
    repo.save(txn1)
    repo.save(txn2)
    repo.delete("D001")
    loaded = repo.load_all()
    assert len(loaded) == 1
    assert loaded[0].serial_number == "D002"
