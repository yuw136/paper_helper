import json
import logging
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from asyncpg import Connection

from database import get_async_db_connection
from config import UPLOADS_DIR, get_embed_model
from models.paper import Paper, PaperChunk
from report_pipeline.ingest_pipeline import parse_pdf_to_md, chunk_document
from chatbox.utils.extract_relative_path import extract_relative_path
from managers.storage_manager import StorageManager

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
#return file metadata (not the actual file)
async def get_file_by_id(file_id: str, db: Connection = Depends(get_async_db_connection)):
    paper = await db.fetchrow("SELECT title, topic, local_pdf_path FROM paper WHERE id = $1", file_id)
    report = await db.fetchrow("SELECT title, topic, local_pdf_path FROM report WHERE id = $1", file_id)

    if paper:
        # Return the API URL for streaming the PDF, not the local path
        return {"title": paper["title"], "topic": paper["topic"], "path": f"/api/pdf/{file_id}"}

    if report:
        # Return the API URL for streaming the PDF, not the local path
        return {"title": report["title"], "topic": report["topic"], "path": f"/api/pdf/{file_id}"}

    raise HTTPException(status_code=404, detail="File not found")


@files_router.get("/api/pdf-url/{file_id}")

async def get_pdf_url(file_id: str, db: Connection = Depends(get_async_db_connection)):
    #get signed storage url for the pdf file from database
    paper = await db.fetchrow(
        "SELECT title, local_pdf_path, storage_url FROM paper WHERE id = $1", 
        file_id
    )
    report = await db.fetchrow(
        "SELECT title, local_pdf_path, storage_url FROM report WHERE id = $1", 
        file_id
    )

    if paper:
        title = paper["title"]
        storage_url = paper["storage_url"]
    elif report:
        title = report["title"]
        storage_url = report["storage_url"]
    else:
        raise HTTPException(status_code=404, detail="File not found")

    # Supabase mode: return signed URL
    if StorageManager.is_supabase_mode():
        if not storage_url:
            raise HTTPException(
                status_code=404, 
                detail="File has no storage_url configured"
            )
        
        try:
            #1 hour limit for signed URL
            signed_url = StorageManager.get_signed_url(storage_url, expires_in=3600)
            return JSONResponse({
                "type": "url",
                "url": signed_url,
                "title": title
            })
        except Exception as e:
            logger.error(f"Failed to get signed URL: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to get file URL: {str(e)}"
            )
    
    # Local mode: return API endpoint URL
    else:
        return JSONResponse({
            "type": "api",
            "url": f"/api/pdf/{file_id}",
            "title": title
        })


@files_router.get("/api/pdf/{file_id}")
async def get_pdf_file(file_id: str, db: Connection = Depends(get_async_db_connection)):
    #this method is only used in local mode
    paper = await db.fetchrow(
        "SELECT title, local_pdf_path, storage_url FROM paper WHERE id = $1", 
        file_id
    )
    report = await db.fetchrow(
        "SELECT title, local_pdf_path, storage_url FROM report WHERE id = $1", 
        file_id
    )

    if paper:
        title = paper["title"]
        storage_url = paper["storage_url"]
        local_path = paper["local_pdf_path"]
    elif report:
        title = report["title"]
        storage_url = report["storage_url"]
        local_path = report["local_pdf_path"]
    else:
        raise HTTPException(status_code=404, detail="File not found")


    if StorageManager.is_supabase_mode():
        # in Supabase mode, should not access this endpoint, use /api/pdf-url instead
        raise HTTPException(
            status_code=400, 
            detail="In Supabase mode, use /api/pdf-url/{file_id} to get a signed URL"
        )
    
    file_path = storage_url if storage_url else local_path
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"PDF file not found on disk"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{title}.pdf"
    )
    


@files_router.post("/api/upload")
async def upload_paper(file: UploadFile = File(...), db: Connection = Depends(get_async_db_connection)):
    # Generate unique ID
    paper_id = str(uuid.uuid4())

    # Prepare filename
    if not file.filename:
        file.filename = f"auto_generated_name_{paper_id}.pdf"
    
    # Read file content
    file_content = await file.read()
    
    # For parsing, we need the file locally (temporary)
    import tempfile
    temp_file_path = None
    
    try:
        # Save to temp file for parsing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Upload to storage (local or Supabase)
        display_path, storage_url = await StorageManager.upload_paper(
            file_content=file_content,
            filename=file.filename,
            topic="uploads"  # Default topic for user uploads
        )
        
        # Use transaction to ensure atomicity of database operations
        async with db.transaction():
            # Insert paper record with both paths
            await db.execute(
                """INSERT INTO paper (id, title, topic, local_pdf_path, storage_url) 
                   VALUES ($1, $2, $3, $4, $5)""",
                paper_id, "uploaded", file.filename, display_path, storage_url
            )

            # Parse PDF and chunk document (using temp file)
            parsed_md = parse_pdf_to_md(temp_file_path)
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
                    """INSERT INTO paperchunk (chunk_index, text, metadata_json, paper_id, embedding) 
                       VALUES ($1, $2, $3, $4, $5)""",
                    paper_chunk.chunk_index, paper_chunk.text, paper_chunk.metadata_json, 
                    paper_chunk.paper_id, paper_chunk.embedding
                )

            return {"message": "Paper uploaded successfully", "id": paper_id}

    except Exception as e:
        # Clean up: delete from storage if upload succeeded but DB failed
        if storage_url:
            await StorageManager.delete_file(storage_url)
        raise HTTPException(status_code=500, detail=f"{str(e)}")
    
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
