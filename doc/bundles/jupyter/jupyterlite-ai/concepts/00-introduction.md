---
type: Concept
title: JupyterLite AI 简介
description: jupyterlite-ai 是 JupyterLab/Notebook 7/JupyterLite 的浏览器端 AI 扩展，提供代码补全和智能聊天功能，支持多模型 Provider 和 MCP 协议
tags: [jupyterlite-ai, introduction, overview]
generated: { by: "ai:trae-claude", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: https://github.com/jupyterlite/ai
    title: jupyterlite/ai GitHub Repository
  - id: source
    resource: /references/source-code.md
    title: JupyterLite AI 源码参考
---

# JupyterLite AI 简介

jupyterlite-ai 是面向 JupyterLab 4.4+、Notebook 7.4+ 和 JupyterLite 的 AI 智能助手扩展。它在浏览器中直接运行，通过 Vercel AI SDK 对接多种大语言模型，为用户提供代码补全、智能对话、命令执行和网页抓取等能力。

## 核心特性

- **多模型支持**：内置 Anthropic Claude、Google Gemini、Mistral AI、OpenAI GPT 以及通用 OpenAI 兼容接口（支持 Ollama、LiteLLM 等本地部署）
- **代码智能补全**：在 Notebook 和编辑器中提供 AI 驱动的行内代码补全
- **智能聊天**：侧边栏和主区域双模式聊天面板，支持多会话管理
- **工具调用**：AI 可发现并执行 JupyterLab 命令、抓取网页内容、加载技能包
- **MCP 协议支持**：通过 Model Context Protocol 接入外部工具服务器
- **技能系统**：支持从文件系统加载 Markdown 格式的 AI 技能（SKILL.md）
- **Diff 预览**：代码修改提供 Cell/File 级别的 Diff 对比视图
- **JupyterLite 兼容**：完全在浏览器中运行，无需后端 Python 服务

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| AI 核心 | Vercel AI SDK (`ai` 包) | LLM 交互、Tool Loop、流式响应 |
| 模型适配 | @ai-sdk/* 系列包 | 各 Provider 的 SDK 适配 |
| UI 框架 | Lumino | Widget 生命周期、信号系统、命令系统 |
| IDE 平台 | JupyterLab 4.x | 插件系统、文档管理、状态栏 |
| 聊天组件 | @jupyter/chat | ChatWidget、MultiChatPanel、CRDT 同步 |
| 密钥管理 | jupyter-secrets-manager | API Key 安全存储 |
| 工具协议 | @ai-sdk/mcp + jupyter-mcp-manager | MCP 服务器连接与工具发现 |
| Schema 验证 | Zod | 工具输入参数验证 |
| 构建 | webpack + ts-jupyter | TypeScript 编译与 Lab Extension 打包 |

## 架构分层

jupyterlite-ai 采用清晰的三层架构：

1. **Agent 核心层** (`@jupyternaut/agent`)：AI 代理执行引擎，包含 Provider 管理、Tool 管理、Skill 管理、Agent 执行循环
2. **Persona 编排层** (`@jupyternaut/persona`)：JupyterLab 插件编排，注册所有核心服务（Provider、Tool、Skill、Agent 工厂、设置面板、代码补全）
3. **Chat UI 层** (`@jupyterlite/ai`)：聊天界面实现，包含多面板管理、工具栏、聊天命令、模型处理器

三层之间通过 Lumino Token 进行依赖注入，层间耦合度低，便于第三方扩展。

## 安装要求

- JupyterLab >= 4.4.0 或 Notebook >= 7.4.0
- Node.js（构建时需要）
- Python 3.8+（pip 安装）

```bash
# 安装扩展
pip install jupyterlite-ai

# 安装含 JupyterLab/JupyterLite/Notebook 的完整依赖
pip install jupyterlite-ai[jupyter]
```

## 相关概念

- [架构概览](01-architecture-overview.md)
- [Token 依赖注入系统](02-token-di-system.md)
- [Provider 模型管理](03-provider-system.md)
- [Tool 工具系统](04-tool-system.md)
