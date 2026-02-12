
import arxiv
import os
import requests
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import cast

from chatbox.chat_agents.state import AgentState
from chatbox.chat_agents.retrieve import search_base, search_by_excerpt_with_context, search_opening_chunks_by_id, search_opening_chunks_by_query

from chatbox.utils.create_message import create_message
from chatbox.core.config import get_deduce_model, get_writing_model

# Deduce model for reasoning tasks (route, grade, transform)
deduce_model = get_deduce_model()

# Writing model for text generation tasks (summarize, generate)
writing_model = get_writing_model()

#classes for structured output
class RouteQuery(BaseModel):
    """route to the source of the answer to the original question."""
    data_source: str = Field(
        ...,
        description="Given a user question, choose to route it to 'global_search' or 'vectorstore'. "
                    "If the user mentions online search or find other resources, use 'global_search'. "
                    "Otherwise, default to 'vectorstore'."
    )

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")


class RetrievalPlan(BaseModel):
    """Plan for selecting retrieval tools."""

    selected_tools: list[str] = Field(
        description="Choose from: tavily, semantic_scholar, db_chunk. Can be multiple tools."
    )
    reason: str = Field(description="Short reason for the tool selection.")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0.")


def _format_document(source: str, title: str, content: str, url: str = "") -> str:
    safe_title = title.strip() if title else "N/A"
    safe_url = url.strip() if url else "N/A"
    safe_content = content.strip() if content else ""
    return (
        f"[SOURCE: {source}]\n"
        f"Title: {safe_title}\n"
        f"URL: {safe_url}\n"
        f"Content:\n{safe_content}"
    )


def _search_semantic_scholar(query: str, max_results: int = 2) -> list[str]:
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,url,year",
    }
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get("data", [])
    except Exception as e:
        print(f"Semantic Scholar search failed: {e}")
        return []

    docs = []
    for item in data:
        abstract = (item.get("abstract") or "").strip()
        if not abstract:
            continue
        docs.append(
            _format_document(
                source="semantic_scholar",
                title=item.get("title", "Untitled"),
                content=abstract,
                url=item.get("url", ""),
            )
        )
    return docs


def _search_tavily(query: str, max_results: int = 2) -> list[str]:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        print("TAVILY_API_KEY is not set, skip Tavily search.")
        return []

    endpoint = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False,
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        response.raise_for_status()
        results = response.json().get("results", [])
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []

    docs = []
    for item in results:
        snippet = (item.get("content") or "").strip()
        if not snippet:
            continue
        docs.append(
            _format_document(
                source="tavily",
                title=item.get("title", "Untitled"),
                content=snippet,
                url=item.get("url", ""),
            )
        )
    return docs


def _normalize_selected_tools(selected_tools: list[str]) -> list[str]:
    valid = {"tavily", "semantic_scholar", "db_chunk"}
    normalized = []
    for tool in selected_tools:
        name = tool.strip().lower()
        if name in valid and name not in normalized:
            normalized.append(name)
    return normalized



def route_question(state: AgentState):
    print("--- ROUTE QUESTION ---")
    question = state["original_question"]
    
    structured_llm_router = deduce_model.with_structured_output(RouteQuery)
    
    system = """You are an expert at routing a user question to a vectorstore or global search.
    The vectorstore contains documents about a specific mathematics topic (Local DB).
    The global_search can call multiple tools (Tavily, Semantic Scholar, and global DB chunk search).
    The vectorstore is the default choice.
    Use the vectorstore for general questions about definitions, theorems, proofs, especially when
    the user asks about "this paper", "the paper", "the main theorem", "the main result", "the main proof", etc.
    Use global_search if the user asks for "other results", "related results", "related papers", "related topics",
    or the question is broad/ambiguous and needs baseline external definitions.
    Return either "global_search" or "retrieve" (for vectorstore).
    """
    
    route_prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{question}")]
    )
    
    router = route_prompt | structured_llm_router
    result: RouteQuery = cast(RouteQuery, router.invoke({"question": question}))

    if result.data_source == "global_search":  
        print("--- ROUTE: TO GLOBAL SEARCH ---")
        return "global_search"
    else:
        print("--- ROUTE: TO LOCAL VECTORSTORE ---")
        return "retrieve"

