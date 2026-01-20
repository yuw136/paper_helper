import time

from server.report_pipeline.download_pipeline import download_paper_with_time_window
from server.report_pipeline.ingest_pipeline import ingest_papers
from server.report_pipeline.weekly_report_agent import generate_report
from server.report_pipeline.send_email_pipeline import send_email

from server.config import TOPIC, TIME_WINDOW_DAYS
from datetime import datetime, timedelta

from server.database import engine, create_db_and_tables

topic = TOPIC
start_date = datetime.now() - timedelta(days=TIME_WINDOW_DAYS)
end_date = datetime.now()

def run_weekly_pipeline():
    print("\n" + "="*50)
    print("🚀 WEEKLY RESEARCH AGENT PIPELINE START")
    print("="*50 + "\n")

    # Step 1: 下载
    print("\n>>> STEP 1: DOWNLOADING PAPERS")
    download_paper_with_time_window(topic)
    
    # Step 2: 入库 (耗时操作，通常包含解析和向量化)
    print("\n>>> STEP 2: INGESTING TO DATABASE")
    ingest_papers()
    
    # Step 3: 写作
    print("\n>>> STEP 3: WRITING REPORT")
    generate_report(topic, start_date, end_date)
    
    # Step 4: 发送
    print("\n>>> STEP 4: SENDING EMAIL")
    send_email()
    
    print("\n" + "="*50)
    print("✅ PIPELINE FINISHED SUCCESSFULLY")
    print("="*50 + "\n")

if __name__ == "__main__":
    create_db_and_tables()
    # 可以在这里加一个简单的计时
    start_time = time.time()
    run_weekly_pipeline()
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")