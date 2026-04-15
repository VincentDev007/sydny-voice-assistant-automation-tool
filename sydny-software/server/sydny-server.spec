import shutil
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

ffmpeg_path = shutil.which('ffmpeg')
if not ffmpeg_path:
    raise RuntimeError("ffmpeg not found. Install it with: brew install ffmpeg")

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[
        (ffmpeg_path, '.'),
        *collect_dynamic_libs('ctranslate2'),
    ],
    datas=[
        *collect_data_files('faster_whisper'),
        *collect_data_files('ctranslate2'),
    ],
    hiddenimports=[
        'ctranslate2',
        'faster_whisper',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='sydny-server',
    debug=False,
    strip=False,
    upx=False,
    console=True,
    onefile=True,
)
