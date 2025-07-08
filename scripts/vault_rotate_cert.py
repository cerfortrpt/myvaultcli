import subprocess
import json
import keyring
import os
import sys

# Configuration
CN = "fingerprint-client"
TTL = "72h"
ROLE = "fingerprint-client"
CERT_FILE = "user.crt"
KEY_FILE = "user.key"
CA_FILE = "vault-ca.crt"
ALIAS_NAME = "Vault Fingerprint Cert"
VAULT_CA_PATH = f"pki/issue/{ROLE}"
CERT_AUTH_PATH = f"auth/cert/certs/{ROLE}"

def exit_with_error(message, code=1):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)

def main():
    print("Requesting a new certificate from Vault...")

    try:
        result = subprocess.run(
            ["vault", "write", "-format=json", VAULT_CA_PATH,
             f"common_name={CN}", f"ttl={TTL}"],
            capture_output=True, check=True, text=True
        )
        issued_data = json.loads(result.stdout)
    except FileNotFoundError:
        exit_with_error("Vault CLI not found. Please install it and check your PATH.")
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Vault certificate request failed: {e.stderr.strip()}")
    except json.JSONDecodeError:
        exit_with_error("Invalid JSON received from Vault.")
    except Exception as e:
        exit_with_error(f"Unexpected error requesting cert: {e}")

    cert = issued_data["data"]["certificate"]
    key = issued_data["data"]["private_key"]
    ca = issued_data["data"]["issuing_ca"]

    try:
        with open(CERT_FILE, "w") as f:
            f.write(cert)
        with open(KEY_FILE, "w") as f:
            f.write(key)
        with open(CA_FILE, "w") as f:
            f.write(ca)
    except Exception as e:
        exit_with_error(f"Failed to write certificate files: {e}")

    print("Registering certificate in Vault's cert auth backend...")

    try:
        subprocess.run([
            "vault", "write", CERT_AUTH_PATH,
            f"display_name={CN}",
            "policies=user",
            f"certificate=@{CERT_FILE}"
        ], check=True)
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Failed to register cert with Vault: {e.stderr.strip()}")

    print("Storing certificate in macOS Keychain...")

    try:
        keyring.set_password("vault_cert_auth", "cert", cert)
        keyring.set_password("vault_cert_auth", "key", key)
    except Exception as e:
        exit_with_error(f"Failed to store credentials in Keychain: {e}")
    


    subprocess.run([
            "rm", "vault-ca.crt"
        ], check=True)
    
    subprocess.run([
            "rm", "user.crt"
        ], check=True)
    
    subprocess.run([
            "rm", "user.key"
        ], check=True)
    print("Certificate successfully stored and registered.")

if __name__ == "__main__":
    main()
