# src/splitter_app/services/google_api.py  (keep the filename you use now)
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import io

def _service(credentials_path):
    creds = Credentials.from_authorized_user_file(credentials_path)
    return build('drive', 'v3', credentials=creds)

def _whoami(service):
    # Works with Drive scope: returns the authed user email/display name
    about = service.about().get(fields='user(displayName,emailAddress)').execute()
    return about['user']['emailAddress'], about['user']['displayName']

def _assert_file_accessible(service, file_id: str):
    # Preflight: verify the file exists *and* the authed user can see it.
    return service.files().get(
        fileId=file_id,
        supportsAllDrives=True,
        fields='id,name,driveId,owners(emailAddress,displayName),permissions'
    ).execute()

def upload_to_drive(drive_file_id, local_file_path, credentials_path):
    service = _service(credentials_path)
    email, _ = _whoami(service)

    try:
        _assert_file_accessible(service, drive_file_id)
    except HttpError as e:
        if e.resp.status == 404:
            raise FileNotFoundError(
                f"Drive file '{drive_file_id}' not found or not shared with {email}. "
                "If the file lives in a Shared Drive, ensure `supportsAllDrives=True` "
                "is used (it is), and that this user has at least Editor access."
            ) from e
        raise

    media_body = MediaFileUpload(local_file_path, mimetype='text/csv')
    try:
        updated = service.files().update(
            fileId=drive_file_id,
            media_body=media_body,
            fields='id',
            supportsAllDrives=True
        ).execute()
    except HttpError as e:
        if e.resp.status in (403, 404):
            raise PermissionError(
                f"Update failed for '{drive_file_id}' as {email}. "
                "Check sharing and scope."
            ) from e
        raise
    print(f"Updated file ID: {updated.get('id')}")

def download_from_drive(file_id, output_path, credentials_path):
    service = _service(credentials_path)
    email, _ = _whoami(service)

    try:
        meta = _assert_file_accessible(service, file_id)
        print(f"Downloading '{meta['name']}' (id={meta['id']}) as {email}")
    except HttpError as e:
        if e.resp.status == 404:
            raise FileNotFoundError(
                f"Drive file '{file_id}' not found or not shared with {email}."
            ) from e
        raise

    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    with io.FileIO(output_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%")
    print(f"Downloaded to {output_path}")
