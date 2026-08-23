---
type: reference
scope: openai-codex
name: source
version: "0.1.0"
description: >
  OpenAI Codex CLI 源码文件索引，按组件分类（Node.js CLI / Rust 工作区 /
  Python SDK / 文档 / 构建系统），每条标注对应的事实 ID。
---

# Source Reference — OpenAI Codex CLI

源码根目录：`d:\spaces\SpecWeave\external\libs\ai\agents\codex\`

## 1. 根目录与工作区配置

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `README.md` | 项目介绍、安装方式（curl/Homebrew/npm）、文档链接 | F-005 |
| `AGENTS.md` | Rust/codex-rs 贡献指南：代码风格、crate 命名、测试约定、TUI 规范 | F-006, F-028, F-033, F-038, F-043, F-079 |
| `CHANGELOG.md` | 重定向到 GitHub Releases 页面 | — |
| `package.json` | 根 monorepo 包定义（`codex-monorepo`），Prettier 与 hooks schema 脚本 | F-001, F-004 |
| `pnpm-workspace.yaml` | pnpm 工作区包列表与供应链安全策略 | F-002, F-003 |
| `MODULE.bazel` | Bazel 模块定义（bzlmod），LLVM/Windows SDK/MSVC 工具链 | F-008 |
| `BUILD.bazel` | 根 Bazel 构建文件，平台定义（Linux glibc、Windows gnullvm/msvc） | F-009 |
| `justfile` | Just 任务运行器配置，工作目录 `codex-rs`，测试/构建/Bazel 别名 | F-010, F-078 |
| `SECURITY.md` | 安全漏洞报告策略 | — |
| `LICENSE` | Apache-2.0 许可证 | F-082 |

## 2. Node.js CLI（codex-cli/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-cli/package.json` | npm 包 `@openai/codex` 定义，bin 映射，Node >=16，ESM | F-011, F-012 |
| `codex-cli/bin/codex.js` | 统一启动器：平台检测、可选依赖解析、信号转发、子进程 spawn | F-013–F-017 |

## 3. Rust 工作区（codex-rs/）

### 3.1 工作区配置

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/Cargo.toml` | Cargo 工作区根，130+ members，edition 2024，依赖与 Clippy lint 配置 | F-006, F-007, F-080 |
| `codex-rs/README.md` | 重定向到官方 CLI 文档 | — |
| `codex-rs/config.md` | 重定向到 docs/config.md | — |
| `codex-rs/rust-toolchain.toml` | Rust 工具链版本固定 | — |
| `codex-rs/clippy.toml` | Clippy 额外配置 | — |

### 3.2 CLI 二进制（codex-rs/cli/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/cli/src/main.rs` | 主 CLI 入口，`MultitoolCli` 定义，子命令路由 | F-018–F-024 |
| `codex-rs/cli/src/lib.rs` | 沙箱命令结构（Seatbelt/Landlock/Windows）、登录函数导出 | F-023 |
| `codex-rs/cli/src/app_cmd.rs` | 桌面应用启动（macOS/Windows） | — |
| `codex-rs/cli/src/mcp_cmd.rs` | MCP 服务器管理子命令 | F-067 |
| `codex-rs/cli/src/doctor.rs` | 安装诊断命令 | — |
| `codex-rs/cli/Cargo.toml` | CLI crate 依赖配置 | — |

### 3.3 TUI（codex-rs/tui/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/tui/src/main.rs` | 独立 TUI 二进制入口（较薄） | F-031 |
| `codex-rs/tui/src/lib.rs` | TUI 库根，100+ 子模块声明，禁止 stdout/stderr | F-025, F-027 |
| `codex-rs/tui/src/app.rs` | 顶层 `App` 状态与运行循环 | F-028 |
| `codex-rs/tui/src/app_event.rs` | `AppEvent` 内部消息总线 | F-029 |
| `codex-rs/tui/src/tui.rs` | 终端抽象层（crossterm/ratatui、alternate screen、raw mode） | F-030 |
| `codex-rs/tui/src/chatwidget.rs` | 聊天组件（高触文件，AGENTS.md 点名） | F-028 |
| `codex-rs/tui/src/cli.rs` | TUI 的 clap 参数定义 | — |
| `codex-rs/tui/src/markdown.rs` | Markdown 渲染 | — |
| `codex-rs/tui/styles.md` | TUI 样式指南 | F-032 |
| `codex-rs/tui/Cargo.toml` | TUI crate 依赖（ratatui、crossterm 等） | F-026 |

