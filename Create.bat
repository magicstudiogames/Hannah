echo # -*- mode: python ; coding: utf-8 -*- > Hannah.spec && ^
echo a = Analysis(['Hannah.py'], pathex=[], binaries=[], datas=[], hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0) >> Hannah.spec && ^
echo pyz = PYZ(a.pure) >> Hannah.spec && ^
echo exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='Hannah', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None, console=False, disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None, uac_admin=True) >> Hannah.spec && ^
python -m PyInstaller Hannah.spec
