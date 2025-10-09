# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['trainer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),
        ('assets/icon.icns', 'assets')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='Curiosity Trainer',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon="assets/icon.ico"
)

app = BUNDLE(exe,
    name='Curiosity Trainer.app',
    icon="assets/icon.icns",
    bundle_identifier=None,
    info_plist={
        "LSBackgroundOnly": False,
        "CFBundleDisplayName": "Curiosity Trainer",
        "CFBundleName": "Curiosity Trainer",
        "CFBundleShortVersionString": "0.1.0"
    })