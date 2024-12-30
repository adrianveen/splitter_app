import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def initial_upload(local_csv_path, credentials_path):
    """
    Uploads the specified CSV to Google Drive and returns the file ID.
    """
    # Load credentials (assumes OAuth-based file like token.json or credentials.json)
    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build('drive', 'v3', credentials=creds)

    # Prepare file metadata (the name you'll see in Drive)
    file_metadata = {'name': 'transactions.csv'}

    # Indicate it's a CSV
    media = MediaFileUpload(local_csv_path, mimetype='text/csv')

    # Create (upload) the file
    created_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = created_file.get('id')
    print(f"Uploaded '{local_csv_path}' to Drive with file ID: {file_id}")
    return file_id

def main():
    # Adjust if the CSV or credentials.json are in different locations
    local_csv_path = "../transactions.csv"
    credentials_path = "token.json"

    if not os.path.isfile(local_csv_path):
        print(f"Error: '{local_csv_path}' does not exist.")
        sys.exit(1)

    if not os.path.isfile(credentials_path):
        print(f"Error: '{credentials_path}' does not exist.")
        sys.exit(1)

    # Perform the upload
    file_id = initial_upload(local_csv_path, credentials_path)
    print("\nStore this file_id for future downloads/updates:")
    print(file_id)

if __name__ == "__main__":
    main()
