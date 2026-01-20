import os
import dotenv
import nest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from llama_parse import LlamaParse, ResultType
from llama_index.core import SimpleDirectoryReader
from llama_index.core.readers.base import BaseReader

load_dotenv()

# 这行在测试中没用，但在jupyter notebook或fastapi中由于需要先开启一个
# 事件循环，所以需要做异步嵌套，所以需要这个
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
    # 1. 配置解析器
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

    # 2. 检查文件是否存在
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"can't find file: {pdf_path}")
    
    print("sent to LlamaParse 处理 (需要几秒钟)...")

    # 使用 file_extractor 将 parser 挂载到 SimpleDirectoryReader
    file_extractor: dict[str, BaseReader] = {".pdf": parser}

    # 3. 读取并解析
    documents = SimpleDirectoryReader(
        input_files=[pdf_path], file_extractor=file_extractor
    ).load_data()

    # 4. 查看结果
    print(f"\n--- 解析完成! 共有 {len(documents)} 个文档对象 ---")

    # # 查看每个文档的信息:llama parser会分成几个文档返回
    # for i, doc in enumerate(documents):
    #     print(f"文档 {i+1}: {len(doc.text)} 字符")
    #     # 如果有元数据，也可以打印
    #     if doc.metadata:
    #         print(f"  元数据: {doc.metadata}")

    # 合并所有文档的文本
    full_text = "\n\n".join([doc.text for doc in documents])

    print(f"\n总字符数: {len(full_text)}")
    print("\n--- 预览前 500 个字符 ---")
    print(full_text[:500])

    # 5. 保存
    output_path = pdf_path.replace(".pdf", ".md").replace("pdfs", "mds")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"\n✓ Markdown saved to: {output_path}")
    
    return full_text


if __name__ == "__main__":
    # 测试代码
    pdf_path = str(SCRIPT_DIR / "data/pdfs/2310.01340v2.Extensions_of_Schoen__Simon__Yau_and_Schoen__Simon_theorems_via_iteration_à_la_De_Giorgi.pdf")
    parse_pdf(pdf_path)
