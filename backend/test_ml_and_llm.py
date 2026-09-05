"""
Verification script for ML Percentile Predictor and LLM College Predictor.
"""

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    with TestClient(app) as client:
        print("\n--- 1. Testing ML Percentile Predictor for MHT-CET ---")
        # 150 marks out of 200
        res = client.post("/api/cutoffs/predict-percentile", json={"exam": "MHT-CET", "marks": 150.0})
        print("Status:", res.status_code)
        data = res.json()
        print("Response:", data)
        assert res.status_code == 200
        assert data["exam"] == "MHT-CET"
        assert data["max_marks"] == 200
        assert 98.0 <= data["predicted_percentile"] <= 99.5
        assert "State Merit Rank" in data["estimated_rank"]

        print("\n--- 2. Testing ML Boundary Validation (Marks > 200 for MHT-CET) ---")
        res_err = client.post("/api/cutoffs/predict-percentile", json={"exam": "MHT-CET", "marks": 250.0})
        print("Status (Expected 422):", res_err.status_code)
        print("Error detail:", res_err.json())
        assert res_err.status_code == 422
        assert "exceed" in res_err.json()["detail"].lower()

        print("\n--- 3. Testing ML Percentile Predictor for JEE Main ---")
        # 180 marks out of 300
        res_jee = client.post("/api/cutoffs/predict-percentile", json={"exam": "JEE Main", "marks": 180.0})
        print("Status:", res_jee.status_code)
        data_jee = res_jee.json()
        print("Response:", data_jee)
        assert res_jee.status_code == 200
        assert data_jee["max_marks"] == 300
        assert 97.5 <= data_jee["predicted_percentile"] <= 99.2
        assert "All India Rank" in data_jee["estimated_rank"]

        print("\n--- 4. Testing ML Percentile Predictor for JEE Advanced ---")
        # 180 marks out of 360
        res_adv = client.post("/api/cutoffs/predict-percentile", json={"exam": "JEE Advanced", "marks": 180.0})
        print("Status:", res_adv.status_code)
        data_adv = res_adv.json()
        print("Response:", data_adv)
        assert res_adv.status_code == 200
        assert data_adv["max_marks"] == 360
        assert 96.5 <= data_adv["predicted_percentile"] <= 99.0

        print("\n--- 5. Testing LLM College Predictor ---")
        payload = {
            "exam": "MHT-CET",
            "marks": 150.0,
            "percentile": 98.95,
            "category": "OBC",
            "location": "Pune",
            "round": "Round 1",
            "preferred_courses": [
                "Computer Engineering (CSE)",
                "Information Technology (IT)",
                "Artificial Intelligence & Machine Learning",
            ]
        }
        res_llm = client.post("/api/cutoffs/predict-colleges-llm", json=payload)
        print("Status:", res_llm.status_code)
        data_llm = res_llm.json()
        print("Summary:", data_llm["summary"])
        print(f"Total Colleges returned: {len(data_llm['colleges'])}")
        for col in data_llm["colleges"][:4]:
            print(f"  [{col['chance_tier']}] {col['college_name']} - {col['branch']} (Cutoff: {col['cutoff_percentile']}%, Chance: {col['chance_percentage']}%)")
            print(f"     Reason: {col['ai_reasoning'][:90]}...")

        assert res_llm.status_code == 200
        assert len(data_llm["colleges"]) >= 15
        assert data_llm["summary"]["candidate_percentile"] == 98.95
        assert any(c["chance_tier"] == "Safe" for c in data_llm["colleges"])

        print("\n--- 6. Testing ML Low-Percentile Advisory (< 30%ile) ---")
        res_low_ml = client.post("/api/cutoffs/predict-percentile", json={"exam": "MHT-CET", "marks": 15.0})
        assert res_low_ml.status_code == 200
        data_low_ml = res_low_ml.json()
        print(f"Status: {res_low_ml.status_code}")
        print(f"Predicted Percentile: {data_low_ml['predicted_percentile']}")
        print(f"Advisory Message: {data_low_ml['advisory_message']}")
        assert data_low_ml["predicted_percentile"] < 30.0
        assert data_low_ml["advisory_message"] is not None
        assert "private college" in data_low_ml["advisory_message"].lower()

        print("\n--- 7. Testing LLM Low-Percentile College Advisory & Recommendations ---")
        payload_low = {
            "exam": "MHT-CET",
            "percentile": 22.5,
            "category": "Open",
            "location": "Pune",
            "round": "Round 1",
            "preferred_courses": ["Computer Engineering (CSE)"],
        }
        res_low_llm = client.post("/api/cutoffs/predict-colleges-llm", json=payload_low)
        assert res_low_llm.status_code == 200
        data_low_llm = res_low_llm.json()
        print(f"Status: {res_low_llm.status_code}")
        print(f"Summary: {data_low_llm['summary']}")
        print(f"Colleges count: {len(data_low_llm['colleges'])}")
        assert data_low_llm["summary"]["is_low_percentile"] is True
        assert data_low_llm["summary"]["advisory_message"] is not None
        assert "private" in data_low_llm["summary"]["advisory_message"].lower()
        assert len(data_low_llm["colleges"]) >= 15
        print(f"First college: {data_low_llm['colleges'][0]['college_name']}")
        print(f"First reasoning: {data_low_llm['colleges'][0]['ai_reasoning']}")

        print("\n--- 8. Testing Minimum 15 Colleges Across Diverse Percentiles & Specialized Branches ---")
        test_branches = [
            (85.0, "Robotics & Automation"),
            (70.0, "Cyber Security"),
            (50.0, "Mechatronics"),
            (35.0, "Aerospace Engineering"),
        ]
        for test_pct, test_branch in test_branches:
            p_test = {
                "exam": "MHT-CET",
                "percentile": test_pct,
                "category": "Open",
                "location": "All Maharashtra",
                "round": "Round 1",
                "preferred_courses": [test_branch],
            }
            res_t = client.post("/api/cutoffs/predict-colleges-llm", json=p_test)
            assert res_t.status_code == 200
            d_t = res_t.json()
            cols_count = len(d_t["colleges"])
            print(f"  Tested {test_pct}%ile for '{test_branch}' -> {cols_count} colleges returned (>= 15)")
            assert cols_count >= 15

        print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_tests()
