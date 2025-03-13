from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.conversation import Conversation
from datetime import datetime


async def get_conversation_by_id(db: AsyncSession, conversation_id: str):
    result = await db.execute(select(Conversation).where(Conversation.conversation_id == conversation_id))
    return result.scalars().first()


async def create_conversation(db: AsyncSession, conversation_id: str, thread_id: str):
    conv = Conversation(conversation_id=conversation_id, thread_id=thread_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def update_last_used(db: AsyncSession, conversation: Conversation):
    conversation.last_used = datetime.utcnow()
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def delete_conversation(db: AsyncSession, conversation_id: str):
    result = await db.execute(delete(Conversation).where(Conversation.conversation_id == conversation_id))
    await db.commit()
    return result.rowcount
