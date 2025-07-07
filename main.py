import argparse
import importlib.util
import os
import sys
import hashlib
import urllib.request
import subprocess

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

def fetch_expected_sha():
    version = __version__  # Optional: parse from your app version
    url = f"https://github.com/cerfortrpt/myvaultcli/releases/download/{version}/main.sha256"
  #  print("Getting hash from url " + url)

    try:
        result = subprocess.run(
            ["curl", "-sL", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Could not fetch expected SHA256: {e.stderr.strip()}")
        return None

def enforce_self_integrity():
    expected = fetch_expected_sha()
    actual = get_sha256(get_self_path())
    if not expected or not actual:
        print("Integrity check failed (missing or unreadable hash).")
        sys.exit(1)
    if expected != actual:
        print("Integrity check failed! The binary may have been tampered with.")
        print(f"Expected: {expected}\nActual:   {actual}")
        sys.exit(1)


def enforce_latest_version():
    try:
        result = subprocess.run(
            ["gh", "release", "view", "--repo", "cerfortrpt/myvaultcli", "--json", "tagName", "-q", ".tagName"],
            capture_output=True,
            check=True,
            text=True
        )
        tag = result.stdout.strip()
    except Exception as e:
        print(f"Failed to fetch latest version via GitHub CLI: {e}")
        sys.exit(1)


    latest = "v" + str(tag.lstrip("v"))
    if latest and not latest==__version__:
        print("Run \"brew upgrade myvault\" to install latest version: " + latest)
        sys.exit(1)
      



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

    #enforce latest of version of cli or exit
    enforce_latest_version()


    parser = argparse.ArgumentParser(prog="myvault")
    parser.add_argument("--version", action="version", version=f"myvault {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # fingerprint
    subparsers.add_parser("fingerprint", help="Authenticate to Vault using fingerprint")

    # rotate
    subparsers.add_parser("rotate", help="Rotate Vault client certificates")

    # status
    subparsers.add_parser("status", help="Show Vault certificate status")

    # clean
    subparsers.add_parser("clean", help="Remove local certificates and tokens")

    # version
    subparsers.add_parser("version", help="Show CLI version")

    # verify
    subparsers.add_parser("verify", help="Verify CLI binary and config integrity")


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