#retrieval node， need to be optimized
def retrieve(state: AgentState):
    original_q = state["original_question"]
    current_q = state.get("current_question", original_q)
    paper_id = state.get("paper_id", None)
    user_excerpts = state.get("user_excerpts", [])
    
    all_retrieved_docs: list[str] = []
    seen_texts = set()
    
    # search by original question
    print(f"--- SEARCHING BY QUESTION: {original_q[:50]}... ---")
    docs_by_question = search_base(original_q, paper_id=paper_id, top_k=3)
    
    for doc_tuple in docs_by_question:
        chunk, paper = doc_tuple
        if chunk.text not in seen_texts:
            all_retrieved_docs.append(
                _format_document(
                    source="local_db",
                    title=getattr(paper, "title", "Local database chunk"),
                    content=chunk.text,
                    url="",
                )
            )
            seen_texts.add(chunk.text)
    
    print(f"Found {len(docs_by_question)} docs by question")
    
    # search by user excerpts
    if user_excerpts:
        print(f"--- SEARCHING BY USER EXCERPTS: {len(user_excerpts)} items ---")
        
        for i, excerpt in enumerate(user_excerpts):
            excerpt_content = excerpt
            print(f"  Excerpt {i+1}: {excerpt_content[:50]}...")
            
            docs_by_excerpt = search_base(
                excerpt_content, 
                paper_id=paper_id, 
                top_k=2  
            )
            
            for doc_tuple in docs_by_excerpt:
                chunk, paper = doc_tuple
                if chunk.text not in seen_texts:
                    all_retrieved_docs.append(
                        _format_document(
                            source="local_db",
                            title=getattr(paper, "title", "Local database chunk"),
                            content=chunk.text,
                            url="",
                        )
                    )
                    seen_texts.add(chunk.text)
            
            print(f"  Found {len(docs_by_excerpt)} related docs for excerpt {i+1}")
    
    # search by transformed question
    if current_q and current_q != original_q:
        print(f"--- SEARCHING BY TRANSFORMED QUERY ---")
        docs_by_transformed = search_base(current_q, paper_id=paper_id, top_k=2)
        
        for doc_tuple in docs_by_transformed:
            chunk, paper = doc_tuple
            if chunk.text not in seen_texts:
                all_retrieved_docs.append(
                    _format_document(
                        source="local_db",
                        title=getattr(paper, "title", "Local database chunk"),
                        content=chunk.text,
                        url="",
                    )
                )
                seen_texts.add(chunk.text)
        
        print(f"Found {len(docs_by_transformed)} docs by transformed query")
    
    print(f"--- TOTAL: {len(all_retrieved_docs)} unique documents for RAG ---")
    
    return {
        "documents": all_retrieved_docs,
        "source": "local",
        "search_count": state.get("search_count", 0) + 1,
    }

#global search node
def global_search(state: AgentState):
    print("--- GLOBAL SEARCH DISPATCH ---")
    question = state.get("current_question", state["original_question"])
    user_excerpts = state.get("user_excerpts", [])
    excerpt_context = "\n".join(user_excerpts[:3]) if user_excerpts else "N/A"

    planner_llm = deduce_model.with_structured_output(RetrievalPlan)
    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are selecting retrieval tools for a math assistant.
Available tools:
- tavily: web pages, broad definitions, general/ambiguous questions, community-style explanations.
- semantic_scholar: related papers and research abstracts for academic/general scholarly questions.
- db_chunk: search all chunks in local database; best when question/excerpt mentions concrete references.

