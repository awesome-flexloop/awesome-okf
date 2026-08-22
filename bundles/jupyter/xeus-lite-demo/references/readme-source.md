---
type: Reference
title: README 使用说明信源
description: xeus-lite-demo README.md 的完整内容登记，包含三步部署流程、内核安装示例、插件安装说明
tags: [readme, deployment-guide, xeus-lite, jupyterlite, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: https://github.com/jupyterlite/xeus-lite-demo/blob/main/README.md
    title: xeus-lite-demo README.md
---

## 源文件路径

`README.md`（仓库根目录）

## 原文要点

### 项目描述

> This GitHub template allows you to create deployments of JupyterLite with a custom set of conda packages.

### 三步部署流程

1. **Apply the GitHub template**：点击 "Use this template" 按钮，选择组织和项目名，创建仓库
2. **Enable GitHub Pages from Actions**：在仓库设置中启用 GitHub Pages（Source 选择 GitHub Actions）
3. **Customize conda environment**：编辑 `environment.yml` 添加所需包

### 部署 URL 格式

`https://{USERNAME}.github.io/{DEMO_REPO_NAME}`

### 内核/包安装方式

通过编辑 `environment.yml` 添加，文档链接：https://jupyterlite-xeus.readthedocs.io/en/latest/environment.html

### 示例配置

**示例1：Python + NumPy + Matplotlib**

```yml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - matplotlib
```

**示例2：R + coursekata**

```yml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-r
  - r-coursekata
```

**示例3：C++ 内核**

```yml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-cpp
```

### 插件安装方式

JupyterLite 插件（如 `jupyterlite-terminal`）添加到 `.github/build-environment.yml` 文件。

### 演示动画

包含 `deploy.gif` 演示操作步骤。
