from datetime import datetime
import os
import json
import shutil

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import TextNode
from sqlmodel import Session, select
from llama_parse import LlamaParse, ResultType
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter

from server.database import engine
from server.models import Paper, PaperChunk
from server.config import METADATA_DIR, ARCHIVED_DIR, MD_DIR, CHUNK_SIZE, CHUNK_OVERLAP, get_embed_model

# For backward compatibility with string paths
PARSED_DIR = str(MD_DIR)

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def load_metadata_logs():
    all_papers = []
    if not os.path.exists(str(METADATA_DIR)):
        return []

    for meta_file in os.listdir(str(METADATA_DIR)):
        if meta_file.endswith(".json"):
            with open(os.path.join(str(METADATA_DIR), meta_file), "r", encoding="utf-8") as f:
                papers_metadata = json.load(f)
                all_papers.extend(papers_metadata)

    return all_papers

def parse_pdf_to_md(file_path: str):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found")
        return 
    
    output_dir = os.path.dirname(file_path).replace("pdfs", "mds")
    output_filename = os.path.basename(file_path).replace(".pdf", ".md")
    output_path = os.path.join(output_dir, output_filename)

    #check if md already exists
    if os.path.exists(output_path):
        print(f"File {output_path} already exists")
        return ""

    #if not, parse pdf to md
    try:
        parsing_instruction = "The document contains complex mathematical formulas and theorems. Please strictly preserve all mathematical formatting. Output all math equations in LaTeX format, wrapping inline math in $...$ and display math in $$...$$. Ensure superscripts (like R^n) and subscripts are correctly formatted."
        parser = LlamaParse(
            result_type=ResultType.MD,  # pyright: ignore[reportCallIssue]
            parse_mode="parse_page_with_agent", # pyright: ignore[reportCallIssue]
            model="openai-gpt-4-1-mini", # pyright: ignore[reportCallIssue]
            output_tables_as_HTML=True, # pyright: ignore[reportCallIssue]
            system_prompt_append= parsing_instruction, # pyright: ignore[reportCallIssue]
            page_separator="\n\n---\n\n", # pyright: ignore[reportCallIssue]
            language="en"    # pyright: ignore[reportCallIssue]
        )
        
        print("sent to LlamaParse...")
        file_extractor: dict[str, BaseReader] = {".pdf": parser}
        documents = SimpleDirectoryReader(
            input_files=[file_path], file_extractor=file_extractor
        ).load_data()
        print(f"\n--- Parsing completed! There are {len(documents)} document objects ---")
        
        #write to md
        text_content = "\n\n".join([doc.text for doc in documents])
        ensure_dir(output_dir)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"\n✓ Markdown saved to: {output_path}")

        return text_content

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        raise Exception(f"Error parsing {file_path}: {e}")

def chunk_document(md_text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[TextNode]:
    document = Document(text=md_text)

    parser = MarkdownNodeParser()
    base_nodes = parser.get_nodes_from_documents([document])

    text_splitter = SentenceSplitter(chunk_size=chunk_size, 
                    chunk_overlap=chunk_overlap)

    nodes = text_splitter(base_nodes)

    print(f"Document chunked into {len(nodes)} nodes.\n")
    
    return nodes  # type: ignore

def ingest_papers():
    ensure_dir(str(ARCHIVED_DIR))
    embed_model = get_embed_model()

    #1. scan all metadata logs, and then ingest all of them
    json_files = [f for f in os.listdir(str(METADATA_DIR)) if f.endswith(".json")]
    if not json_files:
        print("No new metadata logs found")
        return 
    
    with Session(engine) as session:
        for json_file in json_files:
            filepath = os.path.join(str(METADATA_DIR), json_file)
            with open(filepath, "r", encoding="utf-8") as f:
                paper_list = json.load(f)
            
            for metadata in paper_list:
                paper_id = metadata["paper_id"]
                
                #check if paper already exists
                paper = session.get(Paper, paper_id)
                if paper:
                    print(f"Paper {paper_id} already exists in database, skipping...")
                    continue

                #if not, save the paper and paper chunks
                #get parsed md text
                md_text = parse_pdf_to_md(metadata["file_path"])
                if not md_text:
                    print(f"Error parsing {metadata['file_path']}, skipping...")
                    continue
                
                #save paper
                new_paper = Paper(
                    id=paper_id,
                    title=metadata["title"],
                    authors=metadata["authors"],
                    published_date=datetime.fromisoformat(metadata["published_date"]),
                    topic=metadata["topic"],
                    local_pdf_path=metadata["file_path"],
                    abstract=metadata["abstract"],      
                    arxiv_url=metadata["arxiv_url"],
                )

                session.add(new_paper)
                session.commit()
                session.refresh(new_paper)

                #save paper chunks
                nodes = chunk_document(md_text)
                node_texts = [node.text for node in nodes]
                embeddings = embed_model.get_text_embedding_batch(node_texts)
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
                
                print(f"storing {len(node_texts)} vectors successfully")
        
            print(f"Ingested {len(paper_list)} papers successfully, archived log file: {json_file}")

            #2. move ingested metadata logs to archived
            shutil.move(filepath, os.path.join(str(ARCHIVED_DIR), json_file))
            print(f"Archived log file: {json_file}")


if __name__ == "__main__":
    ingest_papers()