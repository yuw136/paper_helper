from datetime import datetime
from typing import Optional, Sequence
from pgvector.sqlalchemy import Vector
from sqlmodel import SQLModel
from sqlmodel import Field, Column

class Report(SQLModel, table=True):
    id: str = Field(primary_key=True)
    topic: Optional[str] = Field(default=None)
    start_date: datetime
    end_date: datetime
    local_pdf_path: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    #contents
    title: str
    # content_tex: str
    content_md: str

    #embeddings, long term memory
    summary_embedding: Sequence[float] | None = Field(default=None, sa_column=Column(Vector(1536)))
    
