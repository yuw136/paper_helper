def build_arxiv_query(keywords: list[str], categories: list[str]) -> str:
    """
    Example: 
    keywords=["minimal surface", "harmonic map"], categories=["math.DG"]
    Returns:
    'cat:math.DG AND (all:"minimal surface" OR all:"harmonic map")'
    """

    #construct category part
    cat_part = " OR ".join([f"cat:{c}" for c in categories])
    if len(categories) > 1:
        cat_part = f"({cat_part})"
        
    #construct keyword part
    kw_part = " OR ".join([f'all:"{k}"' for k in keywords])
    if len(keywords) > 1:
        kw_part = f"({kw_part})"
    
    #combine category and keyword part
    if cat_part and kw_part:
        return f"{cat_part} AND {kw_part}"
    elif cat_part:
        return cat_part
    else:
        return kw_part

