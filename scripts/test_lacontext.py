try:
    import LocalAuthentication
    print("✅ LocalAuthentication module successfully imported.")
    context = LocalAuthentication.LAContext.alloc().init()
    print("LAContext object created:", context)
except Exception as e:
    print("❌ LocalAuthentication import or usage failed:", str(e))
    raise
