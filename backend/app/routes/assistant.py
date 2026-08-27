from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.assistant_service import generate_assistant_reply

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])


class MessageItem(BaseModel):
    role: str = "user"
    content: str


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[dict] = Field(default_factory=list)


@router.post("")
async def assistant_chat(request: AssistantRequest, db=Depends(get_db)):
    reply = await generate_assistant_reply(request.message.strip(), db=db, history=request.history)
    return {"status": "success", "reply": reply}