import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from splitter_app.config import (
    SCOPES,
    CLIENT_SECRETS_FILE,
    ENV_CREDENTIALS_VAR,
)
from splitter_app.config import default_config_path  # your ~/.config/.../token.json
from splitter_app.config import CREDENTIALS_FILE as _orig_credentials_file
import splitter_app.config as _config


def ensure_credentials() -> str:
    """
    Make sure we have a valid token.json in the user config dir.
    Returns the path to the credentials file to use.
    """
    # 1) Decide where to store the token
    token_path_str = os.getenv(ENV_CREDENTIALS_VAR) or str(default_config_path)
    token_path = Path(token_path_str)

    # 2) Load existing token if it exists
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path_str, SCOPES)

    # 3) If no (valid) creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # ensure directory exists & save the token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    # 4) Monkey-patch config.CREDENTIALS_FILE so download/upload use the new token
    _config.CREDENTIALS_FILE = token_path_str
    return token_path_str
