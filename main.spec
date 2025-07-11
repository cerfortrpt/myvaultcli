# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('scripts', './scripts')],
    hiddenimports=['objc', 'Foundation', 'LocalAuthentication', 'keyring', 'cryptography',         'cryptography.hazmat.bindings._rust',
        'cryptography.hazmat.backends.openssl.backend',
        'cryptography.x509',
        'cryptography.x509.name',
        'cryptography.x509.oid'],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
hookspath=['./hooks'],
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
