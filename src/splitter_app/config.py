# src/splitter_app/config.py
"""
Central configuration for the Contribution Splitter app:
- Google Drive integration constants
- Local file paths
- Default participants and categories
- Category-to-letter mapping for serial numbers
- Support for loading OAuth credentials from an external path via env var or default config location
"""
import os
from pathlib import Path
from splitter_app.utils import resource_path


# at the top, after your imports
SCOPES: list[str] = ["https://www.googleapis.com/auth/drive.file"]

# path to your OAuth2 client-secrets JSON (downloaded from Google Cloud Console)
# You can override this with the environment variable below to point to a
# different client (e.g., when testing a new GCP project).
ENV_CLIENT_SECRETS_VAR = "GOOGLE_CLIENT_SECRETS_FILE"
_env_client_secrets = os.getenv(ENV_CLIENT_SECRETS_VAR)
if _env_client_secrets:
    CLIENT_SECRETS_FILE: str = str(Path(_env_client_secrets))
else:
    CLIENT_SECRETS_FILE: str = resource_path("resources/credentials.json")

# --- Environment variable for external credentials ---
# If set, this path overrides the default token path
ENV_CREDENTIALS_VAR = "GOOGLE_TOKEN_PATH"

# --- Google Drive Settings ---
# The Drive file ID for the transactions CSV
# You can override this per environment/session using GOOGLE_DRIVE_FILE_ID
ENV_DRIVE_FILE_ID_VAR = "GOOGLE_DRIVE_FILE_ID"
DRIVE_FILE_ID: str = os.getenv(ENV_DRIVE_FILE_ID_VAR) or "1UNCEKJkpZ0nLDauX4Z2S_p01e64Th_wV"

# Path to OAuth2 credentials JSON
# Priority:
# 1) Path from ENV_CREDENTIALS_VAR
# 2) Default at ~/.config/splitter_app/token.json
_env_token_path = os.getenv(ENV_CREDENTIALS_VAR)
default_config_path = Path.home() / ".config" / "splitter_app" / "token.json"

if _env_token_path:
    # Use the path from the environment variable, even if it doesn't yet exist
    CREDENTIALS_FILE: str = str(Path(_env_token_path))
else:
    # Fall back to the standard config directory; the token will be created here
    CREDENTIALS_FILE: str = str(default_config_path)

# Local path where the transactions CSV is stored/loaded
LOCAL_CSV_PATH: str = resource_path("transactions.csv")

# --- Application Defaults ---
# Initial list of participants
PARTICIPANTS: list[str] = ["Adrian", "Vic"]

# Default transaction categories
TRANSACTION_CATEGORIES: list[str] = [
    "Food & Drinks",
    "Travel",
    "Groceries",
    "Other",
]

# Mapping from transaction category to serial-code letter
CATEGORY_MAP: dict[str, str] = {
    "Food & Drinks": "A",
    "Travel":        "B",
    "Groceries":     "C",
    "Other":         "D",
}
