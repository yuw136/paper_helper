# 
import logging
import sys
from contextlib import asynccontextmanager, AsyncExitStack
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chatbox.api.chat import chat_router
from chatbox.api.files import files_router

from chatbox.core.config import settings
from chatbox.chat_agents.graph import initialize_agent, cleanup_agent
from database import DATABASE_URL, init_db_pool, close_db_pool, get_async_db_connection

logger = logging.getLogger("uvicorn")

#async context manager for agent app
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    #There are two things in app: file system and agent. We want file system to work
    #even if agent is not working, while if file system is not working, we exit the app

    #initialize db for file system
    try:
        await init_db_pool()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e
    
    #initialize agent
    try:
        await initialize_agent()
        logger.info("Agent initialized")
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        logger.error("Agent feature disabled")
    

    yield 
    await cleanup_agent()
    logger.info("Agent cleaned up")

    await close_db_pool()
    logger.info("Database closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # 这里引用配置里的值
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(files_router)

if __name__ == "__main__":
    import uvicorn
    # For Windows, use SelectorEventLoop
    if sys.platform == 'win32':
        uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)