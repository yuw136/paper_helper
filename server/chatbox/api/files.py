import json
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from asyncpg import Connection

from database import get_async_db_connection
from config import UPLOADS_DIR, get_embed_model
from models.paper import Paper, PaperChunk
from report_pipeline.ingest_pipeline import ensure_dir, parse_pdf_to_md, chunk_document

os.makedirs(UPLOADS_DIR, exist_ok=True)
files_router = APIRouter(tags=["files"])

embed_model = get_embed_model()

#not used yet
@files_router.get("/papers")
async def get_papers(db: Connection = Depends(get_async_db_connection)):
    rows = await db.fetch("SELECT * FROM paper")
    
    return [dict(row) for row in rows]

#get both papers and reports
@files_router.get("/files")
async def get_files(db: Connection = Depends(get_async_db_connection)):
    papers = await db.fetch("SELECT * FROM paper")
    reports = await db.fetch("SELECT * FROM report")
    
    return {
        "papers": [dict(paper) for paper in papers],
        "reports": [dict(report) for report in reports]
    }



@files_router.get("/{file_id}")
async def get_paper(file_id: str, db: Connection = Depends(get_async_db_connection)):
    row = await db.fetchrow("SELECT * FROM paper WHERE id = $1", file_id)
    
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return dict(row)

@files_router.post("/upload")
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
                "INSERT INTO paper (id, title, local_pdf_path) VALUES ($1, $2, $3)",
                paper_id, file.filename, file_path
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
