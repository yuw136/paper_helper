import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel

from chatbox.chat_agents.graph import get_agent_app
from chatbox.chat_agents.state import AgentState


chat_router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    thread_id: str
    query: str
    paper_id: str

@chat_router.post("/chat")
async def chat(body: ChatRequest):
    agent_app = await get_agent_app()
    config: RunnableConfig = {"configurable": {"thread_id": body.thread_id}}
    
    inputs: AgentState = {
        "original_question": body.query,
        "current_question": body.query,
        "paper_id": body.paper_id,
        "documents": [],
        "answer": "",
        "search_count": 0,
        "source": "local",
        "summary": "",
        "messages": [HumanMessage(content=body.query)]
    }

    async def chat_agent_stream():
        async for chunk in agent_app.astream(inputs, config=config):
            for node_name, node_output in chunk.items():
                if node_output:
                    event = {"node": node_name, "output": node_output}
                    yield f"data: {json.dumps(event, default=str)}\n\n"
    
    return StreamingResponse(chat_agent_stream(), media_type="text/event-stream")
