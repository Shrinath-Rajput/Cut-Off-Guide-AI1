import requests

url = "http://127.0.0.1:8000/api/auth/send-otp"
payload = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890"
}
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173"
}

print(f"Sending POST to {url} with headers {headers}")
response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print("Response Headers:")
for k, v in response.headers.items():
    if k.lower().startswith("access-control"):
        print(f"  {k}: {v}")

print("Response Body:")
print(response.json())

assert response.status_code == 200, "Expected status code 200"
assert response.json().get("status") == "success", "Expected status 'success'"
assert "sessionId" in response.json(), "Expected sessionId in response"

print("CORS and OTP API test passed successfully!")
