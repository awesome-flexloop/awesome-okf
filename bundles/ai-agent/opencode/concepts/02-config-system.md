---
type: Concept
title: 配置系统
description: OpenCode V2 配置规范，包括 opencode.json/jsonc 配置文件、.opencode 目录结构、env.d.ts 类型定义和 tui.json TUI 配置
tags: [config, opencode.json, opencode.jsonc, mcp, agents, providers, plugins]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - /references/source.md
---

# 配置系统

OpenCode V2 配置系统正在从旧版 `config.json` 迁移到新的 `opencode.json`/`opencode.jsonc` 格式。配置规范定义在 `specs/v2/config.md` 中，包含 11 个审查组。

## 配置文件发现

V2 core 从以下位置发现配置文档（`specs/v2/config.md:16`）：

1. 全局配置目录
2. 祖先项目目录
3. `.opencode` 配置目录

支持的文件名为 `opencode.json` 或 `opencode.jsonc`。旧版 `config.json` 文件名在 V2 中不被支持。

## .opencode 目录

项目根目录下的 `.opencode/` 目录包含：

| 文件/目录 | 用途 |
|----------|------|
| `opencode.jsonc` | 项目级 OpenCode 配置 |
| `tui.json` | TUI 插件配置 |
| `env.d.ts` | 环境类型声明（声明 `*.txt` 模块） |
| `agent/` | 自定义 agent 定义（如 `triage.md`） |
| `command/` | 自定义命令（如 ai-deps、changelog、commit、issues、learn、rmslop、translate） |
| `glossary/` | 多语言术语表（17 种语言） |
| `themes/` | 自定义主题（如 `mytheme.json`） |

### tui.json 结构

