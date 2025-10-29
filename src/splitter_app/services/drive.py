# src/splitter_app/services/drive.py
"""Wrapper around Google Drive CSV upload/download using the shared google_api module.

Provides simple, project-specific functions to sync the transactions CSV.
Handles existing file permission issues by removing or resetting permissions.
"""

import os
from pathlib import Path

# Import the config module so we can read its values dynamically.  This allows
# tests and the authentication flow to modify paths at runtime (e.g. when
# `ensure_credentials` updates `config.CREDENTIALS_FILE`).
from splitter_app import config

from .google_api import download_from_drive as _download_from_drive
from .google_api import upload_to_drive as _upload_to_drive

__all__ = ["download_csv", "upload_csv"]


def download_csv() -> None:
    """Download the transactions CSV from Google Drive to the local path.

    If a previous CSV exists, try to remove it first to avoid permission errors.
    """
    # Ensure target directory exists
    Path.mkdir(Path(config.LOCAL_CSV_PATH).parent, exist_ok=True)

    # If the file already exists, attempt to remove or reset permissions
    if Path(config.LOCAL_CSV_PATH).exists():
        try:
            os.chmod(config.LOCAL_CSV_PATH, 0o666)
            Path(config.LOCAL_CSV_PATH).unlink()
        except PermissionError:
            msg = (
                f"Cannot overwrite existing CSV at '{config.LOCAL_CSV_PATH}'.\n"
                "Please close any programs that may be using it or adjust file permissions."
            )
            raise PermissionError(
                msg,
            )

    # Perform download
    _download_from_drive(
        config.DRIVE_FILE_ID,
        Path(config.LOCAL_CSV_PATH),
        Path(config.CREDENTIALS_FILE),
    )


def upload_csv() -> None:
    """Upload the local transactions CSV to Google Drive, replacing the existing file."""
    if not Path(config.LOCAL_CSV_PATH).exists():
        msg = f"Local CSV not found: {config.LOCAL_CSV_PATH}"
        raise FileNotFoundError(msg)
    _upload_to_drive(
        config.DRIVE_FILE_ID,
        Path(config.LOCAL_CSV_PATH),
        Path(config.CREDENTIALS_FILE),
    )
