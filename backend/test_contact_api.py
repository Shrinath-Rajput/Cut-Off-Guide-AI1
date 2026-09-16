import asyncio
import httpx
from fastapi.testclient import TestClient

def test_api():
    from app.main import app
    client = TestClient(app)
    
    payload = {
        "name": "API Test",
        "email": "test@example.com",
        "subject": "General Inquiry",
        "message": "This is a test message via API."
    }
    
    # We must trigger the lifespan context to connect to DB
    with TestClient(app) as client:
        response = client.post("/api/contact", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

if __name__ == "__main__":
    test_api()
