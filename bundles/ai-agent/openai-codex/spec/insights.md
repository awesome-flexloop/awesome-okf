---
type: spec
title: "OpenAI Codex 架构洞察"
description: "基于事实清单提炼的 Codex CLI 三语言架构洞察，含证据、反常识与行动建议。"
tags: [codex, architecture, insight, okf]
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# OpenAI Codex 架构洞察

## 洞察一：Node.js 只是"信使"，Rust 才是本体

- **陈述**：`@openai/codex` 这个 npm 包本身不承载任何 agent 逻辑，`bin/codex.js` 的职责只有三件事——根据 `process.platform`/`process.arch` 推导 target triple、定位 `vendor/<triple>/bin/codex` 下的原生二进制、把 argv 与信号转发给该子进程。
- **证据**：F-008、F-011、F-012、F-017、F-018。
- **反常识**：许多开发者把 Codex CLI 当作"又一个 Node 命令行工具"。实际上 `codex-cli/package.json` 的 `files` 只打包 `bin/codex.js`（约 250 行），真正干活的是 `codex-rs/cli` crate 编译出的 `codex` 二进制；Node 层存在的意义是抹平 npm 生态的平台差异，让 `npm install -g @openai/codex` 能按操作系统拉取对应的平台包（`@openai/codex-linux-x64` 等）。
- **行动**：排查 Codex 行为问题时应分清层级——启动/分发问题看 `bin/codex.js`，CLI/TUI/配置问题看 `codex-rs/`；阅读二进制来源时直接看 `codex-rs/cli/src/main.rs` 而非 Node 层。

## 洞察二：`codex` 是"多工具统一入口"，交互式 TUI 只是默认路径

- **陈述**：`codex` 二进制通过 `MultitoolCli` 聚合了 30+ 个子命令；无子命令时参数才转发给交互式 TUI（`TuiCli`），有子命令时走对应逻辑。
- **证据**：F-045、F-046、F-047、F-048、F-050、F-057。
- **反常识**：直觉上"codex"就是那个聊天 TUI。但源码显示 TUI 和 `exec`、`review`、`login`、`mcp`、`plugin`、`app-server` 等是平级子命令，`codex exec`（别名 `e`）才对应"非交互脚本执行"。换句话说，同一个二进制既是 TUI、又是脚本引擎、又是 JSON-RPC 服务端（app-server）。
- **行动**：学习 Codex 时不要把文档中的"CLI"窄化为 TUI；自动化场景优先使用 `codex exec`，程序化集成场景优先使用 `codex app-server`（也是 Python SDK 的底层）。

## 洞察三：`docs/` 内多数文档是"已迁移"空壳，真相在 `codex-rs` 源码

- **陈述**：仓库根 `docs/` 下的 `config.md`、`sandbox.md`、`skills.md`、`agents_md.md`、`exec.md`、`example-config.md` 几乎都是跳转到 `developers.openai.com` 的占位符；真正的配置结构与默认值分别在 `codex-rs/config/src/config_toml.rs` 与 `codex-rs/config/defaults.toml`。
- **证据**：F-027、F-028、F-036、F-042（`docs/config.md` 仅剩 hooks 说明）。
- **反常识**：对着官方 `docs/` 目录学配置会"扑空"——它不包含 `model`/`approval_policy`/`sandbox_mode`/`mcp_servers` 等字段说明。而 `ConfigToml` 是一个拥有上百字段的扁平大结构（见 F-028 起的字段），真实 schema 由 `#[schemars]` 从 Rust 结构生成。
- **行动**：把 `config_toml.rs` 的 `ConfigToml` 与 `defaults.toml` 当作配置的"权威 schema"来读；官方网页文档仅作概念补充。

## 洞察四：SKILL.md 的契约极小，且解析器带"容错修复"

- **陈述**：一个技能（Skill）的必需元数据只有 `name`（≤64 字符）与 `description`；`short-description` 等为可选，且解析器会尝试修复第三方技能里"坏的 YAML 标量"（如 `description: Build for AWS: ECS`）。
- **证据**：F-061、F-062、F-063、F-064、F-065；`parser.rs` 第98-181行 `repair_frontmatter_scalar_fields`。
- **反常识**：技能系统表面"神秘"，实际加载门槛极低——一个目录里放一个带两个 frontmatter 字段的 `SKILL.md` 即可；是否允许隐式调用默认 `true`（F-067），作用域只是 `user/repo/system/admin` 四级字符串（F-069）。
- **行动**：编写自定义技能时只需保证 `name` 与 `description`，把复杂逻辑放在正文；理解技能注入时机时区分"显式调用"与"隐式调用"（`allow_implicit_invocation`）。

## 洞察五：Python SDK 是 `app-server` 的 stdio JSON-RPC 客户端，而非独立 agent 实现

- **陈述**：`openai-codex` 通过 `subprocess.Popen` 启动已安装的 `codex` 二进制（参数 `["app-server", "--listen", "stdio://"]`），用读写进程 stdin/stdout 的 JSON-RPC 行协议通信；高层 `Codex`/`Thread`/`TurnHandle` 只是该协议的同步/异步封装。
- **证据**：F-080、F-082、F-084、F-085、F-086、F-089、F-090。
- **反常识**：SDK 并不"内嵌"模型推理，也不重写 agent 循环；它依赖 `openai-codex-cli-bin` 这个运行时依赖（F-080），找不到时抛出 `FileNotFoundError`（`_installed_codex_path`）。所谓的"异步版本"（`AsyncCodex`）是用线程/队列把同步子进程读写包成 async 接口。
- **行动**：使用 SDK 前必须保证本机有 `codex` 运行时（或显式设 `CodexConfig.codex_bin`）；要理解其能力边界就去读 `client.py` 的 `*_start`/`*_notification` 方法映射，而不是指望 SDK 自我实现功能。