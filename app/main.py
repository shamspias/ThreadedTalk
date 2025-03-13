from fastapi import FastAPI
from app.api.endpoints import conversation
from app.db.session import engine
from app.db.base import Base

app = FastAPI(title="Assistant Conversation API")

app.include_router(conversation.router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    # Create database tables if they do not exist.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
