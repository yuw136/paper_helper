"""
Windows-compatible server startup script.
This ensures the event loop policy is set before anything else.
"""
import sys
import asyncio

# MUST be first: Set event loop policy for Windows before any other imports
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    import uvicorn
    from chatbox.main import app
    
    # Use the uvicorn config with our pre-configured event loop
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        loop="asyncio"  # Use asyncio loop (will use our SelectorEventLoop)
    )
    server = uvicorn.Server(config)
    
    if sys.platform == 'win32':
        # On Windows, run with our pre-configured event loop
        asyncio.run(server.serve())
    else:
        asyncio.run(server.serve())
