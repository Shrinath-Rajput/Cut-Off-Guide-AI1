import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    with TestClient(app) as client:
        print("Testing basic list (pagination default)")
        response = client.get("/api/colleges")
        assert response.status_code == 200
        data = response.json()
        print("Response structure:", list(data.keys()))
        assert "data" in data
        print("Total records:", data.get("total"))
        
        print("\nTesting pagination (page=1, limit=1)")
        response = client.get("/api/colleges?page=1&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 1
        print("Received", len(data["data"]), "record(s)")

        print("\nTesting search (search=Stanford)")
        response = client.get("/api/colleges?search=Stanford")
        assert response.status_code == 200
        data = response.json()
        print("Found", data["total"], "records matching 'Stanford'")
        for c in data["data"]:
            print(f" - {c['name']}")

        print("\nTesting state filter (states=California)")
        response = client.get("/api/colleges?states=California")
        assert response.status_code == 200
        data = response.json()
        print("Found", data["total"], "records in California")
        for c in data["data"]:
            print(f" - {c['name']}, {c['state']}")

        print("\nTesting sorting (sort=fees)")
        response = client.get("/api/colleges?sort=fees")
        assert response.status_code == 200
        data = response.json()
        fees = [c['feeValue'] for c in data["data"]]
        print("Fees ordered:", fees)
        
        print("\nAll API tests passed!")

if __name__ == "__main__":
    run_tests()
