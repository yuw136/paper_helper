import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from chatbox.chat_agents.graph import initialize_agent, cleanup_agent, get_agent_app
from chatbox.chat_agents.state import AgentState
from chatbox.utils.create_message import create_message


async def test_persistence():
    print("测试 3: 持久化与会话记忆")
    
    thread_id = "persistence_test_session"
    
    try:
        print("\n--- 运行 1: 创建第一次对话 ---")
        await initialize_agent()
        agent = await get_agent_app()
        
        inputs: AgentState = {
            "original_question": "What is Lu's Conjecture?",
            "current_question": "What is Lu's Conjecture?",
            "paper_id": "2601.07194v1",
            "documents": [],
            "answer": "",
            "search_count": 0,
            "source": "local",
            "summary": "",
            "messages": [HumanMessage(content="What is Lu's Conjecture?")],
            "user_excerpts": []
        }
        
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        
        first_search_count = None
        async for chunk in agent.astream(inputs, config=config):
            for node_name, node_output in chunk.items():
                print(f"[{node_name}]", end=" ")
                if "search_count" in node_output:
                    first_search_count = node_output["search_count"]
        
        print(f"\n第一次对话 search_count: {first_search_count}")
        
        await cleanup_agent()
        
        print("\n--- 运行 2: 模拟重启后继续对话 ---")
        await initialize_agent()
        agent = await get_agent_app()
        
        inputs2: AgentState = {
            "original_question": "Tell me more about it",
            "current_question": "Tell me more about it",
            "paper_id": "2601.07194v1",
            "documents": [],
            "answer": "",
            "search_count": 0,
            "source": "local",
            "summary": "",
            "messages": [HumanMessage(content="Tell me more about it")],
            "user_excerpts": []
        }
        
        message_count = 0
        second_search_count = None
        
        async for chunk in agent.astream(inputs2, config=config):
            for node_name, node_output in chunk.items():
                print(f"[{node_name}]", end=" ")
                
                if "messages" in node_output:
                    message_count = len(node_output["messages"])
                
                if "search_count" in node_output:
                    second_search_count = node_output.get("search_count")
        
        print(f"\n对话历史消息数: {message_count}")
        print(f"第二次对话 search_count: {second_search_count}")
        
        if message_count >= 2:
            print("✅ 成功保留对话历史")
        else:
            print("⚠️ 对话历史未保留")
        
        await cleanup_agent()
        
        print("\n--- 运行 3: 验证新会话是独立的 ---")
        await initialize_agent()
        agent = await get_agent_app()
        
        new_thread_config: RunnableConfig = {"configurable": {"thread_id": "new_session"}}
        
        inputs3: AgentState = {
            "original_question": "How does authors prove Lu's Conjecture?",
            "current_question": "How does authors prove Lu's Conjecture?",
            "paper_id": "2601.07194v1",
            "documents": [],
            "answer": "",
            "search_count": 0,
            "source": "local",
            "summary": "",
            "messages": [HumanMessage(content="How does authors prove Lu's Conjecture?")],
            "user_excerpts": []
        }
        
        new_message_count = 0
        async for chunk in agent.astream(inputs3, config=new_thread_config):
            for node_name, node_output in chunk.items():
                if "messages" in node_output:
                    new_message_count = len(node_output["messages"])
        
        print(f"新会话消息数: {new_message_count}")
        
        if new_message_count < message_count:
            print("✅ 新会话正确隔离")
        else:
            print("⚠️ 会话隔离可能有问题")
        
        await cleanup_agent()
        print("\n✅ 持久化测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        await cleanup_agent()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_persistence())
    sys.exit(0 if success else 1)
