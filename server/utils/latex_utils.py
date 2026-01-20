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
