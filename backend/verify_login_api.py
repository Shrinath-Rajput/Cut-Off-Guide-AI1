import urllib.request
import urllib.error
import json

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

print("=== 1. Health Check ===")
with urllib.request.urlopen("http://127.0.0.1:8000/api/health") as r:
    print(r.status, json.loads(r.read().decode("utf-8")))

print("\n=== 2. USER Login (rajputshrinath349@gmail.com) ===")
s, body = post("http://127.0.0.1:8000/api/auth/login", {"username": "rajputshrinath349@gmail.com", "password": "Shrinath@12345"})
user = body.get("user") or {}
print(f"Status: {s}, Role: {user.get('role')}, Msg: {body.get('message')}, HasToken: {bool(body.get('token'))}")

print("\n=== 3. ADMIN Login (ankitakenjale75@gmail.com) ===")
s, body = post("http://127.0.0.1:8000/api/auth/login", {"username": "ankitakenjale75@gmail.com", "password": "Ankita@123"})
user = body.get("user") or {}
print(f"Status: {s}, Role: {user.get('role')}, Msg: {body.get('message')}, HasToken: {bool(body.get('token'))}")

print("\n=== 4. SUPER ADMIN Login (fourise@gmail.com) ===")
s, body = post("http://127.0.0.1:8000/api/auth/login", {"username": "fourise@gmail.com", "password": "123456"})
user = body.get("user") or {}
print(f"Status: {s}, Role: {user.get('role')}, Msg: {body.get('message')}, HasToken: {bool(body.get('token'))}")

print("\n=== 5. Wrong Password Rejection ===")
s, body = post("http://127.0.0.1:8000/api/auth/login", {"username": "rajputshrinath349@gmail.com", "password": "WrongPassword999"})
print(f"Status: {s}, Error detail: {body.get('detail') or body.get('message')}")
