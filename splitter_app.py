import sys
import csv
import string
from datetime import datetime
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

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

        # Main container widget
        container = QWidget()
        self.setCentralWidget(container)

        # Main layout
        main_layout = QVBoxLayout()

        # --- INPUT FORM ---
        form_layout = QGridLayout()

        # 1) Transaction name
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Transaction Name", "Paid By", "Group", "Date", "Amount", "Category","Split"]
        )
        # Configure the table to stretch columns
        header = self.table.horizontalHeader()
        for column in range(self.table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.Stretch)
        # Enable scrolling in both directions
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)

        main_layout.addWidget(self.table)

        # --- SUMMARY / WHO OWES WHOM ---
        summary_layout = QGridLayout()
        
        self.summary_label = QLabel("No transactions yet.")
        summary_layout.addWidget(self.summary_label, 0, 0)
        main_layout.addLayout(summary_layout)

        delete_entry_button = QPushButton("Delete Entry")
        
        delete_entry_button.clicked.connect(self.delete_entry)
        summary_layout.addWidget(delete_entry_button, 0, 1)

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

        # Add row to table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        self.table.setItem(row_position, 0, QTableWidgetItem(transaction_desc))
        self.table.setItem(row_position, 1, QTableWidgetItem(paid_by))
        self.table.setItem(row_position, 2, QTableWidgetItem(group))
        self.table.setItem(row_position, 3, QTableWidgetItem(date_selected))
        self.table.setItem(row_position, 4, QTableWidgetItem(f"${amount:.2f}"))
        self.table.setItem(row_position, 5, QTableWidgetItem(category)) 
        self.table.setItem(row_position, 6, QTableWidgetItem(split_name))

        # Reset form fields
        self.desc_input.clear()
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())

        # Append transaction to CSV
        self.append_to_csv(
            [transaction_desc, 
             paid_by, 
             group, 
             date_selected, 
             f"{amount:.2f}", 
             category, 
             split_name]
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
                    # Convert amount to $X.XX
                    try:
                        amount_val = float(row[4])
                        self.table.setItem(row_position, 4, QTableWidgetItem(f"${amount_val:.2f}"))
                    except ValueError:
                        self.table.setItem(row_position, 4, QTableWidgetItem(row[4]))
                    self.table.setItem(row_position, 5, QTableWidgetItem(row[5]))
                    self.table.setItem(row_position, 6, QTableWidgetItem(row[6]))
                    
                    # for col_index, col_value in enumerate(row):
                    #     if col_index == 3:  # Amount column
                    #         col_value = f"${float(col_value):.2f}"
                    #     self.table.setItem(row_position, col_index, QTableWidgetItem(col_value))
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
            name_item = self.table.item(row, 0)
            paid_by_item = self.table.item(row, 1)
            group_item = self.table.item(row, 2)
            date_item = self.table.item(row, 3)
            amount_item = self.table.item(row, 4)
            category_item = self.table.item(row, 5)
            split_item = self.table.item(row, 6)

            if not (name_item and paid_by_item and amount_item and split_item):
                continue

            paid_by = paid_by_item.text()
            amount = float(amount_item.text().replace('$', ''))
            split_name = split_item.text()
            fraction_list = self.split_options.get(split_name, [0.5, 0.5])

            # Increase net for the payer
            net_amounts[paid_by] += amount

            # Subtract each participant's share
            for i, person in enumerate(self.participants):
                owed = amount * fraction_list[i]
                net_amounts[person] -= owed

        # Build the summary string
        summary_str = "Overall Balance Summary:\n"
        for person in self.participants:
            balance = net_amounts[person]
            if balance < 0:
                # For negative amounts, show as -$XXX.XX
                summary_str += f"{person}: -${abs(balance):.2f}\n"
            else:
                # For zero or positive amounts, show as $XXX.XX
                summary_str += f"{person}: ${balance:.2f}\n"

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
                transaction_desc = self.table.item(row, 0).text()
                self.table.removeRow(row)

                # Remove the selected row from the CSV file
                with open(CSV_FILENAME, "r", newline="", encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)

                with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    for line in rows:
                        if line[0] != transaction_desc:
                            writer.writerow(line)
                self.update_summary()
                self.update_group_summary()
        else:
            QMessageBox.warning(self, "No Entry Selected", "Please select an entry to delete.")

    def normalize_group_name(sel, group_name):
        """
        Normalize the group name by converting to lowercase, stripping spaces, and removing punctuation.
        """
        return group_name.strip().lower().translate(str.maketrans('', '', string.punctuation))

    def update_group_summary(self):
        """
        Summarizes the amount owed by group and populates the group_summary_table.
        """
        group_totals = {}

        for row in range(self.table.rowCount()):
            group_item = self.table.item(row, 2)
            amount_item = self.table.item(row, 4)
            split_item = self.table.item(row, 6)

            if not (group_item and amount_item and split_item):
                continue

            group = self.normalize_group_name(group_item.text())
            amount = float(amount_item.text().replace('$', ''))
            split_name = split_item.text()
            fraction_list = self.split_options.get(split_name, [0.5, 0.5])

            if group not in group_totals:
                group_totals[group] = {person: 0 for person in self.participants}

            for i, person in enumerate(self.participants):
                owed = amount * fraction_list[i]
                group_totals[group][person] += owed

        self.group_summary_table.setRowCount(0)  # Clear existing rows

        for group, totals in group_totals.items():
            row_position = self.group_summary_table.rowCount()
            self.group_summary_table.insertRow(row_position)
            self.group_summary_table.setItem(row_position, 0, QTableWidgetItem(group.capitalize()))
            self.group_summary_table.setItem(row_position, 1, QTableWidgetItem(f"${totals['Vic']:.2f}"))
            self.group_summary_table.setItem(row_position, 2, QTableWidgetItem(f"${totals['Adrian']:.2f}"))
    

def main():
    app = QApplication(sys.argv)
        # Set Fusion style
    app.setStyle("Fusion")
    
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
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
