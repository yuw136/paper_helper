from pathlib import Path
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core import Document
from llama_index.core.schema import TextNode

__all__ = ["chunk_document"]

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent


def chunk_document(md_text: str, chunk_size: int = 1024, chunk_overlap: int = 200) -> list[TextNode]:
  
    # 1. Wrap into Document object
    document = Document(text=md_text)

    # 2. Initialize chunker
    # It will automatically split based on headers (#, ##, ###)
    parser = MarkdownNodeParser()

    # 3. Execute splitting: first split into nodes by section
    base_nodes = parser.get_nodes_from_documents([document])

    # If node is too large, split into 1024-byte chunks with 200 character overlap between chunks
    text_splitter = SentenceSplitter(chunk_size=chunk_size, 
                    chunk_overlap=chunk_overlap)

    nodes = text_splitter(base_nodes)

    # 4. Check results
    print(f"Original document was split into {len(nodes)} nodes.\n")
    
    return nodes  # type: ignore


