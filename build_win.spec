# PyInstaller spec for Scholar Summit Email Scraper
# This configuration produces a one-file Windows executable.

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

a = Analysis(
    ['app/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

datas += collect_data_files('PyQt6', includes=['Qt6/**'])
binaries = collect_dynamic_libs('PyQt6')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries + binaries,
    a.zipfiles,
    a.datas + datas,
    [],
    name='SS_Scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
