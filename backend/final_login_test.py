import sys
import json
import requests

BASE = "http://localhost:5000"
USER_EMAIL = "rajputshrinath349@gmail.com"
USER_PASSWORD = "Shrinath@12345"
WRONG_PASSWORD = "WrongPass@999"
ADMIN_EMAIL = "ankitakenjale75@gmail.com"
ADMIN_PASSWORD = "Ankita@123"
SUPER_ADMIN_EMAIL = "fourise@gmail.com"
SUPER_ADMIN_PASSWORD = "123456"

def test_health():
    print("=== A. MongoDB & Backend Health ===")
    r = requests.get("%s/api/health" % BASE, timeout=5)
    body = r.json()
    ok = r.status_code == 200 and body.get("status") == "ok" and body.get("database") == "ok"
    print("Health: %s  body=%s" % ("PASS" if ok else "FAIL", json.dumps(body)))
    return ok

def test_normal_user_correct_password():
    print("")
    print("=== D. Existing USER correct password (should SUCCEED -> requiresOtp=True) ===")
    r = requests.post(
        "%s/api/auth/login" % BASE,
        json={"username": USER_EMAIL, "password": USER_PASSWORD},
        timeout=15,
        headers={"Content-Type": "application/json"},
    )
    print("Status: %d" % r.status_code)
    try:
        body = r.json()
        print("Response: %s" % json.dumps(body, indent=2)[:1200])
    except:
        print("Raw text: %s" % r.text[:500])
    ok = r.status_code == 200
    if ok:
        try:
            body = r.json()
            ok = (body.get("status") in ("success", "pending_otp")) and body.get("requiresOtp") is True and bool(body.get("uid")) and bool(body.get("user"))
        except:
            ok = False
    print("Result: %s" % ("PASS - Login succeeded, requiresOtp flow ready" if ok else "FAIL"))
    print("  - No MongoDB WinError? %s" % ("YES" if "10061" not in r.text and "WinError" not in r.text else "NO - ERROR PRESENT!"))
    print("  - No raw mongo error string in message field? %s" % ("YES" if "localhost:27017" not in r.text else "NO!"))
    return ok

def test_normal_user_wrong_password():
    print("")
    print("=== E. Existing USER WRONG password (negative test -> should FAIL with 401 Invalid) ===")
    r = requests.post(
        "%s/api/auth/login" % BASE,
        json={"username": USER_EMAIL, "password": WRONG_PASSWORD},
        timeout=15,
        headers={"Content-Type": "application/json"},
    )
    print("Status: %d" % r.status_code)
    try:
        body = r.json()
        print("Response: %s" % json.dumps(body, indent=2))
    except:
        print("Raw text: %s" % r.text[:500])
    ok = r.status_code == 401
    if ok:
        try:
            detail = r.json().get("detail", "")
            ok = isinstance(detail, str) and ("Invalid" in detail or "password" in detail.lower())
        except:
            ok = False
    print("Result: %s" % ("PASS - Wrong password correctly rejected with Invalid credentials 401" if ok else "FAIL"))
    print("  - No MongoDB WinError? %s" % ("YES" if "10061" not in r.text and "WinError" not in r.text else "NO - ERROR PRESENT!"))
    return ok

def test_admin_login():
    print("")
    print("=== F. Regression: Admin login ===")
    r = requests.post(
        "%s/api/admin/login" % BASE,
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
        headers={"Content-Type": "application/json"},
    )
    print("Status: %d" % r.status_code)
    try:
        body = r.json()
        print("Response status: %s, has token: %s, role: %s" % (
            body.get("status"), bool(body.get("token")), body.get("user", {}).get("role")
        ))
    except:
        print("Raw: %s" % r.text[:300])
    ok = r.status_code == 200
    try:
        body = r.json()
        ok = ok and body.get("status") == "success" and bool(body.get("token")) and body.get("user", {}).get("role") == "ADMIN"
    except:
        ok = False
    print("Result: %s" % ("PASS - Admin login OK, token received, role=ADMIN" if ok else "FAIL"))
    print("  - No MongoDB WinError? %s" % ("YES" if "10061" not in r.text and "WinError" not in r.text else "NO!"))
    return ok

def test_super_admin_login():
    print("")
    print("=== G. Regression: Super Admin login via /api/auth/login ===")
    r = requests.post(
        "%s/api/auth/login" % BASE,
        json={"username": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
        timeout=15,
        headers={"Content-Type": "application/json"},
    )
    print("Status: %d" % r.status_code)
    try:
        body = r.json()
        print("Response status: %s, has token: %s, role: %s" % (
            body.get("status"), bool(body.get("token")), body.get("user", {}).get("role")
        ))
    except:
        print("Raw: %s" % r.text[:300])
    ok = r.status_code == 200
    try:
        body = r.json()
        ok = ok and body.get("status") == "success" and bool(body.get("token")) and body.get("user", {}).get("role") == "SUPER_ADMIN"
    except:
        ok = False
    print("Result: %s" % ("PASS - Super Admin login OK, token received, role=SUPER_ADMIN" if ok else "FAIL"))
    print("  - No MongoDB WinError? %s" % ("YES" if "10061" not in r.text and "WinError" not in r.text else "NO!"))
    return ok

if __name__ == "__main__":
    print("=" * 80)
    print("FINAL VERIFICATION TEST SUITE - NORMAL USER LOGIN FIX")
    print("=" * 80)
    results = {}
    results["A_health"] = test_health()
    results["D_user_correct"] = test_normal_user_correct_password()
    results["E_user_wrong"] = test_normal_user_wrong_password()
    results["F_admin"] = test_admin_login()
    results["G_super_admin"] = test_super_admin_login()
    print("")
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    for k, v in results.items():
        print("  %s: %s" % (k, "PASS" if v else "FAIL"))
    all_ok = all(results.values())
    print("")
    print("OVERALL: %s" % ("ALL TESTS PASSED" if all_ok else "SOME TESTS FAILED"))
    sys.exit(0 if all_ok else 1)
