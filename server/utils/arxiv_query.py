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

def search_arxiv_by_titles(titles: List[str], max_results_per_title: int = 3) -> List[str]:
    REQUEST_DELAY = 0.02
    arxiv_ids = []
    client = arxiv.Client()
    
    for title in titles:
        try:
            normalized_title = _normalize_title(title)
            
            # 1.try exact title search
            search = arxiv.Search(
                query=f'ti:"{normalized_title}"',
                max_results=max_results_per_title,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = list(client.results(search))
            
            # 2. if exact search failed, try keyword search
            if not results:
                logger.info(f"    Exact title search failed, trying keyword search...")
                search = arxiv.Search(
                    query=f'all:"{normalized_title}"',
                    max_results=max_results_per_title,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                results = list(client.results(search))
            
            if results:
                # find the most similar result
                best_match = None
                best_similarity = 0
                
                for paper in results:
                    similarity = _title_similarity_score(title, paper.title)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = paper
                
                # only accept results with high similarity (avoid mis-matching)
                if best_match and best_similarity >= 0.8:
                    arxiv_ids.append(best_match.get_short_id())
                    logger.info(f"    Found match with similarity {best_similarity:.2f}")
                else:
                    logger.info(f"    No good match found (best similarity: {best_similarity:.2f})")
                    
            time.sleep(REQUEST_DELAY)
            
        except Exception as e:
            logger.info(f"    Failed to search arXiv for '{title[:50]}...': {e}")
            continue
    
    return arxiv_ids


def _normalize_title(title: str) -> str:
    """标准化标题以提高匹配率"""
    import unicodedata
    
    # change the title to NFKD standard form (handle various unicode variations)
    title = unicodedata.normalize('NFKD', title)
    
    # replace common punctuation variations
    replacements = {
        '–': '-',  # en-dash to hyphen
        '—': '-',  # em-dash to hyphen
        ''': "'", 
        ''': "'",
        '"': '"',  # smart double quote
        '"': '"',
        '…': '...',
    }
    for old, new in replacements.items():
        title = title.replace(old, new)
    
    # remove extra spaces
    title = ' '.join(title.split())
    
    return title


def _title_similarity_score(title1: str, title2: str) -> float:
    """calculate the similarity score between two titles (0-1)"""
    t1 = _normalize_title(title1.lower())
    t2 = _normalize_title(title2.lower())
    
    if t1 == t2:
        return 1.0
    
    words1 = set(t1.split())
    words2 = set(t2.split())
    
    # remove stop words
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'of', 'for', 'to', 'and', 'or', 'with'}
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0.0 else 0.0