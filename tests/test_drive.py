import os
import pytest
from pathlib import Path
import splitter_app.services.drive as drive_module

def test_download_csv_success(tmp_path, monkeypatch):
    # TC-G2: when no existing file, should call underlying download
    fake_id = "FAKEID"
    fake_cred = "FAKECRED"
    fake_path = tmp_path / "transactions.csv"
    # override module constants
    monkeypatch.setattr(drive_module, "LOCAL_CSV_PATH", str(fake_path))
    monkeypatch.setattr(drive_module, "DRIVE_FILE_ID", fake_id)
    monkeypatch.setattr(drive_module, "CREDENTIALS_FILE", fake_cred)
    called = {}
    def fake_download(file_id, out_path, cred_path):
        called['args'] = (file_id, out_path, cred_path)
    monkeypatch.setattr(drive_module, "_download_from_drive", fake_download)
    drive_module.download_csv()
    assert called['args'] == (fake_id, str(fake_path), fake_cred)

def test_download_csv_permission_error(tmp_path, monkeypatch):
    # TC-G2: simulate permission error when removing existing file
    fake_path = tmp_path / "transactions.csv"
    fake_path.write_text("data")
    monkeypatch.setattr(drive_module, "LOCAL_CSV_PATH", str(fake_path))
    # make os.remove raise PermissionError
    monkeypatch.setattr(drive_module.os, "remove", lambda p: (_ for _ in ()).throw(PermissionError("locked")))
    with pytest.raises(PermissionError):
        drive_module.download_csv()

def test_upload_csv_file_not_found(tmp_path, monkeypatch):
    # TC-G3: upload when no local CSV should raise FileNotFoundError
    fake_path = tmp_path / "transactions.csv"
    monkeypatch.setattr(drive_module, "LOCAL_CSV_PATH", str(fake_path))
    with pytest.raises(FileNotFoundError):
        drive_module.upload_csv()

def test_upload_csv_success(tmp_path, monkeypatch):
    # TC-G3: when file exists, should call underlying upload
    fake_path = tmp_path / "transactions.csv"
    fake_path.write_text("data")
    fake_id = "FILEID"
    fake_cred = "CREDPATH"
    monkeypatch.setattr(drive_module, "LOCAL_CSV_PATH", str(fake_path))
    monkeypatch.setattr(drive_module, "DRIVE_FILE_ID", fake_id)
    monkeypatch.setattr(drive_module, "CREDENTIALS_FILE", fake_cred)
    called = {}
    def fake_upload(file_id, local_path, cred_path):
        called['args'] = (file_id, local_path, cred_path)
    monkeypatch.setattr(drive_module, "_upload_to_drive", fake_upload)
    drive_module.upload_csv()
    assert called['args'] == (fake_id, str(fake_path), fake_cred)
