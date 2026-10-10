---
type: Wiki Tutorial
title: "认识 Tauri 2.0 与 Electron"
description: "两种桌面跨平台开发方案的本质差异——体积极小化背后的架构逻辑"
tags: [Tauri, Electron, 桌面开发, 跨平台, WebView, Rust]
sources:
  - id: wechat-frontend-god-tauri-electron
    resource: "https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg"
    title: "取代 Electron？Tauri 2.0 做到全平台适配、轻量化！"
  - id: electron-why
    resource: "https://www.electronjs.org/docs/latest/why-electron"
    title: "Why Electron（Electron 官方文档）"
  - id: tauri-20-release
    resource: "https://v2.tauri.app/blog/tauri-20/"
    title: "Tauri 2.0 Stable Release（Tauri 官方博客）"
generated: { by: process:wechat-public-okf, at: 2026-10-10 }
status: draft
stale_after: 2027-10-10
---

# 认识 Tauri 2.0 与 Electron

## 一句话概览

**Electron** 用 Web 技术栈做桌面应用——它把完整 Chromium 和 Node.js **打包进每个应用**；**Tauri 2.0** 也用 Web 技术栈，但**不带头**渲染引擎，改用**操作系统自带的系统 WebView**，并把后端换成了轻量的 **Rust**。这决定了二者在体积、性能、生态上的根本分野[^wechat] [^electron] [^tauri20]。

## Electron 的痛点集中在哪里

Electron 一度是桌面跨平台开发的第一选择：Web 技术栈上手快，前端开发者能直接做桌面应用。但它的架构决定了「每个应用都要携带完整 Chromium 内核 + Node.js 运行时，无法按需精简」[^wechat]。

由此带来的体验问题很直接：

- **体积大**：简单应用 80MB 起步，复杂应用超过 300MB（文章作者参考值，未复测）[^wechat]；
- **内存高**：空闲内存常超 120MB，复杂场景可破 1GB（作者参考值）[^wechat]；
- **启动慢**：1-4 秒，中低端设备更慢；
- **久用变卡**：长期运行 CPU 占用居高不下。

这些覆盖了「下载快不快、安装占不占地、跑得卡不卡」的用户直接感受。[^wechat]

## Tauri 2.0：把「轻」做到极致的思路

Tauri 的思路完全不同——**不打包浏览器内核，直接调用系统原生 WebView**[^wechat]：

| 平台 | 使用的系统 WebView |
|------|-------------------|
| Windows | WebView2（基于 Chromium 的 Edge WebView） |
| macOS | WKWebView |
| Linux | WebKitGTK |

应用只打包**核心业务代码 + Rust 后端**，所以体积极小。以基础 Markdown 编辑器为例，Electron 约 120MB，Tauri 2.0 约 5-10MB（最小可到 3.5MB）——体积缩小 10 倍以上[^wechat]。

> **本质差异**：Electron 在打包期「编译期捆绑」完整渲染引擎，Tauri 在运行期「复用」目标操作系统已装的系统 WebView。前者换来渲染一致性，后者换来轻量（但依赖目标机 WebView 版本）。

## 关键事实速查

| 维度 | Electron | Tauri 2.0 |
|------|----------|-----------|
| 渲染引擎 | 自带 Chromium | 系统 WebView（WebView2/WKWebView/WebKitGTK） |
| 后端运行时 | Node.js | Rust |
| 最小粒度 | 整包携带引擎 | 仅业务代码 + 轻量 Rust 二进制 |
| 典型演示体积 | 约 120MB（Markdown 编辑器） | 5-10MB（最小 3.5MB） |

## 参考文献

[^wechat]: 前端之神（林三心不学挖掘机），《取代 Electron？Tauri 2.0 做到全平台适配、轻量化！》，https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg
[^electron]: Electron 官方文档《Why Electron》，https://www.electronjs.org/docs/latest/why-electron
[^tauri20]: Tauri 官方博客《Tauri 2.0 Stable Release》，https://v2.tauri.app/blog/tauri-20/