import asyncio
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.assistant_service import generate_assistant_reply

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])


class MessageItem(BaseModel):
    role: str = "user"
    content: str


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[dict] = Field(default_factory=list)


@router.post("")
async def assistant_chat(request: AssistantRequest):
    reply = await asyncio.to_thread(
        generate_assistant_reply,
        request.message.strip(),
        history=request.history,
    )
    return {"status": "success", "reply": reply}