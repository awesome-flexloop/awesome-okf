---
type: Concept
title: OpenTUI 包生态与导入入口
description: 区分发布包、package subpath、workspace manifest 与官方入口文档，选择适合的 OpenTUI API 面。
source: "OpenTUI release script, package manifests, and official entrypoint documentation"
tags: [opentui, packages, entrypoints, runtime]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: packages
    resource: /references/package-surface.md
    title: 发布包与入口面登记
  - id: source-code
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
  - id: official-docs
    resource: /references/official-documentation.md
    title: 官方文档
---

# OpenTUI 包生态与导入入口

OpenTUI 的 npm package root、包内 subpath exports、workspace 目录和构建时生成的发布入口是不同层次。选择依赖时先决定应用模型，再从对应 package 的官方 entrypoint 表查准确 import path；不要把目录名直接当作稳定的 public API。

## 七个发布 package root

固定 commit 中的 `scripts/npm-publish.ts` 将以下七个 package root 放入发布清单。统计口径是 `RELEASE_PACKAGES` 数组中的 `releasePackage(...)` 条目，不是 workspace 的目录数、平台二进制包数或 `exports` 子路径数。[固定清单](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/scripts/npm-publish.ts#L43-L50)

| Package | 入口责任 |
|---|---|
| `@opentui/core` | renderer、renderables、终端 input、buffer、插件与 shared types |
| `@opentui/react` | React reconciler、JSX catalogue、hooks 与组件 |
| `@opentui/solid` | Solid reconciler、JSX、hooks 与组件 |
| `@opentui/keymap` | host-agnostic 键位映射、commands、addons 与 host adapters |
| `@opentui/qrcode` | QR 编码、终端输出和框架组件注册 |
| `@opentui/three` | Three.js WebGPU renderer 与相关终端场景适配 |
| `@opentui/ssh` | SSH server builder、authentication、middleware 与 sessions |

具体功能与可导入 subpath 请以[官方 Package entry points](https://opentui.com/docs/reference/package-entrypoints/) 为准。表格只给学习导航，不枚举每个 subpath 的所有符号。

## 常用入口选择

- **直接控制组件树**：从 `@opentui/core` 导入 `createCliRenderer` 和所需 renderable。
- **测试 Core 组件**：从 `@opentui/core/testing` 取测试 renderer 与 mock 驱动。
- **React UI**：从 `@opentui/react` 导入 `createRoot`、hooks 或组件；renderer factory 仍来自 `@opentui/core`。
- **Solid UI**：从 `@opentui/solid` 导入 `render`、hooks 或组件；Core primitives 仍可由 `@opentui/core` 导入。
- **复杂快捷键**：按需选 `@opentui/keymap` 及对应 host adapter。
- **QR、Three.js、SSH**：分别查 `@opentui/qrcode`、`@opentui/three`、`@opentui/ssh` 的官方指南和入口表。

Core manifest 直接声明 `.`、`./testing`、`./yoga`、runtime plugin、Tree-sitter worker 和 node assets 等入口。官方 entrypoints 文档同时列举了 framework-specific 和发布映射入口。例如 React 文档列出的 `@opentui/react/renderer` 由发布入口资料说明；在 workspace manifest 中不能简单假设每个文档入口都各有同名源码目录。[Core exports](https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/package.json#L91-L138) · [React entrypoints](https://opentui.com/docs/reference/package-entrypoints/)

## 版本和环境读法

本次源码基线 commit 为 `f8f608e2b9a41685d613a1156708ff06c826c3ce`。Core manifest 的 package version 和官方 `0.6.6` release notes 分别是版本字段；源码 checkout 没有精确匹配的 release tag。不要把三者合并成一句“本文就是某某 tag 源码”。

根 README 的开发要求为 Bun 1.4.1+ 与 Zig 0.16.0；Core manifest engines 则声明 Bun `>=1.3.14` 与 Node `>=26.4.0`。前者是开发环境要求，后者是 Core package 的运行时声明，不能互相替代。[源码快照登记](/references/source-code-snapshot.md)

## 选型顺序

先从 Core 学会渲染和关闭，再按团队现有 UI 模型选择 React 或 Solid。这样可以把终端行为和框架 reconciler 分开理解。若应用需要 Keymap 等额外能力，再将其作为单独 package 集成；官方入口矩阵可用来确认 host 支持、subpath 和关联指南。

## 相关概念

- [OpenTUI 生态总览](/concepts/00-ecosystem-overview.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [React binding](/concepts/06-react-binding.md)
- [Solid binding](/concepts/07-solid-binding.md)
- [OpenTUI 生态包](/concepts/09-ecosystem-packages.md)
