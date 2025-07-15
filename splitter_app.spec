# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Adrian\\Documents\\development\\splitter_app\\batch_scripts\\\\..\\splitter_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("src/splitter_app/resources/credentials.json", "resources")
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='splitter_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Adrian\\Documents\\development\\splitter_app\\resources\\wallet-icon.ico'],
)
