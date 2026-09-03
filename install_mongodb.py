#!/usr/bin/env python3
import os
import subprocess
import urllib.request
import sys

MONGODB_URL = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.3.7-signed.msi"
TEMP_DIR = os.path.expandvars(r"%TEMP%")
INSTALLER_PATH = os.path.join(TEMP_DIR, "mongodb-installer.msi")

print("📥 Downloading MongoDB Community Server 8.3.7...")
try:
    urllib.request.urlretrieve(MONGODB_URL, INSTALLER_PATH)
    print(f"✅ Downloaded to {INSTALLER_PATH}")
except Exception as e:
    print(f"❌ Download failed: {e}")
    sys.exit(1)

print("\n📦 Installing MongoDB...")
try:
    # Run the MSI installer with all local features
    result = subprocess.run(
        ["msiexec", "/i", INSTALLER_PATH, "/quiet", "/qn", "ADDLOCAL=all"],
        check=False
    )
    if result.returncode == 0:
        print("✅ MongoDB installed successfully!")
    else:
        print(f"⚠️  Installer returned code {result.returncode}")
except Exception as e:
    print(f"❌ Installation failed: {e}")
    sys.exit(1)

print("\n⏳ Waiting for MongoDB service to start...")
import time
time.sleep(5)

print("\n✅ Setup complete! MongoDB should now be running on localhost:27017")
print("\nTo verify, run:")
print("  mongosh 'mongodb://localhost:27017'")
