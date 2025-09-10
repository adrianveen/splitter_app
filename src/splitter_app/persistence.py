# src/splitter_app/persistence.py
"""
CSV-based repository for storing and loading transactions.
Handles reading, appending, and deleting entries in the CSV file.
Adds support for legacy CSV formats with split descriptions.
"""
import csv
import os
import re
import fcntl
from contextlib import contextmanager
from typing import List

from splitter_app.models import Transaction
from splitter_app.config import PARTICIPANTS


class CSVRepository:
    """
    A repository that uses a CSV file as its backend storage.
    """

    def __init__(self, csv_path: str) -> None:
        """
        :param csv_path: Path to the CSV file storing transactions.
        """
        self.csv_path = csv_path

    @contextmanager
    def _open_locked(self, mode: str, lock: int):
        """Open *csv_path* applying an advisory file lock."""
        # Ensure directory exists before attempting to open
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        with open(self.csv_path, mode, newline='', encoding='utf-8') as f:
            fcntl.flock(f, lock)
            try:
                yield f
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def load_all(self) -> List[Transaction]:
        """
        Load all transactions from the CSV file, handling both new and legacy formats.
        Returns an empty list if the file does not exist or is empty.
        """
        if not os.path.exists(self.csv_path):
            return []

        transactions: List[Transaction] = []
        with self._open_locked('r', fcntl.LOCK_SH) as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                txn = None
                # Try new format: [serial, desc, paid_by, date, group, category, split, amount]
                if len(row) >= 8:
                    try:
                        txn = Transaction.from_csv_row(row)
                    except (ValueError, IndexError):
                        txn = None
                if txn is None:
                    # Fallback: legacy format [serial, desc, paid_by, group, date, amount, category, split_label]
                    try:
                        serial, desc, paid_by, group, date, amount_str, category, split_label = row[:8]
                        amount = float(amount_str)
                        # Parse a fraction in parentheses, e.g. "Even (1/2 each)"
                        m = re.search(r"\((\d+)/(\d+)", split_label)
                        if m:
                            num, den = m.groups()
                            split = round(int(num) / int(den), 1)
                        else:
                            # default to equal split
                            split = round(1.0 / len(PARTICIPANTS), 1)
                        txn = Transaction(
                            serial_number=serial,
                            description=desc,
                            paid_by=paid_by,
                            date=date,
                            group=group,
                            category=category,
                            split=split,
                            amount=amount,
                        )
                    except Exception:
                        # Skip malformed legacy rows
                        continue
                if txn:
                    transactions.append(txn)
        return transactions

    def save(self, txn: Transaction) -> None:
        """
        Append a single transaction to the CSV file.
        Creates the file if it does not exist.
        """
        with self._open_locked('a', fcntl.LOCK_EX) as f:
            writer = csv.writer(f)
            writer.writerow(txn.to_csv_row())

    def delete(self, serial_number: str) -> None:
        """
        Delete a transaction by its serial number.
        Rewrites the CSV file without the matching entry.
        """
        transactions = self.load_all()
        remaining = [t for t in transactions if t.serial_number != serial_number]

        with self._open_locked('w', fcntl.LOCK_EX) as f:
            writer = csv.writer(f)
            for t in remaining:
                writer.writerow(t.to_csv_row())
