---
type: Concept
title: deepcode-cli 项目简介
description: deepcode-cli 是一个基于 DeepSeek V4 模型的终端 AI 编程助手，提供交互式 TUI、非交互执行模式、MCP 工具集成、会话持久化和权限控制系统。
tags: [deepcode-cli, 简介, 安装, 快速开始]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: deepcode-cli 源码信源
---

# deepcode-cli 项目简介

## 概述

deepcode-cli（包名 `@vegamo/deepcode-monorepo`）是一个终端 AI 编程助手，当前版本 `0.2.1`，采用 MIT 许可证。项目以 npm workspaces 组织为 monorepo，包含 CLI 工具、核心库和 VSCode 扩展三个子包。

项目仓库地址：`https://github.com/lessweb/deepcode-cli`

## 功能特性

### 交互式终端界面

CLI 基于 [Ink](https://github.com/vadimdemedes/ink)（React for CLI）构建终端 UI，支持：

- 多行输入与历史导航
- 模型选择、思考模式切换（`/model`）
- Plan Mode 计划模式（`/plan`）
- 斜杠命令菜单（输入 `/` 触发）
- 图片粘贴（`Ctrl+V`）
- Markdown 渲染

### 非交互执行模式

通过 `--exec`（`-x`）参数可在不启动 TUI 的情况下运行单次提示：

```bash
deepcode -x -p "解释这个错误"
```

支持管道输入作为附加上下文：

```bash
cat error.log | deepcode -x -p "Explain this error"
```

### MCP 工具集成

内置 MCP（Model Context Protocol）客户端，可连接外部工具服务器（GitHub、浏览器、文件系统、数据库等），工具以 `mcp__<服务器名>__<工具名>` 命名空间暴露。

### 会话持久化

会话自动保存到 `~/.deepcode/projects/<projectCode>/sessions-index.json`，支持：

- `--resume <sessionId>` 恢复指定会话
- `--last`（`-l`）恢复最近会话
- `--fork <sessionId>` 从已有会话分叉
- `/undo` 回退到历史检查点

### 权限控制

细粒度权限作用域涵盖文件读写、Git 操作、网络访问和 MCP 调用，支持 allow/deny/ask 三种策略和 `allowAll`/`askAll` 默认模式。

### 技能系统

支持从以下目录加载 SKILL.md 格式的技能：

- `~/.deepcode/skills/*/SKILL.md`（用户级原生技能）
- `./.deepcode/skills/*/SKILL.md`（项目级原生技能）
- `~/.agents/skills/*/SKILL.md`（用户级互操作技能）
- `./.agents/skills/*/SKILL.md`（项目级互操作技能）

## 安装

### 环境要求

- Node.js >= 22
- npm >= 10.9.4

### 从源码构建

```bash
git clone https://github.com/lessweb/deepcode-cli.git
cd deepcode-cli
npm install
npm run build
npm link
```

### 配置

首次使用前需配置 API Key。编辑 `~/.deepcode/settings.json`：

```json
{
  "env": {
    "BASE_URL": "https://api.deepseek.com",
    "API_KEY": "sk-xxxxxxxxxxxx"
  }
}
```

默认模型为 `deepseek-v4-flash`，默认上下文窗口为 262144 tokens（DeepSeek V4 模型为 1048576 tokens）。

## 相关概念

- [三包 monorepo 架构](/concepts/01-architecture.md)
- [权限系统](/concepts/02-permission-system.md)
- [MCP 集成](/concepts/03-mcp-integration.md)
- [CLI 命令与会话管理](/concepts/04-cli-commands.md)
