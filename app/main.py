from fastapi import FastAPI
import logging
from app.core.config import settings
from app.api.endpoints import conversation
from app.db.session import engine
from app.db.base import Base

# Determine the global log level based on the DEBUG flag.
log_level = logging.DEBUG if settings.DEBUG else logging.ERROR
logging.basicConfig(level=log_level)

app = FastAPI(title=settings.API_TITLE, debug=settings.DEBUG)

app.include_router(conversation.router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    # Create database tables if they do not exist.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
