#后面再加入使用
def build_arxiv_query(keywords: list[str], categories: list[str]) -> str:
    """
    构造 Arxiv 高级查询语句
    Example: 
    keywords=["minimal surface", "harmonic map"], categories=["math.DG"]
    Returns:
    'cat:math.DG AND (all:"minimal surface" OR all:"harmonic map")'
    """
    
    # 1. 构造分类部分: (cat:math.DG OR cat:math.AP)
    cat_part = " OR ".join([f"cat:{c}" for c in categories])
    if len(categories) > 1:
        cat_part = f"({cat_part})"
        
    # 2. 构造关键词部分: (all:"keyword1" OR all:"keyword2")
    # 包含任意一个关键词即可。如果需要都包含，用 AND。
    kw_part = " OR ".join([f'all:"{k}"' for k in keywords])
    if len(keywords) > 1:
        kw_part = f"({kw_part})"
    
    # 3. 组合
    if cat_part and kw_part:
        return f"{cat_part} AND {kw_part}"
    elif cat_part:
        return cat_part
    else:
        return kw_part

# 使用示例
if __name__ == "__main__":
    # 比如我想看 微分几何(DG) 或 分析(AP) 下，关于 极小曲面 或 调和映照 的文章
    complex_query = build_arxiv_query(
        keywords=["minimal surface", "harmonic map"],
        categories=["math.DG", "math.AP"]
    )
    print(f"生成的查询: {complex_query}")
    
    # 传入之前的下载函数
    # create_db_and_tables()
    # fetch_and_store_papers(query=complex_query)