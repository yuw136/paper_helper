
def extract_relative_path(full_path: str, base_dir: str = "data") -> str:
    """
    Get relative path from full path starting from base_dir.
    
    For local mode (full paths like "D:/project/server/data/pdfs/topic/file.pdf"):
        - Extracts path after base_dir: "pdfs/topic/file.pdf"
    
    For Supabase mode (already relative paths like "pdfs/uploads/file.pdf"):
        - Returns the path as-is since it's already relative
    """
    if not full_path:
        return full_path
    
    # normalize path separator
    normalized_path = full_path.replace('\\', '/')
    
    if base_dir in normalized_path:
        # Local mode: extract path after base_dir
        index = normalized_path.find(base_dir) + len(base_dir)
        return normalized_path[index:].strip("/")
    
    # Supabase mode or already relative: return as-is
    return normalized_path.strip("/")
