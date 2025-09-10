# src/splitter_app/ui/theme.py
import os
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from splitter_app.utils import resource_path

def apply_dark_fusion(app: QApplication, icon_name: str = "wallet-icon.ico") -> None:
    """
    Sets Fusion style, a dark palette, and application icon.
    """
    # 1) Fusion style
    app.setStyle("Fusion")

    # 2) Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    app.setPalette(palette)

    # 3) Application icon (optional)
    icon_path = resource_path(f"resources/images/{icon_name}")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # Avoid crashing if the icon is missing; useful in testing/packaging
        print(f"Warning: icon '{icon_path}' not found; using default icon")


def apply_muji_theme(app: QApplication, icon_name: str = "wallet-icon.ico") -> None:
    """Apply a light, Muji-inspired minimalist palette and basic styling."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f4f3f0"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#2e2e2e"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#fafafa"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#2e2e2e"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e5e4e2"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2e2e2e"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#c6c5b9"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#2e2e2e"))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QTableWidget {
            gridline-color: #d0d0d0;
            alternate-background-color: #fafafa;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            padding: 4px;
            border: 1px solid #d0d0d0;
        }
        QFrame#summaryFrame {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
        }
        """
    )

    icon_path = resource_path(f"resources/images/{icon_name}")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: icon '{icon_path}' not found; using default icon")
