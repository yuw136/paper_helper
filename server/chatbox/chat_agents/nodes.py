
import arxiv
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import cast

from models.paper import Paper, PaperChunk
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
        description="Given a user question, choose to route it to 'web_search' or 'vectorstore'. "
                    "If the user mentions online search or find other resources, use 'web_search'. "
                    "Otherwise, default to 'vectorstore'."
    )

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")



def route_question(state: AgentState):
    print("--- ROUTE QUESTION ---")
    question = state["original_question"]
    
    structured_llm_router = deduce_model.with_structured_output(RouteQuery)
    
    system = """You are an expert at routing a user question to a vectorstore or web search.
    The vectorstore contains documents about a specific mathematics topic (Local DB).
    The web_search allows searching the Arxiv online database.
    The vectorstore is the default choice.
    Use the vectorstore for general questions about definitions, theorems, proofs, especially when
    the user asks about "this paper", "the paper", "the main theorem", "the main result", "the main proof", etc.
    Use web_search only if the user explicitly asks for "other results", "related results", "related papers", "related topics", etc.
    Return either "web_search" or "retrieve" (for vectorstore).
    """
    
    route_prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{question}")]
    )
    
    router = route_prompt | structured_llm_router
    result: RouteQuery = cast(RouteQuery, router.invoke({"question": question}))

    if result.data_source == "web_search":  
        print("--- ROUTE: TO WEB SEARCH ---")
        return "web_search"
    else:
        print("--- ROUTE: TO LOCAL VECTORSTORE ---")
        return "retrieve"

#summary node
def summarize_conversation(state: AgentState):
    summary = state.get("summary", "")
    messages = state["messages"]
    
    # save last 2 messages, summarize the rest
    messages_to_summarize = messages[:-2]
    
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



#retrieval node， need to be optimized
def retrieve(state: AgentState):
    original_q = state["original_question"]
    current_q = state.get("current_question", original_q)
    paper_id = state.get("paper_id", None)
    user_excerpts = state.get("user_excerpts", [])
    
    all_retrieved_docs = []
    seen_texts = set()
    
    # search by original question
    print(f"--- SEARCHING BY QUESTION: {original_q[:50]}... ---")
    docs_by_question = search_base(original_q, paper_id=paper_id, top_k=3)
    
    for doc_tuple in docs_by_question:
        chunk, paper = doc_tuple
        if chunk.text not in seen_texts:
            all_retrieved_docs.append(chunk.text)
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
                    all_retrieved_docs.append(chunk.text)
                    seen_texts.add(chunk.text)
            
            print(f"  Found {len(docs_by_excerpt)} related docs for excerpt {i+1}")
    
    # search by transformed question
    if current_q and current_q != original_q:
        print(f"--- SEARCHING BY TRANSFORMED QUERY ---")
        docs_by_transformed = search_base(current_q, paper_id=paper_id, top_k=2)
        
        for doc_tuple in docs_by_transformed:
            chunk, paper = doc_tuple
            if chunk.text not in seen_texts:
                all_retrieved_docs.append(chunk.text)
                seen_texts.add(chunk.text)
        
        print(f"Found {len(docs_by_transformed)} docs by transformed query")
    
    print(f"--- TOTAL: {len(all_retrieved_docs)} unique documents for RAG ---")
    
    return {"documents": all_retrieved_docs, "search_count": state.get("search_count", 0) + 1}

#web search node
def web_search(state: AgentState):
    print("--- SEARCHING ONLINE ---")
    question = state["original_question"]

    #先用arxiv搜索返回top3的abstract，后面改...
    client = arxiv.Client()
    search = arxiv.Search(
        query=question,
        max_results=3,
        sort_by = arxiv.SortCriterion.Relevance
    )

    results = []
    for result in client.results(search):
        print(f"Title: {result.title}\nSummary: {result.summary}\nurl: {result.pdf_url}")
        results.append(f"Title: {result.title}\nSummary: {result.summary}\nurl: {result.pdf_url}")
    print(f"Found {len(results)} papers from Arxiv online.")
    
    # 直接把在线搜索结果塞给 documents，进入生成环节
    return {"documents": results, "source": "web"}    

def grade_documents(state: AgentState):
    #这里的策略是：如果llm认为找出的文档切片和问题不相关，则又llm修改query再到数据库中匹配
    #如果找到的document和问题相关，则返回，否则进入web_search
    print("--- CHECK: DOCUMENT RELEVANCE ---")
    question = state["current_question"]
    documents = state["documents"]

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
    
    # check all documents and return documents
    filtered_docs = []
    
    for doc in documents:
        # LLM 判断：doc 是否能回答 question？
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
                return "web_search"
        elif source == "web":
            return "not found"
    else:
        return "generate"
    

#answer generation node
def generate(state: AgentState):
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

    # print("--- MESSAGES ---")
    # for msg in messages:
    #     print(f"msg: {msg}\n")

    response = writing_model.invoke(messages)
    # Only add AI message - user message already exists in state from chat.py input
    return {
        "answer": response.content,
        "messages": [create_message("ai", response.content)]
    }

#not found node
def not_found(state: AgentState):
    answer = "Sorry, I searched both locally and on Arxiv but couldn't find relevant info."
    return {"answer": answer, "messages": [create_message("ai", answer)]}
