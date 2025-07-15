# src/splitter_app/utils.py

import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for development and PyInstaller bundles.

    :param relative_path: Path relative to the resources directory or project root.
    :return: Absolute filesystem path to the resource.
    """
    # PyInstaller stores data files in a temp folder referenced by _MEIPASS
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base_path = meipass
    else:
        # Use the directory where this utils.py file resides
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)
