import os
import arxiv
import json
from datetime import datetime, timezone

from sqlmodel import Session, select
from database import engine, USE_SUPABASE
from models import Paper
from config import TARGET_CATEGORIES, PDF_DIR, MAX_RESULTS, TIME_WINDOW, METADATA_DIR
from utils import ensure_dir
from utils.arxiv_query import remove_arxiv_version

DOWNLOAD_ROOT = str(PDF_DIR)

def get_storage_path(topic:str, date:datetime):
    topic_safe = topic.replace(' ', '_')
    year = date.strftime("%Y")
    month = date.strftime("%m")
    return os.path.join(DOWNLOAD_ROOT, topic_safe, year, month)

def download_paper_with_time_window(topic):
    now = datetime.now(timezone.utc)
    start_date = now - TIME_WINDOW
    papers_metadata = []
    
    #build search query
    cat_query = " OR ".join([f"cat:{cat}" for cat in TARGET_CATEGORIES])
    if len(TARGET_CATEGORIES) > 1:
        cat_query = f"({cat_query})"
    query = f'{cat_query} AND (all:"{topic}")' if topic else cat_query
    print(f"Downloading papers with query: {query}")

    client = arxiv.Client()
    #search papers
    search = arxiv.Search(
        query=query,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    #download
    downloaded_count = 0
    with Session(engine) as session:
        for result in client.results(search):
            published_date = result.published
            paper_id = remove_arxiv_version(result.get_short_id())
            paper_title = result.title

            if published_date < start_date:
                break
            
            # Check if paper already exists in database (works for both local and Supabase)
            existing_paper = session.get(Paper, paper_id)
            if existing_paper:
                print(f"Paper {paper_id} already exists in database, skipping...")
                continue
        
            #make dir
            save_dir = get_storage_path(topic, published_date)
            ensure_dir(save_dir)

            #file name:default filename
            file_name = result._get_default_filename()  
            file_path = os.path.join(save_dir, file_name)

            #download
            # In Supabase mode: always download (database is source of truth)
            # In local mode: check local file to avoid re-downloading
            if USE_SUPABASE or not os.path.exists(file_path):
                result.download_pdf(save_dir)
                print(f"Downloaded paper {paper_id} to {save_dir}")
            else:
                print(f"Paper {paper_id} already exists locally at {save_dir}")
            
            #pass to agent to summarize and generate document
            papers_metadata.append({
                "paper_id": paper_id,
                "title": paper_title,
                "authors": ", ".join([author.name for author in result.authors]),
                "categories": result.categories,
                "topic": topic,
                "abstract": result.summary,
                "published_date": published_date.isoformat(),
                "file_path": file_path,
                "arxiv_url": result.pdf_url,
            })
            
            downloaded_count += 1

    #maintain a metadata log, for ingestion pipeline to work on
    if papers_metadata:
        meta_dir = str(METADATA_DIR)
        ensure_dir(meta_dir)
        topic_safe = topic.replace(' ', '_')
        meta_file = os.path.join(meta_dir, f"weekly_batch_{now.strftime('%Y%m%d')}_{topic_safe}.json")

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(papers_metadata, f, indent=2, ensure_ascii=False)
            
        print(f"Downloaded {downloaded_count} papers and saved metadata to {meta_file}")
    else:
        print("No papers found within the time window")
    
    return papers_metadata


if __name__ == "__main__":
    download_paper_with_time_window("minimal surface")