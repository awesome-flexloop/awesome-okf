---
title: libs/ARCHITECTURE.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/ARCHITECTURE.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/ARCHITECTURE.md
---

# libs/ARCHITECTURE.md 引用

Deep Agents 运行时结构和 SDK 起点的架构文档。

## 核心内容

- **三层架构**：Deep Agents（有主见的框架）→ LangChain（Agent 抽象）→ LangGraph（运行时）
- **构造阶段**：`create_deep_agent()` 解析模型/后端、组装中间件栈、构建子 Agent、组合提示、委托给 `create_agent()`
- **执行阶段**：LangGraph 驱动 Agent 循环，模型接收消息历史/系统提示/工具集，工具结果追加到状态，循环直到最终响应
- **中间件栈**：基础脚手架 → 调用者中间件 → 配置文件/尾部中间件；子 Agent 有自己的中间件栈
- **工具表面**：内置中间件贡献标准工具，调用者 tools= 添加，后端决定 Shell 可用性，配置文件可排除工具，权限在调用时强制执行
- **状态与持久化**：`DeepAgentState` 使用 DeltaChannel reducer；图状态/检查点来自 LangGraph，文件系统/记忆持久化来自后端
- **常见起点**：`graph.py`（构造）、`middleware/`（工具可见性/提示注入）、`backends/`（持久化/Shell）、`profiles/`（提供商调优）、`__init__.py`（公共导出）

## 相关概念

- 核心SDK与三层架构
