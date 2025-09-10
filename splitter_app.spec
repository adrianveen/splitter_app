# splitter_app.spec
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# ---- Entry point and where PyInstaller will look for imports ----
block_cipher = None

a = Analysis(
    scripts=["src/splitter_app/main.py"],
    pathex=["src"],              # so it can find `splitter_app` as a top‐level package
    binaries=[],
    datas=[
    ("src/splitter_app/resources/credentials.json", "resources"),
    ("src/splitter_app/resources/images/wallet-icon.ico", "resources/images"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
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
    console=False,     # GUI app
    icon="src/splitter_app/resources/images/wallet-icon.ico",
)
