import asyncio
import json
import re
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import HTTPException, status

from app.core.config import settings
from app.services.prediction_service import get_cutoff_prediction
from app.schemas.prediction import PredictionRequest, InsufficientDataResponse

HUGGINGFACE_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"


def _clean_reply(text: str) -> str:
    if not text:
        return ""
    # Remove reasoning blocks (<think>...</think>)
    cleaned = re.sub(r"<think>[\s\S]*?<\/think>", "", text)
    # Remove rambling internal monologue prefixes
    cleaned = re.sub(r"^(Okay|Alright|Let me see|So|Well),\s+(I need to|I will|let me|I should|I am trying to|I know that)[^\n]*\n*", "", cleaned, flags=re.IGNORECASE)
    # Remove repeated asterisks (e.g., ******, ****, ***)
    cleaned = re.sub(r"\*{3,}", "", cleaned)
    # Replace **word** bold stars with clean text
    cleaned = re.sub(r"\*\*([^\*]+)\*\*", r"\1", cleaned)
    # Replace * bullet with clean bullet point dot
    cleaned = re.sub(r"^\s*[\*\-]\s+", "• ", cleaned, flags=re.MULTILINE)
    # Remove any remaining stray asterisks
    cleaned = cleaned.replace("*", "")
    return cleaned.strip()


async def generate_assistant_reply(message: str, db=None, history: list = None) -> str:
    token = settings.HUGGINGFACE_API_TOKEN or ""
    prediction_info = ""
    lower_msg = message.lower()
    
    if db is not None and ("predict" in lower_msg or "expected" in lower_msg or "2027" in lower_msg):
        target_year = 2027
        match_year = re.search(r'\b(20\d{2})\b', message)
        if match_year:
            target_year = int(match_year.group(1))
            
        course = ""
        college = ""
        if "computer" in lower_msg or "cs" in lower_msg: course = "Computer"
        if "vjti" in lower_msg: college = "VJTI"
        if "coep" in lower_msg: college = "COEP"
        if "mumbai" in lower_msg: college = "Mumbai"
        
        if college or course:
            req = PredictionRequest(college=college, course=course, target_year=target_year)
            pred_resp = await get_cutoff_prediction(db, req)
            if isinstance(pred_resp, InsufficientDataResponse):
                prediction_info = f"\nSYSTEM NOTE: The prediction API reports: {pred_resp.message} (Status: {pred_resp.data_status}). Tell the user exactly this."
            else:
                prediction_info = f"\nSYSTEM NOTE: The prediction API calculated the following for {target_year}: Predicted Cutoff={pred_resp.predicted_cutoff}, Range={pred_resp.lower_bound}-{pred_resp.upper_bound}, Confidence={pred_resp.confidence}, Latest Actual Year={pred_resp.latest_actual_year}. The user is asking about {college} {course}. Use EXACTLY these prediction numbers in your response and mention the latest actual year."

    system_prompt = {
        "role": "system",
        "content": (
            "You are AI Council, a fast, direct, and concise academic admissions counselor for CutoffGuide (India). "
            "STRICT RULES:\n"
            "- Never use markdown asterisks (do NOT output '**', '***', or '******'). Output plain clean text.\n"
            "- Be concise, direct, and fact-focused. Keep answers under 100-140 words.\n"
            "- Start immediately with the direct answer. No introductory fluff.\n"
            "- Use clean bullet points (•) for cutoff trends, placements, and campus advice.\n"
            "- Provide accurate information for MHT CET, JEE Main, JoSAA, and CAP rounds."
            f"{prediction_info}"
        ),
    }

    messages = [system_prompt]

    if history and isinstance(history, list):
        for item in history[-4:]:  # keep last 4 messages for fast context
            if isinstance(item, dict) and "role" in item and "content" in item:
                role = item["role"] if item["role"] in ("user", "assistant") else "user"
                content = str(item["content"]).strip()
                if content:
                    messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message.strip()})

    payload = {
        "model": settings.HUGGINGFACE_MODEL,
        "messages": messages,
        "max_tokens": 180,
        "temperature": 0.1,
    }
    request_data = json.dumps(payload).encode("utf-8")
    request_obj = urllib_request.Request(
        HUGGINGFACE_CHAT_URL,
        data=request_data,
        headers={
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    def fetch_hf():
        if not token:
            return {
                "choices": [{
                    "message": {
                        "content": f"I am currently in offline mode because the HuggingFace API token is not configured. However, I can still help you with your prediction query!\n{prediction_info.replace('SYSTEM NOTE: ', '') if prediction_info else ''}"
                    }
                }]
            }
            
        try:
            with urllib_request.urlopen(request_obj, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            details = exc.read().decode("utf-8", "ignore")[:500]
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Hugging Face request failed: {details}") from exc
        except (urllib_error.URLError, TimeoutError) as exc:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Hugging Face request timed out") from exc
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Hugging Face returned invalid JSON") from exc

    try:
        loop = asyncio.get_event_loop()
        response_data = await loop.run_in_executor(None, fetch_hf)
        if response_data and "choices" in response_data:
            choice = response_data["choices"][0]
            message_data = choice.get("message") or {}
            reply = message_data.get("content") or message_data.get("reasoning_content") or choice.get("text")
            if reply:
                return _clean_reply(reply)
    except Exception as exc:
        print("Hugging Face API call warning:", exc)

    # Resilient fast fallback academic response
    q_lower = message.lower()
    return (
        f"Based on recent MHT-CET, JEE Main, and JoSAA admission data:\n\n"
        f"• Cutoff Dynamics: Top branches (Computer Engineering, IT, AI & Data Science) generally close between the 94th and 99.5th percentiles at tier-1 colleges, while core branches (Mechanical, Civil, Electrical) range from the 82nd to 92nd percentiles.\n"
        f"• Placement Outlook: Leading institutes record average salary packages between ₹7.5 LPA and ₹16.0 LPA, with recruiters like TCS, Infosys, Barclays, Amazon, and L&T.\n"
        f"• Recommended Action: In CAP rounds, list dream institutions in preferences 1–5, achievable colleges in 6–15, and secure backup options in subsequent slots."
    )