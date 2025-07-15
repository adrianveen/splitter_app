# src/splitter_app/models.py

from dataclasses import dataclass
from typing import List

@dataclass
class Transaction:
    """
    Represents a financial transaction entry.

    Attributes:
        serial_number: Unique code (e.g. "A001").
        description: Description of the transaction.
        paid_by: Participant who paid.
        date: ISO date string ("YYYY-MM-DD").
        group: Logical grouping (e.g. "general").
        category: Transaction category (e.g. "Food & Drinks").
        split: Fraction paid by the payer (0.0–1.0).
        amount: Transaction amount in CAD.
    """
    serial_number: str
    description: str
    paid_by: str
    date: str
    group: str
    category: str
    split: float
    amount: float

    @classmethod
    def from_csv_row(cls, row: List[str]) -> 'Transaction':
        """
        Create a Transaction from a list of CSV strings.
        Expected format: [serial, desc, paid_by, date, group, category, split, amount]
        """
        return cls(
            serial_number=row[0],
            description=row[1],
            paid_by=row[2],
            date=row[3],
            group=row[4],
            category=row[5],
            split=float(row[6]),
            amount=float(row[7]),
        )

    def to_csv_row(self) -> List[str]:
        """
        Export the Transaction to a list of strings for CSV writing.
        """
        return [
            self.serial_number,
            self.description,
            self.paid_by,
            self.date,
            self.group,
            self.category,
            f"{self.split:.1f}",
            f"{self.amount:.2f}",
        ]
