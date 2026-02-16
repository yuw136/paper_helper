from datetime import datetime
from typing import Any, Optional
import json
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


def _normalize_excerpts_for_response(raw_excerpts: Any, message_id: str) -> list[dict[str, Any]]:
    """Normalize legacy excerpt formats so frontend always receives objects with id/content."""
    if not isinstance(raw_excerpts, list):
        return []

    normalized: list[dict[str, Any]] = []
    for index, excerpt in enumerate(raw_excerpts):
        fallback_id = f"{message_id}-excerpt-{index}"
        if isinstance(excerpt, str):
            normalized.append({"id": fallback_id, "content": excerpt})
            continue

        if isinstance(excerpt, dict):
            content = excerpt.get("content")
            if not isinstance(content, str):
                continue

            normalized_excerpt = dict(excerpt)
            normalized_excerpt["id"] = str(normalized_excerpt.get("id") or fallback_id)
            normalized_excerpt["content"] = content
            normalized.append(normalized_excerpt)

    return normalized


class ExcerptPayload(BaseModel):
    id: str
    content: str
    pageNumber: Optional[int] = None
    boundingRect: Optional[dict[str, float]] = None
    timestamp: Optional[int] = None


class ChatRequest(BaseModel):
    thread_id: str
    message_id: str
    file_id: str
    content: str
    excerpts: list[ExcerptPayload]
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

        # Resolve chat target type (paper/report) and initialize agent state once per thread.
        paper = await db.fetchrow(
            "SELECT id, topic FROM paper WHERE id = $1",
            request.session.fileId,
        )
        report = None if paper else await db.fetchrow(
            "SELECT id, topic FROM report WHERE id = $1",
            request.session.fileId,
        )
        if not paper and not report:
            raise HTTPException(status_code=404, detail="Chat target file not found")

        if paper:
            initial_paper_id = paper["id"]
            initial_topic = paper["topic"] or ""
        else:
            if report is None:
                raise HTTPException(status_code=404, detail="Chat target file not found")
            initial_paper_id = ""
            initial_topic = report["topic"] or ""

        initial_state: AgentState = {
            "original_question": "",
            "current_question": "",
            "paper_id": initial_paper_id,
            "paper_topic": initial_topic,
            "documents": [],
            "answer": "",
            "search_count": 0,
            "source": "local",
            "messages": [],
            "summary": "",
            "user_excerpts": [],
        }

        agent_app = await get_agent_app()
        config: RunnableConfig = {"configurable": {"thread_id": request.session.id}}
        await agent_app.aupdate_state(config, initial_state)

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
            normalized_excerpts = _normalize_excerpts_for_response(
                msg.additional_kwargs.get("excerpts"),
                str(msg.id),
            )
            if normalized_excerpts:
                message_dict["excerpts"] = normalized_excerpts
           
        result.append(message_dict)
    return result


@chat_router.post("/api/chat")
async def chat(body: ChatRequest, db: Connection = Depends(get_async_db_connection)):
    #assemble message
    thread_id = body.thread_id
    file_id = body.file_id
    message_id = body.message_id
    content = body.content
    excerpt_payloads = [excerpt.model_dump(exclude_none=True) for excerpt in body.excerpts]
    excerpt_texts = [
        excerpt.content
        for excerpt in body.excerpts
        if isinstance(excerpt.content, str) and excerpt.content.strip()
    ]
    timestamp = body.timestamp

    user_message = HumanMessage(
        content=content,
        id=message_id,          
        additional_kwargs={
            "timestamp": timestamp,  # Store as milliseconds int (same as frontend)
            "excerpts": excerpt_payloads,
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

    agent_app = await get_agent_app()
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    existing_state = await agent_app.aget_state(config)
    existing_values = existing_state.values if existing_state and existing_state.values else {}
    
    inputs: AgentState = {
        "original_question": content,
        "current_question": content,
        "paper_id": existing_values.get("paper_id", ""),
        "paper_topic": existing_values.get("paper_topic", ""),
        "documents": [],
        "semantic_docs": [],
        "tavily_docs": [],
        "db_docs": [],
        "selected_tools": [],
        "retrieval_reason": "",
        "retrieval_confidence": 0.0,
        "answer": "",
        "search_count": 0,
        "source": "local",
        "summary": existing_values.get("summary", ""),
        "messages": [user_message],
        "user_excerpts": excerpt_texts
    }

    async def chat_agent_stream():
        """Stream events from agent execution, including token-by-token LLM generation"""
        current_node = None
        
        async for event in agent_app.astream_events(inputs, config=config, version="v2"):
            event_type = event["event"]
            
            # Track current node from metadata
            metadata = event.get("metadata", {})
            if "langgraph_node" in metadata:
                node_name = metadata["langgraph_node"]
                if node_name != current_node:
                    current_node = node_name
            
            # 1. Node start events - send status updates only, no data output
            if event_type == "on_chain_start":
                if "langgraph_node" in metadata:
                    node_name = metadata["langgraph_node"]
                    print(f"[Node Start] {node_name}")
                    
                    yield f"data: {json.dumps({
                        'type': 'node_status',
                        'node': node_name
                    })}\n\n"
            
            # 2. Node end events 
            elif event_type == "on_chain_end":
                if "langgraph_node" in metadata:
                    node_name = metadata["langgraph_node"]
                    print(f"[Node End] {node_name}")
            
            # 3. LLM streaming events 
            elif event_type == "on_chat_model_stream":
                if current_node == "generate" or current_node == "not_found":
                    chunk = event.get("data", {}).get("chunk")
                    
                    # Extract content from the chunk (safely handle different types)
                    if chunk and hasattr(chunk, 'content'):
                        content = getattr(chunk, 'content', None)
                        if content and isinstance(content, str):
                            print(f"[LLM Stream] {content}")
                            
                            # Send token chunks to frontend
                            yield f"data: {json.dumps({
                                'type': 'llm_stream',
                                'node': current_node,
                                'chunk': content
                            })}\n\n"
            
            elif event_type == "on_chain_error":
                error = event.get("data", {}).get("error", "Unknown error")
                print(f"[Error] {error}")
                
                yield f"data: {json.dumps({
                    'type': 'error',
                    'error': str(error)
                })}\n\n"
    
    return StreamingResponse(chat_agent_stream(), media_type="text/event-stream")
