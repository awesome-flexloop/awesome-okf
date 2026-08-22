---
type: Example
title: 基本使用
description: 从安装配置到交互式和非交互模式的基本使用示例，涵盖 API Key 配置、会话管理和 MCP 服务器配置。
tags: [deepcode-cli, 示例, 快速开始, 基础用法]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: deepcode-cli 源码信源
---

# 基本使用

## 前置条件

- Node.js >= 22
- npm >= 10.9.4
- DeepSeek API Key

## 步骤 1：安装

从源码构建并全局链接：

```bash
git clone https://github.com/lessweb/deepcode-cli.git
cd deepcode-cli
npm install
npm run build
npm link
```

验证安装：

```bash
deepcode --version
```

## 步骤 2：配置 API Key

创建用户级配置文件 `~/.deepcode/settings.json`：

```json
{
  "env": {
    "BASE_URL": "https://api.deepseek.com",
    "API_KEY": "sk-xxxxxxxxxxxx"
  }
}
```

默认模型为 `deepseek-v4-flash`。可通过 `MODEL` 环境变量或 `model` 字段切换：

```json
{
  "env": {
    "BASE_URL": "https://api.deepseek.com",
    "API_KEY": "sk-xxxxxxxxxxxx",
    "MODEL": "deepseek-v4-pro"
  },
  "thinkingEnabled": true,
  "reasoningEffort": "max"
}
```

也可通过 `DEEPCODE_` 前缀的环境变量覆盖配置：

```bash
export DEEPCODE_MODEL=deepseek-v4-pro
export DEEPCODE_API_KEY=sk-xxxxxxxxxxxx
deepcode
```

## 步骤 3：启动交互式 TUI

在项目目录中直接运行：

```bash
cd /path/to/your/project
deepcode
```

启动后可直接输入提示并按 Enter 发送。输入 `/` 打开斜杠命令菜单。

### 常用斜杠命令

```
/model     选择模型和思考模式
/plan      切换 Plan Mode
/new       开始新对话
/mcp       查看 MCP 服务器状态
/skills    列出可用技能
/undo      回退到历史检查点
/exit      退出
```

## 步骤 4：非交互模式

使用 `--exec`（`-x`）运行单次提示，不启动 TUI：

```bash
deepcode -x -p "列出当前目录下的所有 TypeScript 文件"
```

管道输入作为附加上下文：

```bash
cat package.json | deepcode -x -p "这个项目的主要依赖是什么？"
```

非交互模式的退出码：
- `0`：成功
- `1`：失败
- `130`：被中断（Ctrl+C）

## 步骤 5：会话管理

### 恢复最近会话

```bash
deepcode --last
```

### 恢复指定会话

```bash
deepcode --resume 123e4567-e89b-12d3-a456-426614174000
```

### 从会话分叉

```bash
deepcode --fork 123e4567-e89b-12d3-a456-426614174000
```

### 非交互模式下恢复会话

```bash
deepcode -x --resume 123e4567-e89b-12d3-a456-426614174000 -p "继续之前的工作"
```

## 步骤 6：配置 MCP 服务器

编辑 `~/.deepcode/settings.json`，添加 `mcpServers` 字段：

```json
{
  "env": {
    "BASE_URL": "https://api.deepseek.com",
    "API_KEY": "sk-xxxxxxxxxxxx"
  },
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

启动后在 TUI 中输入 `/mcp` 查看服务器状态和工具列表。MCP 工具以 `mcp__<服务器名>__<工具名>` 格式调用，例如 `mcp__github__search_code`。

## 步骤 7：配置项目级权限

在项目根目录创建 `.deepcode/settings.json`，配置权限策略：

```json
{
  "permissions": {
    "allow": ["read-in-cwd", "query-git-log"],
    "deny": ["delete-out-cwd"],
    "ask": ["write-out-cwd", "network", "mcp"],
    "defaultMode": "allowAll"
  }
}
```

在不可信环境中使用更严格的策略：

```json
{
  "permissions": {
    "defaultMode": "askAll",
    "deny": ["delete-out-cwd", "mutate-git-log"]
  }
}
```

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [CLI 命令与会话管理](/concepts/04-cli-commands.md)
- [权限系统](/concepts/02-permission-system.md)
- [MCP 集成](/concepts/03-mcp-integration.md)
