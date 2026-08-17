import asyncio
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    with TestClient(app) as client:
        print("Testing cutoff search (VJTI Mumbai match)")
        payload1 = {
            "course": "Computer Engineering",
            "category": "Open",
            "gender": "Male",
            "university": "Mumbai",
            "location": "Mumbai",
            "round": "Round 1"
        }
        response1 = client.post("/api/cutoffs/search", json=payload1)
        assert response1.status_code == 200
        data1 = response1.json()
        print("Result 1:", data1)
        assert data1["suggestion"] == "VJTI Mumbai"

        print("\nTesting cutoff search (COEP Pune match)")
        payload2 = {
            "course": "Computer",
            "category": "OBC",
            "gender": "Female",
            "location": "Pune",
            "round": "Round 2"
        }
        response2 = client.post("/api/cutoffs/search", json=payload2)
        assert response2.status_code == 200
        data2 = response2.json()
        print("Result 2:", data2)
        assert data2["suggestion"] == "COEP Pune"
        
        print("\nTesting cutoff search (No match)")
        payload3 = {
            "course": "Mechanical",
            "category": "SC/ST",
            "location": "Nagpur"
        }
        response3 = client.post("/api/cutoffs/search", json=payload3)
        assert response3.status_code == 200
        data3 = response3.json()
        print("Result 3:", data3)
        assert data3["suggestion"] == "No exact matches found. Try adjusting your filters."

        print("\nAll cutoff search tests passed!")

if __name__ == "__main__":
    run_tests()
