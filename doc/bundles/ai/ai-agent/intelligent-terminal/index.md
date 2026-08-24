---
okf_version: "0.2"
title: "Intelligent Terminal"
description: "Windows Terminal原生AI Agent集成 - ACP协议驱动的智能终端增强框架"
tags:
  - ai-agent
  - terminal
  - windows-terminal
  - acp
  - cpp
  - rust
  - com
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/microsoft/terminal
related:
  - "[[ai-agent-fundamentals]]"
  - "[[hermes-agent]]"
  - "[[deepseek-harness]]"
  - "[[cordis]]"
---

# Intelligent Terminal

Intelligent Terminal 是 Windows Terminal 的原生 AI Agent 集成方案（Windows Terminal Agent / WTA），采用 C++/Rust 双语言实现。核心是 Helper+Master 双进程架构，通过经典 COM ITerminalProtocol 接口和命名管道传输层实现 ACP JSON-RPC 2.0 协议通信，内置5个Agent（copilot/claude/codex/gemini/opencode）、OSC 133自动错误修复管线、Agent Pane XAML UI面板、wtcli命令行工具，以及wt-agent-hooks插件自动升级机制。

## 🧩 概念导航（Concepts）

### 核心架构
- [dual-process-architecture](concepts/dual-process-architecture.md) — 双进程架构：Helper+Master设计、SharedWta单例、Job Object容器、Pre-warm预暖、崩溃锁存
- [acp-json-rpc-protocol](concepts/acp-json-rpc-protocol.md) — ACP JSON-RPC 2.0协议：两跳传输、session路由、反压处理、ClientLink/AgentLink兼容层、请求方法全集
- [com-protocol-server](concepts/com-protocol-server.md) — COM协议服务器：经典COM ITerminalProtocol、CLSID分品牌、MTA线程模型、事件投递异步队列
- [named-pipe-transport](concepts/named-pipe-transport.md) — 命名管道传输层：`\\.\pipe\wta-master-<GUID>`通信、指数退避重试、管道发现文件机制

### Agent管理
- [agent-registry](concepts/agent-registry.md) — Agent注册表系统：KNOWN_AGENTS静态表、AgentProfile结构、5个内置Agent配置、ACP命令构建、GPO过滤
- [agent-pane-ui](concepts/agent-pane-ui.md) — Agent面板UI集成：XAML AgentPaneContent控件、36px顶部栏、Stash/Restore生命周期、跨窗口拖拽桥接

### 自动化与配置
- [osc133-autofix](concepts/osc133-autofix.md) — OSC 133自动修复管线：OSC 133;D标记传播、ProtocolVtSequenceReceived事件、AutofixState状态机
- [hooks-auto-upgrade](concepts/hooks-auto-upgrade.md) — Hooks自动升级机制：MSIX捆绑hooks插件、bundle版本快路径、per-CLI升级流程、opt-in策略
- [settings-configuration](concepts/settings-configuration.md) — Agent设置系统：MTSM全局设置+Profile级设置、JSON配置、设置UI、热重载、GPO策略覆盖
- [wtcli-command-tool](concepts/wtcli-command-tool.md) — wtcli命令行工具：C++ CLI通过COM控制WT、键名翻译、SendEvent JSON封装、CliChannel路径解析

## 🎯 示例导航（Examples）

- [configure-agent-profile](examples/configure-agent-profile.md) — 配置Agent Profile：settings.json配置Agent CLI路径、委托Agent、模型参数
- [use-agent-pane](examples/use-agent-pane.md) — 使用Agent面板：快捷键操作、Stash/Restore、拖拽分屏、会话管理
- [enable-autofix-osc133](examples/enable-autofix-osc133.md) — 启用OSC 133自动修复：Shell Integration配置、OSC 133协议启用、PowerShell/bash/zsh/fish支持
- [develop-custom-agent](examples/develop-custom-agent.md) — 开发自定义ACP Agent：实现ACP JSON-RPC规范、initialize握手、session管理、流式响应

## 📚 参考导航（References）

- [intelligent-terminal-sources](references/intelligent-terminal-sources.md) — Windows Terminal AI Agent集成双进程架构、ACP协议、COM服务器、WTA编排器源码路径与关键文件清单

## 🔗 关联 Bundle

- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与跨项目模式
- [hermes-agent](../hermes-agent/index.md) — Hermes Agent可作为ACP Agent接入WTA
- [deepseek-harness](../deepseek-harness/index.md) — DeepSeek Harness支持ACP协议服务端
- [cordis](../cordis/index.md) — Cordis插件架构模式参考

---

> **信任声明**：本文档基于 Windows Terminal Agent (WTA) 源码逐模块分析，经 OKF 五阶段流程（R→I→E→V→C）生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot
> 
> **内容统计**：10 个概念 + 4 个示例 + 1 个信源 = 15 个内容文档

```{toctree}
:hidden:

concepts/acp-json-rpc-protocol
concepts/agent-pane-ui
concepts/agent-registry
concepts/com-protocol-server
concepts/dual-process-architecture
concepts/hooks-auto-upgrade
concepts/named-pipe-transport
concepts/osc133-autofix
concepts/settings-configuration
concepts/wtcli-command-tool
examples/configure-agent-profile
examples/develop-custom-agent
examples/enable-autofix-osc133
examples/use-agent-pane
references/intelligent-terminal-sources
.spec/facts
```