Rules:
1) If question or user excerpt mentions explicit references/papers/ids, use db_chunk.
2) If question is broad or ambiguous (example: "what is convergence"), include tavily.
3) If question asks related/similar papers or general academic literature, or the excerpt/question mentions academic context such as paper or names, include semantic_scholar.
4) If uncertain, choose 2-3 tools.
Return selected_tools using only: tavily, semantic_scholar, db_chunk.""",
            ),
            (
                "human",
                "Question:\n{question}\n\nUser excerpts (optional):\n{excerpt_context}",
            ),
        ]
    )
    planner = planner_prompt | planner_llm
    try:
        plan: RetrievalPlan = cast(
            RetrievalPlan,
            planner.invoke({"question": question, "excerpt_context": excerpt_context}),
        )
        selected_tools = _normalize_selected_tools(plan.selected_tools)
        if not selected_tools:
            selected_tools = ["tavily", "semantic_scholar", "db_chunk"]
        confidence = max(0.0, min(1.0, float(plan.confidence)))
        reason = plan.reason.strip() if plan.reason else "No reason provided."
    except Exception as e:
        print(f"Tool planning failed, fallback to all tools: {e}")
        selected_tools = ["tavily", "semantic_scholar", "db_chunk"]
        confidence = 0.0
        reason = "Planner failed, fallback to all tools."

    print(f"Selected tools: {selected_tools}, confidence: {confidence:.2f}")
    return {
        "source": "web",
        "selected_tools": selected_tools,
        "retrieval_confidence": confidence,
        "retrieval_reason": reason,
    }


def semantic_scholar_search(state: AgentState):
    print("--- SEMANTIC SCHOLAR SEARCH ---")
    selected_tools = state.get("selected_tools", [])
    if selected_tools and "semantic_scholar" not in selected_tools:
        print("Skip Semantic Scholar by planner decision.")
        return {"semantic_docs": []}
    question = state.get("current_question", state["original_question"])
    docs = _search_semantic_scholar(question, max_results=2)
    print(f"Found {len(docs)} docs from Semantic Scholar.")
    return {"semantic_docs": docs}


def tavily_search(state: AgentState):
    print("--- TAVILY SEARCH ---")
    selected_tools = state.get("selected_tools", [])
    if selected_tools and "tavily" not in selected_tools:
        print("Skip Tavily by planner decision.")
        return {"tavily_docs": []}
    question = state.get("current_question", state["original_question"])
    docs = _search_tavily(question, max_results=2)
    print(f"Found {len(docs)} docs from Tavily.")
    return {"tavily_docs": docs}


def db_chunk_search(state: AgentState):
    print("--- GLOBAL DATABASE CHUNK SEARCH ---")
    selected_tools = state.get("selected_tools", [])
    if selected_tools and "db_chunk" not in selected_tools:
        print("Skip DB chunk search by planner decision.")
        return {"db_docs": []}
    question = state.get("current_question", state["original_question"])
    docs_with_meta = search_base(question, paper_id=None, top_k=2)
    seen_texts = set()
    docs: list[str] = []

    for chunk, paper in docs_with_meta:
        if chunk.text in seen_texts:
            continue
        seen_texts.add(chunk.text)
        docs.append(
            _format_document(
                source="global_db_chunk",
                title=getattr(paper, "title", "Global database chunk"),
                content=chunk.text,
                url="",
            )
        )

    print(f"Found {len(docs)} docs from global database chunk search.")
    return {"db_docs": docs}

def grade_documents(state: AgentState):
    # Strategy: If LLM thinks the retrieved document chunks are irrelevant to the question,
    # let LLM modify the query and search the database again.
    # If the documents are relevant to the question, return them; otherwise, proceed to global_search
    print("--- CHECK: DOCUMENT RELEVANCE ---")
    question = state.get("current_question", state["original_question"])
    documents = list(state.get("documents", []))
    documents.extend(state.get("semantic_docs", []))
    documents.extend(state.get("tavily_docs", []))
    documents.extend(state.get("db_docs", []))

    structured_llm_grader = deduce_model.with_structured_output(GradeDocuments)
    system_prompt = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    If the document answers the question directly or indirectly, grade it as relevant. \n
    If the document is irrelevant to the question, grade it as irrelevant. \n
    Finally, if the document is relevant, output yes, otherwise output no."""
    
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )
    
    retrieval_grader = grade_prompt | structured_llm_grader
    
    # check all documents and keep relevant context only
    filtered_docs = []
    
    for doc in documents:
        # LLM judges: can doc answer the question?
        score: GradeDocuments = cast(GradeDocuments, retrieval_grader.invoke({"question": question, "document": doc}))
        if score.binary_score == "yes":
            filtered_docs.append(doc)
            
    return {"documents": filtered_docs}
            
