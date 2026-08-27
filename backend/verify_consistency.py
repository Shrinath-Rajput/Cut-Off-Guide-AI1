import asyncio
import os
import sys

# Set a dummy huggingface token for the test if not present
os.environ["HUGGINGFACE_API_TOKEN"] = "hf_dummy_token"
os.environ["HUGGINGFACE_MODEL"] = "meta-llama/Llama-3.2-3B-Instruct"

from app.core.database import connect_to_mongo, get_db, close_mongo_connection
from app.schemas.prediction import PredictionRequest
from app.services.prediction_service import get_cutoff_prediction
from app.services.assistant_service import generate_assistant_reply

# Mock the HuggingFace API call in assistant_service to avoid network errors
import app.services.assistant_service as assistant_service
import json

async def mock_fetch_hf(*args, **kwargs):
    # This will simulate the HF response after the prediction context is injected
    class DummyChoice:
        @staticmethod
        def get(key):
            if key == "message":
                # Extract the prompt that was built to see what the LLM sees
                pass
            return "This is a mock LLM response."
            
    return {"choices": [{"message": {"content": "This is a mock response from the LLM."}}]}


async def verify_consistency():
    await connect_to_mongo()
    db = get_db()
    
    print("--- 1. Testing Prediction Service ---")
    req = PredictionRequest(college="VJTI", course="Computer", target_year=2027)
    pred_res = await get_cutoff_prediction(db, req)
    print("Prediction Service Result:")
    print(pred_res.model_dump_json(indent=2))
    
    print("\n--- 2. Testing AI Assistant Service Context ---")
    # We want to see what context is actually passed to the LLM
    # Let's temporarily intercept the request payload
    original_urllib_request = assistant_service.urllib_request.urlopen
    
    captured_payload = None
    
    class MockResponse:
        def __init__(self):
            self.status = 200
        def read(self):
            return json.dumps({
                "choices": [{"message": {"content": "The predicted cutoff for VJTI Computer Science in 2027 is 100.0 (Range: 99.88 - 100.0) based on historical data up to 2025."}}]
            }).encode('utf-8')
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
            
    def mock_urlopen(req, timeout):
        nonlocal captured_payload
        captured_payload = json.loads(req.data.decode('utf-8'))
        return MockResponse()
        
    assistant_service.urllib_request.urlopen = mock_urlopen
    
    user_msg = "What is the expected cutoff for Computer Science at VJTI in 2027?"
    
    try:
        reply = await generate_assistant_reply(user_msg, db=db)
        print("\nAI Assistant Final Reply:")
        print(reply)
        
        print("\nCaptured System Prompt sent to LLM:")
        system_prompt = next(m for m in captured_payload["messages"] if m["role"] == "system")
        print(system_prompt["content"])
        
    finally:
        assistant_service.urllib_request.urlopen = original_urllib_request
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(verify_consistency())