### 3.4 Core Agent（codex-rs/core/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/core/src/lib.rs` | core 库根，模块声明，deprecated 类型别名 | F-034, F-035, F-037 |
| `codex-rs/core/src/codex_thread.rs` | `CodexThread` 核心对话/线程类型 | F-035 |
| `codex-rs/core/src/agent/mod.rs` | agent 子模块（resolver/control/registry/role/status） | F-036 |
| `codex-rs/core/src/config/mod.rs` | 配置集成层（权限、网络、OSS、features、MCP、模型） | F-039 |
| `codex-rs/core/src/exec.rs` | 命令执行逻辑、超时、输出上限 | F-044 |
| `codex-rs/core/src/spawn.rs` | 子进程生成、沙箱环境变量 | F-042, F-043 |
| `codex-rs/core/src/shell.rs` | Shell 类型建模（Zsh/Bash/Sh/PowerShell/Cmd） | F-045 |
| `codex-rs/core/src/safety.rs` | `SafetyCheck` 补丁安全评估 | F-046 |
| `codex-rs/core/src/agents_md.rs` | AGENTS.md 发现与加载 | F-054–F-059 |
| `codex-rs/core/src/skills.rs` | Skills 显式/隐式调用与分析埋点 | F-052 |
| `codex-rs/core/src/mcp.rs` | `McpManager` 线程环境协调 | F-066 |
| `codex-rs/core/src/thread_manager.rs` | `ThreadManager` 线程生命周期管理 | F-035 |
| `codex-rs/core/Cargo.toml` | core crate 配置 | — |

### 3.5 沙箱与执行（codex-rs/sandboxing/, execpolicy/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/sandboxing/src/lib.rs` | 平台沙箱统一入口（Linux bwrap/landlock、macOS seatbelt、Windows） | F-040, F-041 |
| `codex-rs/sandboxing/src/landlock.rs` | Linux Landlock 沙箱后端 | F-040 |
| `codex-rs/sandboxing/src/seatbelt.rs` | macOS Seatbelt 沙箱后端 | F-040 |
| `codex-rs/sandboxing/src/bwrap.rs` | Linux bubblewrap 后端 | F-040 |
| `codex-rs/execpolicy/src/lib.rs` | 执行策略引擎（规则解析、PrefixRule、NetworkRuleProtocol） | F-048 |
| `codex-rs/execpolicy/src/rule.rs` | 规则类型定义 | F-048 |
| `codex-rs/execpolicy/src/parser.rs` | 策略文件解析器 | F-048 |

### 3.6 Skills（codex-rs/skills/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/skills/src/lib.rs` | Skills crate 根，系统 skills 嵌入与安装 | F-049–F-051 |
| `codex-rs/skills/src/loading.rs` | Skill 加载器与缓存 | F-049 |
| `codex-rs/skills/src/parser.rs` | SKILL.md frontmatter 解析 | F-049 |
| `codex-rs/skills/src/model.rs` | `SkillMetadata`、`SkillPolicy` 等模型 | F-049 |
| `codex-rs/skills/src/mentions.rs` | `@mention` 提取 | F-049 |
| `codex-rs/skills/src/invocation.rs` | 隐式 skill 调用检测 | F-049 |

### 3.7 MCP（codex-rs/codex-mcp/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/codex-mcp/src/lib.rs` | MCP 运行时、目录、工具缓存、资源客户端 | F-065 |
| `codex-rs/codex-mcp/src/tools.rs` | `ToolInfo` 工具定义 | F-065 |
| `codex-rs/mcp-server/src/main.rs` | MCP server 二进制（stdio） | F-068 |

