---
okf_version: "0.2"
title: "Agency Agents App"
description: "Agency Agents原生桌面应用 - Tauri 2 + Svelte 5的多Agent工作台"
tags:
  - ai-agent
  - desktop-app
  - tauri
  - svelte5
  - rust
  - multi-agent
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/agency-agents/agency-agents-app
related:
  - "[[ai-agent-fundamentals]]"
  - "[[agency-agents]]"
  - "[[hermes-agent]]"
---

# Agency Agents App

Agency Agents App 是基于 Agency Agents 构建的原生桌面应用，采用 Tauri 2（Rust后端）+ Svelte 5（Runes响应式前端）技术栈。核心包括三源Catalog模型（bundled/managed/userClone）、五状态安装协调模型、约35个Tauri命令分4组（基础设施/GitHub/更新器/Corpus/安装协调）、7导航分区侧边栏、命令面板（⌘K）、三态主题系统，以及5个Preset Teams策展团队和Loadout导入导出。

## 🧩 概念导航（Concepts）

- [tauri-backend-commands](concepts/tauri-backend-commands.md) — Tauri后端命令系统：约35个命令分4组、Rust模块组织、keyring跨平台密钥、OAuth Device Flow、DTO序列化约定
- [svelte5-runes-architecture](concepts/svelte5-runes-architecture.md) — Svelte 5 Runes架构：$state/$derived/$effect响应式、class-based单例Store、7导航分区、三态主题、命令面板
- [catalog-install-store](concepts/catalog-install-store.md) — Catalog安装与Store状态管理：三源模型、五状态协调、Corpus三哈希索引、模块级去重reconcile、懒加载缓存

## 🎯 示例导航（Examples）

- [build-tauri-app](examples/build-tauri-app.md) — 构建Tauri桌面应用：pnpm依赖安装、Rust编译、开发模式启动、前后端命令调用、跨平台构建

## 📚 参考导航（References）

- [agency-agents-app-sources](references/agency-agents-app-sources.md) — Agency Agents App源码结构、Rust后端命令、Svelte前端组件、数据模型与状态管理信源清单

## 🔗 关联 Bundle

- [agency-agents](../agency-agents/index.md) — Agency Agents核心Persona库与NEXUS编排框架
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念
- [hermes-agent](../hermes-agent/index.md) — Hermes Agent Gateway模式参考

---

> **信任声明**：本文档基于 Agency Agents App v0.3.0 源码逐模块分析，经 OKF 五阶段流程生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

concepts/catalog-install-store
concepts/svelte5-runes-architecture
concepts/tauri-backend-commands
examples/build-tauri-app
references/agency-agents-app-sources
```
