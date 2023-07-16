import sys
from cx_Freeze import setup, Executable

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable("main.py", base=base, icon="icon.ico")]

setup(
    name="CountdownStreamer",
    version="1.0",
    description="Displays a countdown timer via virtual camera output provided by OBS",
    executables=executables
)