import asyncio
import sys
import json
from pathlib import Path

try:
    import httpx
except ImportError:
    print("需要安装 httpx: pip install httpx")
    sys.exit(1)


async def test_chat_endpoint():
    print("测试 4: HTTP API 端点")
    
    base_url = "http://localhost:8000"
    url = f"{base_url}/chat"
    
    payload = {
        "thread_id": "test_session_http",
        "query": "What is the main theorem?",
        "paper_id": "2601.07194v1"
    }
    
    try:
        print(f"\n正在连接到 {url}...")
        print(f"请求数据: {json.dumps(payload, indent=2)}")
        
        async with httpx.AsyncClient() as client:
            async with client.stream('POST', url, json=payload, timeout=60.0) as response:
                print(f"状态码: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ 请求失败，状态码: {response.status_code}")
                    return False
                
                nodes_received = []
                answer_received = False
                
                print("\n接收到的节点:")
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            node_name = data.get('node')
                            nodes_received.append(node_name)
                            print(f"  [{node_name}]", end=" ")
                            
                            if node_name == 'generate':
                                output = data.get('output', {})
                                answer = output.get('answer', '')
                                if answer:
                                    answer_received = True
                                    print(f"\n  答案: {answer[:100]}...")
                            
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️ JSON 解析错误: {e}")
                
                print(f"\n\n总共执行了 {len(nodes_received)} 个节点")
                
                if answer_received:
                    print("✅ 成功接收到答案")
                else:
                    print("⚠️ 未接收到答案")
                
                print("\n--- 测试第二次请求（同一会话） ---")
                payload2 = {
                    "thread_id": "test_session_http",
                    "query": "Can you explain more?",
                    "paper_id": "2601.07194v1"
                }
                
                async with client.stream('POST', url, json=payload2, timeout=60.0) as response2:
                    nodes_count = 0
                    async for line in response2.aiter_lines():
                        if line.startswith('data: '):
                            nodes_count += 1
                    
                    print(f"第二次请求执行了 {nodes_count} 个节点")
                
                print("\n✅ API 测试完成")
                return True
                
    except httpx.ConnectError:
        print(f"❌ 连接失败: 无法连接到 {base_url}")
        print("请确保服务器正在运行: python server/chatbox/main.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("注意: 此测试需要服务器正在运行")
    print("启动服务器: cd server/chatbox && python main.py")
    print("")
    
    success = asyncio.run(test_chat_endpoint())
    sys.exit(0 if success else 1)
