---
type: Reference
title: OpenTUI 发布包与入口面登记
description: 记录发布脚本中的 package root 清单，并说明官方文档所列 subpath exports 与包数采用不同统计口径。
tags: [opentui, packages, entrypoints, api]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-release-script
    resource: https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/scripts/npm-publish.ts#L43-L50
    title: 固定 commit 的 release package 清单
  - id: opentui-entrypoints
    resource: https://opentui.com/docs/reference/package-entrypoints/
    title: 官方 package entrypoints 参考
  - id: opentui-core-manifest
    resource: https://github.com/anomalyco/opentui/blob/f8f608e2b9a41685d613a1156708ff06c826c3ce/packages/core/package.json#L91-L138
    title: Core package exports
---

# OpenTUI 发布包与入口面登记

## Release package roots

发布脚本 `RELEASE_PACKAGES` 数组列出以下七个发布包：

| 包名 | 教程入口 |
|---|---|
| `@opentui/core` | renderer、renderables、输入、测试与 shared types |
| `@opentui/react` | React reconciler、JSX、hooks 与组件 |
| `@opentui/solid` | Solid reconciler、JSX、hooks 与组件 |
| `@opentui/three` | Three.js WebGPU renderer 与终端场景集成 |
| `@opentui/qrcode` | QR 编码、终端渲染与框架组件注册 |
| `@opentui/keymap` | host-agnostic 键位映射、addons 与 host adapters |
| `@opentui/ssh` | SSH server builder、认证、中间件与会话 |

七项数字来自 `scripts/npm-publish.ts` 中 `RELEASE_PACKAGES` 的 `releasePackage(...)` 条目计数；它不表示 workspace 目录数、全部 exports subpaths 数、生成的平台包数或所有内部依赖数。

## Entry point 边界

官方 entrypoints 页面进一步列出各 package 的 root 与 subpath。例如 Core 包提供 `@opentui/core/testing`、`@opentui/core/yoga`、runtime plugin、Tree-sitter worker 等入口；React 文档列出 `@opentui/react/renderer` 和 `@opentui/react/test-utils`；Solid 文档列出 preload、Bun plugin、components 与 JSX runtime。

Core workspace manifest 的 `exports` 是固定 commit 的源码视图；官方 entrypoints 是发布文档视图。两者用途不同，个别入口可能来自构建时生成的发布映射，不应从 workspace manifest 单独推断完整的发布入口清单。

## 版本与环境边界

- 固定源码 commit：`f8f608e2b9a41685d613a1156708ff06c826c3ce`。
- Core manifest package version：`0.6.6`。
- 官方文档 release notes：`0.6.6`。
- package root 与运行时支持要求以对应 manifest 和官方 runtime-support/entrypoints 页面为准；不要用根 README 的开发工具要求替代 package engines 字段。

## 相关概念

- [包生态与入口](/concepts/01-packages-and-entrypoints.md)
- [OpenTUI 生态包](/concepts/09-ecosystem-packages.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
