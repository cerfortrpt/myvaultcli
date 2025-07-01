# Touch ID and Cert Auth for Vault:
- This is done with a custom cli that pulls+rotate certs from vault, stores in a mac user’s local keychain, and uses the cert to login with a user’s touch id.

## macOS Keychain:
- The keychain is encrypted at rest using macOS system services
- The encryption key is derived from your login password, secured by the Secure Enclave (on newer Macs)
- Only accessible by your login password / fingerprint

## Security Posture:
- A client certificate is securely stored in the macOS Keychain.
- Access to the certificate is protected by Touch ID.
- Authentication with Vault is done without passwords or tokens.
- The cert is transmitted over mutual TLS to prove identity.
- The Vault server can map cert identity to a role/policy.
- Wrapped cli is compiled and (will eventually be) signed

### Biggest problems: 
- Local hardware enforcement limits scalability
- User error with storing certs securely
- Heavily macos dependent
- Not all macs have the same functionality with keychain
- At this moment, the binary is not signed

### Biggest strengths:
- Strong local security
- - Private keys and Vault tokens are never stored in plaintext on disk.
- - 2FA solution (mac keychain and fingerprint)
- Convenient/Light
- - Simply use touch id and you are logged in
- - Only Vault CLI and binary need to be installed
- - Using Vault as a CA makes rotation and role mapping easy
- Minimal Attack Surface
- - Vault auth over Mutual TLS
- -Tight identity binding to device + user
- -Auth wrapper (will be) signed as a binary, minimizing tampering risk
->Control over the entire trust chain

## Next steps: 
1. 🔒 Sign and Notarize the Binary
While this doesn’t “hide” the binary, it ensures tamper detection. macOS will warn or block execution if the binary has been modified.
Benefits:
Prevents modification without re-signing
Adds visible security to users (valid Developer ID)
Enables Gatekeeper and TCC trust
OR Make this a vault plugin and register as an auth method. Problem is it wouldn’t serve much benefit to make a plugin because it will be just as secure as the above.

2. Add in windows support (windows hello)


To install:
```
brew tap cerfortrpt/tools
brew install myvault
```

## Supports the below commands:
```
myvault -h
myvault fingerprint
myvault rotate
```
Fingerprint: Uses the stored cert in your keychain to log into vault
Rotate: Stores/rotates a cert from vault into your keychain
