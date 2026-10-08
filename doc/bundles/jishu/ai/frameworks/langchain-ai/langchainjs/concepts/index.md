# LangChain.js 核心概念

- 总览 — LangChain.js 是什么、架构分层、设计哲学与组件生态
- Runnable 接口 — 统一执行抽象、四维调用模型、LCEL 组合子与配置传播
- 消息系统 — BaseMessage 类型层次、tool_call 一等公民、多模态内容块
- 工具定义 — StructuredTool 类层次、Zod/JSON Schema 双轨制、tool 工厂
- 提示模板 — PromptTemplate、ChatPromptTemplate、MessagesPlaceholder
- ReAct Agent — createAgent、LangGraph 图拓扑、状态管理与结构化输出
- Middleware — Agent 横切扩展、六钩子织入、洋葱模型与内置中间件
- Document 与 Embedding — 文档数据模型、向量化抽象与 RAG 基础

```{toctree}
:hidden:
:maxdepth: 7

document-embedding
message-system
middleware
overview
prompt-templates
react-agent
runnable-interface
tool-definition
```
