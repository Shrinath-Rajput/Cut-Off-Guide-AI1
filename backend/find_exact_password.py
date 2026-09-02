import asyncio
import re
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import verify_password

target_hash = "$bcrypt-sha256$v=2,t=2b,r=12$HXSIleurlXY/t.7VASrhuu$5EYXWvqQ1owQ86SyjdqMqfkzKi/O2Oe"

# Collect all potential candidate passwords from repository files
candidates = set()

# Basic candidates
base_words = [
    "Shrinath", "shrinath", "SHRINATH", "Rajput", "rajput", "RAJPUT",
    "ShrinathRajput", "Shrinath_Rajput", "shrinath_rajput", "ShrinathRajput01",
    "Shrinath@123456", "Shrinath@123", "Shrinath#123", "Shrinath#123456",
    "Shrinath$123456", "Shrinath123456", "Shrinath123", "Shrinath@1", "Shrinath@2",
    "Rajput@123456", "Rajput@123", "Rajput#123456", "Rajput#123", "Rajput123456",
    "rajputshrinath349", "rajputshrinath", "rajput349", "shrinath349",
    "9699510445", "919699510445", "7057895977", "9881342272", "8390096490",
    "Admin@123", "Admin@123456", "Ankita@123", "Fourise@123", "Fourise@123456",
    "Cutoff@123", "Cutoff@123456", "CutoffGuide@123", "CutoffGuideAI",
    "Pass@123", "Pass@123456", "Password@123", "Password@123456", "Password123",
    "123456", "12345678", "123456789", "1234567890",
    "LegacyPass@2026", "Legacy@Setup2026!", "AnyPassword123!", "FreshPass@2026",
    "Secure@TestPass123!", "Test@123", "test@123", "TestPass@123", "TestPass@2026"
]
for w in base_words:
    candidates.add(w)

# Scan workspace files for potential password strings (e.g. quotes)
root_dir = Path(__file__).resolve().parent.parent
for root, dirs, files in os.walk(root_dir):
    if ".git" in root or "node_modules" in root or ".venv" in root or "venv" in root or "mongo_data" in root:
        continue
    for f in files:
        if f.endswith((".py", ".js", ".jsx", ".json", ".env", ".md", ".txt", ".log")):
            try:
                content = Path(root, f).read_text(encoding="utf-8", errors="ignore")
                # find quoted strings between 4 and 30 chars
                matches = re.findall(r'["\']([A-Za-z0-9@#$%^&*_+=!~-]{4,30})["\']', content)
                for m in matches:
                    candidates.add(m)
            except Exception:
                pass

print(f"Total candidate passwords collected: {len(candidates)}")

found = None
count = 0
for pwd in candidates:
    count += 1
    if count % 200 == 0:
        print(f"Checked {count}/{len(candidates)}...")
    try:
        if verify_password(pwd, target_hash):
            print(f"\n=======================================================")
            print(f"MATCH FOUND! Password is: {pwd}")
            print(f"=======================================================\n")
            found = pwd
            break
    except Exception:
        pass

if not found:
    print("No match found in collected candidates.")
