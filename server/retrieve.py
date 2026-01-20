import stat
from sqlmodel import Session, select, col
from typing import Optional

from server.database import engine
from server.models import PaperChunk, Paper
from server.config import get_embed_model

# 获取 Embedding 模型
embed_model = get_embed_model()

def search_base(query:str, paper_id: Optional[str] = None, top_k: int = 3):
    
    # 1.query -> vector
    query_vector = embed_model.get_query_embedding(query)

    with Session(engine) as session:
        # 2.query by vector, order by distance
        statement =(
            select(PaperChunk, Paper)
            .join(Paper)
            .order_by(PaperChunk.embedding.cosine_distance(query_vector)) #type:ignore
            .limit(top_k)
        )
        if paper_id:
            # SQLModel 会自动把这个转换成 SQL 的 WHERE paper_chunk.paper_id = '...'
            statement = statement.where(PaperChunk.paper_id == paper_id)

        results = session.exec(statement).all()
        print(f"\n find {len(results)} chunks:\n")
        
        for i, (chunk, paper) in enumerate(results):
            
            print(f"[Metadata]: {chunk.metadata_json}")
            print(f"[Content]: \n{chunk.text[:50]}...") 
            print("-" * 50)
            
        return results


def search_opening_chunks_by_id(paper_id: str):
    with Session(engine) as session:
        statement = (
            select(PaperChunk)
            .where(PaperChunk.paper_id == paper_id)
            .where(PaperChunk.chunk_index.in_([0,1])) #type:ignore
            .order_by(col(PaperChunk.chunk_index))
        )

        results = session.exec(statement).all()
        return [result.text for result in results]

def search_opening_chunks_by_query(query: str, top_k: int = 3):
    query_vector = embed_model.get_query_embedding(query)
    with Session(engine) as session:
        statement = (
            select(PaperChunk)
            .where(PaperChunk.chunk_index.in_([0,1])) #type:ignore
            .order_by(PaperChunk.embedding.cosine_distance(query_vector)) #type:ignore
            .limit(top_k)
        )
        results = session.exec(statement).all()
        return [result.text for result in results]
    
if __name__ == "__main__":
    # 这里的 query 换成你那篇论文里具体的某个定理名，比如 "Bernstein theorem"
    search_base("what is the scheon-simon-yau theorem? what is author's extension?",paper_id = "2310.01340v2")