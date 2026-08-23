---
type: Concept
title: 工作区架构
description: >
  Codex CLI 仓库是一个多语言 monorepo，结合 pnpm workspace（Node.js）、
  Cargo workspace（Rust，130+ crate）和 Python SDK（uv_build），
  并使用 Bazel 作为辅助构建系统。本文详解三部分职责划分与构建系统。
tags: [openai-codex, workspace, monorepo, pnpm, cargo, bazel, architecture]
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

# 工作区架构

Codex CLI 仓库是一个多语言 monorepo，根目录同时管理 Node.js、Rust 和 Python 三种语言的包，并使用 Bazel 作为跨语言构建与测试系统。

## 顶层结构

```
codex/
├── codex-cli/          # Node.js CLI 启动器（npm 包）
├── codex-rs/           # Rust 工作区（130+ crate，全部核心逻辑）
├── sdk/
│   └── python/         # Python SDK
├── docs/               # 文档（多为重定向到官方站）
├── scripts/            # 构建与打包脚本
├── patches/            # Bazel 补丁（V8、Windows 链接等）
├── third_party/        # 第三方依赖（V8、WezTerm、PowerShell、Wine）
├── tools/              # 开发工具（argument-comment-lint 等）
├── bazel/              # Bazel 规则与平台定义
├── .codex/skills/      # 项目本地 skills
├── MODULE.bazel        # Bazel bzlmod 定义
├── BUILD.bazel         # 根 Bazel 构建文件
├── justfile            # Just 任务运行器
├── package.json        # 根 pnpm monorepo 配置
└── pnpm-workspace.yaml # pnpm 工作区定义
```

## 三部分职责划分

### Node.js（codex-cli/）

Node.js 部分仅承担 npm 生态分发职责：

- 包名 `@openai/codex`，通过 `bin/codex.js` 注册 `codex` 命令
- 检测平台 triple（`x86_64-unknown-linux-musl` 等），从六个平台可选依赖包中定位 Rust 二进制
- 转发 SIGINT/SIGTERM/SIGHUP 信号到子进程
- 镜像子进程退出码
- 不包含任何 agent 逻辑

pnpm 工作区只包含三个包：

```yaml
packages:
  - codex-cli
  - codex-rs/responses-api-proxy/npm
  - sdk/typescript
```

### Rust（codex-rs/）

Rust 工作区是全部功能的实现载体，包含 130+ crate。crate 命名统一使用 `codex-` 前缀（如 `codex-core`、`codex-tui`、`codex-sandboxing`）。

关键 crate 分组：

| 分组 | Crate |
|------|-------|
| CLI 入口 | `cli` |
| TUI | `tui` |
| Agent 核心 | `core`、`core-api`、`protocol` |
| 沙箱 | `sandboxing`、`linux-sandbox`、`windows-sandbox-rs`、`bwrap` |
| 执行 | `exec`、`exec-server`、`execpolicy`、`shell-command` |
| 配置 | `config` |
| Skills | `skills`、`ext/skills` |
| MCP | `codex-mcp`、`mcp-server`、`rmcp-client` |
| 扩展 | `ext/agent`、`ext/goal`、`ext/mcp`、`ext/queue`、`ext/items` |
| 服务 | `app-server`、`app-server-protocol`、`app-server-client` |
| 工具库 | `utils/` 下 20+ 小 crate |

Rust 工作区使用 edition 2024，版本 `0.0.0`，Apache-2.0 许可证。

### Python（sdk/python/）

Python SDK 包名 `openai-codex`，使用 `uv_build` 构建后端：

- 依赖 `pydantic>=2.12` 和 `openai-codex-cli-bin==0.147.0`（固定版本的 Rust 二进制）
- 提供同步 `Codex` 和异步 `AsyncCodex` 客户端
- 通过子进程 JSON-RPC 与 Rust 二进制通信
- 包含从 app-server 协议 schema 自动生成的 Pydantic 模型

## 构建系统

### Cargo（主要）

Rust 工作区使用标准 Cargo：

```bash
cd codex-rs
cargo build                          # 调试构建
cargo run --bin codex -- "prompt"    # 运行
cargo build --release                # 发布构建
```

项目使用 `just` 作为任务运行器，工作目录设为 `codex-rs/`：

```bash
just c "prompt"       # cargo run --bin codex
just exec "prompt"    # cargo run --bin codex -- exec
just test             # cargo nextest run（非直接 cargo test）
just fmt              # 格式化（Rust + Python + Bazel + Prettier）
just fix -p codex-tui # Clippy 自动修复
```

### Bazel（辅助）

Bazel 用于跨平台构建、远程执行（RBE）、端到端基准测试和参数注释 lint：

```python
# MODULE.bazel
module(name = "codex")
bazel_dep(name = "bazel_skylib", version = "1.9.0")
bazel_dep(name = "platforms", version = "1.0.0")
bazel_dep(name = "protobuf", version = "34.0.bcr.1")
bazel_dep(name = "llvm", version = "0.8.11")
```

Bazel 配置了自定义平台，处理 Linux glibc、Windows gnullvm/msvc ABI 等交叉编译需求。V8 依赖（用于 `v8-poc` crate）通过补丁定制。

常用 Bazel 命令：

```bash
just bazel-codex -- "prompt"         # Bazel 构建并运行 codex
just bazel-test                       # Bazel 运行全部测试
just build-for-release               # bazel build //codex-rs/cli:release_binaries
just bazel-lock-update                # 更新 MODULE.bazel.lock
```

### Python 构建

Python SDK 使用 `uv`：

```bash
cd sdk/python
uv sync                               # 安装依赖
uv run pytest                         # 运行测试
uv build                              # 构建包
```

## 代码质量工具链

| 工具 | 用途 |
|------|------|
| `rustfmt` | Rust 格式化 |
| Clippy | Rust lint（workspace 级别配置了 30+ deny 规则） |
| `cargo-nextest` | 测试运行器 |
| `insta` | 快照测试（尤其 TUI） |
| `prettier` | JSON/Markdown/YAML/JS 格式化 |
| `ruff` | Python lint 和格式化 |
| `buildifier` | Bazel/Starlark 格式化 |
| argument-comment-lint | 自定义 Dylint，检查位置参数注释 |

Clippy 配置特别严格，`unwrap_used`、`expect_used`、`redundant_clone`、`manual_map` 等均设为 `deny`。

## 相关概念

- [Rust 核心与 TUI](./02-rust-core-tui.md)
- [Node.js CLI 入口](./03-nodejs-cli.md)
- [Python SDK](./06-python-sdk.md)
- [简介](./00-introduction.md)
