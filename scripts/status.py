import keyring
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone

def load_cert():
    cert_pem = keyring.get_password("vault_cert_auth", "cert")
    if not cert_pem:
        print("❌ No certificate found in Keychain.")
        return

    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    subject_cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    issuer_cn = cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    not_after = cert.not_valid_after_utc
    now = datetime.now(timezone.utc)

    print("✅ Certificate found")
    print(f"  Subject: CN={subject_cn}")
    print(f"  Issuer: CN={issuer_cn}")
    print(f"  Expires: {not_after.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    if not_after < now:
        print(f"  ⚠️ Certificate expired on {not_after.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        days_left = (not_after - now).days
        print(f"  Valid for: {days_left} days")

def main():
    load_cert()

if __name__ == "__main__":
    main()
