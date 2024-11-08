# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['FinanceDownloader/src/GUI.py'],
    pathex=['FinanceDownloader/src'],  # Incluimos el directorio 'src'
    binaries=[],
    datas=[],
    hiddenimports=['Downloader'],  # Usamos solo 'Downloader' ya que es un paquete
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Crear el archivo pyz, necesario para empaquetar los scripts en un solo archivo
pyz = PYZ(a.pure)

# Crear el ejecutable en un solo archivo
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mantén False para modo ventana
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,  # Aquí habilitamos el empaquetado en un solo archivo
)

# Asegúrate de que el ejecutable esté empaquetado en un solo archivo
