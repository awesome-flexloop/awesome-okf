---
type: Reference
title: JupyterLite 应用框架源码信源
description: "@jupyterlite/application包的JupyterLiteApp应用框架、扩展加载机制的源码API登记"
tags: [application, jupyterlab, extension, plugin, app]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:08:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: app-package
    resource: /references/app-source.md
    title: packages/application/
---

## 源码位置

- `packages/application/src/` — 应用框架核心
- `packages/application-extension/src/` — 应用默认扩展
- `app/` — 各应用构建配置（lab/notebook/repl等）

## 应用架构

JupyterLite 复用 JupyterLab 的插件架构，基于 Lumino 的 Application/Plugin 系统：

```
┌─────────────────────────────────────────────┐
│            JupyterLiteApp (前端)              │
│  ┌─────────────────────────────────────────┐│
│  │  JupyterFrontEnd (JupyterLab基类)        ││
│  │  ├─ Plugin系统 (Token/Provider)          ││
│  │  ├─ CommandRegistry (命令系统)           ││
│  │  ├─ Shell (布局Shell)                    ││
│  │  └─ ServiceManager (服务管理器)           ││
│  └─────────────────────────────────────────┘│
│                                             │
│  核心插件 (@jupyterlite/*-extension):        │
│  ├─ services-extension: 内核/内容/会话服务   │
│  ├─ apputils-extension: 工具函数            │
│  ├─ notebook-application-extension: Notebook│
│  └─ repl-extension: REPL界面                │
└─────────────────────────────────────────────┘
```

## 构建配置（app/rspack.config.js）

前端使用 Rspack（Rust-based Webpack 替代）进行构建：
- 入口：`app/index.js`（bootstrap）
- 多应用构建：lab/notebook/repl/consoles/edit/tree/doc
- 输出：静态文件（HTML/JS/WASM），可部署到任意静态文件服务器

## Service Worker

JupyterLite 使用 Service Worker 实现：
1. **离线缓存**：缓存应用静态资源（JS/CSS/WASM）
2. **Drive API桥接**：Worker内的同步XHR `POST /api/drive` 被Service Worker拦截，转发到主线程BrowserStorageDrive
3. **内核文件系统**：DriveFS挂载后，Pyodide内核的所有文件操作通过Service Worker同步转发
