"""Docstring for splitter_app.services.auth."""

import os
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import splitter_app.config as _config
from splitter_app.config import (
    CLIENT_SECRETS_FILE,
    ENV_CREDENTIALS_VAR,
    SCOPES,
    default_config_path,  # your ~/.config/.../token.json
)


def ensure_credentials() -> str:
    """Make sure we have a valid token.json in the user config dir.

    Returns the path to the credentials file to use.

    This function handles the OAuth flow robustly:
    - If no credentials exist, triggers new OAuth flow
    - If credentials exist but are invalid, attempts token refresh
    - If refresh fails (e.g., invalid_grant errors), falls back to new OAuth flow
    - Ensures the app continues to work even with expired/invalid refresh tokens
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
            try:
                creds.refresh(Request())
            except RefreshError:
                # If refresh fails (e.g., invalid_grant), fall back to full OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE,
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        # ensure directory exists & save the token with restricted permissions
        token_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        Path.chmod(token_path, 0o600)

    # 3) Ensure creds are valid and cover required scopes
    need_reauth = False
    if creds:
        try:
            # If token missing required scopes, reauth
            if SCOPES and (
                not creds.scopes or any(scope not in creds.scopes for scope in SCOPES)
            ):
                need_reauth = True
            elif not creds.valid:
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except RefreshError:
                        # Common when scopes changed (invalid_scope) — force re-consent
                        need_reauth = True
                else:
                    need_reauth = True
        except Exception:
            # Any unexpected issue reading/refreshing -> reauth
            need_reauth = True
    else:
        need_reauth = True

    if need_reauth:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            SCOPES,
        )
        creds = flow.run_local_server(port=0)

    # 4) Monkey-patch config.CREDENTIALS_FILE so download/upload use the new token
    _config.CREDENTIALS_FILE = token_path_str
    return token_path_str
