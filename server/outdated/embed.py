import os
import json
from pathlib import Path
from sqlmodel import Session, select
from llama_index.core.schema import TextNode
from typing import cast

from server.database import engine, create_db_and_tables
from server.models import Paper, PaperChunk
from server.chunk import chunk_document  # pyright: ignore[reportAttributeAccessIssue]
from server.config import get_embed_model

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

__all__ = ["save_node_to_postgres"]

# 获取 Embedding 模型
embed_model = get_embed_model()


def save_node_to_postgres(paper_id: str, nodes: list[TextNode]):
    """
    Embed nodes and save them to PostgreSQL database.
    
    Args:
        paper_id: The paper ID in the database
        nodes: List of nodes to embed and save
    """
    node_texts = [node.text for node in nodes]
    embeddings = embed_model.get_text_embedding_batch(node_texts)

    with Session(engine) as session:
        paper = session.get(Paper, paper_id)
        if not paper:
            print(f"paper with id {paper_id} not in database, add to database first")
            return

        print(f"writing paper id:{paper_id}'s chunk into database")
        for i, node in enumerate(nodes):
            chunk = PaperChunk(
                chunk_index = i,
                text = node.text,
                metadata_json=json.dumps(node.metadata),
                paper_id = paper_id,
                embedding=embeddings[i]
            )
            session.add(chunk)
        
        session.commit()
        print(f"storing {len(nodes)} vectors successfully")


if __name__ == "__main__":
    # 测试代码
    create_db_and_tables()
    
    md_path = SCRIPT_DIR / "data/mds/2310.01340v2.Extensions_of_Schoen__Simon__Yau_and_Schoen__Simon_theorems_via_iteration_à_la_De_Giorgi.md"
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 使用 chunk_document 函数
    nodes = chunk_document(md_text)

    save_node_to_postgres("2310.01340v2", nodes=nodes)       