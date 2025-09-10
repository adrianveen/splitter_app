import pytest
from splitter_app.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem
from PySide6.QtCore import QDate

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])

def test_on_split_changed_updates_ower_label(app):
    win = MainWindow(["Alice","Bob"], ["Cat"])
    win._on_split_changed(0.7)
    assert win.ower_label.text() == "Ower: 0.3"

def test_on_add_clicked_emits_transaction_added(app):
    win = MainWindow(["Alice","Bob"], ["Cat"])
    # populate form
    win.desc_input.setText("  Test Desc  ")
    win.amount_input.setText("123.45")
    win.date_input.setDate(QDate(2025, 7, 14))
    win.group_input.setText("GroupX")
    win.category_combo.setCurrentText("Cat")
    win.payer_spin.setValue(0.6)

    # capture the emitted data by connecting a slot
    captured = {}
    def catcher(data):
        captured['data'] = data

    win.transaction_added.connect(catcher)
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
    # simulate no row selected
    monkeypatch.setattr(win.table, "selectedItems", lambda: [])

    calls = []
    def fake_warning(parent, title, msg, *args, **kwargs):
        calls.append((title, msg))

    monkeypatch.setattr(QMessageBox, "warning", fake_warning)
    win._on_delete_clicked()

    assert calls, "Expected a warning to be shown"
    title, msg = calls[0]
    assert "No Entry Selected" in title

def test_on_delete_clicked_emits_serial(app):
    win = MainWindow(["A","B"], ["Cat"])
    win.table.setRowCount(1)
    serial = "42"
    item = QTableWidgetItem(serial)
    win.table.setItem(0, 0, item)

    # avoid needing real selection handling
    win.table.setCurrentCell(0, 0)
    win.table.selectRow(0)
    win.table.selectedItems = lambda: [item]

    captured = {}
    def catcher(sn):
        captured['sn'] = sn

    win.transaction_deleted.connect(catcher)
    win._on_delete_clicked()

    assert captured.get('sn') == serial


def test_group_summary_table_sorting_enabled(app):
    win = MainWindow(["A", "B"], ["Cat"])
    assert win.group_summary_table.isSortingEnabled()


def test_dark_mode_action_toggles_theme(app, monkeypatch):
    win = MainWindow(["A", "B"], ["Cat"])

    called = {"mode": None}
    monkeypatch.setattr(
        "splitter_app.ui.main_window.apply_dark_fusion",
        lambda a: called.update(mode="dark"),
    )
    monkeypatch.setattr(
        "splitter_app.ui.main_window.apply_muji_theme",
        lambda a: called.update(mode="light"),
    )

    win.dark_mode_action.setChecked(True)
    assert called["mode"] == "dark"
    win.dark_mode_action.setChecked(False)
    assert called["mode"] == "light"
