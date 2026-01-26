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
├── frontend/                    # 前端应用
│   ├── src/                     # 源代码
│   │   ├── apis/                # API 接口
│   │   │   └── Api.tsx
│   │   │
│   │   ├── components/          # React 组件
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── ExcerptTag.tsx
│   │   │   ├── FileDirectory.tsx
│   │   │   ├── FileSystemView.tsx
│   │   │   ├── HistorySelector.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── PDFViewer.tsx
│   │   │   ├── SelectionTip.tsx
│   │   │   └── ui/              # UI 组件库
│   │   │
│   │   ├── pages/               # 页面组件
│   │   │   ├── LandingPage.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── PDFReaderPage.tsx
│   │   │   └── Signup.tsx
│   │   │
│   │   ├── styles/              # 样式文件
│   │   ├── utils/               # 工具函数
│   │   ├── App.tsx              # 应用入口
│   │   ├── main.tsx             # 主文件
│   │   ├── routes.tsx           # 路由配置
│   │   └── types.tsx            # 类型定义
│   │
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts           # Vite 配置
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
│   │   │   ├── chat.py          # 聊天API
│   │   │   └── files.py         # 文件管理API
│   │   │
│   │   ├── chat_agents/         # 对话智能体
│   │   │   ├── __init__.py
│   │   │   ├── graph.py         # LangGraph 图定义
│   │   │   ├── nodes.py         # 图节点实现
│   │   │   ├── retrieve.py      # 检索逻辑
│   │   │   └── state.py         # 状态定义
│   │   │
│   │   ├── core/                # 核心配置
│   │   │   ├── chat_agents.db   # 聊天数据库
│   │   │   ├── config.py        # 聊天模块配置
│   │   │   └── logging.py       # 日志配置
│   │   │
│   │   └── utils/               # 工具函数
│   │       ├── create_message.py       # 消息创建工具
│   │       └── extract_relative_path.py # 路径提取工具
│   │
│   ├── managers/                # 管理器模块
│   │   └── file_manager.py      # 文件管理器
│   │
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── paper.py             # 论文模型
│   │   ├── report.py            # 报告模型
│   │   └── session.py           # 会话模型
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
│   │   ├── run_all_agent_tests.py    # 运行所有智能体测试
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
│   ├── config.py                # 全局配置
│   ├── database.py              # 数据库配置
│   ├── delete_papers.py         # 删除论文脚本
│   ├── fix_existing_papers.py   # 修复论文脚本
│   ├── requirements.txt         # Python依赖
│   └── run_server.py            # 服务器启动脚本
│
├── .env.example                 # 环境变量示例（提交到Git）
├── .gitignore                   # Git忽略文件
├── CONFIG_GUIDE.md              # 配置指南
├── docker-compose.yml           # Docker编排配置
├── langgraph.json               # LangGraph配置
├── paper-helper.code-workspace  # VS Code 工作区配置
├── PROJECT_STRUCTURE.md         # 项目结构文档（本文件）
├── pyproject.toml               # Python项目配置
├── README.md                    # 项目说明
├── start.ps1                    # Windows启动脚本
└── stop.ps1                     # Windows停止脚本
```

## 模块说明

### 前端 (frontend/)
- **src/apis/**: API请求封装
- **src/components/**: React组件（包括shadcn/ui组件库）
- **src/pages/**: 页面级组件
- **src/utils/**: 前端工具函数
- **Vite**: 构建工具，提供快速的开发体验

### 后端 (server/)
- **chatbox/**: 聊天机器人核心模块，基于LangGraph实现
  - chat_agents/: 智能体图结构和检索逻辑
  - api/: FastAPI路由和端点
  - core/: 配置和日志
- **report_pipeline/**: 论文报告生成流水线
  - ArXiv下载、数据摄入、邮件发送
- **managers/**: 业务逻辑管理器（文件管理等）
- **models/**: 数据库模型定义（SQLAlchemy）
- **utils/**: 通用工具函数（ArXiv查询、LaTeX处理等）

### 配置文件
- **.env.example**: 环境变量模板（安全上传到Git）
- **CONFIG_GUIDE.md**: 配置指南文档
- **docker-compose.yml**: Docker容器编排（PostgreSQL数据库）
- **langgraph.json**: LangGraph智能体配置
- **pyproject.toml**: Python项目元数据和依赖
- **server/config.py**: 全局配置（路径、模型、流水线参数）
- **server/chatbox/core/config.py**: 聊天模块配置（CORS、数据库、模型）
