import time

from report_pipeline.download_pipeline import download_paper_with_time_window
from report_pipeline.ingest_pipeline import ingest_papers
from report_pipeline.weekly_report_agent import generate_report
from report_pipeline.send_email_pipeline import send_email

from config import TOPIC, TIME_WINDOW_DAYS
from datetime import datetime, timedelta

from database import engine, create_db_and_tables

start_date = datetime.now() - timedelta(days=TIME_WINDOW_DAYS)
end_date = datetime.now()

def run_weekly_pipeline():
    print("\n" + "="*50)
    print("🚀 WEEKLY RESEARCH AGENT PIPELINE START")
    print("="*50 + "\n")

    # Step 1: Download
    print("\n>>> STEP 1: DOWNLOADING PAPERS")
    download_paper_with_time_window(TOPIC)
    
    # Step 2: Ingest to database (time-consuming operation, usually includes parsing and vectorization)
    print("\n>>> STEP 2: INGESTING TO DATABASE")
    ingest_papers()
    
    # Step 3: Writing
    print("\n>>> STEP 3: WRITING REPORT")
    generate_report(TOPIC, start_date, end_date)
    
    # Step 4: Send email
    print("\n>>> STEP 4: SENDING EMAIL")
    send_email(TOPIC)
    
    print("\n" + "="*50)
    print("✅ PIPELINE FINISHED SUCCESSFULLY")
    print("="*50 + "\n")

if __name__ == "__main__":
    create_db_and_tables()
    # Can add simple timing here
    start_time = time.time()
    run_weekly_pipeline()
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")