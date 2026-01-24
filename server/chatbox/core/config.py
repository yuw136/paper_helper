import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from project root (two levels up from this file)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

#================== settings ==================
class Settings(BaseSettings):
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite 
        "http://localhost:3000",
    ]
    
    # Database configuration (从 .env 读取)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    
    # API Keys (从 .env 读取)
    LLAMA_CLOUD_API_KEY: str
    OPENAI_API_KEY: str
    DEEPSEEK_API_KEY: str
    
    # LangChain/LangGraph settings (从 .env 读取)
    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent.parent / ".env"),
        extra="ignore"
    )

settings = Settings()  # type: ignore[call-arg]

#chat session persistence settings (use same PostgreSQL database as Paper/PaperChunk)
# Import from database.py to ensure same connection string
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database import DATABASE_URL
DB_CONNECTION_STRING = DATABASE_URL

# ================== model configuration ==================

# Chat model (for writing and report generation)
CHAT_MODEL_NAME = os.getenv("CHAT_MODEL_NAME", "gpt-4o")
CHAT_MODEL_TEMPERATURE = float(os.getenv("CHAT_MODEL_TEMPERATURE", "0.2"))

# Mini model (for agent_graph)
MINI_MODEL_NAME = os.getenv("MINI_MODEL_NAME", "gpt-4o-mini")
MINI_MODEL_TEMPERATURE = float(os.getenv("MINI_MODEL_TEMPERATURE", "0"))


# ================== model instances (singleton) ==================
_write_model = None
_llm_model = None

def get_write_model():
    global _write_model
    if _write_model is None:
        _write_model = ChatOpenAI(model=CHAT_MODEL_NAME, temperature=CHAT_MODEL_TEMPERATURE)  # type: ignore
    return _write_model

def get_llm_model():
    global _llm_model
    if _llm_model is None:
        _llm_model = ChatOpenAI(model=MINI_MODEL_NAME, temperature=MINI_MODEL_TEMPERATURE)  # type: ignore
    return _llm_model
