# src/splitter_app/controllers.py

from collections import defaultdict
from PySide6.QtWidgets import QTableWidgetItem

from splitter_app.models import Transaction
from splitter_app.persistence import CSVRepository
from splitter_app.config import (
    LOCAL_CSV_PATH,
    DRIVE_FILE_ID,
    CREDENTIALS_FILE,
    PARTICIPANTS,
    CATEGORY_MAP,
)


class SplitterController:
    """
    Controller for the Contribution Splitter app.
    Connects the UI (MainWindow) signals to business logic,
    manages transactions via CSVRepository, and updates the UI.
    """

    def __init__(self, window):
        self.window = window
        self.repo = CSVRepository(LOCAL_CSV_PATH)
        # Connect UI signals to controller methods
        window.transaction_added.connect(self.add_transaction)
        window.transaction_deleted.connect(self.delete_transaction)

    def initialize(self):
        """Load initial data from CSV and update the UI."""
        txns = self.repo.load_all()
        self._refresh_view(txns)

    def add_transaction(self, data: dict):
        """Create Transaction, save it, and refresh UI."""
        serial = self._generate_serial(data["category"])
        txn = Transaction(
            serial_number=serial,
            description=data["description"],
            paid_by=data["paid_by"],
            date=data["date"],
            group=data["group"],
            category=data["category"],
            split=data["split"],
            amount=float(data["amount"]),
        )
        self.repo.save(txn)
        self._refresh_view(self.repo.load_all())

    def delete_transaction(self, serial_number: str):
        """Delete by serial_number and refresh UI."""
        self.repo.delete(serial_number)
        self._refresh_view(self.repo.load_all())

    def _refresh_view(self, txns: list[Transaction]):
        """Populate the transactions table, summary label, and group summary."""
        # Transactions table
        table = self.window.table
        table.setRowCount(len(txns))
        for row, t in enumerate(txns):
            table.setItem(row, 0, QTableWidgetItem(t.serial_number))
            table.setItem(row, 1, QTableWidgetItem(t.description))
            table.setItem(row, 2, QTableWidgetItem(t.paid_by))
            table.setItem(row, 3, QTableWidgetItem(t.group))
            table.setItem(row, 4, QTableWidgetItem(t.date))
            table.setItem(row, 5, QTableWidgetItem(f"{t.amount:.2f}"))
            table.setItem(row, 6, QTableWidgetItem(t.category))
            table.setItem(row, 7, QTableWidgetItem(f"{t.split:.1f}"))

        # Summary label
        total = sum(t.amount for t in txns)
        per_person = (total / len(PARTICIPANTS)) if PARTICIPANTS else 0.0
        self.window.summary_label.setText(
            f"Total: {total:.2f}, Per Person: {per_person:.2f}"
        )

        # Group summary
        summary = self._calculate_group_summary(txns)
        self._populate_group_summary(summary)

    def _generate_serial(self, category: str) -> str:
        """Generate a new serial_number based on category map and existing txns."""
        letter = CATEGORY_MAP.get(category, "Z")
        existing = [t for t in self.repo.load_all() if t.category == category]
        next_num = len(existing) + 1
        return f"{letter}{next_num:03d}"

    def _calculate_group_summary(
        self, txns: list[Transaction]
    ) -> dict[str, dict[str, float]]:
        """Compute total paid by each participant per group."""
        summary: dict[str, dict[str, float]] = defaultdict(
            lambda: {p: 0.0 for p in PARTICIPANTS}
        )
        for t in txns:
            summary[t.group][t.paid_by] += t.amount
        return summary

    def _populate_group_summary(
        self, summary: dict[str, dict[str, float]]
    ):
        """Update the group summary table in the UI."""
        table = self.window.group_summary_table
        table.setRowCount(len(summary))
        for row, (group, amounts) in enumerate(summary.items()):
            table.setItem(row, 0, QTableWidgetItem(group))
            for col, p in enumerate(PARTICIPANTS, start=1):
                amount = amounts.get(p, 0.0)
                table.setItem(row, col, QTableWidgetItem(f"{amount:.2f}"))
