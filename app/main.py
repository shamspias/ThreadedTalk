from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import conversation
from app.db.session import engine
from app.db.base import Base

# Determine the global log level based on the DEBUG flag.
log_level = logging.DEBUG if settings.DEBUG else logging.ERROR
logging.basicConfig(level=log_level)

app = FastAPI(title=settings.API_TITLE, debug=settings.DEBUG)

# Use ALLOWED_ORIGINS from settings for CORS configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Will be a list, thanks to our custom loader
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    conversation.router,
    prefix="/api",
    tags=["LangGraph SDK API"]
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
