---
title: 第十章 智能体通信协议
type: reference
bundle: /datawhale/hello-agents
chapter: 10
part: 第三部分：高级知识扩展
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter10/第十章%20智能体通信协议.md
---

# 第十章 智能体通信协议

## 章节概要

本章讲解MCP、A2A、ANP三种通信协议，它们分别解决Agent-工具、Agent-Agent、Agent网络三个层次的通信标准化问题。

## 核心知识点

### 通信协议的核心价值
解决没有协议时的N×M适配器问题：
- 代码重复（HTTP、错误处理、认证）
- 难以维护（API变更影响所有工具）
- 无法复用（不同开发者的工具不兼容）
- 扩展性差（新服务需大量编码）

协议提供：标准化接口、互操作性、动态发现、可扩展性。

### MCP（Model Context Protocol）
- **提出方**：Anthropic
- **定位**：智能体与外部工具/资源的标准化通信
- **哲学**："上下文共享"，不仅是RPC，还共享丰富上下文信息
- **解决**：Agent如何统一访问文件系统、数据库、API等外部服务
- **类比**：USB-C接口统一外设连接
- **生态**：相对成熟，推荐选择大公司背书的MCP工具

### A2A（Agent-to-Agent Protocol）
- **提出方**：Google
- **定位**：智能体间点对点通信
- **哲学**："对等通信"，每个Agent既是提供者也是消费者
- **解决**：Agent如何像人类团队一样对话、协商、协作
- **特点**：避免中心化协调器瓶颈

### ANP（Agent Network Protocol）
- **维护方**：开源社区
- **定位**：大规模智能体网络基础设施
- **哲学**："去中心化服务发现"
- **解决**：成百上千Agent的网络中如何发现和连接服务
- **状态**：概念阶段，尚无成熟生态

### 三协议对比

| 维度 | MCP | A2A | ANP |
|------|-----|-----|-----|
| 通信对象 | Agent↔工具 | Agent↔Agent | Agent网络 |
| 哲学 | 上下文共享 | 对等通信 | 去中心化发现 |
| 成熟度 | 相对成熟 | 发展中 | 概念阶段 |
| 选型 | 访问外部服务 | 多Agent协作 | 大规模生态 |

### HelloAgents三层协议架构

**协议实现层**：
- MCP基于FastMCP库（客户端+服务器）
- A2A基于Google官方a2a-sdk
- ANP自研轻量级实现（概念模拟）

**工具封装层**：
- MCPTool、A2ATool、ANPTool均继承BaseTool
- 一致的`run()`方法

**智能体集成层**：
- 协议工具注册到Agent工具系统
- Agent通过统一接口使用协议

## 配套代码（code/chapter10/）
14个递进示例：从连接测试→MCP基础→GitHub MCP→Agent集成→多Agent协作→A2A客户端/服务器→ANP初始化/任务分发/负载均衡→天气MCP服务器

## 相关概念
- [通信协议](/datawhale/hello-agents/concepts/communication-protocols)
- [多Agent协作](/datawhale/hello-agents/concepts/multi-agent-collaboration)
