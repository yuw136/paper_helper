import time
import logging

from report_pipeline.download_pipeline import download_paper_with_time_window
from report_pipeline.download_and_parse_references import (
    download_references_for_papers,
    get_recently_downloaded_papers
)
from report_pipeline.ingest_pipeline import ingest_papers
from report_pipeline.weekly_report_agent import generate_report
from report_pipeline.send_email_pipeline import send_email

from config import TOPICS, TIME_WINDOW_DAYS
from datetime import datetime, timedelta

from database import engine, create_db_and_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

start_date = datetime.now() - timedelta(days=TIME_WINDOW_DAYS)
end_date = datetime.now()

def run_weekly_pipeline():
    logger.info("\n" + "="*50)
    logger.info("WEEKLY RESEARCH AGENT PIPELINE START")
    logger.info("="*50 + "\n")

    # Step 1: Download main papers
    logger.info("\n>>> STEP 1: DOWNLOADING PAPERS AND THEIR REFERENCES")
    for topic in TOPICS:
        papers_metadata = download_paper_with_time_window(topic)
        paper_ids = [paper_metadata["paper_id"] for paper_metadata in papers_metadata]
        download_references_for_papers(paper_ids, topic)
        
    # Step 3: Ingest all papers to database
    logger.info("\n>>> STEP 3: INGESTING TO DATABASE")
    ingest_papers()
    
    # Step 4: Generate reports
    logger.info("\n>>> STEP 4: WRITING REPORT")
    for topic in TOPICS:
        generate_report(topic, start_date, end_date)
    
    # Step 5: Send email
    logger.info("\n>>> STEP 5: SENDING EMAIL")
    for topic in TOPICS:
        send_email(topic)
    
    logger.info("\n" + "="*50)
    logger.info("✅ PIPELINE FINISHED SUCCESSFULLY")
    logger.info("="*50 + "\n")

if __name__ == "__main__":
    create_db_and_tables()
    # Can add simple timing here
    start_time = time.time()
    run_weekly_pipeline()
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")