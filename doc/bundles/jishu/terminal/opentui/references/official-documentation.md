---
type: Reference
title: OpenTUI 官方文档登记
description: 登记 OpenTUI 官方文档入口、0.6.6 发布说明及本 bundle 覆盖的官方学习主题。
tags: [opentui, official-docs, documentation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-docs
    resource: https://opentui.com/docs/
    title: OpenTUI 官方文档
  - id: opentui-release-066
    resource: https://opentui.com/docs/releases/0.6.6/
    title: OpenTUI 0.6.6 发布说明
---

# OpenTUI 官方文档登记

## 信源信息

| 项目 | 值 |
|---|---|
| 官方文档入口 | [opentui.com/docs](https://opentui.com/docs/) |
| 本次盘点日期 | 2026-10-20 |
| 文档版本参照 | 官方文档中的 `0.6.6` release notes |
| 官方发布说明 | [0.6.6](https://opentui.com/docs/releases/0.6.6/) |
| 与源码关系 | 官方文档版本和固定源码 commit 分开标识；遇到差异时在教程中分别注明 |

## 覆盖页面

- 入门：Quickstart、runtime support。
- Core 概念：renderer、renderables、layout、keyboard、interaction、lifecycle、testing。
- Framework bindings：React、Solid。
- Native 机制：native rendering、frames and output、host I/O and time。
- Package/reference：package entrypoints、API index、renderables 与 Yoga。
- 扩展包：Keymap、QRCode、Three.js、SSH 等对应指南。
- Release notes：`0.6.6` 发布说明。

上述页面用于交叉核验面向用户的使用路径与 API 说明。源码事实仍以 [固定源码快照](/references/source-code-snapshot.md) 为准；官方文档中 `next` 或未标记为 `0.6.6` 的内容不自动视为该发布版能力。

## 阅读与引用约定

1. 概念文档使用官方页面补充使用约束、学习路径和面向读者的解释。
2. 关键类、函数、类型与生命周期行为须同时对照固定源码，或明确标注其证据只来自官方文档。
3. 页面链接采用官方站点路径；引用本 bundle 内其它信源登记时使用 bundle-relative `/references/...` 路径。

## 相关概念

- [OpenTUI 生态总览](/concepts/00-ecosystem-overview.md)
- [React binding](/concepts/06-react-binding.md)
- [Solid binding](/concepts/07-solid-binding.md)
- [Native layout 与渲染](/concepts/03-layout-and-native-rendering.md)
