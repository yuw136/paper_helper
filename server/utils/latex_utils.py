import re

def clean_latex_output(content: str) -> str:
    r"""
    Clean AI-generated LaTeX output by removing:
    1. Markdown code block markers (```latex, ```)
    2. Document structure commands (\documentclass, \begin{document}, \end{document}, etc.)
    3. Preamble commands (\usepackage, \geometry, etc.)
    """
    # Remove markdown code block markers
    content = re.sub(r'```latex\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    
    # Remove \documentclass line
    content = re.sub(r'\\documentclass\{[^}]*\}', '', content)
    
    # Remove \usepackage lines
    content = re.sub(r'\\usepackage(\[[^\]]*\])?\{[^}]*\}', '', content)
    
    # Remove \geometry lines
    content = re.sub(r'\\geometry\{[^}]*\}', '', content)
    
    # Remove \title, \author, \date lines
    content = re.sub(r'\\title\{[^}]*\}', '', content)
    content = re.sub(r'\\author\{[^}]*\}', '', content)
    content = re.sub(r'\\date\{[^}]*\}', '', content)
    
    # Remove \begin{document} and \end{document}
    content = re.sub(r'\\begin\{document\}', '', content)
    content = re.sub(r'\\end\{document\}', '', content)
    
    # Remove \maketitle
    content = re.sub(r'\\maketitle', '', content)
    
    # Remove \section* lines (summary sections from nested documents)
    content = re.sub(r'\\section\*\{Summary\}', '', content)
    
    # Clean up excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    
    return content.strip()


def escape_latex_text(text: str) -> str:
    """
    Escape special LaTeX characters in plain text (no math mode).
    Use this ONLY for author names and other guaranteed plain text.
    """
    if not text:
        return text
    
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text


def escape_latex_preserve_math(text: str) -> str:
    """
    Escape special LaTeX characters, but preserve math mode content ($...$).
    Use this for titles, abstracts, and AI summaries that may contain LaTeX math.
    """
    if not text:
        return text
    
    # Find all math mode regions
    math_regions = []
    # Use a placeholder that won't have special characters that get escaped
    placeholder_template = "XXXMATHPLACEHOLDERXXX{}"
    
    # Match $...$ (inline) and $$...$$ (display)
    # Handles nested braces and escaped dollars
    math_pattern = r'(?<!\\)\$\$[^\$]+?\$\$|(?<!\\)\$[^\$]+?\$'
    
    def save_math(match):
        math_regions.append(match.group(0))
        return placeholder_template.format(len(math_regions) - 1)
    
    # Replace math with placeholders
    text_with_placeholders = re.sub(math_pattern, save_math, text)
    
    # Escape special characters in non-math text
    # NOTE: Don't escape backslash for LaTeX commands, only for text
    # We need to be careful here - if backslash is already LaTeX, don't escape it
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '_': r' ',  # Replace underscores with spaces for better readability
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    
    escaped_text = text_with_placeholders
    for char, replacement in replacements.items():
        escaped_text = escaped_text.replace(char, replacement)
    
    # Restore math regions
    for i, math_content in enumerate(math_regions):
        escaped_text = escaped_text.replace(
            placeholder_template.format(i), 
            math_content
        )
    
    return escaped_text