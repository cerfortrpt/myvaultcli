# build.py
import subprocess
from pathlib import Path

def write_version():
    version_file = Path("scripts/version.py")
    try:
        version = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], text=True).strip()
    except subprocess.CalledProcessError:
        version = "v0.0.0"

    version_file.write_text(f'__version__ = "{version}"\n')
    print(f"✅ Injected version {version} into myvaultcli/scripts/version.py")

if __name__ == "__main__":
    write_version()
