from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    SYNC_DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    ASSISTANT_DEPLOYMENT_URL: str = "https://api.langgraph.com"
    ASSISTANT_GRAPH_ID: str = "your_graph_id"
    ASSISTANT_ID: str = "your_graph_id"
    ASSISTANT_API_KEY: str = ""
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
