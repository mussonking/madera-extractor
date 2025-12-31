# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file pour Folios Extractor.

Build: pyinstaller --clean build.spec
Output: dist/FoliosExtractor.exe
"""

import os

block_cipher = None

# Chemin de base
base_path = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(base_path, 'src', 'main.py')],
    pathex=[os.path.join(base_path, 'src')],
    binaries=[],
    datas=[
        # Inclure UnRAR.exe
        (os.path.join(base_path, 'src', 'bin', 'UnRAR.exe'), 'bin'),
        # Inclure le fichier de config par défaut
        (os.path.join(base_path, 'folios-extractor.conf'), '.'),
    ],
    hiddenimports=[
        'py7zr',
        'winotify',
        'send2trash',
    ],
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
    name='FoliosExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compression UPX si disponible
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de fenêtre console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Ajouter une icône ici si disponible: icon='icon.ico'
)
