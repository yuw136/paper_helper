import os
import arxiv
import json
from datetime import datetime, timezone

from server.config import TARGET_CATEGORIES, PDF_DIR, MAX_RESULTS, TIME_WINDOW, METADATA_DIR

DOWNLOAD_ROOT = str(PDF_DIR)

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_storage_path(topic:str, date:datetime):
    """
    format path: data/pdfs/topic/year/month
    """
    year = date.strftime("%Y")
    month = date.strftime("%m")
    return os.path.join(DOWNLOAD_ROOT, topic, year, month)

def download_paper_with_time_window(topic):
    """
    download papers within the time window
    """
    now = datetime.now(timezone.utc)
    start_date = now - TIME_WINDOW
    papers_metadata = []
    
    #build search query
    cat_query = " OR ".join([f"cat:{cat}" for cat in TARGET_CATEGORIES])
    if len(TARGET_CATEGORIES) > 1:
        cat_query = f"({cat_query})"
    query = f'({cat_query}) AND (all:"{topic}")' if topic else cat_query
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
    for result in client.results(search):
        published_date = result.published
        paper_id = result.get_short_id()
        paper_title = result._get_default_filename()

        if published_date < start_date:
            break
    
        #make dir
        save_dir = get_storage_path(topic, published_date)
        ensure_dir(save_dir)

        #file name:paper_id+paper_title.pdf
        file_name = f"{paper_id}_{paper_title}.pdf"
        file_path = os.path.join(save_dir, file_name)

        #download
        if not os.path.exists(file_path):
            result.download_pdf(file_path)
        else:
            print(f"Paper {paper_id} already exists in {file_path}, skipping...")
        
        #pass to agent to summarize and generate document
        papers_metadata.append({
            "paper_id": paper_id,
            "title": paper_title,
            "authors": result.authors,
            "categories": result.categories,
            "topic": topic,
            "abstract": result.summary,
            "published_date": published_date,
            "file_path": file_path,
            "arxiv_url": result.pdf_url,
        })
        
        downloaded_count += 1

    #maintain a metadata log, for ingestion pipeline to work on
    if papers_metadata:
        meta_dir = str(METADATA_DIR)
        ensure_dir(meta_dir)
        meta_file = os.path.join(meta_dir, f"weekly_batch_{now.strftime('%Y%m%d')}.json")

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(papers_metadata, f, indent=2, ensure_ascii=False)
            
        print(f"Downloaded {downloaded_count} papers and saved metadata to {meta_file}")
    else:
        print("No papers found within the time window")
    
    return papers_metadata


if __name__ == "__main__":
    download_paper_with_time_window("minimal surface")