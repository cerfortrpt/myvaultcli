import argparse
import importlib.util
import os
import sys
import hashlib

from scripts.version import __version__

BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))




def get_self_path():
    return sys.executable if getattr(sys, 'frozen', False) else __file__

def get_sha256(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"Error computing hash for {filepath}: {e}")
        return None

def read_expected_sha256():
    base_path = os.path.dirname(get_self_path())
    sha_file = os.path.join(base_path, "main.sha256")
    try:
        with open(sha_file, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Could not read expected SHA256 file: {e}")
        return None

def enforce_self_integrity():
    expected = read_expected_sha256()
    actual = get_sha256(get_self_path())
    if not expected or not actual:
        print("❌ Integrity check failed (missing or unreadable hash).")
        sys.exit(1)
    if expected != actual:
        print("❌ Integrity check failed! The binary may have been tampered with.")
        print(f"Expected: {expected}\nActual:   {actual}")
        sys.exit(1)
    else:
        print("✅ Self-integrity check passed.")



def import_script(script_name):
    script_path = os.path.join(BASE_DIR, "scripts", f"{script_name}.py")
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():

#integrity check: compare expected hash with hash at runtime
#force cli to not except commands if failed
    enforce_self_integrity()

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["fingerprint", "rotate", "status", "clean", "version", "verify"])
    parser.add_argument("--version", action="version", version=f"myvault {__version__}")
    args = parser.parse_args()


    if args.command == "fingerprint":
        import_script("vault_fingerprint").main()
    elif args.command == "rotate":
        import_script("vault_rotate_cert").main()
    elif args.command == "clean":
        import_script("clean").main()
    elif args.command == "status":
        import_script("status").main()
    elif args.command == "version":
        print(f"myvault CLI version {__version__}")
    elif args.command == "verify":
        enforce_self_integrity()
    
if __name__ == "__main__":
    main()
