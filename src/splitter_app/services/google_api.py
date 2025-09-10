"""Thin wrappers around the Google Drive API.

The original implementation imported the google-api-python-client at module
import time.  In environments where that dependency is not available (for
example during unit tests or on machines that do not interact with Google
Drive) merely importing this module would raise ``ModuleNotFoundError``.

To make the rest of the application testable without the optional Google
libraries installed we try to import the client lazily and fall back to
stubbed ``None`` objects when the import fails.  The public functions check for
these stubs and raise a clear ``ImportError`` only when they are actually used.
This mirrors the behaviour of other optional dependencies and keeps unrelated
code paths working.
"""

try:  # pragma: no cover - exercised indirectly in tests
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google.oauth2.credentials import Credentials
except ModuleNotFoundError:  # pragma: no cover - executed when library missing
    build = MediaFileUpload = MediaIoBaseDownload = Credentials = None

def upload_to_drive(drive_file_id, local_file_path, credentials_path):
    """Upload ``local_file_path`` to the Drive file ``drive_file_id``.

    Raises
    ------
    ImportError
        If the Google API client libraries are not installed.
    """
    if build is None or MediaFileUpload is None or Credentials is None:
        raise ImportError(
            "google-api-python-client is required to upload files to Drive"
        )

    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build("drive", "v3", credentials=creds)

    media_body = MediaFileUpload(local_file_path, mimetype="text/csv")

    updated_file = (
        service.files()
        .update(fileId=drive_file_id, media_body=media_body, fields="id")
        .execute()
    )

    print(f"Updated existing file with ID: {updated_file.get('id')}")


def download_from_drive(file_id, output_path, credentials_path):
    """Download the Drive file ``file_id`` to ``output_path``.

    The function mirrors :func:`upload_to_drive` in its error handling; an
    :class:`ImportError` is raised if the Google API client is missing.  This
    keeps the rest of the application usable without the dependency installed
    and allows tests to patch these functions easily.
    """
    if (
        build is None
        or MediaIoBaseDownload is None
        or Credentials is None
    ):
        raise ImportError(
            "google-api-python-client is required to download files from Drive"
        )

    import io

    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download progress: {int(status.progress() * 100)}%")
    print(f"Downloaded to {output_path}")
