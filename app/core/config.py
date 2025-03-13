from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    SYNC_DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    ASSISTANT_DEPLOYMENT_URL: str = "https://api.langgraph.com"
    ASSISTANT_GRAPH_ID: str = "your_graph_id"
    ASSISTANT_ID: str = "your_graph_id"
    ASSISTANT_API_KEY: str = ""
    API_TITLE: str = "Assistant Conversation API"
    DEBUG: bool = False
    # Use a custom json_loads function so that a comma-separated string is split into a list.
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        env="ALLOWED_ORIGINS",
        json_loads=lambda v: [i.strip() for i in v.split(",")] if v else ["*"]
    )

    class Config:
        env_file = ".env"


settings = Settings()
