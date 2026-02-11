import os
import time
import arxiv
import requests
import logging
from datetime import datetime, timezone
from typing import List, Set, Optional

from sqlmodel import Session, select
from database import engine
from models.paper import Paper
from config import PDF_DIR, METADATA_DIR
from managers.storage_manager import StorageManager, PAPERS_BUCKET, get_supabase_client
from utils import ensure_dir
from utils.arxiv_query import search_arxiv_by_titles, remove_arxiv_version

# Setup logging (stdout goes to Render logs automatically)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Ensures output to stdout
)
logger = logging.getLogger(__name__)

DOWNLOAD_ROOT = str(PDF_DIR)
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
REQUEST_DELAY = 0.02  # 20ms delay to respect rate limit (100 req/s)

def get_references_from_semantic_scholar(arxiv_id: str, limit: int = 100) -> List[str]:
    # Correct endpoint: /paper/arXiv:{paper_id}/references
    arxiv_id = remove_arxiv_version(arxiv_id)
    url = f"{SEMANTIC_SCHOLAR_API}/paper/arXiv:{arxiv_id}/references"
    params = {
        'fields': 'externalIds,title',  #
        'limit': limit  
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 404:
            logger.info(f"  Paper {arxiv_id} not found in Semantic Scholar")
            return []
        
        if response.status_code != 200:
            logger.warning(f"  Error fetching references for {arxiv_id}: HTTP {response.status_code}")
            return []
        
        data = response.json()
        # /references endpoint returns {"data": [...], "offset": ..., "next": ...}
        references = data.get('data', [])
        
        # Extract arXiv IDs from references
        arxiv_refs = []
        arxiv_search_needed = []  # Papers that need arXiv search by title
        
        for ref in references:
            cited_paper = ref.get('citedPaper', {})
            if not cited_paper:
                continue
                
            # Get external_ids and title
            external_ids = cited_paper.get('externalIds')
            title = cited_paper.get('title', '')
            
            # Priority 1: Use existing arXiv ID if available
            if external_ids and isinstance(external_ids, dict) and 'ArXiv' in external_ids:
                arxiv_id_ref = external_ids['ArXiv']
                if arxiv_id_ref: 
                    arxiv_refs.append(arxiv_id_ref)
            # Priority 2: Try to find on arXiv by title (fallback for all papers without arXiv ID)
            elif title and len(title.strip()) > 0:
                arxiv_search_needed.append(title)
        
        # Search arXiv for papers without arXiv ID
        if arxiv_search_needed:
            logger.info(f"  Searching arXiv for {len(arxiv_search_needed)} papers by title...")
            found_by_title = search_arxiv_by_titles(arxiv_search_needed)
            arxiv_refs.extend(found_by_title)
            logger.info(f"  Found {len(found_by_title)} additional papers by title search")
        
        logger.info(f"  Total: {len(arxiv_refs)} arXiv papers (out of {len(references)} total references)")
        return arxiv_refs
    
    except requests.exceptions.RequestException as e:
        logger.error(f"  Network error fetching references for {arxiv_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"  Unexpected error fetching references for {arxiv_id}: {e}")
        return []


def download_paper_by_arxiv_id(arxiv_id: str, topic: str, session: Session) -> Optional[dict]:
    # Check if paper already exists in database
    arxiv_id = remove_arxiv_version(arxiv_id)
    existing_paper = session.get(Paper, arxiv_id)
    if existing_paper:
        logger.info(f"  Paper {arxiv_id} already exists in database, skipping...")
        return None
    
    # Fetch paper from arXiv
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    
    try:
        results = list(client.results(search))
        
        if not results:
            logger.warning(f"  Paper {arxiv_id} not found on arXiv")
            return None
        
        result = results[0]
        published_date = result.published
        paper_title = result.title
        
        # Create save directory (same structure as download_pipeline.py)
        topic_safe = topic.replace(' ', '_')
        year = published_date.strftime("%Y")
        month = published_date.strftime("%m")
        save_dir = os.path.join(DOWNLOAD_ROOT, topic_safe, year, month)
        ensure_dir(save_dir)
        
        # Download PDF to local
        file_name = result._get_default_filename()
        local_file_path = os.path.join(save_dir, file_name)
        
        # Download PDF (always download if not exists locally for processing)
        if not os.path.exists(local_file_path):
            result.download_pdf(save_dir)
            logger.info(f"  Downloaded paper {arxiv_id} to {save_dir}")
        else:
            logger.info(f"  Paper {arxiv_id} already exists locally at {save_dir}")
            return None
    
        # Prepare paths for storage (same as ingest_pipeline.py)
        # display_path: relative path for frontend tree display
        display_path = f"pdfs/{topic_safe}/{year}/{month}/{file_name}"
        
        # Upload to Supabase Storage if in Supabase mode
        if StorageManager.is_supabase_mode():
            try:
                storage_path = display_path  # Use same structure in bucket
                supabase_client = get_supabase_client()
                
                # Check if file already exists in Supabase to avoid duplicate upload
                try:
                    # Try to list files in the directory to check existence
                    dir_path = f"pdfs/{topic_safe}/{year}/{month}"
                    file_list = supabase_client.storage.from_(PAPERS_BUCKET).list(path=dir_path)
                    file_exists = any(f.get('name') == file_name for f in file_list)
                except Exception as list_error:
                    # If listing fails, assume file doesn't exist
                    logger.debug(f"  Could not check file existence: {list_error}")
                    file_exists = False
                
                if file_exists:
                    logger.info(f"  Paper {arxiv_id} already exists in Supabase Storage, skipping upload")
                    return None
                else:
                    # Upload file
                    with open(local_file_path, 'rb') as f:
                        file_content = f.read()
                    
                    supabase_client.storage.from_(PAPERS_BUCKET).upload(
                        path=storage_path,
                        file=file_content,
                        file_options={"content-type": "application/pdf"}
                    )
                    
                    storage_url = f"{PAPERS_BUCKET}/{storage_path}"
                    logger.info(f"  Uploaded to Supabase Storage: {storage_url}")
                
            except Exception as e:
                logger.error(f"  Failed to handle Supabase Storage: {e}")
                logger.warning(f"  Continuing with local path only...")
                storage_url = local_file_path
        else:
            # Local mode: storage_url is the full local path
            storage_url = local_file_path

        # Prepare metadata (consistent with download_pipeline.py and ingest_pipeline.py)
        paper_metadata = {
            "paper_id": arxiv_id,
            "title": paper_title,
            "authors": ", ".join([author.name for author in result.authors]),
            "categories": result.categories,
            "topic": topic,
            "abstract": result.summary,
            "published_date": published_date.isoformat(),
            "file_path": local_file_path,  # For ingest_pipeline to read and parse
            "display_path": display_path,   # For frontend display
            "storage_url": storage_url,     # For actual file access
            "arxiv_url": result.pdf_url,
        }
        
        return paper_metadata
    
    except Exception as e:
        logger.error(f"  Error downloading paper {arxiv_id}: {e}")
        return None

#This function is only used for once in download pipeline. We don't recusively download references.
def download_references_for_papers(
    paper_ids: List[str],
    topic: str,
    rate_limit_delay: float = REQUEST_DELAY
) -> dict:
    downloaded_papers = []
    skipped_count = 0
    all_reference_ids: Set[str] = set()
    
    logger.info(f"Processing {len(paper_ids)} papers to get their references...")
    
    # Step 1: Collect all unique reference IDs from all papers
    for paper_id in paper_ids:
        logger.info(f"\nFetching references for paper: {paper_id}")
        
        # Get references from Semantic Scholar
        arxiv_refs = get_references_from_semantic_scholar(paper_id)
        time.sleep(rate_limit_delay)  # Rate limiting
        
        if arxiv_refs:
            logger.info(f"  Found {len(arxiv_refs)} arXiv references")
            all_reference_ids.update(arxiv_refs)
        else:
            logger.info(f"  No arXiv references found")
    
    # Step 2: Download only new references (check database for duplicates)
    logger.info(f"\n{'='*60}")
    logger.info(f"Total unique references collected: {len(all_reference_ids)}")
    logger.info(f"Checking database for existing papers...")
    logger.info(f"{'='*60}\n")
    
    with Session(engine) as session:
        for ref_id in all_reference_ids:
            # Check if already in database (source of truth)
            existing_paper = session.get(Paper, ref_id)
            if existing_paper:
                logger.debug(f"  Reference {ref_id} already in database, skipping")
                skipped_count += 1
                continue
            
            # Download new reference
            logger.info(f"Downloading reference: {ref_id}")
            paper_metadata = download_paper_by_arxiv_id(ref_id, topic, session)
            
            if paper_metadata:
                downloaded_papers.append(paper_metadata)
                logger.info(f"Successfully downloaded {ref_id}")
            else:
                skipped_count += 1
    
    # Save metadata log
    if downloaded_papers:
        meta_dir = str(METADATA_DIR)
        ensure_dir(meta_dir)
        
        now = datetime.now(timezone.utc)
        meta_file = os.path.join(
            meta_dir, 
            f"references_batch_{now.strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        import json
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(downloaded_papers, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Downloaded {len(downloaded_papers)} new reference papers")
        logger.info(f"Skipped {skipped_count} papers (already in database or not found)")
        logger.info(f"Total unique references: {len(all_reference_ids)}")
        logger.info(f"Metadata saved to: {meta_file}")
        logger.info(f"{'='*60}")
    else:
        logger.info(f"\n{'='*60}")
        logger.info(f"No new papers downloaded")
        logger.info(f"Skipped {skipped_count} papers (already in database)")
        logger.info(f"Total unique references: {len(all_reference_ids)}")
        logger.info(f"{'='*60}")
    
    return {
        "downloaded": len(downloaded_papers),
        "skipped": skipped_count,
        "total_references": len(all_reference_ids),
        "papers": downloaded_papers
    }

def get_recently_downloaded_papers() -> List[str]:
    paper_ids = []
    meta_dir = str(METADATA_DIR)
    
    if not os.path.exists(meta_dir):
        return paper_ids
    
    # Get all JSON files from metadata directory
    import json
    for filename in os.listdir(meta_dir):
        if filename.endswith('.json') and not filename.startswith('references'):
            filepath = os.path.join(meta_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    papers_metadata = json.load(f)
                    for paper in papers_metadata:
                        if 'paper_id' in paper:
                            paper_ids.append(paper['paper_id'])
            except Exception as e:
                logger.debug(f"Failed to read {filename}: {e}")
    
    return paper_ids


#only used in test so far
def get_papers_from_database(topic: str, limit: Optional[int] = None) -> List[str]:
    with Session(engine) as session:
        query = select(Paper.id)
        query = query.where(Paper.topic == topic)
        if limit:
            query = query.limit(limit)
        
        results = session.exec(query).all()
        return list(results)


if __name__ == "__main__":
    # Example usage: Download references for papers in database
    logger.info("Fetching papers from database...")
    paper_ids = get_papers_from_database(topic = "minimal surface", limit=10)  # Limit to 10 papers for testing
    
    if not paper_ids:
        logger.warning("No papers found in database. Please run download_pipeline.py first.")
    else:
        logger.info(f"Found {len(paper_ids)} papers in database")
        logger.info(f"Starting reference download (no recursion)...\n")
        
        stats = download_references_for_papers(paper_ids=paper_ids, topic="minimal surface")
        
        logger.info("\n=== Final Statistics ===")
        logger.info(f"Total unique references: {stats['total_references']}")
        logger.info(f"New papers downloaded: {stats['downloaded']}")
        logger.info(f"Papers skipped: {stats['skipped']}")
