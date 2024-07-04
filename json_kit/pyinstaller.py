import PyInstaller.__main__
from pathlib import Path

HERE = Path(__file__).parent.absolute()
path_to_main = str(HERE / "cli.py")

def install():
    PyInstaller.__main__.run([
        path_to_main,
        '--name=json-kit',
        '--onefile',
        '--windowed',
    ])
