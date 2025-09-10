# src/splitter_app/services/sheets.py
"""Utilities for reading transactions from Google Sheets."""
from splitter_app import config
from splitter_app.models import Transaction
from .google_api import read_sheet as _read_sheet

__all__ = ["load_transactions"]

def load_transactions():
    """Fetch transactions from the configured Google Sheet."""
    values = _read_sheet(
        config.SHEETS_SPREADSHEET_ID,
        config.SHEETS_RANGE,
        config.CREDENTIALS_FILE,
    )
    transactions: list[Transaction] = []
    for row in values:
        if len(row) < 8:
            continue
        try:
            transactions.append(Transaction.from_csv_row(row))
        except (ValueError, IndexError):
            continue
    return transactions
