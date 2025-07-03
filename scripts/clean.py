import keyring
from keyring.errors import PasswordDeleteError

def remove_cert():
    cert_pem = keyring.get_password("vault_cert_auth", "cert")
    if not cert_pem:
        print("Nothing found to delete.")
        return
    else:
        print("Removing cert...")
        try:
            keyring.delete_password("vault_cert_auth", "cert")
            keyring.delete_password("vault_cert_auth", "key")
        except:

        # Re-check to confirm deletion
            cert_pem = keyring.get_password("vault_cert_auth", "cert")
            
            if not cert_pem or PasswordDeleteError==-25244:
                print("🧹 Removed cert and key from Keychain.")
        else:
            print("Failed to delete. Does myvault lack permissions to delete the cert in Keychain?")


def main():
    remove_cert()


if __name__ == "__main__":
    main()
