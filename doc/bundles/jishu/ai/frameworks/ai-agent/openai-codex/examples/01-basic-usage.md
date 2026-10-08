---
type: Example
title: CLI 基本使用
description: >
  安装 Codex CLI 后的基本使用示例：启动交互式 TUI、非交互执行、
  对话、代码生成与修改、会话管理。基于实际 CLI 子命令和参数。
tags: [openai-codex, cli, basic-usage, tui, exec, examples]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# CLI 基本使用

本文展示 Codex CLI 的常见使用方式，包括安装、交互式对话、非交互执行、代码生成和会话管理。

## 前置条件

- 操作系统：macOS 12+、Ubuntu 20.04+/Debian 10+、或 Windows 11（通过 WSL2）
- Git 2.23+（可选，用于 PR 辅助功能）
- 4 GB RAM 最低（8 GB 推荐）
- ChatGPT 账户（Plus/Pro/Business/Edu/Enterprise）或 OpenAI API Key

## 安装

### 方式一：官方安装脚本

**macOS / Linux：**

```shell
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

**Windows（PowerShell）：**

```shell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

默认从 `https://releases.openai.com/codex` 下载，回退到 GitHub Releases。

### 方式二：npm

```shell
npm install -g @openai/codex
```

### 方式三：Homebrew（macOS）

```shell
brew install --cask codex
```

### 验证安装

```shell
codex --version
```

## 首次登录

安装后运行 `codex`，选择 **Sign in with ChatGPT** 进行浏览器登录。也可以使用 API Key：

```shell
# 通过 stdin 传入 API Key
printenv OPENAI_API_KEY | codex login --with-api-key

# 或设备码登录
codex login --device-auth

# 查看登录状态
codex login status

# 登出
codex logout
```

## 交互式 TUI

### 启动交互界面

直接运行 `codex` 不带参数即进入全屏终端界面：

```shell
codex
```

在 TUI 中可以：
- 输入自然语言对话
- 审批或拒绝命令执行
- 查看 diff 并接受/拒绝代码修改
- 使用 `/` 斜杠命令
- 切换模型和权限配置

### 带初始 prompt 启动

```shell
codex "explain this codebase to me"
```

### 指定工作目录

```shell
codex -C /path/to/project "find all TODO comments"
```

### 附加图片

```shell
codex -i screenshot.png "what does this UI element do?"
```

### 远程连接

将 TUI 连接到远程 app-server：

```shell
codex --remote ws://remote-host:port
codex --remote wss://remote-host:port --remote-auth-token-env CODEX_TOKEN
codex --remote unix:///path/to/socket
```

## 非交互执行（codex exec）

`codex exec`（别名 `codex e`）用于脚本、CI 和一次性任务：

### 基本执行

```shell
codex exec "write unit tests for src/auth.ts"
```

### 指定沙箱模式

```shell
# 只读模式（不修改文件）
codex exec --sandbox read-only "analyze the dependency tree"

# 工作区可写（默认）
codex exec --sandbox workspace-write "fix the lint errors"

# 完全访问（谨慎使用）
codex exec --sandbox danger-full-access "run the database migration"
```

### 严格配置检查

```shell
codex exec --strict-config "generate API docs"
```

### 代码审查

```shell
codex review
```

## 会话管理

### 恢复会话

```shell
# 显示会话选择器
codex resume

# 恢复最近的会话
codex resume --last

# 按 ID 恢复
codex resume <session-uuid>

# 显示所有会话（包括非交互的）
codex resume --all --include-non-interactive
```

### 分叉会话

基于已有会话创建新分支：

```shell
codex fork --last
codex fork <session-uuid>
```

### 归档与删除

```shell
codex archive <session>
codex unarchive <session>
codex delete <session>
codex delete <uuid> --force    # 跳过确认（仅 UUID）
```

### 向会话排队消息

```shell
codex queue --session <id> "follow up: also add error handling"
```

### 浏览所有会话

```shell
codex agents
```

## 配置

### 使用配置文件

在 `$CODEX_HOME/config.toml`（通常是 `~/.codex/config.toml`）中配置：

```toml
model = "gpt-5"
sandbox_mode = "workspace-write"

[features]
# 启用实验性功能
unified_exec = true
```

### 配置 Profile

```shell
# 使用自定义 profile（$CODEX_HOME/<name>.config.toml）
codex -p my-profile "run with custom config"
codex exec -p ci "build and test"
```

### 命令行配置覆盖

```shell
codex -c model=gpt-5 -c sandbox_mode=read-only "quick question"
```

### Feature Flags

```shell
codex --enable unified_exec "do something"
codex --disable some_feature "do another thing"
codex features list
codex features enable unified_exec
codex features disable unified_exec
```

## MCP 服务器管理

```shell
# 列出已配置的 MCP 服务器
codex mcp list

# 添加 MCP 服务器
codex mcp add <name> -- <command> [args...]

# 移除 MCP 服务器
codex mcp remove <name>
```

## 插件管理

```shell
codex plugin list
codex plugin add <plugin>
codex plugin remove <plugin>
codex plugin marketplace
```

## 沙箱直接使用

不经过 agent，直接在 Codex 沙箱中运行命令：

```shell
# macOS（Seatbelt）
codex sandbox --permission-profile read-only -- ls -la /

# Linux（Landlock）
codex sandbox -P workspace-write -C /path/to/project -- npm test

# 指定 profile 和配置层
codex sandbox -P my-profile -p my-profile -- ./script.sh
```

## 诊断与维护

```shell
# 诊断安装、配置、认证和运行时健康
codex doctor

# 更新 Codex
codex update

# 生成 shell 补全
codex completion bash > /etc/bash_completion.d/codex
codex completion zsh > ~/.zsh/completions/_codex
codex completion fish > ~/.config/fish/completions/codex.fish
```

## 日志与调试

```shell
# 启用 TUI 日志文件
codex -c log_dir=./.codex-log
tail -F ./.codex-log/codex-tui.log

# 通过 RUST_LOG 控制日志级别
RUST_LOG=debug codex exec "test"
RUST_LOG=codex_core=trace codex
```

## 从源码构建运行

```shell
git clone https://github.com/openai/codex.git
cd codex/codex-rs

# 使用 just
just c "explain this codebase"
just exec "run non-interactively"

# 或直接使用 cargo
cargo run --bin codex -- "your prompt here"
```

## 相关示例

- [Python SDK 使用](02-python-sdk.md)

## 相关概念

- [Rust 核心与 TUI](../concepts/02-rust-core-tui.md)
- [沙箱执行模型](../concepts/04-sandbox-execution.md)
- [Node.js CLI 入口](../concepts/03-nodejs-cli.md)
