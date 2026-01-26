import json
import logging
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from asyncpg import Connection

from database import get_async_db_connection
from config import UPLOADS_DIR, get_embed_model
from models.paper import Paper, PaperChunk
from report_pipeline.ingest_pipeline import parse_pdf_to_md, chunk_document
from chatbox.utils.extract_relative_path import extract_relative_path

os.makedirs(UPLOADS_DIR, exist_ok=True)
files_router = APIRouter(tags=["files"])

embed_model = get_embed_model()

logger = logging.getLogger(__name__)

#not used yet
@files_router.get("/api/papers")
async def get_papers(db: Connection = Depends(get_async_db_connection)):
    rows = await db.fetch("SELECT id, title, topic, local_pdf_path FROM paper")
    
    papers = []
    for row in rows:
        relative_path = extract_relative_path(row["local_pdf_path"],"data")
        if relative_path:
            papers.append({
                "id": row["id"],
                "title": row["title"],
                "topic": row["topic"],
                "path": relative_path
            })
    return papers

#get both papers and reports
@files_router.get("/api/files")
async def get_files(db: Connection = Depends(get_async_db_connection)):
    paper_rows = await db.fetch("SELECT id, title, topic, local_pdf_path FROM paper")
    report_rows = await db.fetch("SELECT id, title, topic, local_pdf_path FROM report")
    
    papers = []
    for row in paper_rows:
        logger.log(1,f"{row["title"]} detected")
        relative_path = extract_relative_path(row["local_pdf_path"], "data")
        if relative_path:
            papers.append({
                "id": row["id"],
                "title": row["title"],
                "topic": row["topic"],
                "path": relative_path
            })
    
    reports = []
    for row in report_rows:
        logger.log(1,f"{row["title"]} detected")
        relative_path = extract_relative_path(row["local_pdf_path"], "data")
        if relative_path:
            reports.append({
                "id": row["id"],
                "title": row["title"],
                "topic": row["topic"],
                "path": relative_path
            })
    
    return {"papers": papers, "reports": reports}


@files_router.get("/api/{file_id}")
#return full path of the file
async def get_file_by_id(file_id: str, db: Connection = Depends(get_async_db_connection)):
    paper = await db.fetchrow("SELECT title, topic, local_pdf_path FROM paper WHERE id = $1", file_id)
    report = await db.fetchrow("SELECT title, topic, local_pdf_path FROM report WHERE id = $1", file_id)

    if paper:
        path = paper["local_pdf_path"]
        return {"title": paper["title"], "topic": paper["topic"], "path": path}

    if report:
        path = report["local_pdf_path"]
        return {"title": report["title"], "topic": report["topic"], "path": path}

    raise HTTPException(status_code=404, detail="File not found")
    
    

@files_router.post("/api/upload")
async def upload_paper(file: UploadFile = File(...), db: Connection = Depends(get_async_db_connection)):
    # Generate unique ID
    paper_id = str(uuid.uuid4())

    # Save file to disk
    if not file.filename:
        file.filename = f"auto_generated_name_{paper_id}.pdf"
    file_path = os.path.join(str(UPLOADS_DIR), file.filename)

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Use transaction to ensure atomicity of database operations
    async with db.transaction():
        try:
            # Insert paper record
            await db.execute(
                "INSERT INTO paper (id, title, topic, local_pdf_path) VALUES ($1, $2, $3, $4)",
                paper_id, "uploaded", file.filename, file_path
            )

            # Parse PDF and chunk document
            parsed_md = parse_pdf_to_md(file_path)
            if not parsed_md:
                raise ValueError("Failed to parse PDF")

            nodes = chunk_document(parsed_md)
            node_texts = [node.text for node in nodes]
            embeddings = embed_model.get_text_embedding_batch(node_texts)

            # Insert paper chunks
            for i, node in enumerate(nodes):
                paper_chunk = PaperChunk(
                    chunk_index=i,
                    text=node.text,
                    metadata_json=json.dumps(node.metadata),
                    paper_id=paper_id,
                    embedding=embeddings[i]
                )
                await db.execute(
                    "INSERT INTO paperchunk (chunk_index, text, metadata_json, paper_id, embedding) VALUES ($1, $2, $3, $4, $5)",
                    paper_chunk.chunk_index, paper_chunk.text, paper_chunk.metadata_json, 
                    paper_chunk.paper_id, paper_chunk.embedding
                )

            # Transaction auto-commits on success
            return {"message": "Paper uploaded successfully"}

        except Exception as e:
            # Transaction auto-rollbacks on exception
            # Clean up saved file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"{str(e)}")
