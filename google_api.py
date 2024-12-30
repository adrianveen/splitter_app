from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_to_drive(drive_file_id, local_file_path, credentials_path):
    """
    Updates an existing Drive file (by drive_file_id) with the local CSV.
    """
    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build('drive', 'v3', credentials=creds)

    media_body = MediaFileUpload(local_file_path, mimetype='text/csv')

    updated_file = service.files().update(
        fileId=drive_file_id,
        media_body=media_body,
        fields='id'
    ).execute()

    print(f"Updated existing file with ID: {updated_file.get('id')}")


def download_from_drive(file_id, output_path, credentials_path):
    """
    Downloads the CSV from Google Drive and saves it locally.
    
    :param file_id: The file ID on Google Drive.
    :param output_path: Where to save the CSV locally (e.g., "transactions.csv").
    :param credentials_path: Path to your credentials JSON.
    """
    from googleapiclient.http import MediaIoBaseDownload
    import io
    
    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build('drive', 'v3', credentials=creds)
    
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download progress: {int(status.progress() * 100)}%")
    print(f"Downloaded to {output_path}")
