import sys
import json

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import requests

BASE = "http://localhost:5000"

def test_health():
    print("=== Testing backend health ===")
    try:
        r = requests.get("%s/api/health" % BASE, timeout=5)
        print("Status: %d" % r.status_code)
        print("Body: %s" % json.dumps(r.json(), indent=2))
        return r.status_code == 200
    except Exception as e:
        print("ERROR: %s: %s" % (type(e).__name__, e))
        return False

def test_login(username, password, label=""):
    print("")
    print("=== Testing login: %s ===" % label)
    print("Username: %s" % username)
    try:
        r = requests.post(
            "%s/api/auth/login" % BASE,
            json={"username": username, "password": password},
            timeout=15,
            headers={"Content-Type": "application/json"},
        )
        print("Status: %d" % r.status_code)
        try:
            body = r.json()
            print("Response JSON:")
            print(json.dumps(body, indent=2))
        except:
            print("Response raw text:")
            print(r.text[:2000])
    except Exception as e:
        import traceback
        print("REQUEST ERROR: %s: %s" % (type(e).__name__, e))
        traceback.print_exc()

def test_admin_login(email, password, label=""):
    print("")
    print("=== Testing ADMIN login: %s ===" % label)
    print("Email: %s" % email)
    try:
        r = requests.post(
            "%s/api/admin/login" % BASE,
            json={"email": email, "password": password},
            timeout=15,
            headers={"Content-Type": "application/json"},
        )
        print("Status: %d" % r.status_code)
        try:
            body = r.json()
            print("Response JSON:")
            print(json.dumps(body, indent=2))
        except:
            print("Response raw text:")
            print(r.text[:2000])
    except Exception as e:
        import traceback
        print("REQUEST ERROR: %s: %s" % (type(e).__name__, e))
        traceback.print_exc()

if __name__ == "__main__":
    alive = test_health()
    if not alive:
        print("")
        print("Backend not running on 5000, need to start")
        sys.exit(1)
    
    test_admin_login("ankitakenjale75@gmail.com", "Ankita@123", "Admin configured")
    test_login("fourise@gmail.com", "123456", "Super Admin via USER endpoint")
    test_login("rajputshrinath349@gmail.com", "test123", "Normal USER (password unknown, try common)")
    test_login("sarthakpatil12@gmail.com", "test123", "Normal USER 2 (password unknown)")
    test_login("rajputshrinath349@gmail.com", "wrong_password", "Normal USER wrong password")
