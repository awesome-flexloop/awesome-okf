---
type: Concept
title: jupyterlite-lsp 项目介绍
description: jupyterlite-lsp 是什么、解决什么问题、核心特性与项目定位
tags: [introduction, overview, jupyterlite, lsp]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
  - id: yaml-readme
    resource: /references/yaml-plugin-source.md
    title: YAML语言服务器包源码引用
---

## 什么是 jupyterlite-lsp

jupyterlite-lsp 是一个为 [JupyterLite](https://jupyterlite.rtfd.io)（浏览器端 Jupyter）提供 [Language Server Protocol（LSP）](https://microsoft.github.io/language-server-protocol)支持的扩展。它模拟 [jupyter-lsp](https://github.com/jupyter-lsp/jupyterlab-lsp)（JupyterLab 的 LSP 扩展）的 REST 和 WebSocket 端点，使得语言服务器能够完全在浏览器内运行，无需后端 Python 进程。

版本：0.1.0-alpha0（早期开发阶段），许可证：BSD-3-Clause。

## 解决的核心问题

传统的 Jupyter LSP 架构（jupyterlab-lsp）需要：

1. 后端运行一个 Python 进程（jupyter-lsp）管理语言服务器子进程
2. 前端通过 REST API 获取服务器状态，通过 WebSocket 与语言服务器通信
3. 语言服务器本身作为独立进程在服务端运行

JupyterLite 完全运行在浏览器中，没有传统意义上的后端服务器进程。jupyterlite-lsp 通过以下方式解决这个矛盾：

- 在浏览器内创建虚拟 WebSocket 服务端拦截前端连接
- 将语言服务器打包为 Web Worker 在浏览器线程中运行
- 通过 Service Worker 拦截 REST 请求
- 在构建时对 jupyterlab-lsp 前端代码做 Monkey-patch，替换原生 WebSocket 为虚拟 WebSocket

## 核心特性

- **模拟 jupyter-lsp 端点**：提供 `/lsp/status` REST 端点和 `/lsp/ws/<id>` WebSocket 端点
- **内置语言服务器**：当前支持 YAML（同时支持 JSON），通过 Red Hat 的 yaml-language-server 实现
- **可扩展架构**：通过 `ILanguageServers.addLanguageServer()` API 添加新的浏览器端语言服务器
- **零后端依赖**：所有 LSP 逻辑在浏览器端完成，Python 包仅用于 Labextension 资源分发

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | JupyterLab 3.x / JupyterLite 0.1.0-beta.15 |
| LSP 前端集成 | @krassowski/jupyterlab-lsp ^3.10.2 |
| 语言服务器 | yaml-language-server ^1.10.0（Web Worker 运行） |
| 虚拟 WebSocket | mock-socket 库 |
| 消息队列 | wait-queue（AsyncGenerator 桥接） |
| 构建工具 | lerna + yarn workspaces + flit + doit |
| 语言 | TypeScript ~4.9.3 + Python >=3.7 |

## 项目结构

```
jupyterlite-lsp/
├── packages/           # JS/TS 包（lerna monorepo）
│   ├── lsp/            # @jupyterlite/lsp 核心包（插件+Session+Mock桥接）
│   ├── lsp-yaml/       # @jupyterlite/lsp-yaml YAML/JSON 语言服务器
│   └── _meta/          # @jupyterlite/lsp-metapackage 元包
├── src/jupyterlite_lsp/ # Python 包（仅做 labextension 注册）
├── examples/           # JupyterLite 示例配置
├── docs/               # Sphinx 文档
├── dodo.py             # doit 构建脚本
├── package.json        # JS 根配置
└── pyproject.toml      # Python 包配置
```

## 相关概念

- [快速开始](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
- [YAML/JSON 语言服务器](06-yaml-server.md)
