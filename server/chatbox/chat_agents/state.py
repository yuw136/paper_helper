from typing import Optional, TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class _AgentStateRequired(TypedDict):
    original_question: str
    current_question: str

    paper_id: str
    paper_topic: str
    
    documents: List[str]
    answer: str
    search_count: int
    source: str
    messages: Annotated[List[BaseMessage], add_messages]
    summary: str
    user_excerpts: Optional[List[str]]


class AgentState(_AgentStateRequired, total=False):
    selected_tools: List[str]
    retrieval_reason: str
    retrieval_confidence: float
    semantic_docs: List[str]
    tavily_docs: List[str]
    db_docs: List[str]