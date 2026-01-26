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
    Also converts Unicode Greek letters to LaTeX commands (both inside and outside math mode).
    """
    if not text:
        return text
    
    # Greek letter mapping
    greek_letters = {
        'Α': r'\Alpha', 'Β': r'\Beta', 'Γ': r'\Gamma', 'Δ': r'\Delta',
        'Ε': r'\Epsilon', 'Ζ': r'\Zeta', 'Η': r'\Eta', 'Θ': r'\Theta',
        'Ι': r'\Iota', 'Κ': r'\Kappa', 'Λ': r'\Lambda', 'Μ': r'\Mu',
        'Ν': r'\Nu', 'Ξ': r'\Xi', 'Ο': r'\Omicron', 'Π': r'\Pi',
        'Ρ': r'\Rho', 'Σ': r'\Sigma', 'Τ': r'\Tau', 'Υ': r'\Upsilon',
        'Φ': r'\Phi', 'Χ': r'\Chi', 'Ψ': r'\Psi', 'Ω': r'\Omega',
        'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
        'ε': r'\epsilon', 'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta',
        'ι': r'\iota', 'κ': r'\kappa', 'λ': r'\lambda', 'μ': r'\mu',
        'ν': r'\nu', 'ξ': r'\xi', 'ο': r'\omicron', 'π': r'\pi',
        'ρ': r'\rho', 'ς': r'\varsigma', 'σ': r'\sigma', 'τ': r'\tau',
        'υ': r'\upsilon', 'φ': r'\phi', 'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega'
    }
    
    # Find all math mode regions
    math_regions = []
    # Use a placeholder that won't have special characters that get escaped
    placeholder_template = "XXXMATHPLACEHOLDERXXX{}"
    
    # Match $...$ (inline) and $$...$$ (display)
    # Handles nested braces and escaped dollars
    math_pattern = r'(?<!\\)\$\$[^\$]+?\$\$|(?<!\\)\$[^\$]+?\$'
    
    def save_math(match):
        # Convert Greek letters inside math mode as well
        math_content = match.group(0)
        for unicode_char, latex_cmd in greek_letters.items():
            math_content = math_content.replace(unicode_char, latex_cmd)
        math_regions.append(math_content)
        return placeholder_template.format(len(math_regions) - 1)
    
    # Replace math with placeholders (and convert Greek letters inside)
    text_with_placeholders = re.sub(math_pattern, save_math, text)
    
    # Convert Unicode Greek letters outside math mode too
    for unicode_char, latex_cmd in greek_letters.items():
        text_with_placeholders = text_with_placeholders.replace(unicode_char, latex_cmd)
    
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
    
    # Restore math regions (already with Greek letters converted)
    for i, math_content in enumerate(math_regions):
        escaped_text = escaped_text.replace(
            placeholder_template.format(i), 
            math_content
        )
    
    return escaped_text