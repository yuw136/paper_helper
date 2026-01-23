# Agent 测试套件

## 测试文件

### 1. test_checkpointer.py
测试 Checkpointer 生命周期管理
- 初始化 agent
- 获取 agent 实例
- 清理资源
- 验证清理后的状态

### 2. test_conversation.py
测试完整对话流程
- 单次对话执行
- 节点执行顺序
- 答案生成
- 同一会话的多次对话

### 3. test_persistence.py
测试持久化与会话记忆
- 跨重启对话记忆
- 会话状态保存
- 不同会话的隔离

### 4. test_api.py
测试 HTTP API 端点
- SSE 流式响应
- 多次请求
- 会话管理

## 运行测试

### 快速开始

运行所有测试（除了 API 测试）:
```bash
cd server/tests
python run_all_tests.py
```

### 运行单个测试

```bash
# 测试 1: Checkpointer 生命周期
python test_checkpointer.py

# 测试 2: 对话流程
python test_conversation.py

# 测试 3: 持久化
python test_persistence.py

# 测试 4: API（需要先启动服务器）
# 终端 1:
cd server/chatbox
python main.py

# 终端 2:
cd server/tests
python test_api.py
```

## 前置条件

1. 安装依赖:
```bash
pip install -r ../requirements.txt
pip install httpx  # for test_api.py
```

2. 确保数据库中有测试数据:
- paper_id: "2310.01340v2" 应该存在于数据库中
- 或修改测试文件中的 paper_id

3. 设置环境变量:
```bash
export OPENAI_API_KEY="your-api-key"
```

## 测试输出示例

### 成功的测试输出
```
测试 1: Checkpointer 生命周期
✅ Agent 初始化成功
✅ Agent 获取成功
✅ Agent 清理成功
✅ 清理后正确抛出异常

✅ 所有测试通过
```

### 失败的测试输出
```
❌ 测试失败: RuntimeError: Agent app not initialized
```

## 故障排除

### 问题 1: 导入错误
```
ModuleNotFoundError: No module named 'chat_agents'
```
**解决**: 确保从 `server/tests` 目录运行测试

### 问题 2: 数据库连接错误
```
OperationalError: could not connect to server
```
**解决**: 
1. 确保 PostgreSQL 数据库正在运行（通过 Docker 或本地安装）
2. 检查 `database.py` 中的 `DATABASE_URL` 配置
3. 确认数据库连接信息正确（用户名、密码、端口）

### 问题 3: API 测试连接失败
```
❌ 连接失败: 无法连接到 http://localhost:8000
```
**解决**: 先启动服务器 `python server/chatbox/main.py`

### 问题 4: OpenAI API 错误
```
openai.error.AuthenticationError
```
**解决**: 设置正确的 OPENAI_API_KEY

## 清理测试数据

测试会在 PostgreSQL 数据库中创建 checkpointer 表。清理方法:

```sql
-- 连接到数据库
psql -U user -d paper_helper

-- 删除 LangGraph checkpointer 表
DROP TABLE IF EXISTS checkpoints CASCADE;
DROP TABLE IF EXISTS checkpoint_writes CASCADE;
```

或者通过 Python:
```python
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS checkpoints CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS checkpoint_writes CASCADE"))
    conn.commit()
```

## 扩展测试

要添加新测试:

1. 创建新的测试文件 `test_xxx.py`
2. 遵循现有测试的结构
3. 在 `run_all_tests.py` 中添加新测试
4. 更新此 README

## 注意事项

- 测试会实际调用 OpenAI API，可能产生费用
- 持久化测试会创建真实的数据库记录
- 建议在开发环境运行测试
- API 测试需要服务器运行在 localhost:8000
