---
type: Concept
title: Keymap、QRCode、Three 与 SSH 生态包
description: 按功能理解 OpenTUI 的键位映射、QR、Three.js 与 SSH packages，并从官方入口表确认运行时和框架边界。
source: "OpenTUI package manifests and official package documentation"
tags: [opentui, keymap, qrcode, three, ssh]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: package-surface
    resource: /references/package-surface.md
    title: 发布包与入口面登记
  - id: official-docs
    resource: /references/official-documentation.md
    title: 官方文档
  - id: source-code
    resource: /references/source-code-snapshot.md
    title: 固定源码快照
---

# Keymap、QRCode、Three 与 SSH 生态包

OpenTUI 的外围 packages 扩展了 Core 的应用场景。它们不是学习 Core renderer 的前置条件；应先确认自己要解决的是键盘命令组织、QR 输出、WebGPU 画面还是 SSH 远程终端，再查对应指南和 subpath。

## Keymap：把按键组织成命令系统

`@opentui/keymap` 提供 host-agnostic 键位映射核心，可进一步接入 OpenTUI、React、Solid 或 HTML host。官方入口表还列出 extras、addons、testing 和 runtime modules subpaths。适合快捷键受到当前焦点、模式、优先级或多键序列影响的应用；简单的全局快捷键可先从 Core keyboard listener 开始。[Keymap overview](https://opentui.com/docs/keymap/overview/) · [Keymap entrypoints](https://opentui.com/docs/reference/package-entrypoints/)

Keymap 的命令匹配可能改变同一按键是否继续传给 focused renderable。应用应把 dispatch 顺序、scope 和 disposal 纳入测试，而不是只验证配置对象能被创建。

## QRCode：编码与终端/框架组件

`@opentui/qrcode` 提供 QR encoder、segments、error correction、SVG/terminal output 和 `QRCodeRenderable`。官方 entrypoints 还列出 React 与 Solid 集成 subpaths；两种框架的注册名称有区分，不能从一个 JSX 命名形式推断另一个框架采用相同名字。[QR encoder](https://opentui.com/docs/reference/qr-encoder/) · [QR component](https://opentui.com/docs/components/qr-code/)

当只需要生成或输出 QR 时，先使用包的 encoder/renderable API；只有需要框架组件集成时，才额外引入 React/Solid 专用注册入口。

## Three：终端中的 WebGPU 画面

官方 entrypoints 将 `@opentui/three` 标为 Bun-only，并列出 Three.js WebGPU renderer、renderable、sprites、effects、resource pools 和 physics adapters 等表面。它适用于把 Three.js 图形内容接入 OpenTUI 场景的需求，不是 Core 文本 layout 的默认替代品。[Three.js guide](https://opentui.com/docs/reference/three/) · [Package entrypoints](https://opentui.com/docs/reference/package-entrypoints/)

由于运行时和 GPU 能力有额外前置条件，应先确认环境支持，再把此包纳入应用 architecture。其具体 renderable 生命周期与资源池约定应以 Three 指南为准。

## SSH：把 TUI 暴露给远程会话

`@opentui/ssh` 的官方入口说明列出 SSH server builder、authentication、middleware、sessions、logging、errors 与 public types。官方 entrypoints 同时给出其 Bun/Node 运行时版本要求；部署前需对照当前文档和 package engines，而不能用 Core 自身的要求替代。[SSH guide](https://opentui.com/docs/reference/ssh/) · [Package entrypoints](https://opentui.com/docs/reference/package-entrypoints/)

SSH server 是应用拥有的服务资源。关闭时需要协调 server sessions、应用创建的异步资源和 renderer；参见[生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)。

## 查找完整 API

本篇聚焦 package 定位，不枚举每个 subpath 的所有符号。版本升级或新增 integration 时，应先从[发布包与入口登记](/references/package-surface.md)进入官方 entrypoints，再打开对应的 feature guide。所有 package imports 和运行时约束须按固定源码/API 文档复核。

## 相关概念

- [包与入口](/concepts/01-packages-and-entrypoints.md)
- [输入、焦点和 Keymap](/concepts/04-input-focus-and-keymap.md)
- [生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)
- [官方文档登记](/references/official-documentation.md)
