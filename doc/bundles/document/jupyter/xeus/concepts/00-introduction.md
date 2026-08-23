---
type: Concept
title: jupyterlite-xeus 是什么
description: jupyterlite-xeus是JupyterLite的xeus内核集成，将C++实现的Jupyter内核协议（xeus）编译为WebAssembly，实现浏览器端多语言交互式计算
tags: [overview, xeus, jupyterlite, wasm, kernel]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /concepts/00-introduction.md
    title: README.md
  - id: meta
    resource: /references/metasource.md
    title: 项目元数据
---

## 一句话定义

jupyterlite-xeus 是一个 JupyterLite 扩展，它将基于 [xeus](https://github.com/jupyter-xeus/xeus) 的 Jupyter 内核（C++ 实现的 Jupyter 协议）编译为 WebAssembly，通过 emscripten-forge 打包，在浏览器内运行支持多语言的交互式计算环境——无需后端服务器，零网络依赖即可运行。

## 核心定位

| 维度 | jupyterlite-xeus |
|------|------------------|
| **运行位置** | 浏览器端（客户端） |
| **后端依赖** | 无——静态文件部署即可 |
| **内核实现** | C++ (xeus) → WebAssembly (Emscripten) |
| **包分发** | emscripten-forge conda 包（prefix.dev） |
| **通信模型** | Web Worker + SharedArrayBuffer/postMessage |
| **Jupyter版本** | JupyterLab >= 4.0, JupyterLite 0.7~0.8 |

## 支持的内核语言

xeus 是一个可扩展的内核框架，多个语言内核均基于 xeus 实现并编译为 WASM：

| 内核 | 语言 | 包名 |
|------|------|------|
| xeus-python | Python | `xeus-python` |
| xeus-lua | Lua | `xeus-lua` |
| xeus-r | R | `xeus-r` |
| xeus-cpp | C++ | `xeus-cpp` |
| xeus-nelson | Nelson（数值计算） | `xeus-nelson` |
| xeus-javascript | JavaScript | `xeus-javascript` |

> xeus-python 是最常用的内核，默认通过 environment.yml 安装。

## 与 JupyterLite 其他内核的对比

| 特性 | xeus内核 | Pyodide内核 |
|------|----------|-------------|
| Python实现 | CPython（WASM编译） | Pyodide（CPython补丁版） |
| 包管理 | conda（emscripten-forge）+ pip（纯Python） | micropip（PyPI纯Python wheel） |
| 二进制包 | ✅ 支持C扩展（预编译为wasm） | ❌ 仅纯Python或Pyodide特定wheel |
| 通信机制 | xeus C++协议层 | Pyodide JS/Python桥接 |
| 性能 | 原生CPython（接近原生速度） | 带补丁的CPython |
| 生态 | emscripten-forge conda频道 | Pyodide生态 |

## 核心能力

1. **完全浏览器内运行**：所有计算、文件存储、包安装都在浏览器内完成
2. **多语言支持**：通过不同xeus内核支持Python/Lua/R/C++等
3. **动态包管理**：运行时 `%conda install` / `%pip install` 安装新包
4. **跨域隔离自适应**：自动检测 `crossOriginIsolated` 选择最优通信模式
5. **静态部署**：构建产出物为纯静态文件，可部署到任意静态文件服务器

## 项目结构概览

```
jupyterlite-xeus/
├── packages/                    # TypeScript/JavaScript 运行时
│   ├── xeus-core/              # 抽象基类层
│   ├── xeus/                   # empack具体实现
│   └── xeus-extension/         # JupyterLab扩展入口
├── jupyterlite_xeus/           # Python 构建端
│   ├── add_on.py               # XeusAddon构建插件
│   ├── create_conda_env.py     # micromamba环境创建
│   └── _pip.py                 # pip依赖处理
└── environment.yml             # 默认conda环境配置
```

## 学习路径

1. **安装体验**：→ [快速开始](01-getting-started.md)
2. **理解架构**：→ [双语言分层架构](02-architecture.md)
3. **深入机制**：→ [双Worker通信模式](03-dual-worker-modes.md) → [内核生命周期](04-kernel-lifecycle.md)
4. **构建部署**：→ [构建系统详解](05-build-system.md)
5. **扩展定制**：→ [自定义内核集成](09-custom-kernel.md)

## 信源溯源

- 项目描述来自 [README.md](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/README.md)
- 包版本和依赖来自 [package.json](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/package.json) 和 [pyproject.toml](file:///d:/spaces/SpecWeave/external/libs/jupyter/xeus/pyproject.toml)
- 支持内核列表来自 README 特性列表
