import datetime
from sqlmodel import  Field, SQLModel


class ChatSession(SQLModel, table=True):
    id: str = Field(primary_key=True)
    file_id: str = Field(index=True)
    title: str | None = Field(default=None)
    
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now, sa_column_kwargs={"onupdate": datetime.datetime.now})
    