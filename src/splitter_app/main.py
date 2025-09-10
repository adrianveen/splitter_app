# src/splitter_app/main.py

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from splitter_app.ui.theme import apply_light_minimal_theme
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from splitter_app.ui.main_window import MainWindow
from splitter_app.controllers import SplitterController
from splitter_app.services.drive import download_csv, upload_csv
from splitter_app.config import (
    PARTICIPANTS,
    TRANSACTION_CATEGORIES,
    LOCAL_CSV_PATH,
    DRIVE_FILE_ID,
)
from splitter_app.services.auth import ensure_credentials

def main():
    """
    Entry point for the Contribution Splitter application.
    Applies theming, syncs CSV with Drive, shows the UI, and uploads on exit.
    """
    # 1) Create the QApplication early so we can show message boxes
    app = QApplication(sys.argv)
    apply_light_minimal_theme(app)

    # 2) First-run: make sure we have a token.json, then sync down with Drive
    try:
        token_path = ensure_credentials()
    except Exception as e:
        QMessageBox.critical(
            None,
            "Authentication Error",
            f"Could not complete Google OAuth flow:\n{e}"
        )
        sys.exit(1)

    try:
        download_csv()
    except PermissionError as e:
        QMessageBox.critical(
            None,
            "File Permission Error",
            str(e)
        )
        sys.exit(1)
    except FileNotFoundError as e:
        response = QMessageBox.question(
            None,
            "Request Access",
            f"{e}\n\nRequest access to the Drive file?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if response == QMessageBox.Yes:
            url = QUrl(f"https://drive.google.com/file/d/{DRIVE_FILE_ID}/view")
            QDesktopServices.openUrl(url)
        # continue with whatever local data exists
    except Exception as e:
        QMessageBox.warning(
            None,
            "Download Error",
            f"Could not download transactions from Drive:\n{e}"
        )
        # continue with whatever local data exists

    # 3) Show UI
    window = MainWindow(
        participants=PARTICIPANTS,
        categories=TRANSACTION_CATEGORIES,
    )
    window.show()

    # 4) Wire up controller
    controller = SplitterController(window)
    controller.initialize()

    # 5) Run event loop & sync up on exit
    try:
        exit_code = app.exec()
    finally:
        # Upload updated CSV
        if os.path.exists(LOCAL_CSV_PATH):
            try:
                upload_csv()
            except FileNotFoundError as e:
                response = QMessageBox.question(
                    None,
                    "Request Access",
                    f"{e}\n\nRequest access to the Drive file?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if response == QMessageBox.Yes:
                    url = QUrl(f"https://drive.google.com/file/d/{DRIVE_FILE_ID}/view")
                    QDesktopServices.openUrl(url)
            except Exception as e:
                QMessageBox.warning(
                    None,
                    "Upload Error",
                    f"Could not upload transactions to Drive:\n{e}"
                )
        else:
            QMessageBox.information(
                None,
                "No Data",
                "No transactions file found; skipping upload."
            )
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
