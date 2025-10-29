"""# src/splitter_app/utils.py."""

import sys
from pathlib import Path


def _validate_relative(base: str, rel: str) -> str:
    """Resolve *rel* against *base* and ensure it stays within *base*.

    This guards against path traversal attempts such as "../secret" which
    could otherwise expose files outside the packaged resources directory.

    :raises ValueError: if the resolved path escapes the base directory.
    :return: The absolute, normalised path.
    """
    base_abs = Path(base).resolve()
    # Join and normalise to an absolute path
    full_path = (base_abs / rel).resolve()

    # Check if full_path is relative to base_abs (i.e., within the base directory)
    try:
        full_path.relative_to(base_abs)
    except ValueError:
        msg = "Relative path escapes base directory"
        raise ValueError(msg) from None

    return str(full_path)


def resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource, works for development and PyInstaller bundles.

    :param relative_path: Path relative to the resources directory or project root.
    :return: Absolute filesystem path to the resource.
    """
    # PyInstaller stores data files in a temp folder referenced by _MEIPASS
    meipass = getattr(sys, "_MEIPASS", None)

    base_path = meipass or Path(__file__).parent.resolve()

    return _validate_relative(str(base_path), relative_path)
