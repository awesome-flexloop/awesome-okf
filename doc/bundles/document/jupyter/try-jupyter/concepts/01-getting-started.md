---
type: Concept
title: "快速开始：本地构建与预览"
description: "从零开始在本地构建Try Jupyter站点：安装pixi、安装依赖、构建站点、本地预览，以及编辑notebook的推荐方式。"
tags: [getting-started, pixi, build, preview, local-development, setup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml 项目配置"
  - id: readme
    resource: "../../../../../external/libs/jupyter/try-jupyter/README.md"
    title: "README.md"
  - id: ci-source
    resource: "/references/ci-source.md"
    title: "CI/CD工作流"
---

# 快速开始：本地构建与预览

本指南介绍如何在本地构建和预览 Try Jupyter 站点。

## 前置条件

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| Pixi | 最新版 | conda-forge生态的包管理和任务运行工具 |
| 操作系统 | Linux / macOS / Windows | Pixi跨平台支持（linux-64, osx-64, win-64, osx-arm64） |

> **Pixi** 是项目唯一的环境管理和任务运行工具，不需要单独安装Python、Node.js等——pixi会自动管理所有依赖。

### 安装 Pixi

```bash
# Linux/macOS
curl -fsSL https://pixi.sh/install.sh | bash

# Windows (PowerShell)
iwr -useb https://pixi.sh/install.ps1 | iex
```

安装后重启终端，确认 `pixi --version` 可用。

## 克隆项目

```bash
git clone https://github.com/jupyter/try-jupyter.git
cd try-jupyter
```

## 安装依赖

```bash
pixi install
```

此命令会：
1. 创建独立的conda环境（.pixi目录）
2. 安装所有构建和测试依赖（Python≥3.12、Node.js≥22、JupyterLab、JupyterLite、Playwright等30+包）
3. 锁定依赖版本（pixi.lock）

首次运行需要下载约1-2GB的包，请耐心等待。

## 构建站点

```bash
pixi run build
```

执行 `jupyter lite build` 命令：
- 读取 `jupyter_lite_config.json` 配置
- 将 `content/` 目录内容打包
- 编译Xeus内核环境（4个environment-*.yml）
- 生成完整的静态站点到 `dist/` 目录

构建完成后，执行后处理步骤：

```bash
# 过滤xeus内核（只保留5个精选内核）
pixi run filter-kernels

# （可选）注入Plausible分析代码（本地预览通常不需要）
# pixi run add-plausible
```

## 本地预览

构建完成后，用任意HTTP服务器预览dist目录：

```bash
# 方式1：使用Python内置HTTP服务器
cd dist && python -m http.server 8000

# 方式2：使用pixi环境中的Python
pixi run python -m http.server 8000 --directory dist
```

然后在浏览器中打开 http://localhost:8000/lab/index.html

## 运行UI测试（可选）

```bash
# 安装Playwright浏览器（首次需要）
pixi run playwright install --with-deps chromium

# 运行测试
pixi run test
```

测试会自动：
1. 在随机端口启动HTTP服务器
2. 用Playwright打开每个notebook
3. 执行所有cell
4. 检查stderr输出（过滤已知警告）
5. 生成HTML报告到 `ui-tests/report.html`

## 清理构建产物

```bash
pixi run clean
```

删除 `.jupyterlite.doit.db`（doit任务数据库）和 `dist/`（构建产物）。

## 编辑Notebook的推荐方式

项目README明确指出：

> The notebooks in this repository are written with JupyterLite kernels, so if you edit them locally, you will likely over-write the kernel information with your local kernels. As such, the easiest way to make edits is via the Try Jupyter Page.

### 推荐流程（在线编辑）

1. 访问 https://jupyter.org/try-jupyter
2. 在浏览器中打开要编辑的notebook
3. 进行修改
4. 下载修改后的notebook（File → Download）
5. 用下载的文件替换仓库中对应的 `.ipynb` 文件

### 本地编辑注意事项

如果选择本地编辑，注意JupyterLite内核信息会被本地内核覆盖，提交前需要检查kernel metadata是否被修改。

## 完整开发流程速查

```bash
# 1. 安装依赖（首次）
pixi install

# 2. 构建站点
pixi run build && pixi run filter-kernels

# 3. 启动预览服务器
pixi run python -m http.server 8000 --directory dist

# 4. 运行测试（需要另一个终端保持服务器运行，或使用conftest自动启动）
pixi run test

# 5. 清理
pixi run clean
```

## 可用Pixi任务一览

| 任务 | 命令 | 说明 |
|------|------|------|
| `pixi run clean` | `rm -rf .jupyterlite.doit.db dist` | 清理构建产物 |
| `pixi run build` | `jupyter lite build` | 构建JupyterLite站点 |
| `pixi run filter-kernels` | `python scripts/filter_xeus_kernels.py dist` | 过滤xeus内核 |
| `pixi run add-plausible` | `python scripts/add_plausible.py dist` | 注入分析代码 |
| `pixi run test` | `pytest` | 运行UI测试 |
| `pixi run readthedocs` | `cp -r dist $READTHEDOCS_OUTPUT/html` | RTD部署（CI使用） |

## 相关概念

- [架构总览](02-architecture-overview.md)
- [配置系统](03-configuration-system.md)
- [构建管线](05-build-pipeline.md)
- [UI测试框架](07-ui-testing.md)
