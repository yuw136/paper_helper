from datetime import datetime
import json
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel
from asyncpg import Connection

from database import get_async_db_connection
from chatbox.chat_agents.graph import get_agent_app
from chatbox.chat_agents.state import AgentState
from models.session import ChatSession


chat_router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    thread_id: str
    message_id: str
    file_id: str
    content: str
    excerpts: list[str]
    timestamp: int
   

class ChatSessionRequest(BaseModel):
    id: str
    fileId: str
    title: str
    createdAt: int
    updatedAt: int

class CreateChatSessionRequest(BaseModel):
    session: ChatSessionRequest
    
@chat_router.post("/api/create_chat_history")
async def create_chat_history(request: CreateChatSessionRequest,db: Connection = Depends(get_async_db_connection)):
    # Use server time for created_at and updated_at
    now = datetime.now()
    session_data = ChatSession(**{
        "id": request.session.id,
        "file_id": request.session.fileId,
        "title": request.session.title,
        "created_at": now,
        "updated_at": now
})
    try:
        await db.execute( "INSERT INTO chatsession (id, file_id, title, created_at, updated_at) VALUES ($1, $2, $3, $4, $5)", 
            session_data.id, 
            session_data.file_id, 
            session_data.title, 
            session_data.created_at, 
            session_data.updated_at)
        
        return {"message": "Chat session created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")

@chat_router.get("/api/chat_histories/{file_id}")
async def get_chat_histories(file_id: str, db: Connection = Depends(get_async_db_connection)):
    try:
        chat_sessions = await db.fetch("SELECT * FROM chatsession WHERE file_id = $1", file_id)
        
        #change snake_case to camelCase, 
        result = [
            {
                "id": session["id"],
                "fileId": session["file_id"],  
                "title": session["title"],
                "createdAt": int(session["created_at"].timestamp() * 1000),  
                "updatedAt": int(session["updated_at"].timestamp() * 1000)
            }
            for session in chat_sessions
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat sessions: {str(e)}")

@chat_router.get("/api/messages/{thread_id}")
async def get_messages(thread_id: str, db: Connection = Depends(get_async_db_connection)):
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    
    # get agent app and state from langgraph
    agent_app = await get_agent_app()
    state = await agent_app.aget_state(config)
    
    if not state or not state.values:
        return []
    
    messages = state.values.get("messages", [])
    
    # Convert messages to frontend ChatMessage format
    result = []
    for msg in messages:
        # Determine role based on message type
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "ai"
        else:
            role = "system"
        
        # Extract timestamp from message metadata (stored as milliseconds int)
        timestamp = msg.additional_kwargs.get('timestamp', int(datetime.now().timestamp() * 1000))
        message_dict = {
            "id": msg.id,
            "role": role,
            "content": msg.content,
            "timestamp": timestamp,
        }
        
        # Add excerpts if present in message metadata
        if hasattr(msg, 'additional_kwargs') and 'excerpts' in msg.additional_kwargs:
            message_dict["excerpts"] = msg.additional_kwargs['excerpts']
           
        result.append(message_dict)
    return result


@chat_router.post("/api/chat")
async def chat(body: ChatRequest, db: Connection = Depends(get_async_db_connection)):
    #assemble message
    thread_id = body.thread_id
    file_id = body.file_id
    message_id = body.message_id
    content = body.content
    excerpts = body.excerpts
    timestamp = body.timestamp

    user_message = HumanMessage(
        content=content,
        id=message_id,          
        additional_kwargs={
            "timestamp": timestamp,  # Store as milliseconds int (same as frontend)
            "excerpts": excerpts,
        }
    )

    #update chat session title if it is the first user message
    new_title = content[:30] + ("..." if len(content) > 30 else "")
    await db.execute(
        """
        UPDATE chatsession 
        SET title = $1, updated_at = $2 
        WHERE id = $3 AND title = 'New Chat'
        """,
        new_title,
        datetime.now(),
        thread_id
    )

    #check if file is a paper or not
    paper= await db.fetch("SELECT * FROM paper WHERE id = $1", file_id)
    
    agent_app = await get_agent_app()
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    
    inputs: AgentState = {
        "original_question": content,
        "current_question": content,
        "paper_id": file_id if paper else "",
        "documents": [],
        "answer": "",
        "search_count": 0,
        "source": "local",
        "summary": "",
        "messages": [user_message],
        "user_excerpts": excerpts
    }

    async def chat_agent_stream():
        async for chunk in agent_app.astream(inputs, config=config):
            for node_name, node_output in chunk.items():
                if node_output:
                    event = {"node": node_name, "output": node_output}
                    yield f"data: {json.dumps(event, default=str)}\n\n"
    
    return StreamingResponse(chat_agent_stream(), media_type="text/event-stream")
