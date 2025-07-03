import os
import sys
import socket
import ssl
import platform
import subprocess
import hashlib
import urllib.request
from datetime import datetime
import json

from scripts.version import __version__ # Inject this during build or tag parsing if needed

def check_env_var(var):
    value = os.environ.get(var)
    return value is not None, value

def check_network_reachability(host, port=443, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except Exception:
        return False


import re
import urllib.request
import json

def fetch_latest_release_version():
    try:
        result = subprocess.run(
            ["gh", "release", "view", "--repo", "cerfortrpt/myvaultcli", "--json", "tagName", "-q", ".tagName"],
            capture_output=True,
            check=True,
            text=True
        )
        tag = result.stdout.strip()
        return tag.lstrip("v")
    except Exception as e:
        print(f"Failed to fetch latest version via GitHub CLI: {e}")
        return None


def check_touch_id_available():
    try:
        import LocalAuthentication  # bundled via pyobjc
        context = LocalAuthentication.LAContext.alloc().init()
        success, error = context.canEvaluatePolicy_error_(1, None)
        return bool(success)
    except Exception:
        return False

def get_self_hash():
    path = sys.executable if getattr(sys, "frozen", False) else __file__
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def check_vault_reachable():
    vault_addr = os.environ.get("VAULT_ADDR")
    if not vault_addr:
        return False
    try:
        url = vault_addr.rstrip("/") + "/v1/sys/health"
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status in [200, 429, 472, 473, 501]
    except Exception:
        return False

def print_status(label, ok, info=""):
    status = "✅ OK" if ok else "❌ FAIL"
    print(f"{label:<25} {status} {info}")

def run_diagnostics():
    print("\n📦 Running diagnostics for Vault CLI environment...\n")

    ok_addr, vault_addr = check_env_var("VAULT_ADDR")
    print_status("VAULT_ADDR", ok_addr, vault_addr or "(not set)")

    net_ok = check_network_reachability("github.com")
    print_status("Network (GitHub)", net_ok)

    vault_ok = check_vault_reachable()
    print_status("Vault Reachable", vault_ok)

    touch_id_ok = check_touch_id_available()
    print_status("Touch ID Available", touch_id_ok)

    print_status("Platform", True, f"{platform.system()} {platform.release()} ({platform.machine()})")

    print_status("Python", True, f"{platform.python_version()} (PyInstaller: {'Yes' if getattr(sys, 'frozen', False) else 'No'})")


    latest = "v" + str(fetch_latest_release_version())
    if latest:
        if latest==__version__:
            up_to_date=True
        else:
            print(latest)
            print(__version__)
            up_to_date=False

        print_status("CLI Version", up_to_date, f"{__version__} (latest: {latest})")
    else:
        print_status("CLI Version", True, f"{__version__} (could not fetch latest)")


    sha = get_self_hash()
    print_status("Binary SHA256", sha is not None, sha or "")

    print("\n🧪 Diagnostic complete.\n")

def main():
    run_diagnostics()

if __name__ == "__main__":
    run_diagnostics()
