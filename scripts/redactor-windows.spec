# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath('.'))

a = Analysis(
    ['../redactor-gui.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('../core', 'core'),
        ('../utils', 'utils'),
        ('../config', 'config'),
        ('../docs', 'docs'),
    ],
    hiddenimports=[
        'spacy',
        'en_core_web_sm',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'webview',
        'fitz',
        'PyMuPDF',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'threading',
        'queue',
        'json',
        're',
        'os',
        'sys',
        'pathlib',
        'tempfile',
        'hashlib',
        'random',
        'datetime',
        'typing',
        'shutil',
        'dataclasses',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Key: exclude binaries for --onedir mode
    name='redactor-windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an .ico file here later
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='redactor-windows',
)