---
title: libs/code/ARCHITECTURE.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/code/ARCHITECTURE.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/code/ARCHITECTURE.md
---

# libs/code/ARCHITECTURE.md 引用

Deep Agents Code 包的架构概述。

## 核心内容

- **包定位**：基于 deepagents SDK 构建的预构建终端编码 Agent，是一个参考实现
- **双半架构**：
  - 终端客户端：呈现交互式/headless 输出，收集用户输入和审批
  - Agent 服务器：运行编码 Agent 图，连接模型/工具/记忆/技能/后端
  - 通过流式协议通信，分离使 UI 响应且 Agent 核心可独立测试
- **请求流程**：客户端接收输入 → 发送到服务器 → 服务器运行 Agent 流式返回事件 → 客户端渲染并收集人工响应 → 会话状态保留
- **配置分层**：用户、项目、会话、运行时四个作用域
- **扩展点**：技能和子 Agent、工具和 MCP 服务器、沙箱、Hooks 和命令
- **设计权衡**：优化响应式终端体验、可复用 Agent 核心、持久会话、受控工具执行；代价是客户端/服务器边界
- **调试指引**：先判断故障属于哪一侧——呈现/输入属客户端，模型执行/工具/记忆/图启动属服务器
- **相关文档**：DEVELOPMENT.md（本地设置）、COMMANDS.md（命令行为）、HOOKS.md（生命周期钩子）、PRICING.md（成本估算）、THREAT_MODEL.md（安全边界）

## 相关概念

- [Code终端编码Agent](/datawhale/deepagents/concepts/code-module)
