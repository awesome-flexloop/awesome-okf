---
type: Reference
title: 构建环境配置信源
description: .github/build-environment.yml 完整内容登记，定义 CI 中执行 jupyter lite build 所需的构建工具环境
tags: [build-environment, conda, jupyterlite, ci, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-env
    resource: https://github.com/jupyterlite/xeus-lite-demo/blob/main/.github/build-environment.yml
    title: xeus-lite-demo .github/build-environment.yml
---

## 源文件路径

`.github/build-environment.yml`

## 完整内容

```yml
name: build-env
channels:
  - conda-forge
dependencies:
  - python
  - pip
  - jupyter_server
  - jupyterlite-core >=0.7
  - jupyterlite-xeus >=4.3
  - notebook >=7.5
```

## 字段解析

| 字段 | 值 | 说明 |
|------|-----|------|
| `name` | `build-env` | 构建环境名称 |
| `channels` | `conda-forge` | 标准 conda-forge 通道（非 WASM，Linux x86_64 架构） |
| `python` | (latest) | Python 解释器，运行 jupyter lite 命令 |
| `pip` | (latest) | pip 包管理器 |
| `jupyter_server` | (latest) | Jupyter Server，jupyterlite 构建依赖 |
| `jupyterlite-core >=0.7` | 0.7+ | JupyterLite 核心构建工具，提供 `jupyter lite` CLI |
| `jupyterlite-xeus >=4.3` | 4.3+ | xeus 集成插件，使 jupyter lite build 能处理 xeus 内核的 WASM 环境 |
| `notebook >=7.5` | 7.5+ | Jupyter Notebook 7+ 前端，提供经典 Notebook 界面 |

## 关键说明

- 此文件定义的是**Linux CI 构建环境**，运行在 GitHub Actions 的 ubuntu-latest 上
- 所有包是常规 Linux x86_64 conda 包，不是 WASM 包
- `jupyterlite-xeus` 是关键插件，它连接 jupyterlite-core 和 xeus 内核，使构建系统能将 environment.yml 中的 WASM 包打包到静态站点中
- 添加 JupyterLite 插件（如 jupyterlite-terminal）应在此文件中追加，而非 environment.yml
