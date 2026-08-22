---
type: Reference
title: "README 信源"
description: "jupyverse 项目 README 文件，包含项目介绍、安装方法和基本使用说明。"
tags: [readme, source, documentation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: readme
    resource: /external/libs/jupyter/jupyverse/README.md
    title: jupyverse README.md
---

# README 信源

本信源记录 jupyverse 项目 README 中的关键信息。

## 项目定位

Jupyverse 是一组基于 [FPS](https://github.com/jupyter-server/fps) 模块实现的 Jupyter 服务器。

## 安装方式

### PyPI 安装

```bash
pip install "jupyverse[jupyterlab,auth]"
```

### conda-forge 安装

```bash
micromamba create -n jupyverse
micromamba activate jupyverse
micromamba install jupyverse fps-jupyterlab fps-auth
```

### 开发安装

使用 uv 安装所有插件（可编辑模式）：

```bash
uv venv
for dir in ./api/*; do dirname=$(basename "$dir"); uv pip install -e "jupyverse-$dirname @ ./api/$dirname"; done
for dir in ./plugins/*; do dirname=$(basename "$dir"); uv pip install -e "fps-$dirname @ ./plugins/$dirname"; done
uv pip install --group test -e .
```

## 运行测试

```bash
uv run pytest -v
```

## 运行服务器

```bash
uv run jupyverse \
    --disable auth_fief \
    --disable auth_jupyterhub \
    --disable noauth \
    --disable file_watcher_poll \
    --disable notebook
```

`--disable` 参数用于禁用互斥的插件（如多个认证插件只能启用一个）。