`.opencode/tui.json` 配置 TUI 插件数组：

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "plugin": [
    ["./plugins/tui-smoke.tsx", {
      "enabled": false,
      "label": "workspace",
      "keybinds": {
        "smoke_modal": "ctrl+alt+m",
        "smoke_screen": "ctrl+alt+o"
      }
    }]
  ]
}
```

每个插件条目是一个元组：`[插件路径, 选项对象]`。

### env.d.ts

`.opencode/env.d.ts` 为 TypeScript 提供文本模块声明：

```ts
declare module "*.txt" {
  const content: string
  export default content
}
```

这使得 agent prompt 模板文件（如 `compaction.txt`、`title.txt`）可以作为字符串导入。

## V2 配置字段组

### 组 1：文件元数据

- `$schema`：JSON Schema 引用，用于编辑器验证和补全。保留为只读元数据。

### 组 2：进程与服务器设置

| 字段 | 状态 | 说明 |
|------|------|------|
| `shell` | keep | 默认 shell，用于终端和 shell 工具执行 |
| `logLevel` | remove | 无配置消费者，日志从 CLI 输入初始化 |
| `server` | remove | 位置配置在服务器运行后才加载 |
| `autoupdate` | keep | 全局用户偏好，支持 `true`、`false`、`"notify"` |

### 组 3：命令与项目资源

| 字段 | 状态 | V2 变更 |
|------|------|---------|
| `command` | remove | 命名可复用工作流归入 skills |
| `skills` | redesign | 改为本地路径或远程 URL 发现源的简单数组 |
| `reference` | redesign | 重命名为复数 `references`，保留命名本地路径和 Git 仓库条目 |
| `instructions` | keep | 本地路径、glob 模式或远程 URL 数组，自动包含为模型上下文 |

### 组 4：插件

- `plugin` → `plugins`：保留有序加载，支持包字符串或 `{ package, options? }` 对象
- 配置的 `plugins` 列表仅代表包加载的插件
- 本地插件代码从 `.opencode/plugins/` 等目录发现

### 组 5：文件系统与工具运行时

| 字段 | V2 名称 | 说明 |
|------|---------|------|
| `watcher` | `watcher` | 文件系统监视器忽略模式 `{ ignore?: string[] }` |
| `snapshot` | `snapshots` | 文件系统快照（用于 undo/revert） |
| `formatter` | `formatter` | `boolean \| Record<string, entry>` |
| `lsp` | `lsp` | `boolean \| Record<string, entry>`，自定义服务器需声明 extensions |
| `attachment` | `attachments` | 图片处理限制 `{ image?: { auto_resize?, max_width?, max_height?, max_base64_bytes? } }` |
| `tool_output` | `tool_output` | 工具输出截断 `{ max_lines?, max_bytes? }` |

### 组 6：共享与身份

| 字段 | 说明 |
|------|------|
| `share` | `"manual"` \| `"auto"` \| `"disabled"` |
| `autoshare` | remove（使用 `share: "auto"` 替代） |
| `enterprise` | `{ url?: string }` 企业版共享服务端点 |
| `username` | 对话和遥测中的显示用户名 |

### 组 7：提供商与模型选择

- `provider` → `providers`（复数，无兼容别名）
- `disabled_providers`/`enabled_providers` → `experimental.policies` 策略规则
- `model`：默认模型回退
- `small_model`：remove（标题生成应配置 `title` agent）
- Provider/model/variant/options 作为部分补丁（partial patches）编写
- Provider `env` 为认可的凭证环境变量名列表

### 组 8：Agent 与权限

- `agent` → `agents`：命名 map，支持覆盖内置 agent 和定义自定义 agent
- `permission` → `permissions`：有序规则数组 `{ action, resource, effect }`，effect 支持 `"allow"`、`"deny"`、`"ask"`
- `default_agent`：remove
- `mode`：remove（已弃用别名）
- `tools`：remove（工具访问通过 permissions 表达）
- Agent 定义支持 `mode`（`"primary"`/`"subagent"`/`"all"`）、`model`、`variant`、`color`、`description`、`system`、`steps`、`disabled`、`permissions`

### 组 9：集成（MCP）

MCP 配置嵌套在 `mcp.servers` 下：

```jsonc
{
  "mcp": {
    "timeout": { "startup": 30000, "request": 300000 },
    "servers": {
      "github": {
        "type": "local",
        "command": ["npx", "-y", "@github/github-mcp-server"],
        "environment": { "GITHUB_TOKEN": "{env:GITHUB_TOKEN}" }
      },
      "docs": {
        "type": "remote",
        "url": "https://docs.example.com/mcp",
        "headers": { "Authorization": "Bearer {env:DOCS_TOKEN}" },
        "oauth": { "client_id": "...", "client_secret": "...", "scope": "read write" }
      }
    }
  }
}
```

### 组 10：会话生命周期

- `compaction`：自动压缩配置，包含 `auto`、`prune`、`keep.tokens`、`buffer`

### 组 11：弃用和实验性设置

多个旧字段被移除：`layout`、`experimental.disable_paste_summary`、`experimental.batch_tool`、`experimental.openTelemetry`、`experimental.primary_tools`、`experimental.continue_loop_on_deny`。`experimental.mcp_timeout` 移至 `mcp.timeout.request`。

## 当前项目配置示例

`.opencode/opencode.jsonc` 当前仍使用旧版格式：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {},
  "permission": {},
  "references": {
    "effect": {
      "repository": "github.com/Effect-TS/effect-smol",
      "description": "Use for Effect v4 and effect-smol implementation details"
    },
    "opencode-local": {
      "path": "~/.local/share/opencode",
      "description": "Contains opencode logs and data"
    }
  },
  "mcp": {},
  "tools": {
    "github-triage": false,
    "github-pr-search": false
  }
}
```

注意：此文件使用旧版单数键（`provider`、`permission`），V2 迁移尚未在项目自身配置中完成。

## 相关概念

- [OpenCode 简介](/concepts/00-introduction.md)
- [架构概览](/concepts/01-architecture.md)
- [会话与工具](/concepts/03-session-tools.md)
- [部署与基础设施](/concepts/04-deployment-infra.md)
