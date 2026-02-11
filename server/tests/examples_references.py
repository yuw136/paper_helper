"""
Quick Start Guide for download_and_parse_references.py

示例1：为特定论文下载参考文献
====================================
"""
from report_pipeline.download_and_parse_references import (
    download_references_for_papers, 
    get_papers_from_database
)

# 单篇论文的参考文献
paper_ids = ["2601.15213"]
stats = download_references_for_papers(
    paper_ids=paper_ids,
    topic="minimal surface"
)

print(f"Downloaded: {stats['downloaded']}, Skipped: {stats['skipped']}")


# """
# 示例2：批量处理多篇论文
# ====================================
# """

# # 多篇论文
# paper_ids = ["2601.07194", "2601.15213", "2601.16783"]
# stats = download_references_for_papers(
#     paper_ids=paper_ids,
#     topic="minimal surface"
# )


"""
示例3：从数据库获取所有论文并下载参考文献
====================================
"""


# # 获取数据库中所有论文
# all_paper_ids = get_papers_from_database(topic="minimal surface")  # 不限制数量
# print(f"Found {len(all_paper_ids)} papers in database")

# # 下载所有论文的参考文献（谨慎使用，数量可能很大）
# stats = download_references_for_papers(
#     paper_ids=all_paper_ids,
#     topic="minimal surface"
# )


# """
# 示例4：限制数量测试
# ====================================
# """

# # 只获取最近的5篇论文进行测试
# test_paper_ids = get_papers_from_database(topic="minimal surface", limit=5)
# print(f"Testing with {len(test_paper_ids)} papers")

# stats = download_references_for_papers(
#     paper_ids=test_paper_ids,
#     topic="minimal surface"
# )


# """
# 示例5：增加API延迟（如果遇到限流）
# ====================================
# """

# paper_ids = get_papers_from_database(topic="minimal surface", limit=10)

# # 增加延迟到50ms（20 req/s）
# stats = download_references_for_papers(
#     paper_ids=paper_ids,
#     topic="minimal surface",
#     rate_limit_delay=0.05  # 50ms
# )


# """
# 示例6：集成到每周工作流
# ====================================
# """
# from report_pipeline.download_pipeline import download_paper_with_time_window
# from report_pipeline.ingest_pipeline import ingest_papers

# # Step 1: 下载本周的新论文
# topics = ["minimal surface", "elliptic pde"]
# for topic in topics:
#     download_paper_with_time_window(topic)

# # Step 2: 获取数据库中的论文并下载参考文献
# all_papers = get_papers_from_database(topic="minimal surface", limit=20)  # 限制数量
# stats = download_references_for_papers(
#     paper_ids=all_papers,
#     topic="minimal surface"
# )

# # Step 3: 将新下载的参考文献导入数据库
# ingest_papers()

# print(f"Workflow completed! Downloaded {stats['downloaded']} new reference papers")


"""
预期输出示例
====================================

Fetching papers from database...
Found 10 papers in database
Starting reference download (max_depth=1)...

[Depth 0] Processing paper: 2301.00234
  Fetching references from Semantic Scholar...
  Found 15 arXiv references (out of 67 total references)
  Adding 15 references to download queue...

[Depth 1] Processing paper: 2103.00020
  Fetching references from Semantic Scholar...
  Found 8 arXiv references (out of 45 total references)
  Downloading paper 2103.00020...
  Downloaded paper 2103.00020 to data/pdfs/references/2021/03
  Uploaded to Supabase Storage: papers/pdfs/references/2021/03/2103.00020v2.pdf
  ✓ Successfully downloaded 2103.00020

[Depth 1] Processing paper: 2012.12345
  Fetching references from Semantic Scholar...
  Found 12 arXiv references (out of 38 total references)
  Downloading paper 2012.12345...
  Paper 2012.12345 already exists in database, skipping...

============================================================
Downloaded 23 new papers
Skipped 5 papers (already in database or not found)
Processed 38 unique papers in total
Metadata saved to: data/metadata_logs/references_batch_20260208_143052.json
============================================================

=== Final Statistics ===
Total papers processed: 38
New papers downloaded: 23
Papers skipped: 5
"""
