# src/splitter_app/utils.py

import sys
import os


def _validate_relative(base: str, rel: str) -> str:
    """Resolve *rel* against *base* and ensure it stays within *base*.

    This guards against path traversal attempts such as "../secret" which
    could otherwise expose files outside the packaged resources directory.

    :raises ValueError: if the resolved path escapes the base directory.
    :return: The absolute, normalised path.
    """
    rel_norm = os.path.normpath(rel)
    # Join and normalise to an absolute path
    full_path = os.path.abspath(os.path.join(base, rel_norm))
    base_abs = os.path.abspath(base)
    if os.path.commonpath([base_abs, full_path]) != base_abs:
        raise ValueError("Relative path escapes base directory")
    return full_path

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

    return _validate_relative(base_path, relative_path)
