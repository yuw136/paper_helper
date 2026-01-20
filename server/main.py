import os
import arxiv
import re
from pathlib import Path
from sqlmodel import Session, select

# 关键变化：从模块导入
from server.database import engine, create_db_and_tables
from server.models import Paper
from server.parse import parse_pdf
from server.chunk import chunk_document  # pyright: ignore[reportAttributeAccessIssue]
from server.embed import save_node_to_postgres

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
PDF_STORAGE_DIR = str(SCRIPT_DIR / "data/pdfs")
MD_STORAGE_DIR = str(SCRIPT_DIR / "data/mds")

def fetch_and_store_papers(query: str, max_results: int = 5):
    """
    Fetch papers from arXiv and store them in the database and file system.
    
    Args:
        query: arXiv query string
        max_results: Maximum number of results to fetch
    """
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


def process_paper_pipeline(paper_id: str, pdf_path: str):
    """
    Complete pipeline to process a paper: parse PDF -> chunk -> embed -> store.
    
    Args:
        paper_id: The paper ID in the database
        pdf_path: Path to the PDF file
    """
    print(f"\n=== Starting pipeline for paper {paper_id} ===\n")
    
    # Step 1: Parse PDF to markdown
    print("Step 1: Parsing PDF to markdown...")
    md_output_path = os.path.join(MD_STORAGE_DIR, f"{paper_id}.md")
    md_text = parse_pdf(pdf_path)
    
    # Step 2: Chunk the markdown document
    print("\nStep 2: Chunking document...")
    nodes = chunk_document(md_text)
    
    # Step 3: Embed and save to database
    print("\nStep 3: Embedding and saving to database...")
    save_node_to_postgres(paper_id, nodes)
    
    print(f"\n=== Pipeline completed for paper {paper_id} ===\n")


if __name__ == "__main__":
    create_db_and_tables()
    
    # 示例: 获取论文
    query_str = 'au:"Costante Bellettini" AND ti:"Extensions of Schoen Simon Yau and Schoen Simon theorems via iteration"'
    fetch_and_store_papers(query=query_str, max_results=1)
    
    #示例: 处理已有的论文
    paper_id = "2310.01340v2"
    pdf_path = str(SCRIPT_DIR / f"data/pdfs/{paper_id}.pdf")
    if os.path.exists(pdf_path):
        process_paper_pipeline(paper_id, pdf_path)