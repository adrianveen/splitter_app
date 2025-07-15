# src/splitter_app/services/drive.py
"""
Wrapper around Google Drive CSV upload/download using the shared google_api module.
Provides simple, project-specific functions to sync the transactions CSV.
Handles existing file permission issues by removing or resetting permissions.
"""
import os
from .google_api import upload_to_drive as _upload_to_drive, \
                         download_from_drive as _download_from_drive
from splitter_app.config import LOCAL_CSV_PATH, DRIVE_FILE_ID, CREDENTIALS_FILE

__all__ = ["download_csv", "upload_csv"]

def download_csv():
    """
    Download the transactions CSV from Google Drive to the local path.
    If a previous CSV exists, try to remove it first to avoid permission errors.
    """
    # Ensure target directory exists
    os.makedirs(os.path.dirname(LOCAL_CSV_PATH), exist_ok=True)

    # If the file already exists, attempt to remove or reset permissions
    if os.path.exists(LOCAL_CSV_PATH):
        try:
            os.chmod(LOCAL_CSV_PATH, 0o666)
            os.remove(LOCAL_CSV_PATH)
        except PermissionError:
            raise PermissionError(
                f"Cannot overwrite existing CSV at '{LOCAL_CSV_PATH}'.\n"
                "Please close any programs that may be using it or adjust file permissions."
            )

    # Perform download
    _download_from_drive(DRIVE_FILE_ID, LOCAL_CSV_PATH, CREDENTIALS_FILE)


def upload_csv():
    """
    Upload the local transactions CSV to Google Drive, replacing the existing file.
    """
    if not os.path.exists(LOCAL_CSV_PATH):
        raise FileNotFoundError(f"Local CSV not found: {LOCAL_CSV_PATH}")
    _upload_to_drive(DRIVE_FILE_ID, LOCAL_CSV_PATH, CREDENTIALS_FILE)
