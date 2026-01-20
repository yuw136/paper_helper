from pathlib import Path
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core import Document
from llama_index.core.schema import TextNode

__all__ = ["chunk_document"]

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent


def chunk_document(md_text: str, chunk_size: int = 1024, chunk_overlap: int = 200) -> list[TextNode]:
    """
    Chunk a markdown document into nodes.
    
    Args:
        md_text: Markdown text to chunk
        chunk_size: Size of each chunk in bytes (default: 1024)
        chunk_overlap: Overlap between chunks in characters (default: 200)
    
    Returns:
        list[TextNode]: List of chunked nodes
    """
    # 1. 包装成 Document 对象
    document = Document(text=md_text)

    # 2. 初始化分块器
    # 它会根据 header (#, ##, ###) 自动切分
    parser = MarkdownNodeParser()

    # 3. 执行切分：先切成按section切分的node
    base_nodes = parser.get_nodes_from_documents([document])

    # 如果node太大，分成1024字节的chunk，每两个chunk之间overlap 200字符
    text_splitter = SentenceSplitter(chunk_size=chunk_size, 
                    chunk_overlap=chunk_overlap)

    nodes = text_splitter(base_nodes)

    # 4. 检查效果
    print(f"原文档被切成了 {len(nodes)} 个节点。\n")
    
    return nodes  # type: ignore


if __name__ == "__main__":
    # 测试代码
    md_path = SCRIPT_DIR / "data/mds/2310.01340v2.Extensions_of_Schoen__Simon__Yau_and_Schoen__Simon_theorems_via_iteration_à_la_De_Giorgi.md"
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    
    nodes = chunk_document(md_text)
    
    # 打印前 3 个节点看看
    for i, node in enumerate(nodes[:10]):
        print(f"--- Node {i+1} ---")
        # node.metadata 会包含 'Header_1': 'Introduction' 这种层级信息
        print(f"Metadata: {node.metadata}") 
        print(f"Content Preview: {node.get_content()[:200]}...") # 打印前200字
        print(f"Content Preview: {node.get_content()[-200:]}...") # 打印后200字
        print("\n")