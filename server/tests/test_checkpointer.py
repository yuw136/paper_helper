import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from chatbox.chat_agents.graph import initialize_agent, cleanup_agent, get_agent_app


async def test_checkpointer_lifecycle():
    print("测试 1: Checkpointer 生命周期")
    
    try:
        await initialize_agent()
        print("✅ Agent 初始化成功")
        
        agent = await get_agent_app()
        assert agent is not None
        print("✅ Agent 获取成功")
        
        await cleanup_agent()
        print("✅ Agent 清理成功")
        
        try:
            await get_agent_app()
            print("❌ 清理后仍能获取 agent（错误）")
            return False
        except RuntimeError:
            print("✅ 清理后正确抛出异常")
        
        print("\n✅ 所有测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_checkpointer_lifecycle())
    sys.exit(0 if success else 1)
