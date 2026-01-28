from sqlmodel import SQLModel, create_engine
from sqlalchemy import text
import asyncpg
from dotenv import load_dotenv
import os

from models.paper import Paper
from models.report import Report
from models.session import ChatSession

# Load environment variables
load_dotenv()

# Database selection logic
# Priority: USE_SUPABASE > SUPABASE_DATABASE_URL > LOCAL_DATABASE_URL
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

if USE_SUPABASE:
    DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("USE_SUPABASE=true but SUPABASE_DATABASE_URL is not set")
    print(f"Using Supabase database")
else:
    DATABASE_URL = os.getenv("LOCAL_DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("LOCAL_DATABASE_URL is not set")
    print(f"Using local database")

# echo=True will print the generated SQL statements
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    # enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # create all tables
    SQLModel.metadata.create_all(engine)


#async database pool

async_db_pool = None

async def init_db_pool():
    global async_db_pool
    if not async_db_pool:
        async_db_pool = await asyncpg.create_pool(
            dsn = DATABASE_URL,
            min_size = 1,
            max_size = 10,
        )
        print("asyncpg database pool initialized")

async def close_db_pool():
    global async_db_pool
    if async_db_pool:
        await async_db_pool.close()


async def get_async_db_connection():
    global async_db_pool
    if not async_db_pool:
        raise RuntimeError("Database pool not initialized")
    
    async with async_db_pool.acquire() as connection:
        yield connection