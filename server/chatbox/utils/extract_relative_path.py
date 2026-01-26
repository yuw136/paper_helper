
def extract_relative_path(full_path: str, base_dir: str = "data") -> str:
    """get relative path from full path starting from base_dir"""
    if not full_path:
        return full_path
    
    # normalize path separator
    normalized_path = full_path.replace('\\', '/')
    
    if base_dir in normalized_path:
        # find the position of base_dir
        index = normalized_path.find(base_dir) + len(base_dir)
        return normalized_path[index:].strip("/")
    
    # if not found, return empty string
    return "" 
