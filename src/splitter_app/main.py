# src/splitter_app/main.py

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from splitter_app.ui.theme import apply_dark_fusion
from splitter_app.ui.main_window import MainWindow
from splitter_app.controllers import SplitterController
from splitter_app.services.drive import download_csv, upload_csv
from splitter_app.config import PARTICIPANTS, TRANSACTION_CATEGORIES, LOCAL_CSV_PATH


def main():
    """
    Entry point for the Contribution Splitter application.
    Applies theming, syncs CSV with Drive, shows the UI, and uploads on exit.
    Errors during sync are shown via dialogs instead of terminal prints.
    """
    # 1) Create the QApplication early so we can show message boxes
    app = QApplication(sys.argv)
    apply_dark_fusion(app)

    # 2) Sync down with Drive
    try:
        download_csv()
    except PermissionError as e:
        QMessageBox.critical(
            None,
            "File Permission Error",
            str(e)
        )
        sys.exit(1)
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
