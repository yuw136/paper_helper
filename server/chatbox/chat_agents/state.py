from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    original_question: str
    current_question: str
    paper_id: str
    documents: List[str]
    answer: str
    search_count: int
    source: str
    messages: Annotated[List[BaseMessage], add_messages]
    summary: str