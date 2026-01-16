import os
import arxiv
import re
from sqlmodel import Session, select

# 关键变化：从模块导入
from database import engine, create_db_and_tables
from models import Paper  

PDF_STORAGE_DIR = "./data/pdfs"
def fetch_and_store_papers(query: str, max_results: int = 5):
    client = arxiv.Client()
    search = arxiv.Search(
        query= query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    #log 
    print(f"searching for query:{query} ...")
    with Session(engine) as session:
        for result in client.results(search):
            
            #验证数据库中是否已存在
            paper_id = result.get_short_id()
            exist_paper = session.get(Paper,paper_id)
            if exist_paper:
                print(f"paper with id {paper_id} already exists")
                continue

            #文件名和路径
            paper_title = result._get_default_filename()
            file_path = os.path.join(PDF_STORAGE_DIR, paper_title)

            try:
                #下载
                result.download_pdf(dirpath=PDF_STORAGE_DIR, filename=paper_title)
                print(f"download successful for paper id {paper_id}")

                #存数据
                new_paper = Paper(
                    id=paper_id,
                    title=result.title,
                    authors=", ".join([a.name for a in result.authors]),
                    published_date=result.published,
                    category=result.primary_category,
                    local_pdf_path=file_path,
                    abstract=result.summary
                )
                session.add(new_paper)
                session.commit()
            except Exception as e:
                print(f"failed to download or store: {e}")


if __name__ == "__main__":
    create_db_and_tables()
    query_str = 'cat:math.DG AND all:"minimal surface"'
    fetch_and_store_papers(query=query_str)