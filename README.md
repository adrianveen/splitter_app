# Contribution Splitter

A simple Python/Qt (PySide6) application for tracking expenses, splitting costs among participants, and summarizing balances owed or owed to each person. Transactions can be appended to or deleted from a table, and all data is saved in a CSV file.

## Features

- **Add Transactions**  
  - Specify a transaction name (e.g., "Groceries").
  - Select who paid for the transaction.
  - Enter the dollar amount with two decimal places.
  - Optionally change the default date (today) to another date.
  - Choose how the costs should be split (e.g., evenly, 2/3-1/3).
  - Automatically saves the transaction in a CSV file.

- **Delete a Selected Transaction**  
  - Select the row you want to remove in the table.
  - Click the **Delete** button (if implemented as such) or run the deletion action.
  - The entry is removed from the table and from the CSV file.

- **Balances & Summary**  
  - Automatically calculates how much each participant has paid or owes based on the defined split fractions.
  - Displays the total for each participant in a summary section at the bottom, with a `-$` notation for negative balances.

- **CSV Data Persistence**  
  - All transactions are stored in a `transactions.csv` file.
  - New transactions are appended every time you add them.
  - If you delete a transaction, it will be removed from the CSV as well (assuming the deletion logic is included in your code).

## Requirements

- **Python 3.7+**
- **PySide6** (Install via `pip install PySide6`)

## Installation

1. Clone or download this repository.
2. Navigate to the project folder:
   ```bash
   cd your_project_folder
3. Create the conda environment:
   ```bash
   conda env create -f environment.yml
4. Run the application
   ```bash
   python splitter_app.py

## Usage

1. Add a transaction
2. Delete a transaction
3. View Summary

## Customizing

- **Participants**
Edit the `self.participants` list in `splitter_app.py` to add or remove names.
- **Split Options**
Edit the `self.split_options` dictionary to change how costs are fractioned.

## Known Limitations
- Currently, the split logic may assume exactly two participants. If you have more participants, you’ll need to expand how fractions and net balances are computed in the code.
- The application is designed for demonstration purposes and not hardened for production-level error handling or concurrency.