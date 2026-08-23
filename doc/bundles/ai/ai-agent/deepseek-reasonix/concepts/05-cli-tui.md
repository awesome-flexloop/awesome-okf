---
type: Concept
title: CLI 与 TUI
description: CLI 命令系统、chat_tui 终端交互、MCP 管理、provider/model 配置、subagent 管理、plugin 系统
tags: [deepseek-reasonix, cli, tui, bubbletea, mcp, provider, plugin, subagent]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

## CLI 入口

`internal/cli` 包实现 reasonix 的命令行入口：子命令路由、flag 解析、配置组装和退出码。核心是配置驱动——provider 和工具从配置解析，不硬编码。（F-095）

```go
func RunWithBuildInfo(args []string, info BuildInfo) int {
    // 检测语言、迁移旧配置、路由子命令
    if len(args) == 0 && cliIsInteractive() {
        return runInteractiveSession(nil, version)
    }
    switch cmd {
    case "run": // ...
    case "acp": // ...
    case "mcp": // ...
    case "bot": // ...
    case "subagent": // ...
    case "plugin": // ...
    }
}
```

无参数且在交互终端时启动 `chatREPL`（Bubble Tea TUI）。`-p/--print` 标志路由到 `run --print` 一次性打印模式。（F-095）

TUI 使用 `charm.land/bubbletea/v2` 框架，flag 解析使用 `github.com/spf13/pflag`。（F-096）

## 主要子命令

| 子命令 | 说明 |
|--------|------|
| `reasonix` | 无参数启动交互 TUI |
| `reasonix run "task"` | 一次性运行任务 |
| `reasonix setup` | 配置 provider 和 model |
| `reasonix acp` | 启动 ACP 协议服务 |
| `reasonix mcp` | MCP 服务器管理 |
| `reasonix bot` | Bot 网关管理 |
| `reasonix subagent` | Subagent profile 管理 |
| `reasonix plugin` | 插件包管理 |
| `reasonix serve` | HTTP/SSE 服务 |
| `reasonix version` | 版本信息 |

## MCP 管理

`mcp.go` 提供 MCP 服务器管理，CLI 子命令和聊天内 slash 命令共享同一解析器：

```go
func parseMCPAdd(args []string) (config.PluginEntry, error)
```

语法：

```
reasonix mcp add <name> [--http URL | --sse URL] [--env K=V]... [--header K=V]... [command [args...]]
reasonix mcp add -- npx -y chrome-devtools-mcp@latest
reasonix mcp add https://example.com/mcp
```

- `--http/--sse URL` 使其成为远程服务器
- 否则第一个非 flag token 开始 stdio 命令及其参数
- 支持 `--` 分隔符保留命令自己的 flags
- 聊天内 `/mcp add` 和 `/mcp remove` 通过 controller 热连接

（F-097）

## Provider 切换

`/provider` 命令在 TUI 中切换 provider：

```go
func (m *chatTUI) runProviderCommand(input string) {
    if len(args) < 2 {
        m.openProviderPicker()  // 无参数打开选择器
        return
    }
    m.switchToProvider(name)   // 带参数切换
}
```

Provider picker 列出所有已配置且 `Configured()` 的 provider，显示 kind 和模型数量。切换到有多个模型的 provider 时显示交互式选择器。（F-098）

## Model 切换

`/model <ref>` 原地切换模型并携带对话历史：

```go
func (m *chatTUI) runModelSubcommand(input string) {
    // 1. 持久化用户选择到 user config.toml
    m.persistModel(ref)
    // 2. 先 snapshot（防止冲突）
    m.ctrl.Snapshot()
    // 3. 捕获历史和路径（snapshot 后！）
    carried := m.ctrl.History()
    prevPath := m.ctrl.SessionPath()
    // 4. 异步重建 controller（不阻塞 TUI 事件循环）
}
```

关键设计：
- controller 构建**异步执行**，不阻塞 TUI 事件循环
- 先 Snapshot 再捕获历史——snapshot 冲突可能 retarget 到恢复分支
- 切换前重新绑定 session lease

（F-099）

## Subagent 管理

`subagentCommand` 管理 subagent profile：

```
reasonix subagent list [--dir PATH]
reasonix subagent create <name> --description TEXT (--prompt TEXT | --prompt-file PATH)
    [--scope project|global] [--model REF] [--effort LEVEL] [--tools a,b] [--color NAME]
reasonix subagent edit <name> [...]
reasonix subagent delete <name> --yes
reasonix subagent try <name> [--model REF] [--max-steps N] <task>
reasonix subagent run <name> [--model REF] [--max-steps N] <task>
```

支持 `list`、`create`、`edit`、`delete`、`try`（试运行）、`run`（正式运行）子命令。`--prompt-file -` 支持从 stdin 读取系统提示。（F-100）

## Plugin 系统

`pluginCommand` 管理 Extension Protocol v2 插件包：

```
reasonix plugin install <source> [--yes] [--dry-run] [--link] [--replace]
reasonix plugin list
reasonix plugin show <name>
reasonix plugin enable <name>
reasonix plugin disable <name>
reasonix plugin remove <name>
reasonix plugin doctor <name>
reasonix plugin migrate <name> --to-v2
```

支持安装、列出、查看、启用/禁用、移除、诊断、v1→v2 迁移。`--link` 用于开发模式链接本地插件。（F-101）

## TUI 交互

TUI（`chat_tui.go`）基于 Bubble Tea 模型-视图-更新架构，支持：

- Markdown 实时流式渲染（goldmark + chroma 语法高亮）
- Tool call 卡片显示
- 交互式审批（ask 工具的多选问题）
- Slash 命令自动补全
- Provider/model/effort/language 快速切换
- 主题切换
- 会话历史浏览

## 构建信息

版本信息通过 `-ldflags` 注入：

```makefile
LDFLAGS := -s -w \
    -X main.version=$(VERSION) \
    -X main.gitCommit=$(GIT_COMMIT) \
    -X main.buildTimeUTC=$(BUILD_TIME_UTC)
```

`reasonix version --verbose` 显示 git commit 和构建时间，`--json` 输出机器可读格式。

## 相关概念

- [项目架构](/concepts/01-project-architecture.md)——CLI 如何调用 boot.BuildRuntime
- [ACP 协议](/concepts/03-acp-protocol.md)——`reasonix acp` 子命令
- [Bot 网关](/concepts/04-bot-gateway.md)——`reasonix bot` 子命令
- [Fleet 与 Subagent](/concepts/07-fleet-subagents.md)——subagent profile 和 task 工具
- [基础使用示例](/examples/01-basic-usage.md)——安装和基本对话
