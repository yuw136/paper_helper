"""
Simple script to delete all papers from the database.
Run this before re-ingesting papers with corrected Greek letters.
"""
from sqlmodel import Session, select
from database import engine
from models import Paper, PaperChunk

def delete_all_papers():
    """Delete all papers and their chunks from the database."""
    with Session(engine) as session:
        # Get all papers
        papers = session.exec(select(Paper)).all()
        
        if not papers:
            print("No papers found in database")
            return
        
        print(f"Found {len(papers)} papers in database")
        
        for paper in papers:
            print(f"Deleting: {paper.id} - {paper.title}")
            
            # Delete all chunks
            chunks = session.exec(select(PaperChunk).where(PaperChunk.paper_id == paper.id)).all()
            for chunk in chunks:
                session.delete(chunk)
            
            # Delete the paper
            session.delete(paper)
        
        session.commit()
        print(f"\n✓ Successfully deleted {len(papers)} papers and all their chunks")

if __name__ == "__main__":
    print("=" * 60)
    print("DELETING ALL PAPERS FROM DATABASE")
    print("=" * 60)
    delete_all_papers()
    print("=" * 60)
    print("\nNow you can run the ingest pipeline to re-add them with corrections.")
