"""
Script to fix existing papers in the database by re-ingesting them with corrected abstracts.
This will delete the existing papers and re-ingest them with proper Greek letter handling.
"""
from sqlmodel import Session, select
from database import engine
from models import Paper, PaperChunk
from report_pipeline.ingest_pipeline import ingest_papers
import json
import os
from config import METADATA_DIR, ARCHIVED_DIR

def delete_existing_papers():
    """Delete all existing papers and their chunks from the database."""
    with Session(engine) as session:
        # Get all papers
        papers = session.exec(select(Paper)).all()
        
        if not papers:
            print("No papers found in database")
            return
        
        print(f"Found {len(papers)} papers in database")
        
        for paper in papers:
            print(f"Deleting paper: {paper.id} - {paper.title}")
            
            # Delete all chunks associated with this paper
            chunks = session.exec(select(PaperChunk).where(PaperChunk.paper_id == paper.id)).all()
            for chunk in chunks:
                session.delete(chunk)
            
            # Delete the paper
            session.delete(paper)
        
        session.commit()
        print(f"\n✓ Successfully deleted {len(papers)} papers and their chunks")

def move_archived_logs_back():
    """Move archived metadata logs back to metadata directory for re-ingestion."""
    archived_dir = str(ARCHIVED_DIR)
    metadata_dir = str(METADATA_DIR)
    
    if not os.path.exists(archived_dir):
        print("No archived logs found")
        return
    
    json_files = [f for f in os.listdir(archived_dir) if f.endswith(".json")]
    
    if not json_files:
        print("No archived JSON files found")
        return
    
    print(f"\nMoving {len(json_files)} archived log files back to metadata directory...")
    
    for json_file in json_files:
        src = os.path.join(archived_dir, json_file)
        dst = os.path.join(metadata_dir, json_file)
        
        # Move file back
        os.rename(src, dst)
        print(f"  Moved: {json_file}")
    
    print(f"✓ Successfully moved {len(json_files)} files back for re-ingestion")

if __name__ == "__main__":
    print("=" * 60)
    print("FIXING EXISTING PAPERS WITH CORRECTED GREEK LETTERS")
    print("=" * 60)
    
    # Step 1: Delete existing papers
    print("\nStep 1: Deleting existing papers from database...")
    delete_existing_papers()
    
    # Step 2: Move archived logs back
    print("\nStep 2: Moving archived logs back to metadata directory...")
    move_archived_logs_back()
    
    # Step 3: Re-ingest papers
    print("\nStep 3: Re-ingesting papers with corrected abstracts...")
    ingest_papers()
    
    print("\n" + "=" * 60)
    print("✅ COMPLETED! Papers have been re-ingested with corrected abstracts.")
    print("=" * 60)
