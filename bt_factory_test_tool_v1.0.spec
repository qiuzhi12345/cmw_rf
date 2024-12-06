# -*- mode: python -*-

block_cipher = None


a = Analysis(['bt_factory_test_tool_v1.0.py'],
             pathex=['E:\\pyqt_working\\cmw_rftest'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='bt_factory_test_tool_v1.0',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
