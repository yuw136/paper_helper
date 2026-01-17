import os
import json
from dotenv import load_dotenv
from sqlmodel import Session, select
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core import Document
from typing import cast

from database import engine, create_db_and_tables
from models import Paper, PaperChunk

load_dotenv()

with open("./data/mds/2310.01340v2.Extensions_of_Schoen__Simon__Yau_and_Schoen__Simon_theorems_via_iteration_à_la_De_Giorgi.md", "r", encoding="utf-8") as f:
    md_text = f.read()

#chunk the document. If chunk with section is too big, chunk again with 1024byte and 200 overlap
document = Document(text=md_text)

parser = MarkdownNodeParser()

base_nodes = parser.get_nodes_from_documents([document])
text_splitter = SentenceSplitter(chunk_size=1024, 
                chunk_overlap=200)

nodes = text_splitter(base_nodes)

#Embed 
embed_model = OpenAIEmbedding(model_name = "text-embedding-3-small")

def save_node_to_postgres(paper_id, nodes: list[TextNode]):
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

# make sure to initialize
if __name__ == "__main__":
    create_db_and_tables() 

save_node_to_postgres("2310.01340v2",nodes=cast(list[TextNode], nodes))       