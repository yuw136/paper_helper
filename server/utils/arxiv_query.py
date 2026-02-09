import time
import re
import logging
from typing import List

import arxiv

logger = logging.getLogger(__name__)

def remove_arxiv_version(paper_id):
    #change id "2301.00234v1" to "2301.00234"
    return re.sub(r'v\d+$', '', paper_id)

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

def search_arxiv_by_titles(titles: List[str], max_results_per_title: int = 1) -> List[str]:
    REQUEST_DELAY = 0.02  # 20ms delay to respect rate limit 
    arxiv_ids = []
    client = arxiv.Client()
    
    for title in titles:
        try:
            # Search arXiv by title
            search = arxiv.Search(
                query=f'ti:"{title}"',  # Search in title field
                max_results=max_results_per_title,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = list(client.results(search))
            if results:
                # Use the most relevant result
                paper = results[0]
                arxiv_id = paper.get_short_id()
                
                # Simple title similarity check (to avoid false matches)
                if _titles_similar(title, paper.title):
                    arxiv_ids.append(arxiv_id)
                    
            time.sleep(REQUEST_DELAY)  # Rate limiting
            
        except Exception as e:
            logger.info(f"    Failed to search arXiv for '{title[:50]}...': {e}")
            continue
    
    return arxiv_ids


def _titles_similar(title1: str, title2: str, threshold: float = 0.7) -> bool:
    # Convert to lowercase and split into words
    words1 = set(title1.lower().split())
    words2 = set(title2.lower().split())
    
    # Remove common stop words
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'of', 'for', 'to', 'and', 'or', 'with'}
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    if not words1 or not words2:
        return False
    
    # Calculate Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    similarity = intersection / union if union > 0 else 0
    
    return similarity >= threshold


