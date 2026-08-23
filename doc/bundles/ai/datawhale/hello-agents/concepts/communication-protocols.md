---
title: 通信协议 MCP A2A ANP
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/multi-agent-collaboration
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/references/chapter10-communication-protocols
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/第十章%20智能体通信协议.md
---

# 通信协议：MCP / A2A / ANP

智能体通信协议是连接Agent与外部世界、Agent与Agent之间的标准化基础设施。Hello-Agents教程讲解了三种互补的协议，构成从工具访问到大规模Agent网络的完整通信栈。

## 为何需要通信协议

没有协议时，每接入一个新外部服务就要编写专门的Tool类，导致：
- 代码重复（每个工具都要处理HTTP请求、错误处理、认证）
- 难以维护（API变更需修改所有相关工具）
- 无法复用（不同开发者的工具无法直接使用）
- 扩展性差（添加新服务需要大量编码）

通信协议的核心价值：**标准化接口**、**互操作性**、**动态发现**、**可扩展性**。如同互联网的TCP/IP协议让不同设备无需专门适配即可通信。

## MCP：智能体与工具的桥梁

**MCP（Model Context Protocol）** 由Anthropic团队提出，标准化智能体与外部工具/资源的通信方式。

### 设计哲学
"上下文共享"——不仅是RPC协议，更允许Agent和工具之间共享丰富的上下文信息。当Agent访问代码仓库时，MCP服务器不仅提供文件内容，还提供代码结构、依赖关系、提交历史等上下文。

### 解决的问题
将N×M的适配器问题（N个Agent × M个工具）降维为N+M的标准化连接。所有服务以相同方式被访问，无需为每个服务编写专门适配器。

### 典型应用
- 文件系统访问
- 数据库查询
- GitHub/GitLab等代码托管平台
- Slack等通信工具
- 天气、地图等API服务

## A2A：智能体间的对话

**A2A（Agent-to-Agent Protocol）** 由Google团队提出，实现智能体之间的点对点通信。

### 设计哲学
"对等通信"——每个Agent既是服务提供者，也是服务消费者。Agent可以主动发起请求，也可以响应其他Agent的请求，避免中心化协调器瓶颈。

### 与MCP的区别
- MCP关注**Agent与工具**的通信（Agent是主动方，工具是被动方）
- A2A关注**Agent与Agent**的通信（双方都是主动的、对等的）
- A2A支持对话、协商、辩论等人际协作模式

### 典型应用
- 多角色团队协作（研究员+撰写员+编辑）
- Agent间任务委派与协商
- 分布式问题求解

## ANP：智能体网络的基础设施

**ANP（Agent Network Protocol）** 是开源社区维护的概念性协议框架，构建大规模智能体网络。

### 设计哲学
"去中心化服务发现"——在包含成百上千个Agent的网络中，提供服务注册、发现和路由机制，让Agent动态发现网络中的服务，无需预先配置所有连接关系。

### 三层定位
- MCP解决"如何访问工具"
- A2A解决"如何与其他Agent对话"
- ANP解决"如何在大规模网络中发现和连接Agent"

## 三协议对比

| 维度 | MCP | A2A | ANP |
|------|-----|-----|-----|
| 提出方 | Anthropic | Google | 开源社区 |
| 通信对象 | Agent ↔ 工具/资源 | Agent ↔ Agent | Agent网络 |
| 设计哲学 | 上下文共享 | 对等通信 | 去中心化发现 |
| 成熟度 | 生态相对成熟 | 发展中 | 概念阶段 |
| 类比 | USB-C接口 | 人与人对话 | 互联网DNS/路由 |
| 选型建议 | 访问外部服务 | 多Agent协作 | 大规模生态系统 |

## HelloAgents协议架构

采用三层设计：

1. **协议实现层**：
   - MCP基于FastMCP库，提供客户端和服务器功能
   - A2A基于Google官方a2a-sdk
   - ANP为自研轻量级实现（概念模拟）

2. **工具封装层**：
   - MCPTool、A2ATool、ANPTool都继承自BaseTool
   - 提供一致的`run()`方法
   - Agent以相同方式使用不同协议

3. **智能体集成层**：
   - 协议工具注册到Agent的工具系统
   - Agent通过统一工具调用接口使用协议能力

## 相关阅读

- [第十章 智能体通信协议](/ai/datawhale/hello-agents/references/chapter10-communication-protocols)
- [多Agent协作](/ai/datawhale/hello-agents/concepts/multi-agent-collaboration)
- [Agent框架开发](/ai/datawhale/hello-agents/concepts/agent-framework-development)
