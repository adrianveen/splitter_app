# scripts/get_token.py
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

# 1) Path to the client‐secret you downloaded from GCP:
CLIENT_SECRETS = Path.home() / ".config" / "splitter_app" / "client_secret.json"

# 2) Where to write your authorized‐user credentials:
TOKEN_PATH = Path.home() / ".config" / "splitter_app" / "token.json"

# 3) The scopes you need:
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print(f"Written new token to {TOKEN_PATH}")

if __name__ == "__main__":
    main()
