---
type: Concept
title: 快速开始
description: jupyterlite-lsp 的安装方式、开发环境搭建与基本使用
tags: [getting-started, installation, development]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: contributing
    resource: /references/build-source.md
    title: 构建系统源码引用
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
---

## 前置条件

- Node.js >=18,<19
- Python >=3.8,<3.12（开发环境）；运行时要求 Python >=3.7
- [Mambaforge](https://github.com/conda-forge/miniforge/releases)（推荐用于环境管理）

## pip 安装

pip 安装方式在 README 中标记为 TODO（项目处于 alpha 阶段），但可以通过源码安装：

```bash
pip install jupyterlite-lsp
```

## 开发环境搭建

### 1. 创建 conda 环境

```bash
mamba env update --file .binder/environment.yml --prefix .venv
source activate ./.venv
```

.binder/environment.yml 安装的依赖包括：
- nodejs >=18,<19
- jupyterlab >=3.5,<4.0
- jupyterlab-lsp >=3.10.2
- doit-with-toml、flit（构建）
- black、isort、ssort（格式化）
- jupyterlite ==0.1.0b15（通过 pip 安装）

### 2. 安装 JS 依赖

```bash
jlpm setup:js
```

此命令执行 `jlpm --prefer-offline --ignore-optional` 安装依赖，并运行 yarn-deduplicate。

### 3. 安装 Python 包（开发模式）

```bash
jlpm setup:py:pip
jlpm setup:py:ext
```

- `setup:py:pip`：`pip install -e . --no-deps` 可编辑安装
- `setup:py:ext`：`jupyter labextension develop . --overwrite` 链接 labextension

### 4. 一键就绪

使用 doit 任务自动化：

```bash
doit binder
```

此命令执行所有 setup 步骤后输出就绪提示。

### 5. 启动开发服务器

```bash
jupyter lab --no-browser --debug
```

在另一个终端启动 TypeScript 监听编译：

```bash
jlpm watch
```

## 构建 JupyterLite 示例站点

```bash
jlpm lite:build
```

这会在 examples/ 目录执行 `jupyter lite build`，输出到 build/lite/。构建完成后，doit 任务会自动执行 WebSocket patch 步骤，将 jupyterlab-lsp 中的 `new WebSocket` 替换为 `new window.MockWebSocket`。

## 构建发布产物

```bash
doit          # 运行所有任务
doit dist     # 构建 npm 和 Python 包
```

产物输出到 dist/ 目录，包含 SHA256SUMS 校验文件。

## 使用方式

安装后，JupyterLite 站点将自动启用 LSP 功能。当前版本内置 YAML/JSON 语言服务器，在编辑 `.yaml`、`.yml`、`.json` 文件时提供：

- 语法验证
- 自动补全
- 悬停提示
- 跳转到定义

## 调试模式

在 URL 中添加 `LSP_LITE_DEBUG` 参数可启用调试日志：

```
http://localhost:8000/?LSP_LITE_DEBUG
```

此时浏览器控制台会输出 LSP 通信的详细日志（WebSocket 连接、消息收发等）。

## 相关概念

- [项目介绍](/concepts/00-introduction.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [构建系统详解](/concepts/07-build-system.md)
- [本地开发环境搭建](/examples/local-dev-setup.md)
