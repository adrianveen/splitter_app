# src/splitter_app/controllers.py

from collections import defaultdict
from typing import List, Dict
from PySide6.QtWidgets import QTableWidgetItem

from splitter_app.models import Transaction
from splitter_app.persistence import CSVRepository
from splitter_app.config import (
    LOCAL_CSV_PATH,
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

    @staticmethod
    def _allocate_shares(
        amount: float,
        split: float,
        payer: str,
        participants: List[str],
    ) -> Dict[str, float]:
        """
        Allocate `amount` among participants based on `split`:
        - payer gets `round(amount * split, 2)`
        - the remaining is split equally (and rounded) among the others,
          with the last ower absorbing any tiny rounding diff
        Guarantees that sum(shares.values()) == round(amount, 2).
        """
        shares = {p: 0.0 for p in participants}
        n = len(participants)

        if n == 0:
            return shares

        # 1) Payer’s portion
        raw_payer = amount * split
        payer_amt = round(raw_payer, 2)
        shares[payer] = payer_amt

        # 2) Remainder to the others
        if n > 1:
            raw_remainder = amount - raw_payer
            count = n - 1
            base = round(raw_remainder / count, 2)

            others = [p for p in participants if p != payer]
            # assign base to each except last
            for o in others[:-1]:
                shares[o] = base
            # last absorbs any rounding dust
            last = round(raw_remainder - base * (count - 1), 2)
            shares[others[-1]] = last

        return shares

    def _refresh_view(self, txns: List[Transaction]):
        """Populate the transactions table, summary label, and group summary."""
        # 1) Transactions table
        table = self.window.table
        # -------- Prevent the builtin sorter from kicking in mid-populate
        table.setSortingEnabled(False)
        table.clearContents()
        # -----------------
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

        # Re-enable sorting after populating
        table.setSortingEnabled(True)

        # 2) Summary label
        total = round(sum(t.amount for t in txns), 2)
        participants = PARTICIPANTS
        n = len(participants)

        if n == 0:
            # No one to split with
            self.window.summary_label.setText(f"Total: {total:.2f}")
        else:
            balances = {p: 0.0 for p in participants}
            for t in txns:
                shares = self._allocate_shares(
                    amount=t.amount,
                    split=t.split,
                    payer=t.paid_by,
                    participants=participants,
                )
                for p, amt in shares.items():
                    balances[p] += amt

            # Ensure each balance is rounded and build the display parts
            parts = [f"Total: {total:.2f}"]
            for p in participants:
                parts.append(f"{p}: {balances[p]:.2f}")

            self.window.summary_label.setText(", ".join(parts))

        # 3) Group summary
        summary = self._calculate_group_summary(txns)
        self._populate_group_summary(summary)

    def _generate_serial(self, category: str) -> str:
        """Generate a new serial_number based on category map and existing txns."""
        letter = CATEGORY_MAP.get(category, "Z")
        existing = [t for t in self.repo.load_all() if t.category == category]
        next_num = len(existing) + 1
        return f"{letter}{next_num:03d}"

    def _calculate_group_summary(
        self, txns: List[Transaction]
    ) -> Dict[str, Dict[str, float]]:
        """
        Build a dict of group → (participant → total_share)
        reusing the same allocation logic to keep it consistent.
        """
        participants = PARTICIPANTS
        summary: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {p: 0.0 for p in participants}
        )

        for t in txns:
            shares = self._allocate_shares(
                amount=t.amount,
                split=t.split,
                payer=t.paid_by,
                participants=participants,
            )
            for p, amt in shares.items():
                summary[t.group][p] += amt

        return summary

    def _populate_group_summary(
        self, summary: Dict[str, Dict[str, float]]
    ):
        """Update the group summary table in the UI."""
        table = self.window.group_summary_table
        table.setRowCount(len(summary))
        for row, (group, amounts) in enumerate(summary.items()):
            table.setItem(row, 0, QTableWidgetItem(group))
            for col, p in enumerate(PARTICIPANTS, start=1):
                amt = amounts.get(p, 0.0)
                table.setItem(row, col, QTableWidgetItem(f"{amt:.2f}"))
