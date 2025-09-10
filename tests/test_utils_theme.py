import os
import sys
import pytest
from splitter_app.utils import resource_path
from splitter_app.ui.theme import apply_dark_fusion
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

def test_resource_path_development(monkeypatch):
    # no _MEIPASS → base is utils.py directory
    monkeypatch.setattr(sys, "_MEIPASS", None, raising=False)
    base = os.path.abspath(os.path.dirname(resource_path.__globals__['__file__']))
    rel = "foo/bar.txt"
    assert resource_path(rel) == os.path.join(base, rel)

def test_resource_path_meipass(monkeypatch):
    # with _MEIPASS → uses that directory
    fake = "/tmp/meipassdir"
    monkeypatch.setattr(sys, "_MEIPASS", fake, raising=False)
    assert resource_path("x") == os.path.join(fake, "x")


def test_resource_path_rejects_traversal(monkeypatch):
    # Ensure base path is the module dir
    monkeypatch.setattr(sys, "_MEIPASS", None, raising=False)
    with pytest.raises(ValueError):
        resource_path("../evil.txt")

def test_apply_dark_fusion_sets_fusion_style_and_palette(monkeypatch):
    # Creating a fresh QApplication for testing
    app = QApplication.instance() or QApplication([])
    # stub out resource_path to avoid relying on package data
    monkeypatch.setattr(
        "splitter_app.ui.theme.resource_path",
        lambda path: path
    )
    # Should not raise even if file doesn't exist
    apply_dark_fusion(app, icon_name="irrelevant.ico")
    # Style should be Fusion
    assert app.style().objectName() == "fusion"
    pal = app.palette()
    # Window background should be dark
    assert pal.color(QPalette.ColorRole.Window) == QColor(53, 53, 53)


def test_apply_dark_fusion_missing_icon(monkeypatch, capsys):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(
        "splitter_app.ui.theme.resource_path",
        lambda path: path
    )
    # icon path doesn't exist → warning printed
    apply_dark_fusion(app, icon_name="missing.ico")
    captured = capsys.readouterr().out
    assert "missing.ico" in captured
