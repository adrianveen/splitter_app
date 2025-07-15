import pytest

from splitter_app.controllers import SplitterController
from splitter_app.models import Transaction
from splitter_app.config import CATEGORY_MAP

# --- Dummy implementations to isolate controller from real I/O ---

class DummyRepo:
    """In-memory stand-in for CSVRepository—no disk or network access."""
    def __init__(self, _path):
        self._storage = []

    def load_all(self):
        return list(self._storage)

    def save(self, txn):
        self._storage.append(txn)

    def delete(self, serial):
        self._storage = [t for t in self._storage if t.serial_number != serial]

class DummySignal:
    """Minimal Qt-like signal: supports .connect() and .emit()."""
    def __init__(self):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def emit(self, *args, **kwargs):
        for s in self._slots:
            s(*args, **kwargs)

class DummyWindow:
    """Stub view with only the attributes/signals the controller uses."""
    def __init__(self):
        self.transaction_added   = DummySignal()
        self.transaction_deleted = DummySignal()
        self.summary_label = type("Lbl", (), {
            "text": "",
            "setText": lambda self, txt: setattr(self, "text", txt)
        })()
        self.table = None
        self.group_summary_table = None

# --- Apply the dummy repo to all tests in this module ---
@pytest.fixture(autouse=True)
def use_dummy_repo(monkeypatch):
    # Only patch CSVRepository—don't touch download_csv/upload_csv
    monkeypatch.setattr(
        "splitter_app.controllers.CSVRepository",
        DummyRepo
    )

# --- Tests for allocation logic ---

def test_allocate_shares_basic():
    parts = ["Adrian", "Vic"]
    shares = SplitterController._allocate_shares(100.0, 0.5, "Adrian", parts)
    assert shares["Adrian"] == pytest.approx(50.0)
    assert shares["Vic"]    == pytest.approx(50.0)

def test_allocate_shares_payer_all():
    parts = ["Adrian", "Vic"]
    shares = SplitterController._allocate_shares(80.0, 1.0, "Vic", parts)
    assert shares["Vic"]    == pytest.approx(80.0)
    assert shares["Adrian"] == pytest.approx(0.0)

def test_allocate_shares_rounding_dust():
    parts = ["A", "B", "C"]
    shares = SplitterController._allocate_shares(10.0, 0.3, "A", parts)
    assert shares["A"] == pytest.approx(3.00)
    assert shares["B"] == pytest.approx(3.50)
    assert shares["C"] == pytest.approx(3.50)

# --- Tests for serial-number generation ---

def test_generate_serial():
    win = DummyWindow()
    ctrl = SplitterController(win)
    # preload two "Food & Drinks" txns into the dummy repo
    ctrl.repo.save(Transaction("A001", "", "", "", "", "Food & Drinks", 0.5, 10.0))
    ctrl.repo.save(Transaction("A002", "", "", "", "", "Food & Drinks", 0.5, 20.0))

    serial = ctrl._generate_serial("Food & Drinks")
    expected_prefix = CATEGORY_MAP["Food & Drinks"]
    assert serial == f"{expected_prefix}003"

# --- Tests for group-summary calculation ---

def test_calculate_group_summary():
    win = DummyWindow()
    ctrl = SplitterController(win)

    txns = [
        Transaction("E001", "", "Adrian", "2025-07-14", "trip", "Other", 1.0, 40.0),
        Transaction("E002", "", "Vic",    "2025-07-14", "trip", "Other", 0.5, 20.0),
    ]
    summary = ctrl._calculate_group_summary(txns)

    assert summary["trip"]["Adrian"] == pytest.approx(50.0)
    assert summary["trip"]["Vic"]    == pytest.approx(10.0)
