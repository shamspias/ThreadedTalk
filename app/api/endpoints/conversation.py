from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import AsyncGenerator

from app.crud import conversation as crud_conv
from app.schemas.conversation import ConversationCreate, ConversationTextResponse
from app.db.session import get_db
from app.services.assistant_client_manager import GraphManager
from app.core.config import settings

router = APIRouter()

# Instantiate the GraphManager.
graph_manager = GraphManager(
    deployment_url=settings.ASSISTANT_DEPLOYMENT_URL,
    graph_id=settings.ASSISTANT_GRAPH_ID,
    assistant_id=settings.ASSISTANT_ID,
    api_key=settings.ASSISTANT_API_KEY
)


@router.post("/conversation", response_model=ConversationTextResponse)
async def handle_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    conv = await crud_conv.get_conversation_by_id(db, conversation.conversation_id)
    thread_id = conv.thread_id if conv else None

    if conversation.stream:
        if not conv:
            thread_id = await graph_manager._get_or_create_thread(conversation.conversation_id, thread_id)
            await crud_conv.create_conversation(db, conversation.conversation_id, thread_id)
        else:
            await crud_conv.update_last_used(db, conv)

        async def stream_generator() -> AsyncGenerator[bytes, None]:
            try:
                async for chunk in graph_manager.stream_message(
                        message=conversation.message,
                        conversation_id=conversation.conversation_id,
                        images=conversation.images,
                        thread_id=thread_id
                ):
                    yield chunk.encode("utf-8")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        return StreamingResponse(stream_generator(), media_type="text/plain")
    else:
        try:
            if not conv:
                thread_id = await graph_manager._get_or_create_thread(conversation.conversation_id, thread_id)
                conv = await crud_conv.create_conversation(db, conversation.conversation_id, thread_id)
            response_text = await graph_manager.send_message(
                message=conversation.message,
                conversation_id=conversation.conversation_id,
                images=conversation.images,
                thread_id=conv.thread_id
            )
            # Update last used timestamp.
            await crud_conv.update_last_used(db, conv)
            return ConversationTextResponse(response=response_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}", response_model=dict)
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    conv = await crud_conv.get_conversation_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    try:
        await graph_manager.delete_thread(conv.thread_id)
    except Exception as e:
        # Log the error if needed.
        pass
    deleted = await crud_conv.delete_conversation(db, conversation_id)
    return {"deleted": deleted}


@router.delete("/conversation/inactive", response_model=dict)
async def delete_inactive_conversations(unused_from: datetime = Query(...), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(crud_conv.get_conversation_by_id))
    # Alternatively, you can query your models directly here.
    # For each inactive conversation:
    inactive_convs = (
        await db.execute(select().where("last_used < :unused_from", {"unused_from": unused_from}))).scalars().all()
    count = 0
    for conv in inactive_convs:
        try:
            await graph_manager.delete_thread(conv.thread_id)
        except Exception:
            pass
        await db.delete(conv)
        count += 1
    await db.commit()
    return {"deleted_count": count}
