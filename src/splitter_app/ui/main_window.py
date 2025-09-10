# src/splitter_app/ui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QGridLayout,
    QDateEdit, QVBoxLayout, QMessageBox, QHeaderView, QDoubleSpinBox, QHBoxLayout,
    QFrame
)
from PySide6.QtCore import Qt, QDate, Signal

class MainWindow(QMainWindow):
    """
    The pure-UI layer for the Contribution Splitter.
    Emits:
      - transaction_added(dict): when the user clicks “Add Transaction”
      - transaction_deleted(str): serial_number of the entry to delete
    """
    transaction_added = Signal(dict)
    transaction_deleted = Signal(str)

    def __init__(self, 
                 participants: list[str],
                 categories: list[str]):
        super().__init__()
        self.participants = participants
        self.transactions_cat = categories

        self.setWindowTitle("Splitter App v2.0.2")
        self.setMinimumSize(800, 600)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        # --- Central container & main layout ---
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # --- INPUT FORM ---
        form_layout = QGridLayout()
        # 1) Description
        lbl = QLabel("Transaction Description:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 0, 0)
        self.desc_input = QLineEdit()
        form_layout.addWidget(self.desc_input, 0, 1)

        # 2) Paid By
        lbl = QLabel("Paid By:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 1, 0)
        self.paid_by_combo = QComboBox()
        self.paid_by_combo.addItems(self.participants)
        form_layout.addWidget(self.paid_by_combo, 1, 1)

        # 3) Amount
        lbl = QLabel("Amount (CAD):")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 2, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        form_layout.addWidget(self.amount_input, 2, 1)

        # 4) Date
        lbl = QLabel("Date:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 3, 0)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_input, 3, 1)

        # 5) Category
        lbl = QLabel("Category:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 4, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.transactions_cat)
        form_layout.addWidget(self.category_combo, 4, 1)

        # 6) Group
        lbl = QLabel("Group:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 5, 0)
        self.group_input = QLineEdit()
        form_layout.addWidget(self.group_input, 5, 1)

        # 7) Split Fraction
        lbl = QLabel("Payer Fraction:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl, 6, 0)

        # put spin + ower label into a single container in column 1
        split_container = QWidget()
        split_hbox = QHBoxLayout(split_container)
        split_hbox.setContentsMargins(0, 0, 0, 0)
        split_hbox.setSpacing(8)

        self.payer_spin = QDoubleSpinBox()
        self.payer_spin.setRange(0.0, 1.0)
        self.payer_spin.setSingleStep(0.1)
        self.payer_spin.setDecimals(1)
        self.payer_spin.setMinimumWidth(80)
        self.payer_spin.setValue(0.5)   # narrow it down so label fits
        split_hbox.addWidget(self.payer_spin)

        self.ower_label = QLabel("Ower: 0.5")
        self.ower_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        split_hbox.addWidget(self.ower_label)

        split_hbox.addStretch()  # push everything left within that cell

        # now place the whole container in column 1
        form_layout.addWidget(split_container, 6, 1)

        # … leave the signal hookup unchanged:
        self.payer_spin.valueChanged.connect(self._on_split_changed)

        # Add button
        self.add_button = QPushButton("Add Transaction")
        form_layout.addWidget(self.add_button, 7, 0, 1, 2)

        main_layout.addLayout(form_layout)

        # --- TRANSACTIONS TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "serial_number", "Description", "Paid By", "Group",
            "Date", "Amount", "Category", "Split"
        ])
        self.table.setColumnHidden(0, True)  # hide serial internally
        hdr = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        main_layout.addWidget(self.table)

        # --- SUMMARY & DELETE ---
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        self.summary_label = QLabel("No transactions yet.")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()
        self.delete_button = QPushButton("Delete Entry")
        summary_layout.addWidget(self.delete_button)
        main_layout.addWidget(summary_frame)

        # --- GROUP SUMMARY TABLE ---
        self.group_summary_table = QTableWidget()
        # initially 3 columns: Group + 2 people; controller can reset cols later
        self.group_summary_table.setColumnCount(3)
        self.group_summary_table.setHorizontalHeaderLabels(
            ["Group"] + self.participants
        )
        hdr2 = self.group_summary_table.horizontalHeader()
        for col in range(self.group_summary_table.columnCount()):
            hdr2.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.group_summary_table.setAlternatingRowColors(True)
        self.group_summary_table.setSortingEnabled(True)
        main_layout.addWidget(self.group_summary_table)

    def _connect_signals(self):
        self.add_button.clicked.connect(self._on_add_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

    def _on_add_clicked(self):
        """
        Collects form data and emits transaction_added.
        The controller should listen and handle CSV + table + summary updates.
        """
        data = {
            "description": self.desc_input.text().strip(),
            "paid_by": self.paid_by_combo.currentText(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "group": self.group_input.text().strip() or "general",
            "category": self.category_combo.currentText(),
            "split": self.payer_spin.value(),
            "amount": self.amount_input.text().strip(),
        }
        self.transaction_added.emit(data)

    def _on_delete_clicked(self):
        """
        Emits transaction_deleted with the serial_number of the selected row.
        """
        if self.table.selectedItems():
            sn = self.table.item(self.table.currentRow(), 0).text()
            self.transaction_deleted.emit(sn)
        else:
            QMessageBox.warning(self, "No Entry Selected",
                                "Please select an entry to delete.",
                                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
        
    def _on_split_changed(self, payer_frac: float):
        """Update the ower label whenever payer changes."""
        ower_frac = round(1.0 - payer_frac, 1)
        self.ower_label.setText(f"Ower: {ower_frac:.1f}")

    # (Optionally, you can add methods like `set_transactions(...)`,
    #  `update_summary_text(...)`, `populate_group_summary(...)` here
    #  to let your controller push data back into the UI.)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Dummy data just for layout preview
    participants = ["Alice", "Bob"]
    categories = ["Food", "Travel", "Utilities"]

    app = QApplication(sys.argv)
    window = MainWindow(participants, categories)
    window.show()
    sys.exit(app.exec())
