import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import verify_password, pwd_context

hash_val = "$bcrypt-sha256$v=2,t=2b,r=12$HXSIleurlXY/t.7VASrhuu$5EYXWvqQ1owQ86SyjdqMqfkzKi/O2Oe"

words = [
    "Shrinath@123456", "Shrinath@123", "shrinath@123456", "shrinath@123",
    "Shrinath123456", "Shrinath123", "shrinath123456", "shrinath123",
    "Shrinath@2026", "Shrinath@2025", "Shrinath@2024", "Shrinath@2023",
    "Rajput@123456", "Rajput@123", "rajput@123456", "rajput@123",
    "Rajput123456", "Rajput123", "rajput123456", "rajput123",
    "Rajput@2026", "Rajput@2025", "Rajput@2024", "Rajput@2023",
    "ShrinathRajput@123", "ShrinathRajput123", "Shrinath_Rajput",
    "Shrinath_Rajput01", "rajputshrinath349", "rajputshrinath",
    "9699510445", "919699510445",
    "123456", "12345678", "123456789", "1234567890",
    "Password@123", "password@123", "Password123", "password123",
    "Pass@123", "pass@123", "Pass@123456", "pass@123456",
    "Admin@123", "admin@123", "Admin@123456", "admin@123456",
    "LegacyPass@2026", "Legacy@Setup2026!", "AnyPassword123!", "FreshPass@2026",
    "Secure@TestPass123!", "Test@123", "test@123", "TestPass@123", "testpass@123",
    "Cutoff@123", "Fourise@123", "Student@123", "student@123", "Student@123456"
]

print(f"Testing {len(words)} passwords against bcrypt-sha256 hash...")
for w in words:
    try:
        if verify_password(w, hash_val):
            print(f"FOUND MATCH! Password is: '{w}'")
            break
    except Exception as e:
        print(f"Error for {w}: {e}")
else:
    print("No match in list.")
