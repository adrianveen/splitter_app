"""#!/usr/bin/env python."""

import sys
from pathlib import Path

# Add the src directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from splitter_app.config import CREDENTIALS_FILE, DRIVE_FILE_ID
from splitter_app.services.google_api import _assert_file_accessible, _service, _whoami

if __name__ == "__main__":
    svc = _service(Path(CREDENTIALS_FILE))
    email, name = _whoami(svc)
    print(f"Authed as: {name} <{email}>")

    try:
        meta = _assert_file_accessible(svc, DRIVE_FILE_ID)
        print(
            f"Can access: {meta['name']} (id={meta['id']}) driveId={meta.get('driveId')}",
        )
    except Exception as e:
        print("Preflight failed:", repr(e))
