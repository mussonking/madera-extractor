# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file pour l'installateur Folios Extractor.

Build: pyinstaller --clean build_installer.spec
Output: dist/Installer-FoliosExtractor.exe
"""

import os

block_cipher = None
base_path = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(base_path, 'src', 'installer.py')],
    pathex=[os.path.join(base_path, 'src')],
    binaries=[],
    datas=[
        # Inclure FoliosExtractor.exe dans l'installateur
        (os.path.join(base_path, 'dist', 'FoliosExtractor.exe'), '.'),
        (os.path.join(base_path, 'folios-extractor.conf'), '.'),
    ],
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Installer-FoliosExtractor',
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
    uac_admin=True,  # Demande les droits admin automatiquement
    icon=None,
)
