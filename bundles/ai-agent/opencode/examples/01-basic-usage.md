---
type: Example
scope: opencode
name: basic-usage
version: "0.1.0"
source: local
description: "OpenCode 基本使用示例：安装、启动、Agent 切换、GitHub Action 集成"
---

# OpenCode 基本使用示例

## 示例 1：安装 OpenCode

OpenCode 支持多种安装方式。

### 使用安装脚本（推荐）

```bash
curl -fsSL https://opencode.ai/install | bash
```

### 使用包管理器

```bash
# npm
npm i -g opencode-ai@latest

# Homebrew（macOS/Linux）
brew install anomalyco/tap/opencode

# Scoop（Windows）
scoop install opencode

# Chocolatey（Windows）
choco install opencode
```

安装路径优先级：
1. `$OPENCODE_INSTALL_DIR` 环境变量
2. `$XDG_BIN_DIR`
3. `$HOME/bin`（如果存在或可创建）
4. `$HOME/.opencode/bin`（默认回退）

## 示例 2：启动交互式 TUI

在项目目录中运行：

```bash
cd your-project
opencode
```

这将启动全屏终端用户界面（TUI），基于 OpenTUI 和 SolidJS 构建。

### CLI 全局选项

```bash
opencode --help              # 显示帮助
opencode --version           # 显示版本
opencode --print-logs        # 将日志打印到 stderr
opencode --log-level DEBUG   # 设置日志级别（DEBUG/INFO/WARN/ERROR）
opencode --pure              # 不加载外部插件运行
```

## 示例 3：Agent 切换

OpenCode 内置两个主 agent，按 `Tab` 键切换：

- **build**：默认全权限 agent，用于开发工作
- **plan**：只读 agent，用于分析和代码探索
  - 默认拒绝文件编辑
  - 运行 bash 命令前请求权限
  - 适合探索陌生代码库或规划变更

还有一个 **general** 子 agent，用于复杂搜索和多步任务，可通过在消息中使用 `@general` 调用。

## 示例 4：启动 HTTP 服务器

```bash
opencode serve --hostname=127.0.0.1 --port=4096
```

启动后可通过 SDK 客户端连接：

```ts
import { createOpencodeClient } from "@opencode-ai/sdk"

const client = createOpencodeClient({ baseUrl: "http://127.0.0.1:4096" })
```

## 示例 5：GitHub Action 集成

在 GitHub 仓库中创建 `.github/workflows/opencode.yml`：

```yaml
name: opencode

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  opencode:
    runs-on: ubuntu-latest
    if: |
      contains(github.event.comment.body, '/opencode') ||
      contains(github.event.comment.body, '/oc')
    steps:
      - uses: actions/checkout@v4
      - uses: anomalyco/opencode@main
        with:
          model: anthropic/claude-sonnet-4
          agent: build
```

### Action 输入参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `model` | 是 | 模型标识，格式 `provider/model` |
| `agent` | 否 | Agent 名称，必须是主 agent |
| `share` | 否 | 是否共享会话（公开仓库默认 true） |
| `prompt` | 否 | 自定义 prompt 覆盖默认行为 |
| `use_github_token` | 否 | 使用 GITHUB_TOKEN 而非 App token 交换 |
| `mentions` | 否 | 触发短语，逗号分隔，默认 `/opencode,/oc` |
| `variant` | 否 | 模型变体（如 high、max、minimal） |
| `oidc_base_url` | 否 | 自定义 OIDC token 交换 API 地址 |

### 使用方式

在 Issue 或 PR 评论中输入：

- `/opencode`：总结当前讨论
- `/oc 修复这个 bug`：带自定义指令
- `/opencode 审查这段代码`：在 PR review comment 中使用

对于 Issue，Action 会自动创建分支、提交改动并发起 PR。对于 PR，直接推送到对应分支。

## 示例 6：项目配置文件

在项目根目录创建 `opencode.jsonc`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4",
  "shell": "/bin/zsh",
  "share": "manual",
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md"
  ],
  "agents": {
    "reviewer": {
      "model": "anthropic/claude-sonnet-4",
      "description": "Review changes for correctness",
      "system": "Find regressions and missing tests.",
      "mode": "subagent",
      "color": "warning",
      "steps": 12,
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" }
      ]
    }
  },
  "mcp": {
    "timeout": { "startup": 30000, "request": 300000 },
    "servers": {
      "github": {
        "type": "local",
        "command": ["npx", "-y", "@github/github-mcp-server"],
        "environment": { "GITHUB_TOKEN": "{env:GITHUB_TOKEN}" }
      }
    }
  },
  "compaction": {
    "auto": true,
    "prune": true,
    "keep": { "tokens": 2000 },
    "buffer": 10000
  }
}
```

## 示例 7：CLI 命令一览

```bash
# 运行模式
opencode run                    # 启动交互式会话
opencode serve                  # 启动 HTTP 服务器
opencode web                    # 启动 Web 界面

# 会话管理
opencode session list           # 列出会话
opencode session export         # 导出会话

# 模型与提供商
opencode models                 # 列出可用模型
opencode providers              # 列出提供商

# Agent
opencode agent list             # 列出可用 agent

# MCP
opencode mcp list               # 列出 MCP 服务器

# 调试
opencode debug agent            # 调试 agent
opencode debug config           # 查看配置
opencode debug file             # 调试文件
opencode debug lsp              # 调试 LSP

# 维护
opencode upgrade                # 升级 OpenCode
opencode uninstall              # 卸载
opencode db                     # 数据库操作
```
