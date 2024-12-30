import sys
import os
import csv
import string
from datetime import datetime
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtCore import Qt

from google_api import upload_to_drive, download_from_drive

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGridLayout,
    QDateEdit,
    QVBoxLayout,
    QMessageBox,
    QHBoxLayout,
    QHeaderView
)
from PySide6.QtCore import QDate

CSV_FILENAME = "transactions.csv"

CATEGORY_MAP = {
            "Food & Drinks": "A",
            "Travel": "B",
            "Groceries": "C",
            "Other": "D"
        }

# This file ID should point to the existing transactions.csv in Google Drive.
DRIVE_FILE_ID = "1UNCEKJkpZ0nLDauX4Z2S_p01e64Th_wV"
CREDENTIALS_FILE = "resources/token.json"  # or token.json if that’s how you stored OAuth
LOCAL_CSV_PATH = "transactions.csv"    # local file name

class SplitterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contribution Splitter")
        self.setMinimumSize(800, 600)

        # Keep track of participants
        self.participants = ["Adrian", "Vic"]  
        # You can add more participants here

        # Fraction options (customize as needed)
        # Each fraction describes how the transaction is split among all participants.
        # For example, "Even (1/2 each)" means 50% for each of two participants
        # "2/3 - 1/3" means first person gets 2/3, second gets 1/3, etc.
        self.split_options = {
            "Even (1/2 each)": [0.5, 0.5],
            "2/3 - 1/3": [2/3, 1/3],
            "3/4 - 1/4": [3/4, 1/4],
            "1/3 - 2/3": [1/3, 2/3],
            "1/4 - 3/4": [1/4, 3/4],
        }
        self.transactions_cat = ["Food & Drinks", "Travel", "Groceries", "Other"]

        self.serial_numbers_dict = {}

        # Main container widget
        container = QWidget()
        self.setCentralWidget(container)

        # Main layout
        main_layout = QVBoxLayout()

        # --- INPUT FORM ---
        form_layout = QGridLayout()

        # 1) Transaction Description
        transaction_desc_label = QLabel("Transaction Description:")
        transaction_desc_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(transaction_desc_label, 0, 0)

        self.desc_input = QLineEdit()
        form_layout.addWidget(self.desc_input, 0, 1)

        # 2) Person who paid
        paid_by_label = QLabel("Paid By:")
        paid_by_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(paid_by_label, 1, 0)

        self.paid_by_combo = QComboBox()
        self.paid_by_combo.addItems(self.participants)
        form_layout.addWidget(self.paid_by_combo, 1, 1)

        # 3) Transaction amount
        amount_label = QLabel("Amount (CAD):")
        amount_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(amount_label, 2, 0)

        self.amount_input = QLineEdit()
        #self.amount_input.textChanged.connect(self.on_amount_input_changed)
        self.amount_input.setPlaceholderText("0.00")
        form_layout.addWidget(self.amount_input, 2, 1)

        # 4) Transaction date
        date_label = QLabel("Date:")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(date_label, 3, 0)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())  # Default = today
        form_layout.addWidget(self.date_input, 3, 1)

        # 5) Transaction category
        category_label = QLabel("Category:")
        category_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(category_label, 4, 0)

        self.category_combo = QComboBox()
        self.category_combo.addItems(self.transactions_cat)
        form_layout.addWidget(self.category_combo, 4, 1)

        # 6) Group Label
        group_label = QLabel("Group:")
        group_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(group_label, 5, 0)

        self.group_input = QLineEdit()
        form_layout.addWidget(self.group_input, 5, 1)

        # 7) Split fraction
        split_fraction_label = QLabel("Split Fraction:")
        split_fraction_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        form_layout.addWidget(split_fraction_label, 6, 0)
        self.split_combo = QComboBox()
        self.split_combo.addItems(self.split_options.keys())
        form_layout.addWidget(self.split_combo, 6, 1)

        # Add transaction button
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)
        form_layout.addWidget(self.add_button, 7, 0, 1, 2)

        main_layout.addLayout(form_layout)

        # --- TABLE WIDGET FOR DISPLAY ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["serial_number", "Description", "Paid By", "Group", "Date", "Amount", "Category","Split"]
        )
        self.table.setColumnHidden(0, True)  # Hide the serial number column

        # Configure the table to stretch columns
        header = self.table.horizontalHeader()
        for column in range(self.table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.Stretch)

        # Enable scrolling in both directions
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        main_layout.addWidget(self.table)

        # --- SUMMARY / WHO OWES WHOM ---
        summary_layout = QGridLayout()
        
        self.summary_label = QLabel("No transactions yet.")
        summary_layout.addWidget(self.summary_label, 0, 0)
        main_layout.addLayout(summary_layout)

        delete_entry_button = QPushButton("Delete Entry")
        
        delete_entry_button.clicked.connect(self.delete_entry)
        summary_layout.addWidget(delete_entry_button, 0, 1)

        # --- GROUP SUMMARY TABLE ---
        self.group_summary_table = QTableWidget()
        self.group_summary_table.setColumnCount(3)
        self.group_summary_table.setHorizontalHeaderLabels(
            ["Group", "Vic Owes", "Adrian Owes"]
        )
        # Configure the table to stretch columns
        header = self.group_summary_table.horizontalHeader()
        for column in range(self.group_summary_table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.Stretch)
        # Enable scrolling in both directions
        self.group_summary_table.setAlternatingRowColors(True)
        self.group_summary_table.setSortingEnabled(False)

        main_layout.addWidget(self.group_summary_table)
        # Set main layout
        container.setLayout(main_layout)

        # Load any existing transactions from CSV
        self.load_transactions_from_csv()
        self.update_summary()
        self.update_group_summary()

    def add_transaction(self):
        """
        Gathers input data, appends a row to the QTableWidget,
        updates the CSV file, and updates the summary label.
        """
        # Get form values
        transaction_desc = self.desc_input.text().strip()
        paid_by = self.paid_by_combo.currentText()
        date_selected = self.date_input.date().toString("yyyy-MM-dd")
        group = self.group_input.text().strip()
        category = self.category_combo.currentText()

        # Validate amount input
        try:
            amount_str = self.amount_input.text().strip()
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        if transaction_desc == "":
            QMessageBox.warning(self, "Invalid Input", "Transaction Name cannot be empty.")
            return
        
        # Group is entered as "General" if left empty
        if group == "":
            group = "general"
        else:
            group = group.lower()

        # Get the selected split distribution
        split_name = self.split_combo.currentText()
        fraction_list = self.split_options[split_name]

        existing_serial = self.load_existing_serial_numbers()  # Simulate fetched data
        print(f"Existing serial numbers: {existing_serial}")
        serial_number = str(self.generate_serial_number(category, existing_serial, date_selected))
        print(f"New serial number: {serial_number}")
        self.serial_numbers_dict[serial_number] = {
            "transaction_desc": transaction_desc,
            "paid_by": paid_by,
            "group": group,
            "date_selected": date_selected,
            "amount": amount,
            "category": category,
            "split_name": split_name
        }

        # Temporarily disable sorting
        self.table.setSortingEnabled(False)
        # Add row to table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        self.table.setItem(row_position, 0, QTableWidgetItem(serial_number))
        self.table.setItem(row_position, 1, QTableWidgetItem(transaction_desc))
        self.table.setItem(row_position, 2, QTableWidgetItem(paid_by))
        self.table.setItem(row_position, 3, QTableWidgetItem(group))
        self.table.setItem(row_position, 4, QTableWidgetItem(date_selected))
        self.table.setItem(row_position, 5, QTableWidgetItem(f"${amount:.2f}"))
        self.table.setItem(row_position, 6, QTableWidgetItem(category)) 
        self.table.setItem(row_position, 7, QTableWidgetItem(split_name))

        # Re-enable sorting
        self.table.setSortingEnabled(True)

        # Reset form fields
        self.desc_input.clear()
        self.amount_input.clear()
        # self.date_input.setDate(QDate.currentDate())

        # Append transaction to CSV
        self.append_to_csv(
            [serial_number,
            transaction_desc, 
             paid_by, 
             group, 
             date_selected, 
             f"{amount:.2f}", 
             category, 
             split_name
             ]
        )

        # Update summary
        self.update_summary()
        self.update_group_summary()

    def load_transactions_from_csv(self):
        """
        Load existing transactions from CSV and populate the table.
        """
        try:
            with open(CSV_FILENAME, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) < 7:
                        continue
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row[0]))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row[1]))
                    self.table.setItem(row_position, 2, QTableWidgetItem(row[2]))
                    self.table.setItem(row_position, 3, QTableWidgetItem(row[3]))
                    self.table.setItem(row_position, 4, QTableWidgetItem(row[4]))
                    # Convert amount to $X.XX
                    try:
                        amount_val = float(row[5])
                        self.table.setItem(row_position, 5, QTableWidgetItem(f"${amount_val:.2f}"))
                    except ValueError:
                        self.table.setItem(row_position, 5, QTableWidgetItem(row[5]))

                    self.table.setItem(row_position, 6, QTableWidgetItem(row[6]))
                    self.table.setItem(row_position, 7, QTableWidgetItem(row[7]))
                    
        except FileNotFoundError:
            # If the file doesn't exist yet, that's okay.
            pass
         
    def append_to_csv(self, row_data):
        """
        Append a single row to the CSV file.
        """
        with open(CSV_FILENAME, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row_data)

    def update_summary(self):
        """
        Calculate the total amounts each participant has paid,
        apply split fractions, and produce a summary of who owes whom.
        """
        # Tally each person's net = amount paid - amount owed
        net_amounts = {person: 0.0 for person in self.participants}

        row_count = self.table.rowCount()
        for row in range(row_count):
            name_item = self.table.item(row, 1)
            paid_by_item = self.table.item(row, 2)
            amount_item = self.table.item(row, 5)
            split_item = self.table.item(row, 7)

            if not (name_item and paid_by_item and amount_item and split_item):
                continue

            paid_by = paid_by_item.text()
            amount_str = amount_item.text().replace('$', '').strip()
            split_name = split_item.text()

            try:
                amount = float(amount_str)
            except ValueError:
                continue

            fraction_list = self.split_options.get(split_name)
            if not fraction_list:
                continue

            net_amounts[paid_by] += amount * (1 - fraction_list[0]) # Add the full amount paid by the person

            for i, person in enumerate(self.participants):
                if person != paid_by:
                    net_amounts[person] -= amount * fraction_list[1]

        # Build the summary string
        summary_str = "Overall Balance Summary:\n"
        for person in self.participants:
            balance = net_amounts[person]
            if balance < 0:
                summary_str += f"{person}: -${abs(balance):.2f} (owes)\n"
            elif balance > 0:
                summary_str += f"{person}: ${balance:.2f} (is owed)\n"
            else:
                summary_str += f"{person}: $0.00 (even)\n"

        self.summary_label.setText(summary_str)
    
    def delete_entry(self):
        """
        Delete a selected entry from the table and the CSV file.
        """
        # open Qdialog to ask if you would like to remove the file from the table
        if self.table.selectedItems():
            confirm_dialog = QMessageBox()
            confirm_dialog.setIcon(QMessageBox.Question)
            confirm_dialog.setText("Are you sure you want to delete this entry?")
            confirm_dialog.setWindowTitle("Delete Entry")
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm_dialog.setDefaultButton(QMessageBox.No)
            response = confirm_dialog.exec()

            if response == QMessageBox.Yes:
                # Remove the selected row from the table
                row = self.table.currentRow()
                serial_number = self.table.item(row, 0).text()
                print(f"Serial number is: {serial_number}")
                print(f"Removing row {row + 1} from table...")
                self.table.removeRow(row)

                # Remove the selected row from the CSV file
            with open(CSV_FILENAME, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                rows = [line for line in reader if line[0] != serial_number]

            with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
        else:
            QMessageBox.warning(self, "No Entry Selected", "Please select an entry to delete.")
    
        self.update_summary()
        self.update_group_summary()

    def normalize_group_name(sel, group_name):
        """
        Normalize the group name by converting to lowercase, stripping spaces, and removing punctuation.
        """
        return group_name.strip().lower().translate(str.maketrans('', '', string.punctuation))

    def update_group_summary(self):
        """
        Summarizes the amount owed by group and populates the group_summary_table.
        """
        # Clear existing rows
        self.group_summary_table.setRowCount(0)

        # Adjust columns dynamically to match participants
        self.group_summary_table.setColumnCount(len(self.participants) + 1)
        self.group_summary_table.setHorizontalHeaderLabels(["Group"] + self.participants)

        group_totals = {}
    
        for row in range(self.table.rowCount()):
            group_item = self.table.item(row, 3)
            amount_item = self.table.item(row, 5)
            split_item = self.table.item(row, 7)
            paid_by_item = self.table.item(row, 2)
    
            if not (group_item and amount_item and split_item):
                continue
    
            group = self.normalize_group_name(group_item.text())
            try:
                amount = float(amount_item.text().replace('$', '').strip())
            except ValueError:
                print(f"Invalid amount format: {amount_item.text()}")
                continue
    
            split_name = split_item.text()
            fraction_list = self.split_options.get(split_name, [])
            paid_by = paid_by_item.text()
    
            if len(fraction_list) != len(self.participants):
                print(f"Mismatch: Fraction list {fraction_list} does not match participants {self.participants}")
                continue

            if group not in group_totals:
                group_totals[group] = {person: 0 for person in self.participants}

            # Update the group totals
            group_totals[group][paid_by] += amount * (1 - fraction_list[0])
            for i, person in enumerate(self.participants):
                # Calculate the amount owed only if the person didn't pay
                if person != paid_by:                    
                    owed = amount * fraction_list[1]
                    group_totals[group][person] -= owed

        amount_owed = []
        # Clear and populate group_summary_table
        self.group_summary_table.setRowCount(0)
        for group, totals in group_totals.items():
            row_position = self.group_summary_table.rowCount()
            self.group_summary_table.insertRow(row_position)

            # set group name in the first column
            self.group_summary_table.setItem(row_position, 0, QTableWidgetItem(group))


            for col, person in enumerate(self.participants, start=1):
                amount_owed = totals.get(person, 0)
                if amount_owed < 0:
                    amount_owed = abs(amount_owed)
                    self.group_summary_table.setItem(row_position, col, QTableWidgetItem(f"-${amount_owed:.2f} (owes)"))
                elif amount_owed > 0:
                    self.group_summary_table.setItem(row_position, col, QTableWidgetItem(f"${amount_owed:.2f} (is owed)"))
                else:
                    self.group_summary_table.setItem(row_position, col, QTableWidgetItem("$0.00 (even)"))

    def load_existing_serial_numbers(self):
        """Load existing serial numbers from the CSV."""
        try:
            with open(CSV_FILENAME, mode="r") as file:
                reader = csv.reader(file)
                return [row[0] for row in reader if row]  # Ensure row is not empty
        except FileNotFoundError:
            return []
        
    def generate_serial_number(self, category: str, existing_numbers: list, date: str):
        """
        Generate a serial number based on the current date and category.
        
        Parameters:
            category (str): The category for which to generate the serial number.
                            Must be one of ["A", "B", "C", "D"].
            existing_numbers (list): A list of already generated numbers for the current day
                                    and category, e.g., ["20241227-A-0001", ...].
        
        Returns:
            str: The generated serial number.
        """
        # Map categories to letters
        
        if category not in CATEGORY_MAP:
            raise ValueError(f"Invalid category '{category}'. Must be one of {list(CATEGORY_MAP.keys())}.")
        
        category_letter = CATEGORY_MAP[category]
        
        date = date.replace("-", "")

        # Extract the max existing serial for today's category
        max_serial = max(
            (int(num.split("-")[-1]) for num in existing_numbers 
                if num.startswith(f"{date}-{category_letter}")), 
            default = 0
        )
        
        next_serial = max_serial + 1

        return f"{date}-{category_letter}-{next_serial:04d}"
    
    def on_amount_input_changed(self, amount):
        """Set the button as focus when the amount changes."""
        if amount:  # Only set focus if amount is not empty
            self.add_button.setDefault(True)
        else:
            self.add_button.setDefault(False)
    
def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        # Path in a onefile PyInstaller executable
        return os.path.join(sys._MEIPASS, relative_path)
    # Path during development
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    # Attempt to download first, to ensure local CSV is up-to-date
    print("Downloading the latest CSV from Drive...")
    try:
        download_from_drive(DRIVE_FILE_ID, LOCAL_CSV_PATH, CREDENTIALS_FILE)
    except Exception as e:
        print(f"Warning: Could not download from Drive. {e}")
    
    app = QApplication(sys.argv)
    # Set Fusion style
    app.setStyle("Fusion")
    # Set the application icon
    icon_path = resource_path("resources/images/wallet-icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    # Create a custom "dark" Fusion palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))

    # Apply the palette to the app
    app.setPalette(palette)
    window = SplitterApp()
    window.show()
     # Run the event loop, ensuring we can still do an upload after exit.
    try:
        exit_code = app.exec()
    finally:
        # After the user closes the app, upload the updated CSV
        print("Uploading updated CSV to Drive...")
        try:
            if os.path.exists(LOCAL_CSV_PATH):
                upload_to_drive(DRIVE_FILE_ID, LOCAL_CSV_PATH, CREDENTIALS_FILE)
            else:
                print(f"No local CSV found at {LOCAL_CSV_PATH}; skipping upload.")
        except Exception as e:
            print(f"Warning: Could not upload to Drive. {e}")

    sys.exit(exit_code)
    #sys.exit(app.exec())

if __name__ == "__main__":
    main()
