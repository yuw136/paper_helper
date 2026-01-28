import os
import dotenv
import nest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from llama_parse import LlamaParse, ResultType
from llama_index.core import SimpleDirectoryReader
from llama_index.core.readers.base import BaseReader

load_dotenv()

# This line is not needed in tests, but in jupyter notebook or fastapi,
# since an event loop needs to be started first, async nesting is required, so this is needed
nest_asyncio.apply()

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

__all__ = ["parse_pdf"]


def parse_pdf(pdf_path: str) -> str:
    """
    Parse a PDF file using LlamaParse and return the markdown text.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        str: The parsed markdown text
    """
    # 1. Configure parser
    parsing_instruction = "The document contains complex mathematical formulas and theorems. Please strictly preserve all mathematical formatting. Output all math equations in LaTeX format, wrapping inline math in $...$ and display math in $$...$$. Ensure superscripts (like R^n) and subscripts are correctly formatted."
    parser = LlamaParse(
        result_type=ResultType.MD,
        
        # The parsing mode
        parse_mode="parse_page_with_agent",

        # The model to use (rather cheap, looks good)
        model="openai-gpt-4-1-mini",

        # Whether to output tables as HTML in the markdown output
        output_tables_as_HTML=True,

        # append to system prompt
        system_prompt_append="The document contains complex mathematical formulas and theorems. Please strictly preserve all mathematical formatting. Output all math equations in LaTeX format, wrapping inline math in $...$ and display math in $$...$$. Ensure superscripts (like R^n) and subscripts are correctly formatted.\"",

        # page separator
        page_separator="\n\n---\n\n",

        language="en"    
    )

    # 2. Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"can't find file: {pdf_path}")
    
    print("Sent to LlamaParse for processing (will take a few seconds)...")

    # Use file_extractor to mount parser to SimpleDirectoryReader
    file_extractor: dict[str, BaseReader] = {".pdf": parser}

    # 3. Read and parse
    documents = SimpleDirectoryReader(
        input_files=[pdf_path], file_extractor=file_extractor
    ).load_data()

    # 4. View results
    print(f"\n--- Parsing completed! Total {len(documents)} document objects ---")

    # Merge text from all documents
    full_text = "\n\n".join([doc.text for doc in documents])

    print(f"\nTotal characters: {len(full_text)}")
    print("\n--- Preview first 500 characters ---")
    print(full_text[:500])

    # 5. Save
    output_path = pdf_path.replace(".pdf", ".md").replace("pdfs", "mds")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"\n✓ Markdown saved to: {output_path}")
    
    return full_text


