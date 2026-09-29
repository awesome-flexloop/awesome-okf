---
type: concept
scope: awesome-deepseek-agent
name: integration-categories
description: awesome-deepseek-agent 收录工具的四大分类——IDE 插件、CLI 工具、聊天客户端、Agent 平台
---

# 集成分类

awesome-deepseek-agent 收录的工具按使用场景分为四大类。

## IDE 插件

直接嵌入代码编辑器的 AI 编程助手，在编码过程中提供实时补全、重构、调试等功能。

| 工具 | 编辑器 | 特点 |
|---|---|---|
| **Cline** | VS Code | 支持多种 API 供应商的自主编程 Agent，可执行终端命令、创建/编辑文件 |
| **GitHub Copilot** | VS Code/JetBrains 等 | 最广泛使用的 AI 编程助手，通过自定义模型配置接入 DeepSeek |
| **Kilo Code** | VS Code | 开源 AI 编程助手，支持 CLI 和编辑器双模式 |

**接入方式**：通常在插件设置中配置自定义 API endpoint 和 API Key，指向 DeepSeek 的 OpenAI 兼容接口。

## 终端 CLI 工具

在命令行终端中运行的 AI 编程 Agent，适合习惯终端工作流的开发者。

| 工具 | 核心特点 |
|---|---|
| **Claude Code** | Anthropic 官方终端助手，支持通过配置切换到 DeepSeek |
| **Codex** | OpenAI 编程 Agent，支持自定义模型提供商 |
| **Crush** | 华丽的 TUI 界面，多模型支持，LSP 集成 |
| **Deep Code** | 专为 DeepSeek-V4 适配，深度思考+推理强度控制+Agent Skills |
| **DeepSeek-TUI** | Rust 编写，Codex 风格，沙箱执行，MCP 客户端+服务器，1M 上下文 |
| **GitHub Copilot CLI** | GitHub 官方终端助手，Agent 模式支持 |
| **Langcli** | 100% 兼容 Claude Code，支持 DeepSeek V4 等主流模型 |
| **OpenCode** | 开源、终端+网页多形态 |
| **Pi** | 极简框架，树状会话，自定义供应商 |
| **Qwen Code** | 阿里通义团队出品，内置 DeepSeek 支持 |
| **Reasonix** | DeepSeek 原生，Cache-First 循环，MCP 原生 |
| **Oh My Pi** | Pi 的增强分支，专用工具+模型角色+MCP+插件 |

**接入方式**：通过环境变量或配置文件设置 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 指向 DeepSeek API。

## 桌面/聊天客户端

图形界面的 AI 对话客户端，适合非编程场景或多模型切换使用。

| 工具 | 平台 | 特点 |
|---|---|---|
| **Cherry Studio** | Windows/macOS/Linux | 开源跨平台桌面客户端，300+ 助手，MCP、知识库、多模型对话 |
| **WorkBuddy/CodeBuddy** | 跨平台 | 支持自定义 OpenAI 兼容模型配置 |

**接入方式**：在客户端的模型供应商设置中添加自定义 OpenAI 兼容 API，填入 DeepSeek 的 endpoint 和 key。

## AI Agent 框架与平台

可扩展的 Agent 框架和平台，支持接入聊天工具、构建自定义工作流。

| 工具 | 类型 | 特点 |
|---|---|---|
| **AstrBot** | 聊天平台 Agent | 支持 QQ、微信、飞书等多平台接入，Skill+插件+MCP 扩展 |
| **Hermes** | 自我进化 Agent | Nous Research 出品，自动改进自身能力 |
| **LobeHub** | Agent 运营平台 | Agent 团队管理、调度、报告，7×24 自动化运营 |
| **nanobot** | 轻量 Agent | 开源轻量级，聊天集成+记忆+MCP |
| **OpenClaw** | 个人助手 | 飞书/微信接入，Skill 扩展 |

**接入方式**：在 Agent 框架的 LLM 配置中添加 DeepSeek 作为底层模型提供商。

## 快速选择指南

```
你在哪个场景使用 DeepSeek？
│
├── 写代码时随用随问
│   ├── VS Code 用户 → Cline / GitHub Copilot / Kilo Code
│   └── JetBrains 用户 → GitHub Copilot
│
├── 终端工作流爱好者
│   ├── DeepSeek 深度用户 → Deep Code / Reasonix / DeepSeek-TUI
│   ├── Claude Code 兼容需求 → Langcli
│   ├── 极简主义 → Pi
│   └── 功能全面 → Crush / OpenCode
│
├── 桌面 GUI 偏好
│   └── Cherry Studio
│
└── 构建 AI 助手/Agent
    ├── 接入聊天工具(QQ/微信/飞书) → AstrBot / OpenClaw
    ├── 轻量快速 → nanobot
    ├── 研究/自进化 → Hermes
    └── Agent 团队管理 → LobeHub
```
