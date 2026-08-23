---
title: 第六章 框架开发实践
type: reference
bundle: /datawhale/hello-agents
chapter: 6
part: 第二部分：构建你的大语言模型智能体
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter6/第六章%20框架开发实践.md
---

# 第六章 框架开发实践

## 章节概要

本章实战体验AutoGen、AgentScope、CAMEL、LangGraph四个主流Agent框架，理解不同框架的设计理念和协作模式。

## 核心知识点

### 框架的价值
1. **代码复用与效率**：封装Agent Loop核心循环
2. **组件解耦**：模型层/工具层/记忆层分离，可独立替换
3. **状态管理**：上下文窗口、历史持久化、多轮跟踪
4. **可观测性**：事件回调（on_llm_start、on_tool_end等）

### AutoGen（微软）
- **版本**：以0.7.4为例，架构重构
- **核心理念**：对话驱动协作
- **架构**：
  - `autogen-core`：底层基础（LLM交互、消息传递）
  - `autogen-agentchat`：高级对话式接口
  - 异步优先（async/await）
- **核心组件**：
  - AssistantAgent：LLM驱动的任务解决者
  - UserProxyAgent：用户代言人+代码/工具执行器
  - RoundRobinGroupChat：轮询群聊协调
- **实战案例**：模拟软件开发团队（产品经理→工程师→审查员）

### AgentScope（阿里巴巴）
- **定位**：多智能体应用开发平台
- **特点**：易用性+工程化
- **核心能力**：
  - 友好编程接口
  - 内置消息传递机制
  - 分布式部署支持
- **适用**：大规模多Agent系统构建与运维

### CAMEL
- **核心理念**：角色扮演（Role-Playing）协作
- **关键机制**：初始提示（Inception Prompting）
- **工作方式**：设定两个Agent角色和共同任务，自主多轮对话
- **价值**：极大降低多Agent对话流程设计复杂度

### LangGraph（LangChain生态）
- **核心理念**：图结构建模Agent执行流程
- **核心抽象**：
  - 节点（Node）：操作步骤（调用LLM、执行工具）
  - 边（Edge）：跳转逻辑，支持条件分支
  - 循环（Cycles）：原生支持迭代修正
- **优势**：Reflection等迭代工作流实现直观
- **适用**：复杂控制流、条件分支、循环修正场景

### 四框架对比

| 框架 | 协作模式 | 架构特点 | 分布式 |
|------|---------|---------|--------|
| AutoGen | 对话驱动/群聊 | 分层+异步 | 支持 |
| AgentScope | 消息传递 | 工程化平台 | 原生支持 |
| CAMEL | 角色扮演 | 双Agent自主对话 | 有限 |
| LangGraph | 图结构工作流 | 节点+边+循环 | 有限 |

## 相关概念
- [Agent框架开发](/datawhale/hello-agents/concepts/agent-framework-development)
- [多Agent协作](/datawhale/hello-agents/concepts/multi-agent-collaboration)
