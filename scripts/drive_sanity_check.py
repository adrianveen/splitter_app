import sys, os
# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from splitter_app.config import CREDENTIALS_FILE, DRIVE_FILE_ID
from splitter_app.services.google_api import _service, _whoami, _assert_file_accessible

if __name__ == "__main__":
    svc = _service(CREDENTIALS_FILE)
    email, name = _whoami(svc)
    print(f"Authed as: {name} <{email}>")

    try:
        meta = _assert_file_accessible(svc, DRIVE_FILE_ID)
        print(f"Can access: {meta['name']} (id={meta['id']}) driveId={meta.get('driveId')}")
    except Exception as e:
        print("Preflight failed:", repr(e))
