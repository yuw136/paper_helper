from typing import List, TypedDict, Annotated, Optional, cast
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from pydantic import BaseModel, Field

from chatbox.core.config import get_llm_model, DB_CONNECTION_STRING
from chatbox.chat_agents.state import AgentState
from chatbox.chat_agents.nodes import route_question, summarize_conversation, retrieve, web_search, grade_documents, transform_question, generate, not_found, decide_to_generate

# import sys
# if sys.platform == 'win32':
#     import asyncio
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#manually initialize and cleanup agent app
_agent_app = None
_checkpointer_context = None
_checkpointer_instance = None


async def initialize_agent():
    global _agent_app, _checkpointer_context, _checkpointer_instance

    _checkpointer_context = AsyncPostgresSaver.from_conn_string(DB_CONNECTION_STRING)
    _checkpointer_instance = await _checkpointer_context.__aenter__()
    
    await _checkpointer_instance.setup()

    _agent_app = workflow.compile(checkpointer = _checkpointer_instance)
    
    print(f"checkpointer connected to PostgreSQL database at {DB_CONNECTION_STRING}")
    return _agent_app

async def get_agent_app():
    if _agent_app is None:
        raise RuntimeError("Agent app not initialized")
    return _agent_app

async def cleanup_agent():
    global _checkpointer_context, _checkpointer_instance, _agent_app
    
    if _checkpointer_context is not None:
        await _checkpointer_context.__aexit__(None, None, None)
        _checkpointer_context = None
        _checkpointer_instance = None
        _agent_app = None
        print(f"checkpointer disconnected from PostgreSQL database")




#workflow graph
workflow = StateGraph(AgentState)

#add nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("web_search", web_search)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("transform_question", transform_question)
workflow.add_node("generate", generate)
workflow.add_node("summarize_conversation", summarize_conversation)

#failed node: no relevant information found in database or online
workflow.add_node("not_found", not_found)

#add edges
#route question entry point
workflow.set_conditional_entry_point(
    route_question,
    {
        "web_search": "web_search",
        "retrieve": "retrieve",
    }
)

#normal edges
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("web_search","grade_documents")
workflow.add_edge("transform_question","retrieve")

#conditional edges: decide to generate or not
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_question": "transform_question",
        "web_search": "web_search",
        "generate": "generate",
        "not found": "not_found",
    }
)

#exit edges
workflow.add_edge("not_found", "summarize_conversation")
workflow.add_edge("generate", "summarize_conversation")
workflow.add_edge("summarize_conversation", END)

# #compile graph (deprecated - using manual initialization instead)
# async def compile_graph():
#     async with AsyncPostgresSaver.from_conn_string(DB_CONNECTION_STRING) as checkpointer:
#         await checkpointer.setup()
#         agent_app = workflow.compile(checkpointer=checkpointer)
#         return agent_app


#run test
# if __name__ == "__main__":
    #initialize documents and answer, get answer during stream updates
    # question = "What is immersed varifold in this paper?"
    # inputs: AgentState = {
    #     "original_question": question,
    #     "current_question": question,
    #     "paper_id": "2310.01340v2",
    #     "documents": [],
    #     "answer": "",
    #     "search_count": 0,
    #     "source": "local",
    #     "summary": "",
    #     "messages": []
    # }

    # final_answer = None
    # for output in agent_app.astream(inputs):
    #     for node_name, node_output in output.items():
    #         print(f"Finished Node: {node_name}")
    #         if node_output and "answer" in node_output:
    #             final_answer = node_output["answer"]
    
    # print("\n=== Final Answer ===")
    # if final_answer:
    #     print(final_answer)
    # else:
    #     print("Sorry, I couldn't find any relevant information.")
    

