import asyncio
import json
import logging
import re
from urllib import error as urllib_error
from urllib import request as urllib_request
from typing import List, Optional

from app.core.config import settings
from app.services.prediction_service import get_cutoff_prediction
from app.schemas.prediction import PredictionRequest, InsufficientDataResponse

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
HUGGINGFACE_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"


def _clean_reply(text: str) -> str:
    if not text:
        return ""
    # Remove reasoning blocks (<think>...</think>)
    cleaned = re.sub(r"<think>[\s\S]*?<\/think>", "", text)
    # Remove rambling internal monologue prefixes
    cleaned = re.sub(
        r"^(Okay|Alright|Let me see|So|Well),\s+(I need to|I will|let me|I should|I am trying to|I know that)[^\n]*\n*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    # Remove repeated asterisks (e.g., ******, ****, ***)
    cleaned = re.sub(r"\*{3,}", "", cleaned)
    # Replace **word** bold stars with clean text
    cleaned = re.sub(r"\*\*([^\*]+)\*\*", r"\1", cleaned)
    # Replace * bullet with clean bullet point dot
    cleaned = re.sub(r"^\s*[\*\-]\s+", "• ", cleaned, flags=re.MULTILINE)
    # Remove any remaining stray asterisks
    cleaned = cleaned.replace("*", "")
    return cleaned.strip()


def _call_groq(messages: list) -> Optional[str]:
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return None

    url = settings.GROQ_API_URL or "https://api.groq.com/openai/v1/chat/completions"
    model = settings.GROQ_MODEL or "qwen/qwen3.8-27b"

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.4,
    }
    req = urllib_request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            msg = choice.get("message", {})
            content = msg.get("content") or msg.get("reasoning_content") or choice.get("text")
            if content:
                return _clean_reply(content)
    except Exception as exc:
        logging.warning("Groq Assistant API call failed: %s", exc)
    return None


def _call_huggingface(messages: list) -> Optional[str]:
    token = settings.HUGGINGFACE_API_TOKEN
    if not token:
        return None

    payload = {
        "model": settings.HUGGINGFACE_MODEL or "meta-llama/Llama-3.1-8B-Instruct",
        "messages": messages,
        "max_tokens": 350,
        "temperature": 0.3,
    }
    req = urllib_request.Request(
        HUGGINGFACE_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            msg = choice.get("message", {})
            content = msg.get("content") or msg.get("reasoning_content") or choice.get("text")
            if content:
                return _clean_reply(content)
    except Exception as exc:
        logging.warning("HuggingFace Assistant API call failed: %s", exc)
    return None


def generate_assistant_reply(message: str, history: list = None) -> str:
    system_prompt = {
        "role": "system",
        "content": (
            "You are AI Council, an intelligent, helpful academic admissions counselor for CutoffGuide (India).\n"
            "You assist students with engineering, management, medical, and university admissions across India.\n"
            "STRICT RULES:\n"
            "- Always answer the user's specific question directly and accurately with relevant college names, cutoff percentiles, exam details, fees, or placement statistics.\n"
            "- Never output markdown bold asterisks (do NOT use '**' or '***'). Output clean, natural text.\n"
            "- Use clean bullet points (•) where helpful for readability.\n"
            "- Keep responses comprehensive yet concise (120-220 words)."
        ),
    }

    messages = [system_prompt]

    if history and isinstance(history, list):
        for item in history[-6:]:
            if isinstance(item, dict) and "role" in item and "content" in item:
                role = item["role"] if item["role"] in ("user", "assistant") else "user"
                content = str(item["content"]).strip()
                if content:
                    messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message.strip()})

    # 1. Try Groq LLM (High-speed Qwen/Llama)
    reply = _call_groq(messages)
    if reply:
        return reply

    # 2. Try Hugging Face
    reply = _call_huggingface(messages)
    if reply:
        return reply

    # 3. Dynamic contextual fallback
    q = message.lower()
    if "pune" in q or "maharashtra" in q or "mht" in q or "cet" in q:
        return (
            "Key Insights for Maharashtra Engineering Admissions (MHT-CET / CAP Rounds):\n\n"
            "• Top Tier Colleges: COEP Tech (99.2+ percentile for CS/IT), VJTI Mumbai (99.5+), PICT Pune (98.8+), SPIT Mumbai (98.6+), and Walchand Sangli (97.5+).\n"
            "• Core & Specialized Branches: Mechanical, Civil, and Electrical at top institutes close around the 90-95 percentile range.\n"
            "• Placements: Top colleges average ₹10.5 - ₹16.8 LPA, with highest offers exceeding ₹40+ LPA.\n"
            "• Strategy: Fill preferences with dream colleges in choices 1–5, solid target options in 6–15, and safe backups in 16–25."
        )
    elif "iit" in q or "jee" in q or "josaa" in q or "nit" in q:
        return (
            "Key Insights for JEE Main & Advanced / JoSAA Admissions:\n\n"
            "• IIT Cutoffs: Top IITs (Bombay, Delhi, Madras) CSE ranks close within top 60-300 AIR. Newer IITs offer CSE up to 4,000-5,500 AIR.\n"
            "• NIT & IIIT Cutoffs: Top NITs (Trichy, Surathkal, Warangal) CSE closes within 1,500-3,500 JEE Main ranks; other branches extend to 25,000-45,000.\n"
            "• Placement Outlook: Average packages at top NITs/IIITs range between ₹14.0 - ₹24.0 LPA.\n"
            "• Strategy: Prioritize branch vs institute based on your career interests and utilize all CSAB special rounds."
        )
    elif "fees" in q or "scholarship" in q:
        return (
            "Tuition Fees & Financial Aid Overview in India:\n\n"
            "• Government & Unitary Universities: ₹60,000 – ₹1.4 Lakh / year (e.g., COEP, VJTI, DTU, Anna University).\n"
            "• IITs & NITs: ₹1.25 – ₹2.2 Lakh / year with 100% tuition fee waiver for SC/ST/PwD and income-based remissions for Gen/OBC EWS.\n"
            "• Private Universities: ₹2.5 – ₹5.5 Lakh / year (e.g., BITS Pilani, Manipal, VIT, Thapar).\n"
            "• State Scholarships: EBC, TFWS (Tuition Fee Waiver Scheme), and National Scholarship Portal (NSP) provide up to 50-100% tuition concessions."
        )

    return (
        f"Regarding your query on '{message}':\n\n"
        "• Admissions & Cutoffs: Admission cutoffs vary by exam (JEE Main, MHT-CET, GATE, CAT, CUET) and candidate category (General, OBC, SC, ST, EWS).\n"
        "• Verification: Check our College Directory search for exact branch-wise cutoff statistics, fee structures, and placement reports.\n"
        "• Action Step: Select your preferred state in the Colleges tab to view detailed cutoff predictions and placement statistics."
    )