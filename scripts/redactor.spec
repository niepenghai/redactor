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
    exclude_binaries=True,
    name='PDFRedactor',
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
    icon=None,  # You can add an .icns file here later
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDFRedactor',
)

app = BUNDLE(
    coll,
    name='PDFRedactor.app',
    icon=None,  # You can add an .icns file here later
    bundle_identifier='com.redactor.pdfredactor',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleName': 'PDF Redactor',
        'CFBundleDisplayName': 'PDF Redactor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'LSMinimumSystemVersion': '10.15.0',
        'NSRequiresAquaSystemAppearance': False,
    }
)