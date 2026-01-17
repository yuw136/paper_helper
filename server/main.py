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
            
            # 获取paper信息
            paper_id = result.get_short_id()
            paper_title = result._get_default_filename()
            file_path = os.path.join(PDF_STORAGE_DIR, paper_title)
            
            # 检查数据库和文件系统
            exist_in_db = session.get(Paper, paper_id)
            exist_in_fs = os.path.exists(file_path)
            
            # 情况1: 数据库和文件系统都存在
            if exist_in_db and exist_in_fs:
                print(f"paper {paper_id} already exists in both database and file system, skipping...")
                continue
            
            # 情况2: 数据库存在但文件不存在 - 重新下载文件
            elif exist_in_db and not exist_in_fs:
                print(f"paper {paper_id} exists in database but not in file system, re-downloading...")
                try:
                    result.download_pdf(dirpath=PDF_STORAGE_DIR, filename=paper_title)
                    print(f"re-download successful for paper id {paper_id}")
                except Exception as e:
                    print(f"failed to re-download: {e}")
                continue
            
            # 情况3: 文件存在但数据库不存在 - 添加到数据库
            elif not exist_in_db and exist_in_fs:
                print(f"paper {paper_id} already exists in file system, adding to database...")
                try:
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
                    print(f"successfully added paper {paper_id} to database")
                except Exception as e:
                    print(f"failed to add to database: {e}")
                continue
            
            # 情况4: 都不存在 - 下载并添加到数据库
            else:
                print(f"paper {paper_id} is new, downloading and adding to database...")
                try:
                    # 下载文件
                    result.download_pdf(dirpath=PDF_STORAGE_DIR, filename=paper_title)
                    print(f"download successful for paper id {paper_id}")
                    
                    # 添加到数据库
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
                    print(f"successfully saved paper {paper_id}")
                except Exception as e:
                    print(f"failed to download or store: {e}")


if __name__ == "__main__":
    create_db_and_tables()
    query_str = 'au:"Costante Bellettini" AND ti:"Extensions of Schoen Simon Yau and Schoen Simon theorems via iteration"'
    fetch_and_store_papers(query=query_str, max_results=1)