import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from chatbox.chat_agents.graph import initialize_agent, cleanup_agent, get_agent_app
from chatbox.chat_agents.state import AgentState


async def test_single_conversation():
    print("测试 2: 完整对话流程")
    
    try:
        await initialize_agent()
        agent = await get_agent_app()
        
        print("\n--- 第一次对话 ---")
        inputs: AgentState = {
            "original_question": "What is the main theorem?",
            "current_question": "What is the main theorem?",
            "paper_id": "2601.07194v1",
            "documents": [],
            "answer": "",
            "search_count": 0,
            "source": "local",
            "summary": "",
            "messages": [HumanMessage(content="What is the main theorem?")]
        }
        
        config: RunnableConfig = {"configurable": {"thread_id": "test_session_1"}}
        
        nodes_executed = []
        final_answer = None
        
        async for chunk in agent.astream(inputs, config=config):
            for node_name, node_output in chunk.items():
                nodes_executed.append(node_name)
                print(f"[{node_name}]", end=" ")
                
                if node_output and "answer" in node_output:
                    final_answer = node_output["answer"]
        
        print(f"\n执行的节点: {' -> '.join(nodes_executed)}")
        
        if final_answer:
            print(f"最终答案: {final_answer[:100]}...")
            print("✅ 成功生成答案")
        else:
            print("⚠️ 未生成答案")
        
        print("\n--- 第二次对话（同一会话） ---")
        inputs2: AgentState = {
            "original_question": "Tell me more details",
            "current_question": "Tell me more details",
            "paper_id": "2601.07194v1",
            "documents": [],
            "answer": "",
            "search_count": 0,
            "source": "local",
            "summary": "",
            "messages": [HumanMessage(content="Tell me more details")]
        }
        
        nodes_executed_2 = []
        async for chunk in agent.astream(inputs2, config=config):
            for node_name, node_output in chunk.items():
                nodes_executed_2.append(node_name)
                print(f"[{node_name}]", end=" ")
        
        print(f"\n执行的节点: {' -> '.join(nodes_executed_2)}")
        
        await cleanup_agent()
        print("\n✅ 对话流程测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_conversation())
    sys.exit(0 if success else 1)
