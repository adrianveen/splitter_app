
# Contribution Splitter

A modern desktop application built with Python and PySide6 for managing shared expenses among multiple participants. The app tracks transactions, splits costs, calculates balances, and synchronizes data with Google Drive, enabling real-time collaboration.

## Features

### Easy Transaction Management

- **Add Transactions**
  - Enter a description, amount (CAD), payer, date, category, group, and payer’s share fraction.
  - Automatically generates unique serial numbers for each entry.
  - Transactions sync instantly with Google Drive.

- **Delete Transactions**
  - Easily delete selected transactions from the interface.
  - Changes reflect immediately both locally and on Google Drive.

### Automatic Balance Calculation

- Clearly displays amounts owed and paid by each participant.
- Summarizes total and group-specific balances for easy understanding.

### Google Drive Sync

- Stores data remotely in a CSV file on Google Drive for easy access and updates.
- Automatically synchronizes transactions upon opening and closing the application.

### User-Friendly Interface

- Dark-themed Fusion style for enhanced readability.
- Interactive tables and summaries dynamically update with user actions.

### Data Persistence

- CSV-based local storage for offline access and resilience.
- Automatically handles legacy data formats.

## Installation

### Option 1: For End Users (Recommended)

Simply download and run the pre-built executable.

- [Download Latest Release (Windows)](https://github.com/adrianveen/splitter_app/releases/latest)
- Extract and run `splitter_app.exe`.

### Option 2: For Developers & Contributors

#### Requirements

- **Python 3.10+**
- **Conda** (recommended) or Python venv
- **PySide6**
- **Google API Python Client Libraries**

#### Setup

1. Clone the repository:

```bash
git clone https://github.com/adrianveen/splitter_app.git
cd splitter_app
```

2. Install dependencies using conda:

```bash
conda env create -f environment.yaml
conda activate splitter_app
```

3. Configure Google Drive API:

- Download OAuth2 credentials from [Google Cloud Console](https://console.cloud.google.com/).
- Save credentials JSON as `resources/credentials.json`.
- Authorize the application upon first run.

4. Launch the app:

```bash
python src/splitter_app/main.py
```

## Usage

- **Add Transactions**: Complete the form fields and click "Add Transaction."
- **Delete Transactions**: Select a transaction row, then click "Delete Entry."
- **Balances & Summaries**: View live-updated financial summaries at the bottom of the app.

## Customization

- **Participants & Categories**: Customize the participants and transaction categories in `config.py`.
- **Split Logic**: Adjustable splits directly through the UI or via configuration.

## Known Limitations

- Primarily optimized for two main participants, expandable with minor code modifications.

## License

This project is licensed under the MIT License. Refer to [LICENSE](https://github.com/adrianveen/splitter_app/blob/main/LICENSE) for complete details.
