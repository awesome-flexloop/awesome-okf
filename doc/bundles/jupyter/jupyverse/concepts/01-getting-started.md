---
type: Concept
title: "快速上手"
description: "安装 Jupyverse、启动服务器、配置插件和基本使用方法，包含 PyPI、conda-forge 和开发安装三种方式。"
tags: [getting-started, install, setup, run, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 信源
  - id: cli
    resource: /references/cli-source.md
    title: CLI 入口信源
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 信源
---

# 快速上手

## 安装

### 从 PyPI 安装

安装带 JupyterLab 前端和认证功能的基础版本：

```bash
pip install "jupyverse[jupyterlab,auth]"
```

也可以按需选择功能组合：

```bash
# 仅 JupyterLab + 无认证（本地开发用）
pip install "jupyverse[jupyterlab,noauth]"

# JupyterLab + 协作功能
pip install "jupyverse[jupyterlab,auth,collaboration]"

# Notebook 7 前端
pip install "jupyverse[notebook,auth]"
```

### 从 conda-forge 安装

使用 `micromamba`（推荐）或 `conda`：

```bash
micromamba create -n jupyverse
micromamba activate jupyverse
micromamba install jupyverse fps-jupyterlab fps-auth
```

### 开发安装

克隆仓库后使用 uv 安装所有包（可编辑模式）：

```bash
git clone https://github.com/jupyter-server/jupyverse.git
cd jupyverse

# 创建虚拟环境
uv venv

# 安装所有 API 包
for dir in ./api/*; do dirname=$(basename "$dir"); uv pip install -e "jupyverse-$dirname @ ./api/$dirname"; done

# 安装所有插件包
for dir in ./plugins/*; do dirname=$(basename "$dir"); uv pip install -e "fps-$dirname @ ./plugins/$dirname"; done

# 安装主包和测试依赖
uv pip install --group test -e .
```

## 启动服务器

### 基本启动

安装完成后，使用 `jupyverse` 命令启动：

```bash
jupyverse
```

默认监听 `127.0.0.1:8000`，打开浏览器访问 http://127.0.0.1:8000/lab 即可使用 JupyterLab。

### 指定认证后端

安装了多个认证插件时，必须禁用互斥的插件：

```bash
jupyverse \
    --disable auth_fief \
    --disable auth_jupyterhub \
    --disable noauth
```

以上命令只启用 `fps-auth`（Token 模式）。使用无认证模式：

```bash
jupyverse --disable auth --disable auth_fief --disable auth_jupyterhub
```

### 常用 CLI 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--host` | 127.0.0.1 | 监听地址 |
| `--port` | 8000 | 监听端口 |
| `--open-browser` | False | 启动后自动打开浏览器 |
| `--backend` | asyncio | 事件循环（asyncio/trio） |
| `--debug` | False | 启用调试日志 |
| `--allow-origin` | - | 添加 CORS 允许源（可多次指定） |
| `--set` | - | 设置配置项（key=value，可多次指定） |
| `--disable` | - | 禁用插件（可多次指定） |
| `--show-config` | False | 显示实际配置后退出 |
| `--help-all` | False | 显示所有配置项说明 |

### 启用协作功能

安装 collaboration extra 后启动时设置 `frontend.collaborative=true`：

```bash
# 协作 + 无认证（本地/测试）
pip install "jupyverse[jupyterlab,noauth,collaboration]"
jupyverse --set "frontend.collaborative=true"

# 协作 + Token 认证
pip install "jupyverse[jupyterlab,auth,collaboration]"
jupyverse --disable auth_fief --disable auth_jupyterhub --disable noauth \
  --set "frontend.collaborative=true"
```

## 运行测试

开发安装后运行测试：

```bash
# uv 方式
uv run pytest -v

# pip 方式
pytest -v
```

## 在线试用

可以通过 Binder 直接在线体验：
- JupyterLab 前端：[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jupyter-server/jupyverse/HEAD?urlpath=jupyverse-jupyterlab)
- Notebook 前端：[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jupyter-server/jupyverse/HEAD?urlpath=jupyverse-notebook)

## 相关概念

- [Jupyverse 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md) — 理解插件架构
- [CLI 与配置系统](11-cli-and-configuration.md) — 详细的配置选项说明
