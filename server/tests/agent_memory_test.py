from typing import cast
import uuid
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig

from server.chat_agents.agent_graph import AgentState, app

# 创建一个固定的 thread_id，这就相当于一个“会话窗口”
thread_id = "session_math_001"
config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

# --- 第一轮对话 ---
print("\n========== Round 1: Define Immersed Varifold ==========")
inputs_1:AgentState = {
    "original_question": "Definition of Immersed Varifold",
    "current_question": "Definition of Immersed Varifold",
    "paper_id": "2310.01340v2",
    "documents": [],
    "answer": "",
    "search_count": 0,
    "source": "local",
    "summary": "",

    # 注意：第一轮需要初始化 messages 列表
    "messages": [HumanMessage(content="Definition of Immersed Varifold",id = str(uuid.uuid4()))]
}
# 运行...
for event in app.stream(inputs_1, config=config):
    pass # 打印过程...

# --- 第二轮对话 ---
print("\n========== Round 2: Ask about what it does in the paper ==========")
# 注意：这里我们不需要再传 "summary"，Checkpointer 会自动从内存加载上一轮的状态！
inputs_2 = cast(AgentState, {
    "original_question": "what is the main result about it in the paper?", 
    "current_question": "what is the main result about it in the paper?",
    "messages": [HumanMessage(content="Is it stable?")]
})
# 运行...
# 这次 LLM 会知道 "It" 指的是 Round 1 里的 "Immersed Varifold"，因为 summary 会包含这个信息。
for event in app.stream(inputs_2, config=config):
    pass