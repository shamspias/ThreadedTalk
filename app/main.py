from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import conversation, logs
from app.db.session import engine
from app.db.base import Base

# Set up the logging configuration
log_level = logging.DEBUG if settings.DEBUG else logging.ERROR
logging.basicConfig(level=log_level)

app = FastAPI(title=settings.API_TITLE, debug=settings.DEBUG)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# If debug mode is enabled, add our in-memory log handler and store it in app state.
if settings.DEBUG:
    from app.core.log_handler import in_memory_handler

    logging.getLogger().addHandler(in_memory_handler)
    app.state.log_handler = in_memory_handler

# Include routers
app.include_router(
    conversation.router,
    prefix="/api",
    tags=["LangGraph SDK API"]
)
app.include_router(
    logs.router,  # See the logs endpoint below
    prefix="/api",
    tags=["Logs"]
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
