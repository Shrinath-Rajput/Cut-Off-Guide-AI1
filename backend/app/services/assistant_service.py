import json
import re
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import HTTPException, status

from app.core.config import settings

HUGGINGFACE_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"


def _clean_reply(text: str) -> str:
    if not text:
        return ""
    # Remove reasoning blocks (<think>...</think>)
    cleaned = re.sub(r"<think>[\s\S]*?<\/think>", "", text)
    # Remove rambling internal monologue prefixes
    cleaned = re.sub(r"^(Okay|Alright|Let me see|So|Well),\s+(I need to|I will|let me|I should|I am trying to|I know that)[^\n]*\n*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def generate_assistant_reply(message: str, history: list = None) -> str:
    if not settings.HUGGINGFACE_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hugging Face API token is not configured",
        )

    system_prompt = {
        "role": "system",
        "content": (
            "You are AI Council, a direct, concise, and accurate academic admissions counselor for CutoffGuide (India). "
            "STRICT GUIDELINES:\n"
            "- Be concise, direct, and fact-focused. Keep answers under 120-180 words.\n"
            "- Do NOT include internal thoughts, rambling reflections, or phrases like 'Okay, let me think'. Start directly with the answer.\n"
            "- For college comparisons or cutoffs, provide 3 to 4 clear bullet points covering: Cutoff Trend, Placements, Location/Campus, and Final Recommendation.\n"
            "- Always be helpful, objective, and accurate regarding MHT CET, JEE Main, JoSAA, CSAB, and CAP rounds."
        ),
    }

    messages = [system_prompt]

    if history and isinstance(history, list):
        for item in history[-6:]:  # keep last 6 messages for context
            if isinstance(item, dict) and "role" in item and "content" in item:
                role = item["role"] if item["role"] in ("user", "assistant") else "user"
                content = str(item["content"]).strip()
                if content:
                    messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message.strip()})

    payload = {
        "model": settings.HUGGINGFACE_MODEL,
        "messages": messages,
        "max_tokens": 350,
        "temperature": 0.2,
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

    try:
        with urllib_request.urlopen(request_obj, timeout=60) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        details = exc.read().decode("utf-8", "ignore")[:500]
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Hugging Face request failed: {details}") from exc
    except (urllib_error.URLError, TimeoutError) as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Hugging Face request timed out") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Hugging Face returned invalid JSON") from exc

    try:
        choice = response_data["choices"][0]
        message_data = choice.get("message") or {}
        reply = message_data.get("content") or message_data.get("reasoning_content") or choice.get("text")
        if not reply:
            raise KeyError("empty model response")
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Hugging Face returned an unexpected response") from exc

    return _clean_reply(reply)