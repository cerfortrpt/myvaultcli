import argparse
import importlib.util
import os
import sys

BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(__file__)

def import_script(script_name):
    script_path = os.path.join(BASE_DIR, "scripts", f"{script_name}.py")
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["fingerprint", "rotate"])
    args = parser.parse_args()

    if args.command == "fingerprint":
        import_script("vault_fingerprint").main()
    elif args.command == "rotate":
        import_script("vault_rotate_cert").main()

if __name__ == "__main__":
    main()
