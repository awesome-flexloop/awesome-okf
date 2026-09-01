---
title: Cookbook 模式目录
type: reference
bundle: pocketflow-patterns
source: cookbook/
---

# Cookbook 模式目录

PocketFlow 官方 cookbook 包含 40+ 示例，按设计模式分类如下。

## Agent 类

| 示例目录 | 说明 | 核心模式 |
|---------|------|---------|
| pocketflow-agent | 基础研究Agent | Agent循环（决策→搜索→回答） |
| pocketflow-deep-research | 深度研究 | 多层Agent循环+摘要 |
| pocketflow-browser-agent | 浏览器Agent | Agent循环+视觉/DOM工具 |
| pocketflow-coding-agent | 编码Agent | Agent+代码执行工具 |
| pocketflow-thinking | 思维链推理 | Agent循环+思维过程 |
| pocketflow-heartbeat | 心跳检查 | Agent循环+状态监控 |

## 多智能体类

| 示例目录 | 说明 | 核心模式 |
|---------|------|---------|
| pocketflow-multi-agent | Taboo游戏 | 双Agent+Queue通信 |
| pocketflow-supervisor | 监督Agent | 外层监督+内层Agent |
| pocketflow-debate | 辩论 | 双Agent对抗+评判 |
| pocketflow-communication | Agent通信 | 消息传递模式 |
| pocketflow-a2a | Agent-to-Agent | A2A协议实现 |
| pocketflow-majority-vote | 多数投票 | 多Agent投票决策 |
| pocketflow-judge | 评判节点 | Agent输出审核 |

## RAG 类

| 示例目录 | 说明 | 核心模式 |
|---------|------|---------|
| pocketflow-rag | 基础RAG | 离线+在线双Flow |
| pocketflow-agentic-rag | Agentic RAG | RAG+Agent循环 |
| pocketflow-chat-memory | 聊天记忆 | RAG+对话历史 |
| pocketflow-notebook-lm | NotebookLM | RAG+播客生成 |

## MapReduce / 批量类

| 示例目录 | 说明 | 核心模式 |
|---------|------|---------|
| pocketflow-map-reduce | 简历评估 | BatchNode MapReduce |
| pocketflow-batch-node | CSV批量处理 | BatchNode |
| pocketflow-batch-flow | 图片批量处理 | BatchFlow |
| pocketflow-nested-batch | 嵌套批量 | 嵌套BatchFlow |
| pocketflow-parallel-batch | 并行翻译 | AsyncParallelBatchNode |
| pocketflow-parallel-batch-flow | 并行图片处理 | AsyncParallelBatchFlow |

## Workflow/HITL 类

| 示例目录 | 说明 | 核心模式 |
|---------|------|---------|
| pocketflow-cli-hitl | CLI交互 | 命令行人机交互 |
| pocketflow-fastapi-hitl | FastAPI交互 | Web HITL |
| pocketflow-fastapi-background | 后台任务 | 异步后台+进度 |
| pocketflow-fastapi-websocket | WebSocket | 流式交互 |
| pocketflow-gradio-hitl | Gradio界面 | GUI HITL |
| pocketflow-streamlit-fsm | Streamlit FSM | 状态机交互 |
| pocketflow-chat | 基础聊天 | 简单对话循环 |
| pocketflow-chat-guardrail | 安全护栏 | 聊天+内容审核 |

## Tool Use 类

| 示例目录 | 说明 | 核心模式 |
|---------|------|---------|
| pocketflow-code-generator | 代码生成 | 代码执行工具 |
| pocketflow-google-calendar | 日历工具 | Google Calendar API |
| pocketflow-mcp | MCP工具 | MCP协议 |
| pocketflow-text2sql | Text2SQL | SQL执行工具 |
| pocketflow-invoice | 发票生成 | PDF生成工具 |
| pocketflow-self-healing-mermaid | 自愈Mermaid | 代码生成+验证循环 |

## 基础示例

| 示例目录 | 说明 |
|---------|------|
| pocketflow-hello-world | Hello World |
| pocketflow-node | 单节点基础 |
| pocketflow-flow | 流程基础 |
| pocketflow-async-basic | 异步基础 |
| pocketflow-batch | 批量基础 |
| pocketflow-structured-output | 结构化输出 |
| pocketflow-llm-streaming | LLM流式输出 |
| pocketflow-agent-skills | Agent技能系统 |
| pocketflow-newsletter | 新闻通讯生成 |
| pocketflow-lead-generation | 线索生成 |
| pocketflow-tao | TAO推理 |
