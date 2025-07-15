import os
import sys
import pytest
from splitter_app.utils import resource_path
from splitter_app.ui.theme import apply_dark_fusion
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

def test_resource_path_development(monkeypatch):
    # no _MEIPASS → base is utils.py directory
    monkeypatch.setattr(sys, "_MEIPASS", None)
    base = os.path.abspath(os.path.dirname(resource_path.__globals__['__file__']))
    rel = "foo/bar.txt"
    assert resource_path(rel) == os.path.join(base, rel)

def test_resource_path_meipass(monkeypatch):
    # with _MEIPASS → uses that directory
    fake = "/tmp/meipassdir"
    monkeypatch.setattr(sys, "_MEIPASS", fake)
    assert resource_path("x") == os.path.join(fake, "x")

def test_apply_dark_fusion_sets_fusion_style_and_palette(monkeypatch):
    # Creating a fresh QApplication for testing
    app = QApplication.instance() or QApplication([])
    # stub out icon lookup to avoid file-not-found
    monkeypatch.setattr(
        resource_path.__globals__['resource_path'],
        "__call__",
        lambda self, path: path
    )
    # Should not raise
    apply_dark_fusion(app, icon_name="irrelevant.ico")
    # Style should be Fusion
    assert app.style().objectName() == "Fusion"
    pal = app.palette()
    # Window background should be dark
    assert pal.color(QPalette.ColorRole.Window) == QColor(53, 53, 53)
