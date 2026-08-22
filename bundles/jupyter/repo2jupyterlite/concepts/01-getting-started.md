---
type: Concept
title: 快速开始
description: 安装 repo2jupyterlite 和 BinderLite 的环境准备、基础验证和第一个构建示例
tags: [getting-started, installation, setup, environment]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: metasource
    resource: /references/metasource.md
    title: 项目元数据信源
  - id: cli-source
    resource: /references/cli-source.md
    title: CLI入口信源
---

本文档介绍如何安装 repo2jupyterlite CLI 工具和 BinderLite Web 应用，并运行第一个构建。

## 安装 CLI 工具

repo2jupyterlite CLI 可通过 pip 安装：

```bash
pip install repo2jupyterlite
```

安装完成后，`repo2jupyterlite` 命令可用（F-004）。

### CLI 核心依赖

安装时自动拉取以下依赖（F-003）：

- `jupyterlite-core[all]`：JupyterLite 核心（含所有可选依赖）
- `jupyterlite-xeus-python`：Xeus Python WASM 内核
- `jupyter-repo2docker`：仓库内容提供者框架
- `yarl`：URL 处理库

Python 版本要求 &gt;= 3.10（F-002）。

### 注意事项

`setup.py` 在安装时会自动执行 `npm i` 和 `npm run build`（F-005），这意味着：

- 安装环境需要 **Node.js** 和 **npm** 可用
- 安装过程会编译前端资源（webpack构建React应用到 binderlite 包目录）
- 如果仅使用 CLI 而不运行 BinderLite Web 应用，前端构建产物虽然生成但不会被使用

## 安装 BinderLite Web 环境

运行 BinderLite Web 应用需要额外的 Conda 环境。使用项目提供的 `environment.yml`：

```bash
# 创建 conda 环境
mamba env create -n binderlite -f environment.yml
# 激活环境
conda activate binderlite
# 从源码安装 repo2jupyterlite（开发模式）
pip install -e .
```

### BinderLite 环境依赖（F-008）

| 包名 | 用途 |
|------|------|
| `mamba` | 快速包管理器 |
| `fastapi` | Web 框架 |
| `uvicorn` | ASGI 服务器 |
| `nodejs` | 前端构建运行时 |
| `pip` | Python 包管理器 |

此外，`run.py` 还导入了以下包（需要通过 pip 安装）：
- `escapism`：字符串安全编码
- `tornado`：异步HTTP客户端（GitHub API请求）
- `traitlets`：配置系统
- `jinja2`：模板引擎
- `python-multipart`：FastAPI 表单处理

### 启动 BinderLite

```bash
uvicorn binderlite.run:app
```

默认监听 `http://127.0.0.1:8000`。

## 验证安装

### CLI 验证

安装后可以通过以下命令验证 CLI 可用：

```bash
repo2jupyterlite --help
```

该命令使用 argparse，接受 `url`、`output_dir` 两个位置参数和 `--ref` 可选参数（F-024）。

### 第一个构建：本地目录

如果当前目录有一个包含 notebook 的项目，可以直接构建：

```bash
repo2jupyterlite ./my-notebooks ./output
```

其中：
- `./my-notebooks` 是包含 notebook 的本地目录（可以包含 `environment.yml` 和 `jupyterlite_config.json`）
- `./output` 是构建输出目录（必须不存在，否则报错退出 F-025）

### 第一个构建：GitHub 仓库

```bash
repo2jupyterlite https://github.com/yuvipanda/environment.yml requirements-build
```

构建完成后，`requirements-build/` 目录包含可静态服务的 JupyterLite 站点：

```bash
# 使用任意静态HTTP服务器预览
cd requirements-build
python -m http.server 8000
# 访问 http://localhost:8000
```

CLI 完成时会打印提示 `Go to http://localhost:8000/{output_dir}`（F-028）。

## 构建输出结构

`jupyter lite build` 生成的静态站点典型结构：

```
output/
├── lab/                    # JupyterLab 界面
│   └── index.html
├── repl/                   # REPL 界面（可选）
├── retro/                  # RetroLab 界面（可选）
├── pyodide/                # Pyodide 内核资源（如果使用xeus-python则是xeus/）
├── kernels/                # 内核规格
├── content/                # 从仓库复制的 notebook 和文件
├── jupyter-lite.ipynb      # 默认空 notebook
├── jupyter-lite.json       # JupyterLite 配置
├── index.html              # 入口页面
└── service-worker.js       # Service Worker（离线支持）
```

如果仓库根目录存在 `jupyterlite_config.json`，会自动作为 `--config` 参数传给 jupyter lite build（F-021）。

## 前端构建说明

BinderLite 的前端是一个 React 18 应用，通过 Webpack 打包。构建命令：

```bash
npm install
npm run build    # 生产构建
npm run watch    # 开发模式（监听文件变更）
```

Webpack 配置将：
- JS/JSX 通过 Babel（preset-env + preset-react automatic）转译
- CSS 通过 style-loader + css-loader 处理
- HTML 模板输出到 `binderlite/templates/index.html`
- JS 输出到 `binderlite/static/index.js`（F-107~F-113）

## 相关概念

- [00-repo2jupyterlite简介](00-introduction.md)
- [02-CLI命令使用](02-cli-usage.md)
- [03-BinderLite Web应用](03-binderlite-web.md)
- [08-整体架构总结](08-architecture-summary.md)
