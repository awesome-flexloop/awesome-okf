# Concepts

- [00 - OpenAI Codex CLI 简介](./00-introduction.md) — 定位、三语言架构、核心功能、安装方式
- [01 - 工作区架构](./01-workspace-architecture.md) — pnpm + Cargo + Python monorepo，Bazel 构建系统，三部分职责划分
- [02 - Rust 核心与 TUI](./02-rust-core-tui.md) — codex-core agent 逻辑、事件驱动 TUI（ratatui/crossterm）、线程管理、终端渲染
- [03 - Node.js CLI 入口](./03-nodejs-cli.md) — bin/codex.js 启动器、平台检测、信号转发、与 Rust 二进制的桥接
- [04 - 沙箱执行模型](./04-sandbox-execution.md) — 平台原生沙箱（Seatbelt/Landlock/bwrap/Windows）、execpolicy、SafetyCheck 三层防御
- [05 - Skills 与 AGENTS.md](./05-skills-agents-md.md) — AGENTS.md 目录树发现、SKILL.md 技能系统、显式/隐式调用、信任边界
- [06 - Python SDK](./06-python-sdk.md) — openai-codex 包、同步/异步客户端、JSON-RPC 子进程通信、认证、沙箱控制

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-workspace-architecture
02-rust-core-tui
03-nodejs-cli
04-sandbox-execution
05-skills-agents-md
06-python-sdk
```
