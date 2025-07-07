import keyring
from keyring.errors import PasswordDeleteError

def remove_cert():
    cert_pem = keyring.get_password("vault_cert_auth", "cert")
    if not cert_pem:
        print("Nothing found to delete.")
        return
    else:
        print("Removing cert...")
        keyring.delete_password("vault_cert_auth", "cert")
        keyring.delete_password("vault_cert_auth", "key")



def main():
    remove_cert()


if __name__ == "__main__":
    main()
