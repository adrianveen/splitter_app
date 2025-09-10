import os
import fcntl
from splitter_app.persistence import CSVRepository
from splitter_app.models import Transaction

def _txn():
    return Transaction("A001", "", "", "", "", "Other", 1.0, 10.0)

def test_save_uses_file_lock(tmp_path, monkeypatch):
    csv_path = tmp_path / "data.csv"
    repo = CSVRepository(str(csv_path))
    calls = []
    def fake_flock(fd, lock):
        calls.append(lock)
    monkeypatch.setattr("splitter_app.persistence.fcntl.flock", fake_flock)
    repo.save(_txn())
    assert fcntl.LOCK_EX in calls

def test_load_all_uses_shared_lock(tmp_path, monkeypatch):
    csv_path = tmp_path / "data.csv"
    repo = CSVRepository(str(csv_path))
    # write initial data without monkeypatch to create file
    repo.save(_txn())
    calls = []
    def fake_flock(fd, lock):
        calls.append(lock)
    monkeypatch.setattr("splitter_app.persistence.fcntl.flock", fake_flock)
    repo.load_all()
    assert fcntl.LOCK_SH in calls
