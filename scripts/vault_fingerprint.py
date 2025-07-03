import keyring
import threading
import subprocess
import os
import traceback
import tempfile
import sys
import LocalAuthentication
import objc

# Constants
LAPolicyDeviceOwnerAuthenticationWithBiometrics = 1
VAULT_ADDR = os.environ.get("VAULT_ADDR")

def exit_with_error(message, code=1):
    print(f"❌ ERROR: {message}", file=sys.stderr)
    sys.exit(code)

def authenticate_with_fingerprint():
    context = LocalAuthentication.LAContext.alloc().init()
    ok, _ = context.canEvaluatePolicy_error_(LAPolicyDeviceOwnerAuthenticationWithBiometrics, None)

    if not ok:
        exit_with_error("Touch ID is not available on this device.")

    print("🔐 Touch ID authentication required...")

    done = threading.Event()
    result = {"success": False}

    def callback(success, error):
        result["success"] = success
        done.set()

    context.evaluatePolicy_localizedReason_reply_(
        LAPolicyDeviceOwnerAuthenticationWithBiometrics,
        "Authenticate to unlock Vault token",
        callback
    )

    done.wait()

    if result["success"]:
        print("✅ Fingerprint accepted.")
    else:
        exit_with_error("Fingerprint authentication failed.")

def get_vault_token_from_keychain():
    print("🔎 Retrieving cert + key from macOS Keychain...")
    try:
        cert = keyring.get_password("vault_cert_auth", "cert")
        key = keyring.get_password("vault_cert_auth", "key")
    except Exception as e:
        exit_with_error(f"Failed to retrieve credentials from Keychain: {e}")

    if not cert or not key:
        exit_with_error("Missing certificate or key in Keychain.")

    return cert, key

def vault_token_login(cert, key):
    if not VAULT_ADDR:
        exit_with_error("VAULT_ADDR environment variable is not set.")

    env = os.environ.copy()
    env["VAULT_ADDR"] = VAULT_ADDR

    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as cert_file:
            cert_file.write(cert)
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(delete=False, mode='w') as key_file:
            key_file.write(key)
            key_path = key_file.name

        print("🔑 Logging in to Vault using certificate...")

        login_result = subprocess.run([
            "vault", "login", "-method=cert",
            f"-client-cert={cert_path}",
            f"-client-key={key_path}"
        ], env=env, capture_output=True, text=True)

        if login_result.returncode != 0:
            exit_with_error(f"Vault login failed: {login_result.stderr.strip()}")

        token_result = subprocess.run(["vault", "token", "lookup"], env=env, capture_output=True, text=True)
        if token_result.returncode != 0:
            exit_with_error(f"Vault token lookup failed: {token_result.stderr.strip()}")

        print("✅ Vault token login successful.")

    except FileNotFoundError:
        exit_with_error("Vault CLI not found. Ensure it's installed and in your PATH.")
    except Exception as e:
        exit_with_error(f"Unexpected error during Vault login: {e}")

def main():
    try:
        authenticate_with_fingerprint()
        cert, key = get_vault_token_from_keychain()
        vault_token_login(cert, key)
    except Exception as e:
        print("Unhandled error:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