def transform_question(state: AgentState):
    print("--- TRANSFORM QUERY ---")
    question = state["original_question"]
    paper_id = state.get("paper_id", None)

    context_text = []
    if paper_id:
        print(f"--- SEARCHING OPENING CHUNKS BY ID: {paper_id} ---")
        context_text.extend(search_opening_chunks_by_id(paper_id))
    else:
        print(f"--- SEARCHING OPENING CHUNKS BY QUERY: {question} ---")
        context_text.extend(search_opening_chunks_by_query(question, top_k=2))

    if not context_text:
        return {"source": "web"}

    context = "\n\n".join(context_text)
    # --- HyDE Prompt ---
    hyde_template = """You are an expert researcher. 
    The user has asked a question. To find the exact answer in the database, we need to align the search query with the terminology used in the papers.
    
    Here are the **Introduction/Abstract segments** of the target paper(s):
    {context}
    
    Your task:
    The aim is to rewrite the user's question to be more specific using the terms found in the text.
    1. Analyze the terminology, notation, and definitions used in the text above.
    2. Analyze the user's question and identify the key concepts and terms. Relate the user's question's concepts and terme
    to the terminology found in the text. If some concepts in user's question are very close to the terminology found in the text,
    replace the user's question's concepts and terms with the terminology found in the text.
    3. If user's question is not related to the terminology found in the text, rewrite minimally.
    """

    hyde_prompt = ChatPromptTemplate.from_template(hyde_template)
    print(f"hyde_prompt: {hyde_prompt}")

    prompt = ChatPromptTemplate.from_messages(
        [("system", hyde_template), ("human", "{question}")]
    )
    hyde_chain = hyde_prompt | deduce_model | StrOutputParser()
    better_question = hyde_chain.invoke({"question": question, "context": context})
    
    return {"current_question": better_question, "search_count": state.get("search_count", 0) + 1}

#conditional edge
def decide_to_generate(state: AgentState):
    filtered_docs = state["documents"]
    source = state.get("source", "local")

    if not filtered_docs:
        if source == "local":
            if state["search_count"] <= 1:
                return "transform_question"
            else:
                return "global_search"
        elif source == "web":
            return "not found"
    else:
        return "generate"
    

#answer generation node
async def generate(state: AgentState):
    print(f"------generating answer for question: {state['current_question']}------")
    question = state["current_question"]
    documents = state["documents"]
    
    summary = state.get("summary", "")
    recent_messages = state.get("messages", [])

    context = "\n\n".join(documents)

    # RAG prompt
    rag_prompt = ChatPromptTemplate.from_template(
        """You are an expert researcher in the field of mathematics.
        You are given a question and a list of documents as context that are relevant to the question.
        Use the context to answer the question. If you don't think the answer is in the context,
        say "Sorry, I don't find relevant information.".
        Keep the answer rigorous and use LaTex to format the math equations in the answer.
        Each context block includes SOURCE, Title and URL. When you use external information,
        cite brief references at the end under a "References" section.
        Prefer source title + URL when URL is available.
        
        Summary of the history of the conversation:
        {summary}
        
        Context:
        {context}
        
        Question: 
        {question}
        """
    )
    

    messages = [SystemMessage(content=rag_prompt
        .format(summary=summary, context=context, question=question))] + recent_messages

    # Use astream() for streaming generation instead of invoke()
    full_response = ""
    async for chunk in writing_model.astream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            # Ensure content is a string before concatenating
            content = chunk.content
            if isinstance(content, str):
                full_response += content
    
    # Return complete answer for state persistence
    return {
        "answer": full_response,
        "messages": [create_message("ai", full_response)]
    }

#not found node
def not_found(state: AgentState):
    answer = "Sorry, I searched both locally and on Arxiv but couldn't find relevant info."
    return {"answer": answer, "messages": [create_message("ai", answer)]}


#summary node
def summarize_conversation(state: AgentState):
    summary = state.get("summary", "")
    messages = state["messages"]
    
    # save last 6 messages, summarize the rest
    messages_to_summarize = messages[:-6]
    
    if not messages_to_summarize:
        return {}

    conversation_str = ""
    for msg in messages_to_summarize:
        if isinstance(msg, HumanMessage):
            conversation_str += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            conversation_str += f"AI: {msg.content}\n"
     
    system_prompt = """Distill the following chat history into a single summary paragraph. 
        Importantly, keep track of mathematical definitions, concepts, and theorems discussed."""
    
    if summary:
        system_prompt += f"\n\nCurrent Summary: {summary}"

    prompt_message = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Conversation to summarize:\n\n{conversation_str}"),
    ]
    response = writing_model.invoke(prompt_message)   

    # Delete old messages from messages
    messages_to_delete = []
    for msg in messages_to_summarize:
        if msg.id:
            messages_to_delete.append(RemoveMessage(id=msg.id))
    
    return {"summary": response.content, "messages": messages + messages_to_delete}
