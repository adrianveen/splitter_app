import pytest
from splitter_app.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QDate

@pytest.fixture(scope="session")
def app():
    # one QApplication for all tests
    return QApplication.instance() or QApplication([])

def test_on_split_changed_updates_ower_label(app):
    win = MainWindow(["Alice","Bob"], ["Cat"])
    win._on_split_changed(0.7)
    assert win.ower_label.text() == "Ower: 0.3"

def test_on_add_clicked_emits_transaction_added(app, monkeypatch):
    win = MainWindow(["Alice","Bob"], ["Cat"])
    # set up form fields
    win.desc_input.setText("  Test Desc  ")
    win.amount_input.setText("123.45")
    win.date_input.setDate(QDate(2025, 7, 14))
    win.group_input.setText("GroupX")
    win.category_combo.setCurrentText("Cat")
    win.payer_spin.setValue(0.6)
    # capture emitted data
    captured = {}
    monkeypatch.setattr(win.transaction_added, "emit", lambda data: captured.setdefault('data', data))
    win._on_add_clicked()
    assert captured['data'] == {
        "description": "Test Desc",
        "paid_by": win.paid_by_combo.currentText(),
        "date": "2025-07-14",
        "group": "GroupX",
        "category": "Cat",
        "split": 0.6,
        "amount": "123.45",
    }

def test_on_delete_clicked_no_selection_shows_warning(app, monkeypatch):
    win = MainWindow(["A","B"], ["Cat"])
    # ensure no selection
    monkeypatch.setattr(win.table, "selectedItems", lambda: [])
    called = {}
    def fake_warn(self, title, msg, *args, **kwargs):
        called['warning'] = (title, msg)
    monkeypatch.setattr(QMessageBox, "warning", fake_warn)
    win._on_delete_clicked()
    assert "No Entry Selected" in called['warning'][0]
