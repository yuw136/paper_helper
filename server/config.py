import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from langchain_openai import ChatOpenAI

load_dotenv()

# get project root directory (now we're in server/, so go up one level)
BASE_DIR = Path(__file__).parent.parent

# ================== path configuration ==================
SERVER_DIR = BASE_DIR / "server"
DATA_DIR = SERVER_DIR / "data"
REPORT_DIR = DATA_DIR / "weekly_reports"
PDF_DIR = DATA_DIR / "pdfs"
MD_DIR = DATA_DIR / "mds"
UPLOADS_DIR = DATA_DIR / "uploads"
METADATA_DIR = DATA_DIR / "metadata_logs"
ARCHIVED_DIR = METADATA_DIR / "archived"

# ensure directories exist
REPORT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)

# ================== pipeline configuration ==================
# ArXiv download settings
TARGET_CATEGORIES =  ["math.DG", "math.AP", "math-ph"]
TOPIC = "minimal surface"
MAX_RESULTS =10
TIME_WINDOW_DAYS = 14
TIME_WINDOW = timedelta(days=TIME_WINDOW_DAYS)

# Document chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# ================== model configuration ==================
# Embedding model
_embed_model = None

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = OpenAIEmbedding(model_name=EMBEDDING_MODEL_NAME)
    return _embed_model