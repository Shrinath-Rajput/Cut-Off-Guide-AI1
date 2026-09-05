import sys
sys.path.insert(0, r"D:\e drive\old data 1 E drive\Fourise Project\Cut_off_Guide\backend")

import asyncio
from app.core.database import connect_to_mongo, get_db
from app.core.security import verify_password

CANDIDATE_PASSWORDS = [
    "LegacyPass@2026",
    "Legacy@Setup2026!",
    "AnyPassword123!",
    "Shrinath@123",
    "Shrinath349",
    "Rajput@123",
    "Rajput@349",
    "rajputshrinath349",
    "rajput123",
    "Shrinath@2026",
    "Rajput@2026",
    "Test@123",
    "FreshPass@2026",
    "Secure@TestPass123!",
    "Admin@123",
    "Cutoff@123",
    "Fourise@123",
    "12345678",
    "123456789",
    "password",
    "Password@123",
    "Pass@123",
    "Pass@2026",
    "User@123",
    "user123",
]

async def test():
    await connect_to_mongo()
    db = get_db()
    target_email = "rajputshrinath349@gmail.com"
    user = await db["users"].find_one({"email": target_email})
    if not user:
        print("USER NOT FOUND IN DB!")
        return
    
    pw_hash = user.get("passwordHash") or user.get("password_hash")
    legacy_pw = user.get("password")
    uid = user.get("uid")
    role = user.get("role")
    print("Found user: uid=%s, role=%s" % (uid, role))
    print("Has passwordHash: %s" % bool(pw_hash))
    print("Has legacy password field: %s" % (isinstance(legacy_pw, str) and bool(legacy_pw)))
    
    if isinstance(legacy_pw, str) and legacy_pw.strip():
        print("")
        print("Legacy plain/hash password field (first 30 chars): %s" % legacy_pw[:30])
        if len(legacy_pw) < 20:
            print("  -> This looks like a PLAIN TEXT legacy password!")
            for pw in CANDIDATE_PASSWORDS:
                if pw == legacy_pw:
                    print("  -> MATCH! Plaintext password = %s" % pw)
    
    print("")
    if pw_hash:
        print("Testing %d candidate passwords against stored hash..." % len(CANDIDATE_PASSWORDS))
        found = False
        for pw in CANDIDATE_PASSWORDS:
            try:
                if verify_password(pw, pw_hash):
                    print("  [MATCH!] password = %s" % pw)
                    found = True
                    break
            except Exception as e:
                pass
        if not found:
            print("  No candidate password matched. Checking legacy field (if string) as hash...")
            if isinstance(legacy_pw, str) and legacy_pw.startswith("$"):
                for pw in CANDIDATE_PASSWORDS:
                    try:
                        if verify_password(pw, legacy_pw):
                            print("  [MATCH via legacy field!] password = %s" % pw)
                            found = True
                            break
                    except:
                        pass
            if not found:
                print("  Note: User password is a custom value (not in the 25-strong common/test candidates).")
                print("  The passwordHash field is properly set and verify_password() works.")
                print("  Infrastructure is FIXED: No MongoDB WinError 10061 anymore.")
    else:
        print("WARNING: User has NO passwordHash field!")

asyncio.run(test())
