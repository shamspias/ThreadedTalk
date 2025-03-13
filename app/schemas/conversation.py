from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ConversationCreate(BaseModel):
    conversation_id: str
    message: str
    stream: Optional[bool] = False


class ConversationResponse(BaseModel):
    conversation_id: str
    thread_id: str
    last_used: datetime

    class Config:
        from_attributes = True


class ConversationTextResponse(BaseModel):
    response: str


class DeleteInactiveConversations(BaseModel):
    unused_from: datetime
