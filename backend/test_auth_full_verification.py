import asyncio
import sys
import json
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

BASE = "http://127.0.0.1:5000"

def run_tests():
    print("=" * 80)
    print("FULL AUTHENTICATION VERIFICATION SUITE")
    print("=" * 80)

    # 1. Health check
    print("\n1. Testing Backend & MongoDB Health...")
    r = requests.get(f"{BASE}/api/health", timeout=5)
    assert r.status_code == 200, f"Health failed: {r.status_code}"
    health_data = r.json()
    print(f"   [OK] Health check: {health_data}")

    # 2. Existing Normal User Login - Correct Credentials
    print("\n2. Testing Existing User Login (rajputshrinath349@gmail.com / Shrinath@12345)...")
    r = requests.post(
        f"{BASE}/api/auth/login",
        json={"username": "rajputshrinath349@gmail.com", "password": "Shrinath@12345"},
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {r.status_code}")
    assert r.status_code == 200, f"User login failed with status {r.status_code}: {r.text}"
    user_data = r.json()
    assert user_data.get("status") == "success", f"Expected status success, got {user_data}"
    assert bool(user_data.get("token")), "Expected JWT token in login response"
    assert user_data.get("user", {}).get("email") == "rajputshrinath349@gmail.com"
    assert user_data.get("user", {}).get("role") == "USER"
    user_token = user_data["token"]
    print(f"   [OK] User login successful! Token received: {user_token[:20]}... Role: {user_data['user']['role']}")

    # 3. Existing Normal User Login - Negative Test: Wrong Password
    print("\n3. Testing Negative Case: Wrong Password...")
    r = requests.post(
        f"{BASE}/api/auth/login",
        json={"username": "rajputshrinath349@gmail.com", "password": "WrongPassword@999"},
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {r.status_code}")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print(f"   [OK] Wrong password correctly rejected with 401: {r.json().get('detail')}")

    # 4. Negative Test: Non-existing User
    print("\n4. Testing Negative Case: Non-existing User...")
    r = requests.post(
        f"{BASE}/api/auth/login",
        json={"username": "nonexistent_user_999@gmail.com", "password": "SomePassword@123"},
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {r.status_code}")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print(f"   [OK] Non-existing email correctly rejected with 401: {r.json().get('detail')}")

    # 5. User /me verification with token
    print("\n5. Testing /api/auth/me with User Token...")
    r = requests.get(
        f"{BASE}/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
        timeout=10
    )
    print(f"   Status: {r.status_code}")
    assert r.status_code == 200, f"/me failed: {r.status_code}"
    me_data = r.json()
    assert me_data.get("status") == "success"
    assert me_data.get("user", {}).get("email") == "rajputshrinath349@gmail.com"
    print(f"   [OK] /api/auth/me verified user: {me_data['user']['name']} ({me_data['user']['email']})")

    # 6. Regression Test: Admin Login
    print("\n6. Testing Admin Login (ankitakenjale75@gmail.com / Ankita@123)...")
    r = requests.post(
        f"{BASE}/api/admin/login",
        json={"email": "ankitakenjale75@gmail.com", "password": "Ankita@123"},
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {r.status_code}")
    assert r.status_code == 200, f"Admin login failed: {r.status_code}"
    admin_data = r.json()
    assert admin_data.get("status") == "success"
    assert bool(admin_data.get("token"))
    assert admin_data.get("user", {}).get("role") == "ADMIN"
    print(f"   [OK] Admin login intact! Role: {admin_data['user']['role']}")

    # 7. Regression Test: Super Admin Login
    print("\n7. Testing Super Admin Login (fourise@gmail.com / 123456)...")
    r = requests.post(
        f"{BASE}/api/auth/login",
        json={"username": "fourise@gmail.com", "password": "123456"},
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    print(f"   Status: {r.status_code}")
    assert r.status_code == 200, f"Super Admin login failed: {r.status_code}"
    super_admin_data = r.json()
    assert super_admin_data.get("status") == "success"
    assert bool(super_admin_data.get("token"))
    assert super_admin_data.get("user", {}).get("role") == "SUPER_ADMIN"
    print(f"   [OK] Super Admin login intact! Role: {super_admin_data['user']['role']}")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
