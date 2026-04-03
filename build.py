"""
build.py — Build PythonEscapeRoom for macOS, Windows, or Linux.
Run with: uv run build.py
"""

import subprocess
import sys

args = [
    sys.executable, "-m", "PyInstaller",
    "--onedir",
    "--name", "PythonEscapeRoom",
    "--add-data", "rooms:rooms",
]

if sys.platform == "darwin":
    args += ["--windowed", "--osx-bundle-identifier", "com.kurt.pythonescaperoom"]
    dist_path = "dist/PythonEscapeRoom.app"
    tip = "Drag it to Applications or double-click to play."
elif sys.platform == "win32":
    args += ["--windowed"]
    dist_path = "dist\\PythonEscapeRoom\\PythonEscapeRoom.exe"
    tip = "Double-click the .exe to play."
else:
    dist_path = "dist/PythonEscapeRoom/PythonEscapeRoom"
    tip = "Run the executable directly."

args.append("app.py")

subprocess.run(args, check=True)

print()
print("✓ Done!")
print(f"  Your app is at: {dist_path}")
print(f"  {tip}")
