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
    # CORS settings - can be overridden by BACKEND_CORS_ORIGINS in .env
    # Format in .env: BACKEND_CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Database configuration (read from .env)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    LOCAL_DATABASE_URL: str
    SUPABASE_DATABASE_URL: str
    
    # API Keys (read from .env)
    LLAMA_CLOUD_API_KEY: str
    OPENAI_API_KEY: str
    # DEEPSEEK_API_KEY: str
    
    # LangChain/LangGraph settings (read from .env)
    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent.parent / ".env"),
        extra="ignore"
    )

settings = Settings()  # type: ignore[call-arg]

# Parse CORS origins from comma-separated string to list
def get_cors_origins() -> list[str]:
    """Parse BACKEND_CORS_ORIGINS from settings into a list"""
    origins = settings.BACKEND_CORS_ORIGINS
    if isinstance(origins, str):
        return [origin.strip() for origin in origins.split(",") if origin.strip()]
    return origins

#chat session persistence settings (use same PostgreSQL database as Paper/PaperChunk)
# Import from database.py to ensure same connection string
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from database import DATABASE_URL
DB_CONNECTION_STRING = DATABASE_URL

# ================== model configuration ==================

# Writing model (for text generation, summarization, answer formatting)
WRITING_MODEL_NAME = os.getenv("WRITING_MODEL_NAME", "gpt-4o")
WRITING_MODEL_TEMPERATURE = float(os.getenv("WRITING_MODEL_TEMPERATURE", "0.2"))

# Deduce model (for reasoning, judgment, math understanding)
# o3-mini and other reasoning models don't support temperature parameter with structured output
DEDUCE_MODEL_NAME = os.getenv("DEDUCE_MODEL_NAME", "o3-mini")
# DEDUCE_MODEL_TEMPERATURE = float(os.getenv("DEDUCE_MODEL_TEMPERATURE", "0"))


# ================== model instances (singleton) ==================
_writing_model = None
_deduce_model = None

def get_writing_model():
    global _writing_model
    if _writing_model is None:
        _writing_model = ChatOpenAI(model=WRITING_MODEL_NAME, temperature=WRITING_MODEL_TEMPERATURE)  # type: ignore
    return _writing_model

def get_deduce_model():
    global _deduce_model
    if _deduce_model is None:
        _deduce_model = ChatOpenAI(model=DEDUCE_MODEL_NAME)  # type: ignore
    return _deduce_model
