---
title: Deep Agents 实战
type: index
bundle: deepagents-in-action
description: Datawhale 出品的 Deep Agents 实战教程，基于 LangChain/LangGraph 生态系统构建生产级 AI Agent，覆盖 Agent Harness 认知、虚拟文件系统、子Agent编排、长期记忆、人机协作、沙箱执行、MCP协议、评分量规与流式传输等14个核心主题。
concepts:
  - /datawhale/deepagents-in-action/concepts/agent-harness
  - /datawhale/deepagents-in-action/concepts/virtual-filesystem-context-engineering
references:
  - /datawhale/deepagents-in-action/references/readme-source
examples:
  - /datawhale/deepagents-in-action/examples/index
---

# Deep Agents 实战

**基于 LangChain / LangGraph 生态，系统构建生产级 AI Agent**

《Deep Agents 实战》是由沧海九粟（LangChain 官方认证大使）出品、Datawhale 开源的实战教程。课程以 Deep Agents（≥0.5）为核心，系统讲授如何在 LangChain/LangGraph 之上构建生产级 AI Agent 所需的横切能力——上下文工程、任务规划、子Agent委派、长期记忆、权限控制、沙箱执行、人机协作、MCP工具生态、自我迭代与流式观测。

> 📺 配套视频发布于 [B站](https://space.bilibili.com/28357052/lists/7757577?type=season)，图文发布于小红书，课程网站部署在 [GitHub Pages](https://datawhalechina.github.io/deepagents-in-action/)。

## 知识地图

### 核心概念

- [Agent Harness——从框架到运行时外壳](concepts/agent-harness.md)——Deep Agents 的核心定位：不重新发明 Agent 循环，而是为 LangGraph 补充生产级横切能力
- [虚拟文件系统与 Context Engineering](concepts/virtual-filesystem-context-engineering.md)——Deep Agents 的上下文工程核心，以 FilesystemBackend 为底座支撑内容落盘、Skills 加载与长期记忆

### 示例

- [示例索引](examples/index.md)——基于 AgentSeek 模板系统的7种可运行项目模板，覆盖14章实验场景

### 信源

- [GitHub 仓库信源](references/readme-source.md)——项目官方仓库地址、版本要求、章节结构与技术栈

## 课程结构

### 准备篇——环境搭建

基于 [AgentSeek](https://github.com/ob-labs/agentseek) 工程化套件快速搭建开发环境，掌握 `agentseek create/info/task/doctor/dev` 统一生命周期入口。

### 认知篇（第1-2章）

- 第1章：从 Agent Framework 到 Agent Harness 的诞生逻辑
- 第2章：5分钟构建第一个 Deep Agent

### 核心篇（第3-6章）

- 第3章：虚拟文件系统——Context Engineering 核心
- 第4章：任务规划与分解（write_todos）
- 第5章：子Agent与上下文隔离
- 第6章：异步子Agent（AsyncSubAgent）

### 进阶篇（第7-12章）

- 第7章：Skills——可复用的Agent能力包
- 第8章：长期记忆（CompositeBackend/StoreBackend）
- 第9章：Human-in-the-Loop（interrupt_on）
- 第10章：沙箱执行（Daytona/LangSmith Sandbox）
- 第11章：文件系统权限（FilesystemPermission）
- 第12章：MCP 标准协议工具生态

### 前沿预览（第13-14章）

- 第13章：Grading Rubrics 评分量规——按验收标准自我迭代
- 第14章：Event Streaming v3——实时观测主Agent、子Agent与工具调用

## AgentSeek 模板体系

| 模板 | 适用章节 | 用途 |
|------|----------|------|
| deepagents/default | 第1、2章 | 最小 Deep Agent 项目 |
| deepagents/content-builder | 第3、7、8、11章 | 内容构建（文件系统、Skills、记忆、权限） |
| deepagents/research | 第4、5、6章 | 研究类（规划、子Agent、异步） |
| deepagents/mcp | 第9、12章 | MCP协议（HITL、工具生态） |
| deepagents/sandbox | 第10章 | 沙箱代码执行 |
| deepagents/streaming | 第14章 | Event Streaming v3 |
| langchain/rubric | 第13章 | 评分量规自我迭代 |

## 外部链接

- GitHub 仓库：https://github.com/datawhalechina/deepagents-in-action
- 课程网站：https://datawhalechina.github.io/deepagents-in-action/
- Deep Agents 官方文档：https://docs.langchain.com/oss/python/deepagents/overview
- 开源协议：CC BY-NC-SA 4.0（内容）/ MIT（代码）

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
