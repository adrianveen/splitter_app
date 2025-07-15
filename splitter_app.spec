# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# ---- Adjust these to match your project’s layout ----
project_root = os.path.abspath(os.path.dirname(__file__))
src_root     = os.path.join(project_root, "src")
app_pkg      = os.path.join(src_root, "splitter_app")
entry_script = os.path.join(app_pkg, "main.py")
icon_file    = os.path.join(app_pkg, "resources", "wallet-icon.ico")
cred_file    = os.path.join(app_pkg, "resources", "credentials.json")

# Collect any additional non‐.py data from your package (if you have more)
# data_files = collect_data_files("splitter_app", includes=["resources/*"])

a = Analysis(
    scripts=[entry_script],
    pathex=[src_root],
    binaries=[],
    datas=[
        # credentials.json → resources/credentials.json inside bundle
        (cred_file, "resources"),
        # icon → root of bundle
        (icon_file, "."),
        # any other assets you need, e.g.:
        # (os.path.join(app_pkg, "resources", "other.png"), "resources"),
    ],
    hiddenimports=[
        # If you use PySide6, include these so Qt binding gets pulled in:
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="splitter_app",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False → GUI app (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
