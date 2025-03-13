from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)
    thread_id = Column(String, nullable=False)
    last_used = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
