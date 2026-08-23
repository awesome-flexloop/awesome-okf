---
type: Concept
title: xeus 与 JupyterLite 生态
description: xeus、JupyterLite、emscripten-forge、jupyterlite-xeus 之间的关系与技术栈
tags: [xeus, jupyterlite, emscripten-forge, wasm, ecosystem, architecture]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
  - id: build-env
    resource: /references/build-env-source.md
    title: 构建环境配置信源
---

## 生态全景

xeus-lite-demo 处于多个开源项目的交汇点，理解这些项目之间的关系有助于掌握其工作原理：

```
┌─────────────────────────────────────────────────────┐
│                   用户浏览器                          │
│  ┌───────────────────────────────────────────────┐  │
│  │           JupyterLite 静态站点                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │  │
│  │  │ Notebook │  │  Lab 界面 │  │  终端/插件  │ │  │
│  │  │   前端   │  │          │  │             │ │  │
│  │  └────┬─────┘  └────┬─────┘  └──────┬──────┘ │  │
│  │       │              │               │        │  │
│  │  ┌────▼──────────────▼───────────────▼──────┐ │  │
│  │  │        Jupyter 协议 (WebSocket/二进制)    │ │  │
│  │  └────┬──────────────┬──────────────┬──────┘ │  │
│  │       │              │              │        │  │
│  │  ┌────▼────┐  ┌─────▼─────┐  ┌────▼─────┐ │  │
│  │  │ xeus-   │  │  xeus-r   │  │  xeus-cpp │ │  │
│  │  │ python  │  │  (R内核)  │  │ (C++内核) │ │  │
│  │  │(Python) │  │           │  │           │ │  │
│  │  └────┬────┘  └─────┬─────┘  └────┬──────┘ │  │
│  │       │              │              │        │  │
│  │  ┌────▼──────────────▼──────────────▼──────┐ │  │
│  │  │     WebAssembly (WASM) 运行时            │ │  │
│  │  │     conda 包 (emscripten-forge 编译)     │ │  │
│  │  └─────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         ▲                                    ▲
         │ 静态文件(HTML/JS/WASM)              │ conda包
         │                                    │
┌────────┴─────────┐  ┌───────────────────────┴──────┐
│  GitHub Pages    │  │  emscripten-forge / prefix.dev│
│  (静态托管)      │  │  (WASM conda包仓库)           │
└──────────────────┘  └──────────────────────────────┘
         ▲
         │ 构建产物
┌────────┴──────────────────────────────────────────┐
│         GitHub Actions (CI 构建)                    │
│  ┌─────────────────────────────────────────────┐   │
│  │ jupyter lite build (jupyterlite-xeus 插件)   │   │
│  │ 读取 environment.yml → 打包 WASM 内核+包     │   │
│  │ 读取 content/ → 打包 Notebook 文件           │   │
│  │ 输出 dist/ → 静态站点                         │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

## 核心组件

### JupyterLite

JupyterLite 是 Jupyter 的浏览器版本，将 JupyterLab 和 Notebook 前端编译为 JavaScript，配合 WebAssembly 内核在浏览器中完整运行。它是整个方案的前端和运行时框架。

- 提供 JupyterLab/Notebook 7 用户界面
- 实现 Jupyter 协议的浏览器端路由
- 管理内核生命周期
- 提供静态站点构建工具（`jupyter lite build`）

### xeus 内核

xeus 是一个 C++ 编写的 Jupyter 内核协议实现框架，支持多种编程语言：

| 内核 | 语言 | 说明 |
|------|------|------|
| xeus-python | Python | 基于 CPython 编译为 WASM，不是 Pyodide |
| xeus-r | R | R 语言的 WASM 内核 |
| xeus-cpp | C++ | C++ 交互式解释器（cling/xeus-cling 的 WASM 版本） |
| xeus-lua | Lua | Lua 语言内核 |
| xeus-ruby | Ruby | Ruby 语言内核 |

> xeus-python 与 Pyodide 的区别：xeus-python 是将标准 CPython 编译为 WASM，而 Pyodide 是 CPython 的一个分支，带有额外的 JavaScript 互操作层。xeus-python 更接近标准 Python 行为。

### emscripten-forge

emscripten-forge 是一个将 conda 包交叉编译为 WebAssembly 的项目。它是 xeus-lite 能够使用 conda 包生态的关键：

- 使用 Emscripten 编译器将 C/C++/Fortran 代码编译为 WASM
- 提供数百个预编译的科学计算包（numpy、pandas、matplotlib、scipy 等）
- 包托管在 prefix.dev 平台上
- 通道地址：`https://repo.prefix.dev/emscripten-forge-dev`

### jupyterlite-xeus

[jupyterlite-xeus](https://jupyterlite-xeus.readthedocs.io/) 是 JupyterLite 的一个插件，将 xeus 内核集成到 JupyterLite 构建系统中：

- 在 `jupyter lite build` 时读取 `environment.yml`
- 从 emscripten-forge 通道下载 WASM conda 包
- 将内核和包打包到静态站点中
- 版本要求 >=4.3（根据 build-environment.yml）

## 技术栈版本关系

| 组件 | 版本约束 | 来源 |
|------|---------|------|
| Python (CI 构建) | 3.12 | deploy.yml 中 actions/setup-python |
| jupyterlite-core | >=0.7 | build-environment.yml |
| jupyterlite-xeus | >=4.3 | build-environment.yml |
| notebook | >=7.5 | build-environment.yml |
| micromamba | 1.5.8-0 | deploy.yml |

## 构建时 vs 运行时

理解 xeus-lite 生态的关键是区分**构建时**和**运行时**：

- **构建时**（在 GitHub Actions 的 Linux 上）：
  - jupyterlite-core 提供 CLI 工具
  - jupyterlite-xeus 插件解析 environment.yml
  - 下载 WASM 包并打包
  - 输出静态文件到 dist/
  
- **运行时**（在用户浏览器中）：
  - 静态文件被加载
  - WASM 内核启动
  - 用户执行 Notebook 代码
  - 代码在浏览器的 WASM 虚拟机中运行

这两个阶段使用完全不同的包集合，这就是为什么需要两个 environment.yml 文件。

## 相关概念

- [双环境模型](02-dual-environment.md) — 详细理解构建环境和运行时环境的区别
- [运行时环境配置](04-runtime-env-config.md) — environment.yml 的配置详解
- [构建环境配置](05-build-env-config.md) — build-environment.yml 的配置详解
- [GitHub 模板三步部署](03-github-template-deploy.md) — 快速上手
