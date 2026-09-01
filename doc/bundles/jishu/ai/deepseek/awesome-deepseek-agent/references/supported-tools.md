---
type: reference
scope: awesome-deepseek-agent
name: supported-tools
description: awesome-deepseek-agent 收录的所有支持 DeepSeek 模型的工具与平台列表
---

# 支持的工具与平台

awesome-deepseek-agent 收录了将 DeepSeek 模型（主要是 DeepSeek-V4-Pro 和 DeepSeek-V4-Flash）集成到主流 AI Agent 和编程助手工具的指南。以下是完整工具列表。

## IDE 插件

| 工具 | 类型 | 简介 |
|---|---|---|
| **Cline** | VS Code 扩展 | 支持多种 API 供应商的 AI 编程助手 |
| **GitHub Copilot** | VS Code 内置 | 内置于 VS Code 的 AI 结对编程助手 |
| **Kilo Code** | CLI + 编辑器扩展 | 支持 CLI 和编辑器扩展的 AI 编程助手 |

## 终端 CLI 工具

| 工具 | 语言/架构 | 简介 |
|---|---|---|
| **Claude Code** | - | 运行在终端内的 AI 编程助手 |
| **Codex** | - | OpenAI 的编程 Agent |
| **Crush** | - | 华丽的开源终端 AI 编程 Agent，支持多模型与 LSP 集成 |
| **Deep Code** | - | 专为 DeepSeek-V4 适配的终端编程助手，支持深度思考、推理强度控制与 Agent Skills |
| **DeepSeek-TUI** | Rust | 面向 DeepSeek-V4 的 Rust 终端编程助手，Codex 风格架构，沙箱化工具，MCP 客户端+服务器，100万 token 上下文 |
| **GitHub Copilot CLI** | - | 终端原生 AI 编程助手，支持 Agent 能力 |
| **Langcli** | - | 100% 兼容 Claude Code、支持 DeepSeek V4 等主流 LLM 的开源编程助手 |
| **OpenCode** | - | 开源 AI 编程助手，提供终端、网页等多种运行形式 |
| **Pi** | - | 极简且高度可扩展的终端编码框架，支持树状会话和自定义供应商 |
| **Qwen Code** | - | 阿里巴巴通义千问团队 Coding Agent CLI，内置 DeepSeek 提供商支持 |
| **Reasonix** | - | DeepSeek 原生编程 Agent，Cache-First 循环，原生支持 MCP |
| **Oh My Pi** | - | 基于 Pi 分支的终端 AI 编程 Agent，OMP 专用工具、模型角色、MCP、插件 |

## 桌面/聊天客户端

| 工具 | 平台 | 简介 |
|---|---|---|
| **Cherry Studio** | 跨平台桌面 | 开源跨平台桌面 AI 客户端，内置 300+ 助手、MCP 支持、知识库、多模型对话 |
| **WorkBuddy/CodeBuddy** | - | 支持自定义 OpenAI 兼容模型配置的 AI Agent 与编程助手 |

## AI Agent 框架与平台

| 工具 | 类型 | 简介 |
|---|---|---|
| **AstrBot** | 聊天平台 Agent | 开源 Agent 助手，支持 QQ、微信、飞书等消息平台，Skill/插件/MCP 扩展 |
| **Hermes** | Agent 框架 | Nous Research 开发的开源自我进化 AI 助手 |
| **LobeHub** | Agent 运营平台 | Chief Agent Operator，通过招聘、排班、报告组织 AI 团队 7×24 运作 |
| **nanobot** | 轻量 Agent | 开源轻量级 AI 智能体，支持聊天平台集成、记忆、MCP |
| **OpenClaw** | 聊天平台助手 | 开源个人 AI 助手，接入飞书/微信，Skill 扩展 |

## 相关资源

- [DeepSeek 开放平台](https://platform.deepseek.com/) — 获取 API Key
- [DeepSeek API 文档](https://api-docs.deepseek.com/zh-cn/) — API 参考与使用指南

## 指南文件

所有工具的接入指南位于仓库 `docs/` 目录，提供中英文版本：

```
docs/
├── astrbot.md / astrbot.zh-CN.md
├── cherry_studio.md / cherry_studio.zh-CN.md
├── claude_code.md / claude_code.zh-CN.md
├── cline.md / cline.zh-CN.md
├── codex.md / codex.zh-CN.md
├── copilot_cli.md / copilot_cli.zh-CN.md
├── crush.md / crush.zh-CN.md
├── deepcode.md / deepcode.zh-CN.md
├── deepseek-tui.md / deepseek-tui.zh-CN.md
├── github_copilot.md / github_copilot.zh-CN.md
├── hermes.md / hermes.zh-CN.md
├── kilo_code.md / kilo_code.zh-CN.md
├── langcli.md / langcli.zh-CN.md
├── lobehub.md / lobehub.zh-CN.md
├── nanobot.md / nanobot.zh-CN.md
├── oh-my-pi.md / oh-my-pi.zh-CN.md
├── openclaw.md / openclaw.zh-CN.md
├── opencode.md / opencode.zh-CN.md
├── pi_mono.md / pi_mono.zh-CN.md
├── qwen_code.md / qwen_code.zh-CN.md
├── reasonix.md / reasonix.zh-CN.md
└── workbuddy.md / workbuddy.zh-CN.md
```
