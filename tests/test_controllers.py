import pytest

from splitter_app.controllers import SplitterController
from splitter_app.models import Transaction
from splitter_app.config import CATEGORY_MAP

"""Unit tests for the SplitterController class.
This test suite verifies the business logic within the SplitterController,
ensuring correct calculations and state management. It uses dummy/mock objects
(`DummySignal`, `DummyWindow`) to simulate the view component's interface,
allowing the controller to be tested in isolation from the actual GUI framework.
Tests cover core functionalities such as:
- Allocation of shares among participants under various split scenarios.
- Generation of unique transaction serial numbers.
- Calculation of group-level financial summaries.
"""
class DummySignal:
    def __init__(self):
        self._slots = []
    def connect(self, slot):
        self._slots.append(slot)
    def emit(self, *args, **kwargs):
        for s in self._slots:
            s(*args, **kwargs)
class DummyWindow:
    """Minimal stub with the signals and widgets the controller expects."""
    def __init__(self):
        # mimic the Qt signals
        self.transaction_added   = DummySignal()
        self.transaction_deleted = DummySignal()

        # summary_label needs setText/text
        self.summary_label = type("Lbl", (), {
            "text": "",
            "setText": lambda self, txt: setattr(self, "text", txt)
        })()

        # these won't be used in these tests, but must exist
        self.table = None
        self.group_summary_table = None

def test_allocate_shares_basic():
    # TC-C2: 50/50 split
    parts = ["Adrian", "Vic"]
    shares = SplitterController._allocate_shares(100.0, 0.5, "Adrian", parts)
    assert shares["Adrian"] == pytest.approx(50.0)
    assert shares["Vic"]    == pytest.approx(50.0)

def test_allocate_shares_payer_all():
    # TC-C3: split=1.0 → payer covers all
    parts = ["Adrian", "Vic"]
    shares = SplitterController._allocate_shares(80.0, 1.0, "Vic", parts)
    assert shares["Vic"]     == pytest.approx(80.0)
    assert shares["Adrian"]  == pytest.approx(0.0)

def test_allocate_shares_rounding_dust():
    # TC-C4: check rounding dust absorption with 3 participants
    parts = ["A", "B", "C"]
    shares = SplitterController._allocate_shares(10.0, 0.3, "A", parts)
    assert shares["A"] == pytest.approx(3.00)
    # remainder = 7.0, /2 = 3.50 each
    assert shares["B"] == pytest.approx(3.50)
    assert shares["C"] == pytest.approx(3.50)

def test_generate_serial(monkeypatch):
    # TC-C1: with two existing "Food & Drinks", next is A003
    win = DummyWindow()
    ctrl = SplitterController(win)
    # stub repo.load_all to return two F&D txns
    monkeypatch.setattr(ctrl.repo, "load_all", lambda: [
        Transaction("A001","","","", "", "Food & Drinks", 0.5, 10.0),
        Transaction("A002","","","", "", "Food & Drinks", 0.5, 20.0),
    ])
    serial = ctrl._generate_serial("Food & Drinks")
    assert serial == f"{CATEGORY_MAP['Food & Drinks']}003"

def test_calculate_group_summary():
    # TC-C6: group "trip" summary: Adrian=50, Vic=10
    win = DummyWindow()
    ctrl = SplitterController(win)
    txns = [
        Transaction("E001", "", "Adrian", "2025-07-14", "trip", "Other", 1.0, 40.0),
        Transaction("E002", "", "Vic",    "2025-07-14", "trip", "Other", 0.5, 20.0),
    ]
    summary = ctrl._calculate_group_summary(txns)
    assert summary["trip"]["Adrian"] == pytest.approx(50.0)
    assert summary["trip"]["Vic"]    == pytest.approx(10.0)
