from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core import Document

# 为了测试，你可以手动复制一段含 LaTeX 的 Markdown 进去，或者读取之前保存的 .md 文件
with open("./data/mds/iteration_for_schoen_simon.md", "r", encoding="utf-8") as f:
    md_text = f.read()

# 1. 包装成 Document 对象
document = Document(text=md_text)

# 2. 初始化分块器
# 它会根据 header (#, ##, ###) 自动切分
parser = MarkdownNodeParser()

# 3. 执行切分：先切成按section切分的node
base_nodes = parser.get_nodes_from_documents([document])

#如果node太大，分成1024字节的chunk，每两个chunk之间overlap 200字符
text_splitter = SentenceSplitter(chunk_size=1024, 
                chunk_overlap=200)

nodes = text_splitter(base_nodes)

# 4. 检查效果
print(f"原文档被切成了 {len(nodes)} 个节点。\n")

# 打印前 3 个节点看看
for i, node in enumerate(nodes[:10]):
    print(f"--- Node {i+1} ---")
    # node.metadata 会包含 'Header_1': 'Introduction' 这种层级信息，非常有用！
    print(f"Metadata: {node.metadata}") 
    print(f"Content Preview: {node.get_content()[:200]}...") # 打印前200字
    print(f"Content Preview: {node.get_content()[-200:]}...") # 打印后200字
    print("\n")