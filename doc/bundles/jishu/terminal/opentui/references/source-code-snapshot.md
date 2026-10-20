---
type: Reference
title: OpenTUI 源码快照登记
description: 登记 OpenTUI 源码仓库的不可变 commit、仓库定位、核心目录与源码事实引用边界。
tags: [opentui, source-code, zig, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-commit
    resource: https://github.com/anomalyco/opentui/tree/f8f608e2b9a41685d613a1156708ff06c826c3ce
    title: OpenTUI 固定源码 commit
---

# OpenTUI 源码快照登记

## 信源坐标

| 项目 | 值 |
|---|---|
| 项目 | OpenTUI，TypeScript API 与 Zig native core 组成的终端 UI 项目 |
| 远端仓库 | `https://github.com/anomalyco/opentui` |
| Git remote（快照记录） | `git@github.com:anomalyco/opentui.git` |
| 固定源码 commit | `f8f608e2b9a41685d613a1156708ff06c826c3ce` |
| commit 页面 | [固定 commit](https://github.com/anomalyco/opentui/commit/f8f608e2b9a41685d613a1156708ff06c826c3ce) |
| 本地只读检出位置 | `external/dao/anomalyco/opentui/`（仅工作区定位，不作为 bundle 引用） |
| 盘点日期 | 2026-10-20 |
| 精确 release tag | 未找到与该 HEAD 精确匹配的 tag |

源码文件引用采用 GitHub `blob/<commit>/<path>#Lx-Ly` 形式，避免依赖本机路径或浮动分支。该 checkout 的根 README 和 Core manifest 各自记录开发工具及运行时版本要求；这些字段不替代本条固定 commit 坐标。

## 核心路径

| 路径 | 本次核验范围 |
|---|---|
| `packages/core/src/` | Core exports、renderer、renderables、testing API 与 renderable tree |
| `packages/react/src/` | React root reconciler 与 renderer cleanup 连接 |
| `packages/solid/src/` | Solid reconciler、renderer adapter 与响应式 hooks |
| `packages/native/src/` | Zig native scene、Yoga node 操作与绘制路径 |
| `packages/web/src/content/docs/` | 官方文档站内容源，作为仓库内版本化文档证据 |
| `scripts/npm-publish.ts` | release package 数组及发布清单 |
| `package.json`、`packages/*/package.json` | workspace、package metadata 与 exports |

## 版本边界

本 bundle 的源码行为事实以 commit `f8f608e2b9a41685d613a1156708ff06c826c3ce` 为准。该 checkout 的 Core manifest 将 package version 记为 `0.6.6`，官方站点也有 `0.6.6` release notes；这两个版本字段单独记录，不据此推断该 commit 对应一个精确 tag。

本页仅记录本次学习覆盖的源码区域，不表示对仓库每个文件、测试或内部符号逐行注释。

## 相关概念

- [OpenTUI 生态总览](/concepts/00-ecosystem-overview.md)
- [Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)
- [Native layout 与渲染](/concepts/03-layout-and-native-rendering.md)
