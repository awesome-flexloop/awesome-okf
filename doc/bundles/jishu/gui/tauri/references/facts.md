---
type: Facts
title: "事实登记表（F 编号）"
description: "《Tauri 2.0 vs Electron》文章事实登记——F-001 ~ F-017，区分页面事实（page_fact）与作者陈述（author_claim）"
sources:
  - id: wechat-frontend-god-tauri-electron
    resource: "https://mp.weixin.qq.com/s/cvvU940cWXLA_qP8NCDkGg"
    title: "取代 Electron？Tauri 2.0 做到全平台适配、轻量化！"
generated: { by: process:wechat-public-okf, at: 2026-10-10 }
---

# 事实登记表（Facts）

> **登记纪律**：本表仅记录页面事实与作者陈述，不含执行者解读。执行者洞察见 [knowledge-map.md](knowledge-map.md)。类型说明：
> - `page_fact`：文章结构、标题、作者、日期、可客观核验的页面属性。
> - `author_claim`：作者提出的建议、因果式表述、价值判断或解读（无论是否科学）。
> - `author_data`：作者引用的具体数据（体积/内存/耗时等），属作者陈述，未在本流程独立复测。

| F | 声明（claim） | 类型 | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 文章标题为《取代 Electron？Tauri 2.0 做到全平台适配、轻量化！》 | page_fact | wechat-frontend-god-tauri-electron | 页面标题 | verified |
| F-002 | 文章发表于公众号「前端之神」，作者署名「林三心不学挖掘机」 | page_fact | wechat-frontend-god-tauri-electron | 页面头部/底部 | verified |
| F-003 | 文章发布页面显示时间为 2026年10月8日 01:46 | page_fact | wechat-frontend-god-tauri-electron | 页面时间戳 | verified |
| F-004 | Electron 需要打包完整 Chromium 内核与 Node.js 运行时，无法按需精简 | author_claim | wechat-frontend-god-tauri-electron | 章节 01 | verified（官方一致） |
| F-005 | Electron 应用体积：简单应用 80MB 起步，复杂应用超过 300MB | author_data | wechat-frontend-god-tauri-electron | 章节 01 | single-source |
| F-006 | Electron 应用空闲内存常超 120MB，复杂场景破 1GB | author_data | wechat-frontend-god-tauri-electron | 章节 01 | single-source |
| F-007 | Electron 应用启动需 1-4 秒，中低端设备更慢；长期运行易卡顿、CPU 占用高 | author_data | wechat-frontend-god-tauri-electron | 章节 01 | single-source |
| F-008 | Tauri 2.0 不打包浏览器内核，调用系统原生 WebView（Windows: WebView2、macOS: WKWebView、Linux: WebKitGTK） | page_fact | wechat-frontend-god-tauri-electron | 章节 02 | verified（官方一致） |
| F-009 | Tauri 2.0 只打包核心业务代码与 Rust 后端 | page_fact | wechat-frontend-god-tauri-electron | 章节 02 | verified |
| F-010 | 基础 Markdown 编辑器示例体积：Electron 约 120MB，Tauri 2.0 约 5-10MB，最小能到 3.5MB，体积缩小 10 倍以上 | author_data | wechat-frontend-god-tauri-electron | 章节 02 | single-source |
| F-011 | Tauri 2.0 核心进程由 Rust 编写，兼顾高性能与内存安全 | page_fact | wechat-frontend-god-tauri-electron | 章节 03 | verified |
| F-012 | Tauri 2.0 启动速度 0.5 秒以内 | author_data | wechat-frontend-god-tauri-electron | 章节 03 | single-source |
| F-013 | Tauri 2.0 空闲内存 30-50MB，日常 60-100MB | author_data | wechat-frontend-god-tauri-electron | 章节 03 | single-source |
| F-014 | Tauri 2.0 相比 1.0 扩展到 iOS、Android 移动端，一次开发多端适配 | page_fact | wechat-frontend-god-tauri-electron | 章节 04 | verified（官方一致） |
| F-015 | Tauri 2.0 兼容 React、Vue、Svelte 等主流前端框架，CLI 更完善、配置简化 | author_claim | wechat-frontend-god-tauri-electron | 章节 04 | verified（官方一致） |
| F-016 | Tauri 2.0 敏感权限默认关闭、需手动开启，叠加 Rust 内存安全特性 | page_fact | wechat-frontend-god-tauri-electron | 章节 04 | verified（官方一致） |
| F-017 | Tauri 2.0 可调用系统通知、文件系统、硬件设备等原生 API，无需第三方插件 | author_claim | wechat-frontend-god-tauri-electron | 章节 04 | verified（官方一致） |
| F-018 | 作者结论：Tauri 2.0 不是对 Electron 的简单替代，而是桌面跨平台开发的一次升级；「吊打 Electron」略显夸张 | author_claim | wechat-frontend-god-tauri-electron | 总结 | single-source |