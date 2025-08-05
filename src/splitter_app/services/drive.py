# src/splitter_app/services/drive.py
"""
Wrapper around Google Drive CSV upload/download using the shared google_api module.
Provides simple, project-specific functions to sync the transactions CSV.
Handles existing file permission issues by removing or resetting permissions.
"""
import os
from .google_api import upload_to_drive as _upload_to_drive, \
                         download_from_drive as _download_from_drive
# Import the config module so we can read its values dynamically.  This allows
# tests and the authentication flow to modify paths at runtime (e.g. when
# `ensure_credentials` updates `config.CREDENTIALS_FILE`).
from splitter_app import config

__all__ = ["download_csv", "upload_csv"]

def download_csv():
    """
    Download the transactions CSV from Google Drive to the local path.
    If a previous CSV exists, try to remove it first to avoid permission errors.
    """
    # Ensure target directory exists
    os.makedirs(os.path.dirname(config.LOCAL_CSV_PATH), exist_ok=True)

    # If the file already exists, attempt to remove or reset permissions
    if os.path.exists(config.LOCAL_CSV_PATH):
        try:
            os.chmod(config.LOCAL_CSV_PATH, 0o666)
            os.remove(config.LOCAL_CSV_PATH)
        except PermissionError:
            raise PermissionError(
                f"Cannot overwrite existing CSV at '{config.LOCAL_CSV_PATH}'.\n"
                "Please close any programs that may be using it or adjust file permissions."
            )

    # Perform download
    _download_from_drive(
        config.DRIVE_FILE_ID, config.LOCAL_CSV_PATH, config.CREDENTIALS_FILE
    )


def upload_csv():
    """
    Upload the local transactions CSV to Google Drive, replacing the existing file.
    """
    if not os.path.exists(config.LOCAL_CSV_PATH):
        raise FileNotFoundError(f"Local CSV not found: {config.LOCAL_CSV_PATH}")
    _upload_to_drive(
        config.DRIVE_FILE_ID, config.LOCAL_CSV_PATH, config.CREDENTIALS_FILE
    )
