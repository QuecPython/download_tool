# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['QuecPythonDownload.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('exes/aboot.tar.gz','./exes'),
        ('exes/blf_tools.tar.gz','./exes'),
        ('exes/Eigen.tar.gz','./exes'),
        ('exes/FC41D.tar.gz','./exes'),
        ('exes/FCM360W.tar.gz','./exes'),
        ('exes/NB.tar.gz','./exes'),
        ('exes/rda.tar.gz','./exes')
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
    name='QuecPythonDownload',
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
