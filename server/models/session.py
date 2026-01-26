

import datetime
from sqlmodel import DateTime, Field, SQLModel
from sqlmodel import Column, String


class ChatSession(SQLModel, table=True):
    id: str = Field(primary_key=True)
    file_id = Column(String, index=True, nullable=False)
    title = Column(String) 
    
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)
    