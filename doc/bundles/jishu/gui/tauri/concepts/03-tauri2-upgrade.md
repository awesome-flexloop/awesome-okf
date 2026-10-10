---
type: Wiki Tutorial
title: "Tauri 2.0 升级点（相比 1.0）"
description: "从「好用」到「更全面」的四大升级——跨端、开发体验、安全权限、系统集成"
tags: [Tauri, Tauri 2.0, iOS, Android, 权限, CLI, 跨平台]
sources:
  - id: wechat-frontend-god-tauri-electron
    resource: "https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg"
    title: "取代 Electron？Tauri 2.0 做到全平台适配、轻量化！"
  - id: tauri-20-release
    resource: "https://v2.tauri.app/blog/tauri-20/"
    title: "Tauri 2.0 Stable Release（Tauri 官方博客）"
generated: { by: process:wechat-public-okf, at: 2026-10-10 }
status: draft
stale_after: 2027-10-10
---

# Tauri 2.0 升级点（相比 1.0）

Tauri 1.0 已经比 Electron 轻，但若论跨端覆盖与开发体验仍有短板。2.0 补齐了这些短板，从「好用」走向「更全面」[^wechat]。

## 四大升级

### 1. 跨端更强：从桌面扩展到移动端

Tauri 2.0 在 Windows / macOS / Linux 之外，新增 **iOS 与 Android** 支持——一套前端代码 + Rust 后端，一次开发多端适配[^wechat] [^tauri20]。这使其从纯桌面框架升级为「桌面 + 移动」的跨平台方案。

### 2. 开发更顺：配置简化 + CLI 更完善

- 项目配置简化；
- CLI（`tauri` 命令行工具）更完善；
- 兼容 **React、Vue、Svelte** 等主流框架，前端开发者几乎无缝上手[^wechat]。

### 3. 安全权限更细：默认关闭、显式授予

- **敏感权限默认关闭**，需要时手动开启；
- 叠加 **Rust 内存安全**特性，稳定性更好[^wechat]。

> 这一「最小权限」设计降低了应用的安全暴露面，是与 Electron「全量 Node 权限」的重要区别。

### 4. 系统集成更深：原生 API 直调

- 系统通知、文件系统、硬件设备等原生能力可直接调用；
- 更接近原生应用体验[^wechat]。

> 说明：文章表述「不用依赖第三方插件」略绝对——多数常用能力可经官方 Rust 命令/能力暴露，但部分深度原生能力仍可能需要官方或社区插件辅助（见 [核验报告](../references/verification.md)）。

## 升级意义：从「好用」到「更全面」

1.0 解决「轻」与「快」，2.0 进一步解决「能不能覆盖更多端、好不好开发、安不安全、原生感强不强」。因此 2.0 的升级不只是版本号变化，而是把 Tauri 从「轻量备选」推向了「桌面 + 移动跨平台的完整方案」[^wechat]。

## 参考文献

[^wechat]: 前端之神，《取代 Electron？Tauri 2.0 做到全平台适配、轻量化！》，https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg
[^tauri20]: Tauri 官方博客《Tauri 2.0 Stable Release》，https://v2.tauri.app/blog/tauri-20/