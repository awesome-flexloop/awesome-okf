---
type: Example
title: 基础使用
description: 安装 Reasonix、配置 provider/model、启动 CLI/TUI 进行基本对话的完整流程
tags: [deepseek-reasonix, install, setup, cli, quickstart]
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

## 安装

### 通过 npm（推荐）

```sh
npm i -g reasonix
```

npm 包会拉取对应平台的预编译原生二进制。（README.md:85）

### 通过 Homebrew（macOS）

```sh
brew install esengine/reasonix/reasonix
```

### 从源码构建

需要 Go 1.25+。模块固定了 `toolchain` 指令，保持 `GOTOOLCHAIN=auto`：

```sh
git clone https://github.com/esengine/DeepSeek-Reasonix.git
cd DeepSeek-Reasonix
make build      # -> bin/reasonix(.exe)
```

交叉编译到 6 个目标：

```sh
make cross      # -> dist/ (darwin|linux|windows × amd64|arm64)
```

构建使用 `CGO_ENABLED=0` 生成完全自包含的静态二进制。（Makefile:15-17, 81-87）

## 配置

首次使用前配置 provider 和 model：

```sh
reasonix setup
```

setup 命令引导选择 provider、输入 API key、选择默认模型。配置保存在 `reasonix.toml` 中。

也可以手动编辑配置文件。Reasonix 是配置驱动的——provider、agent、工具、插件都在 `reasonix.toml` 中声明，无硬编码模型。

### 配置路径

- macOS/Linux：`~/.reasonix`
- Windows：`%APPDATA%\reasonix`

可通过 `REASONIX_HOME` 或 `REASONIX_STATE_HOME` 环境变量覆盖。

## 启动交互会话

```sh
reasonix
```

无参数且在交互终端时，启动 Bubble Tea TUI。你将看到：

- Markdown 实时流式渲染
- 语法高亮的代码块
- Tool call 卡片
- Token 使用量和上下文窗口指示器
- 模型/provider 状态行

### 基本对话

直接输入消息即可与 agent 对话：

```
> 帮我分析这个 Go 项目的结构
```

agent 会使用内置工具（文件读取、grep、glob、bash 等）来调查项目。

### 常用 Slash 命令

在 TUI 中：

| 命令 | 说明 |
|------|------|
| `/init` | 让 Reasonix 创建项目指令文件 |
| `/model <ref>` | 切换模型（携带对话历史） |
| `/provider <name>` | 切换 provider |
| `/mcp add ...` | 热添加 MCP 服务器 |
| `/mcp remove <name>` | 热移除 MCP 服务器 |
| `/effort <level>` | 设置推理 effort |
| `/language <lang>` | 设置语言 |
| `/theme <name>` | 切换主题 |

`/model` 切换是原地进行的——对话历史被携带到新模型，controller 异步重建不阻塞 TUI。

## 一次性运行任务

```sh
reasonix run "implement the TODOs in main.go"
```

`run` 子命令执行一次性任务后退出。使用 `-p/--print` 进入非交互打印模式：

```sh
reasonix -p "what is the current git branch?"
reasonix run --print "list all Go files in this project"
```

无参数的 `-p`/`--print` flag 会被路由到 `run --print`。（cli.go:87-90）

## MCP 服务器管理

添加 MCP 服务器以扩展工具能力：

```sh
# stdio 服务器
reasonix mcp add chrome-devtools npx -y chrome-devtools-mcp@latest

# HTTP 服务器
reasonix mcp add my-api --http https://example.com/mcp

# 带环境变量
reasonix mcp add my-server --env API_KEY=xxx -- ./server-bin --flag
```

也可以在 TUI 中使用 `/mcp add` 热连接，无需重启。

## Subagent Profile

创建和运行 subagent profile：

```sh
# 创建一个代码审查 profile
reasonix subagent create reviewer \
  --description "Senior code reviewer" \
  --prompt "You are a senior code reviewer. Focus on correctness, security, and idiomatic Go." \
  --model deepseek-reasoner \
  --tools "readfile,grep,glob"

# 列出所有 profile
reasonix subagent list

# 试运行（不持久化）
reasonix subagent try reviewer "review internal/agent/agent.go"

# 正式运行
reasonix subagent run reviewer "review internal/acp/"
```

Profile 支持 `--scope project|global`，project 级保存在项目目录，global 级保存在用户配置目录。

## 插件管理

```sh
# 安装插件包
reasonix plugin install <source>

# 列出已安装插件
reasonix plugin list

# 查看插件详情
reasonix plugin show <name>

# 启用/禁用
reasonix plugin enable <name>
reasonix plugin disable <name>

# 诊断
reasonix plugin doctor <name>
```

## 从源码构建开发版本

```sh
# 安装 git pre-push hook
make hooks

# 代码格式化和检查
make fmt
make vet
make lint

# 运行测试
make test
```

pre-push hook 运行 `go vet`。提交前建议运行：

```sh
gofmt -w .
go vet ./...
make lint
go test ./internal/tool/builtin/ ./internal/boot/
```

（REASONIX.md:77-82）

## 相关概念

- [Reasonix 简介](../concepts/00-introduction.md)
- [CLI 与 TUI](../concepts/05-cli-tui.md)——CLI 命令系统详解
- [项目架构](../concepts/01-project-architecture.md)——构建和包结构
- [Bot 网关示例](02-bot-gateway.md)——多平台 IM 接入
