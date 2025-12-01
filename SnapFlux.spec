# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\edi\\Programing\\PlayWRight\\web', 'web'), ('D:\\edi\\Programing\\PlayWRight\\modules', 'modules'), ('D:\\edi\\Programing\\PlayWRight\\chrome', 'chrome')],
    hiddenimports=['eel', 'playwright', 'playwright.sync_api', 'playwright._impl', 'openpyxl', 'PIL', 'requests', 'logging.handlers', 'pandas', 'numpy'],
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
    [],
    exclude_binaries=True,
    name='SnapFlux',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\edi\\Programing\\PlayWRight\\icon.ico'],
    contents_directory='SnapFlux',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SnapFlux',
)
