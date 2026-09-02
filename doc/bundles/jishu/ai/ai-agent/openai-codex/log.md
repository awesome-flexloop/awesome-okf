---
type: Changelog
scope: openai-codex
name: log
version: "0.1.0"
---

# Changelog — openai-codex OKF Bundle

## 2026-09-02

**Migration**: 合并 learning 07/openai/chatgpt-codex-wiki（产品定位/界面设计/用户体验/多平台/定价/洞察等 16 章 + 原始内容采集），与既有源码架构束互补；舍弃空 page.html 与导航文件。

## 0.1.0 — 2026-08-23

### Added

- 初始 OKF v0.2 知识包生成
- **spec/facts.md**：82 条编号事实（F-001 至 F-082），覆盖工作区结构、Node.js CLI、Rust CLI/TUI/core、沙箱执行、Skills、AGENTS.md、配置系统、MCP、Python SDK、构建与测试约定，每条引用文件路径和行号
- **spec/insights.md**：5 个架构级核心洞察
  - Insight 1：三语言分层架构（JS 壳、Rust 核、Python 接口）
  - Insight 2：从单体 core 到微核工作区的逆膨胀治理
  - Insight 3：多层防御沙箱执行模型（平台原语 + 策略引擎 + 审批门控）
  - Insight 4：AGENTS.md + Skills 文件即上下文约定
  - Insight 5：TUI 作为一等公民的事件驱动架构
- **concepts/**：7 篇概念文档（中文）
  - 00-introduction.md：简介、三语言架构、功能特性、安装
  - 01-workspace-architecture.md：pnpm + Cargo + Python monorepo，Bazel 构建
  - 02-rust-core-tui.md：codex-core、TUI 架构、事件循环、终端渲染
  - 03-nodejs-cli.md：bin/codex.js 启动器、平台检测、信号转发
  - 04-sandbox-execution.md：三层防御沙箱、execpolicy、Shell 抽象
  - 05-skills-agents-md.md：AGENTS.md 发现算法、Skills 显式/隐式调用
  - 06-python-sdk.md：同步/异步客户端、JSON-RPC、认证、沙箱控制
- **examples/**：2 篇示例文档
  - 01-basic-usage.md：CLI 安装、TUI、exec、会话管理、配置、MCP、诊断
  - 02-python-sdk.md：SDK 安装、线程管理、流式进度、错误处理、完整示例
- **references/source.md**：源码文件索引，按组件分类，标注事实 ID
- 索引文件：concepts/index.md、examples/index.md、references/index.md
- 根 index.md：bundle 清单（okf_version 0.2），含导航表、学习路径、目录结构

### 来源

- 本地源码路径：`d:\spaces\SpecWeave\external\libs\ai\agents\codex\`
- 阅读关键文件：README.md、AGENTS.md、package.json、pnpm-workspace.yaml、Cargo.toml、MODULE.bazel、BUILD.bazel、justfile、codex-cli/bin/codex.js、cli/src/main.rs、tui/src/{main,lib,app,app_event,tui}.rs、core/src/{lib,exec,spawn,shell,safety,agents_md,skills,mcp,config/mod,codex_thread,agent/mod}.rs、sandboxing/src/lib.rs、execpolicy/src/lib.rs、skills/src/lib.rs、codex-mcp/src/lib.rs、config/src/lib.rs、sdk/python/{README.md,pyproject.toml,src/openai_codex/__init__.py,api.py,client.py,_sandbox.py}、docs/*.md
- 事实提取方法：R Phase 直接阅读源码并记录文件路径与行号
- 验证方法：grep-verification（文件路径与内容已通过实际读取确认）