### 3.8 配置（codex-rs/config/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/config/src/lib.rs` | 配置 crate 根，`CONFIG_TOML_FILE` 常量，模块导出 | F-060, F-061 |
| `codex-rs/config/src/config_toml/` | config.toml 结构定义 | F-061 |
| `codex-rs/config/src/loader.rs` | 分层配置加载器 | F-061 |
| `codex-rs/config/src/merge.rs` | TOML 值合并逻辑 | F-061 |
| `codex-rs/config/src/schema.rs` | JSON Schema 生成 | F-061 |

### 3.9 其他关键 crate

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `codex-rs/protocol/src/lib.rs` | 协议类型（Event、Op、AskForApproval、SandboxPolicy） | — |
| `codex-rs/app-server/src/lib.rs` | app-server JSON-RPC 服务 | F-024 |
| `codex-rs/exec/src/lib.rs` | 非交互 `codex exec` 实现 | F-020 |
| `codex-rs/login/src/lib.rs` | 认证管理（ChatGPT/API key/device code） | — |
| `codex-rs/features/src/lib.rs` | Feature flag 系统（under development/experimental/stable） | F-021 |

## 4. Python SDK（sdk/python/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `sdk/python/README.md` | SDK 文档：安装、快速开始、认证、帮助 | F-076 |
| `sdk/python/pyproject.toml` | 包定义（`openai-codex`），uv_build，pydantic + cli-bin 依赖 | F-070, F-071 |
| `sdk/python/src/openai_codex/__init__.py` | 公共 API 导出（Codex/AsyncCodex/Thread/Sandbox 等） | F-072 |
| `sdk/python/src/openai_codex/api.py` | `Codex` 同步客户端、`AsyncCodex` 异步客户端类定义 | F-073 |
| `sdk/python/src/openai_codex/client.py` | 底层客户端：子进程启动、JSON-RPC 消息路由 | F-074 |
| `sdk/python/src/openai_codex/async_client.py` | 异步客户端实现 | — |
| `sdk/python/src/openai_codex/_sandbox.py` | `Sandbox` 枚举与 wire 策略映射 | F-047 |
| `sdk/python/src/openai_codex/_run.py` | `TurnResult` 结果收集 | — |
| `sdk/python/src/openai_codex/_login.py` | 登录流程封装 | F-076 |
| `sdk/python/src/openai_codex/generated/v2_all.py` | 从 app-server 协议生成的 Pydantic 模型 | F-075 |
| `sdk/python/src/openai_codex/generated/notification_registry.py` | 通知类型注册表 | F-075 |
| `sdk/python/src/openai_codex/errors.py` | 错误类型层次 | — |

## 5. 文档（docs/）

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `docs/install.md` | 系统要求、从源码构建、RUST_LOG 日志配置 | F-077 |
| `docs/contributing.md` | 贡献策略：不接受外部 PR，仅接受 issue | F-081 |
| `docs/CLA.md` | 个人贡献者许可协议 v1.0 | F-082 |
| `docs/config.md` | 配置文档（重定向 + lifecycle hooks 说明） | F-064 |
| `docs/skills.md` | Skills 文档（重定向到官方站） | — |
| `docs/sandbox.md` | 沙箱与审批文档（重定向） | — |
| `docs/agents_md.md` | AGENTS.md 文档（重定向） | — |
| `docs/exec.md` | 非交互模式文档（重定向） | — |
| `docs/execpolicy.md` | 执行策略文档（重定向） | — |
| `docs/slash_commands.md` | 斜杠命令文档 | — |
| `docs/authentication.md` | 认证文档 | — |
| `docs/getting-started.md` | 入门指南 | — |

## 6. 示例 Skills

| 文件 | 说明 | 事实 ID |
|------|------|---------|
| `.codex/skills/test-tui/SKILL.md` | 项目本地 skill 示例 | F-053 |
