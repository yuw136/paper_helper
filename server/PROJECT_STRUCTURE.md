# Paper Helper 项目结构

```
paper_helper/
│
├── .langgraph_api/              # LangGraph API 缓存和检查点
│   ├── .langgraph_checkpoint.*.pckl
│   ├── .langgraph_ops.pckl
│   ├── .langgraph_retry_counter.pckl
│   ├── store.pckl
│   └── store.vectors.pckl
│
├── old_server/                  # 旧版本服务器代码（已废弃）
│   ├── chat-mcp.js
│   ├── chat.js
│   ├── mcp-server.js
│   ├── server.js
│   ├── package.json
│   └── package-lock.json
│
├── public/                      # 前端静态资源
│   ├── favicon.ico
│   ├── index.html
│   ├── logo192.png
│   ├── logo512.png
│   ├── manifest.json
│   └── robots.txt
│
├── server/                      # 后端服务器
│   │
│   ├── chatbox/                 # 聊天机器人模块
│   │   ├── __init__.py
│   │   ├── main.py              # 聊天服务主入口
│   │   │
│   │   ├── api/                 # API 路由
│   │   │   ├── files.py         # 文件管理API
│   │   │   └── routes.py        # 主要路由
│   │   │
│   │   ├── chat_agents/         # 对话智能体
│   │   │   ├── __init__.py
│   │   │   ├── assemble_agent_state.py  # 状态组装
│   │   │   ├── graph.py         # LangGraph 图定义
│   │   │   ├── nodes.py         # 图节点实现
│   │   │   ├── retrieve.py      # 检索逻辑
│   │   │   └── state.py         # 状态定义
│   │   │
│   │   ├── core/                # 核心配置
│   │   │   ├── chat_agents.db   # 聊天数据库
│   │   │   ├── config.py        # 配置文件
│   │   │   └── logging.py       # 日志配置
│   │   │
│   │   └── utils/               # 工具函数
│   │       └── create_message.py # 消息创建工具
│   │
│   ├── managers/                # 管理器模块
│   │   └── file_manager.py      # 文件管理器
│   │
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── paper.py             # 论文模型
│   │   └── report.py            # 报告模型
│   │
│   ├── outdated/                # 废弃代码
│   │   ├── chunk.py
│   │   ├── embed.py
│   │   └── parse.py
│   │
│   ├── report_pipeline/         # 报告生成流水线
│   │   ├── __init__.py
│   │   ├── download_pipeline.py      # 下载流水线
│   │   ├── ingest_pipeline.py        # 数据摄入流水线
│   │   ├── send_email_pipeline.py    # 邮件发送流水线
│   │   └── weekly_report_agent.py    # 周报智能体
│   │
│   ├── tests/                   # 测试文件
│   │   ├── __init__.py
│   │   ├── agent_memory_test.py      # 智能体内存测试
│   │   ├── report_pipeline_test.py   # 报告流水线测试
│   │   ├── run_all_tests.py          # 运行所有测试
│   │   ├── test_api.py               # API测试
│   │   ├── test_checkpointer.py      # 检查点测试
│   │   ├── test_conversation.py      # 对话测试
│   │   ├── test_persistence.py       # 持久化测试
│   │   └── README_TESTS.md           # 测试文档
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── arxiv_query.py       # arXiv查询工具
│   │   ├── latex_utils.py       # LaTeX工具
│   │   └── tex_to_pdf.py        # TeX转PDF工具
│   │
│   ├── __init__.py
│   ├── CHANGES_SUMMARY.md       # 变更摘要
│   ├── config.py                # 全局配置
│   ├── database.py              # 数据库配置
│   ├── requirements.txt         # Python依赖
│   └── run_server.py            # 服务器启动脚本
│
├── .gitignore
├── docker-compose.yml           # Docker编排配置
├── env.example                  # 环境变量示例
├── langgraph.json              # LangGraph配置
├── package.json                # Node.js依赖（前端）
├── package-lock.json
├── pyproject.toml              # Python项目配置
├── README.md                   # 项目说明
├── start.ps1                   # Windows启动脚本
└── stop.ps1                    # Windows停止脚本
```

## 模块说明

### 后端 (server/)
- **chatbox/**: 聊天机器人核心模块，基于LangGraph实现
- **report_pipeline/**: 论文报告生成流水线
- **managers/**: 业务逻辑管理器
- **models/**: 数据库模型定义
- **utils/**: 通用工具函数

### 配置文件
- **docker-compose.yml**: Docker容器编排
- **langgraph.json**: LangGraph智能体配置
- **pyproject.toml**: Python项目元数据
