import argparse
import importlib.util
import os
import sys

from scripts.version import __version__

BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))

def import_script(script_name):
    script_path = os.path.join(BASE_DIR, "scripts", f"{script_name}.py")
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():


    if "--diagnose-local-auth" in sys.argv:
        try:
            import LocalAuthentication
            print("✅ LocalAuthentication imported successfully!")
        except Exception as e:
            print(f"❌ LocalAuthentication import failed: {type(e).__name__}: {e}")
        return


    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["diagnose-local-auth","fingerprint", "rotate", "status", "clean", "version"])
    parser.add_argument("--version", action="version", version=f"myvault {__version__}")
    args = parser.parse_args()


    if args.command == "fingerprint":
        import_script("vault_fingerprint").main()
    elif args.command=="diagnose-local-auth":
        print("testing lacontext")
        import_script("test_lacontext")
    elif args.command == "rotate":
        import_script("vault_rotate_cert").main()
    elif args.command == "clean":
        import_script("clean").main()
    elif args.command == "status":
        import_script("status").main()
    elif args.command == "version":
        print(f"myvault CLI version {__version__}")

if __name__ == "__main__":
    main()
