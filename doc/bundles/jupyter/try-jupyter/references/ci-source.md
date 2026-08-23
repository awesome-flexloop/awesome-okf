---
type: Reference
title: "CI/CD与部署工作流源码"
description: "GitHub Actions工作流（deploy.yml、rtd-preview.yml）和ReadTheDocs配置的完整解析：build→test→deploy三阶段流水线、RTD PR预览"
tags: [github-actions, ci-cd, deploy, github-pages, readthedocs, pixi, build-pipeline]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: deploy-yml
    resource: "../../../../../external/libs/jupyter/try-jupyter/.github/workflows/deploy.yml"
    title: "try-jupyter/.github/workflows/deploy.yml"
  - id: rtd-preview-yml
    resource: "../../../../../external/libs/jupyter/try-jupyter/.github/workflows/rtd-preview.yml"
    title: "try-jupyter/.github/workflows/rtd-preview.yml"
  - id: readthedocs-yml
    resource: "../../../../../external/libs/jupyter/try-jupyter/.readthedocs.yml"
    title: "try-jupyter/.readthedocs.yml"
---

# CI/CD与部署工作流源码

本信源登记CI/CD配置文件的完整结构：GitHub Actions部署工作流、RTD PR预览工作流、ReadTheDocs构建配置。

## 1. .github/workflows/deploy.yml — 主部署工作流

### 触发条件

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: ['*']
```

- `push` 到 main 分支：触发完整 build→test→deploy 流水线
- 任意分支的 `pull_request`：触发 build→test（不部署）

### 权限配置

```yaml
permissions:
  actions: write
  contents: write
  deployments: write
  pages: write
```

### Job 1：build（构建）

运行环境：`ubuntu-latest`

| 步骤 | 动作 | 说明 |
|------|------|------|
| Checkout | `actions/checkout@v4` | 检出代码 |
| Setup pixi | `prefix-dev/setup-pixi@v0.9.3`（pixi-version: v0.71.0, cache: true） | 安装pixi包管理器 |
| Build site | `cp README.md content` → `pixi run build` | 复制README到content目录，执行JupyterLite构建 |
| Filter kernels | `pixi run filter-kernels` | 过滤xeus内核（保留5个） |
| Add analytics | `pixi run add-plausible` | 注入Plausible分析代码 |
| Upload test artifact | `actions/upload-artifact@v4` | 上传dist到 `jupyterlite-dist` artifact |
| Upload pages artifact | `actions/upload-pages-artifact@v4` | 上传dist到GitHub Pages部署artifact |

> **注意**：build步骤中 `cp README.md content` 将README复制到content目录，使得README也作为站点内容可访问。

### Job 2：test（测试）

依赖：`needs: build`
运行环境：`ubuntu-latest`
超时：`timeout-minutes: 30`

| 步骤 | 动作 | 说明 |
|------|------|------|
| Checkout | `actions/checkout@v4` | 检出代码 |
| Setup pixi | `prefix-dev/setup-pixi@v0.9.3` | 安装pixi |
| Download site | `actions/download-artifact@v4` | 从build job下载dist |
| Install browsers | `pixi run playwright install --with-deps chromium` | 安装Playwright Chromium |
| Run tests | `pixi run test` | 执行pytest UI测试 |
| Upload screenshots（失败时） | `actions/upload-artifact@v4`（if: failure()） | 失败时上传截图和视频 |
| Upload results（总是） | `actions/upload-artifact@v4`（if: always()） | 总是上传HTML报告和测试结果 |

失败时上传内容：
- `ui-tests/screenshot_*.png`：失败截图
- `ui-tests/videos`：录屏

总是上传内容：
- `ui-tests/report.html`：HTML测试报告
- `ui-tests/test-results`：测试结果目录

### Job 3：deploy（部署）

依赖：`needs: test`
条件：`if: github.ref == 'refs/heads/main'`（仅main分支）
权限：`pages: write, id-token: write`
环境：`name: github-pages`

| 步骤 | 动作 | 说明 |
|------|------|------|
| Deploy | `actions/deploy-pages@v4`（id: deployment） | 部署到GitHub Pages |

部署URL通过 `${{ steps.deployment.outputs.page_url }}` 获取。

### 工作流依赖关系

```
build (所有分支/PR)
  ↓ (artifact: jupyterlite-dist)
test (依赖build)
  ↓ (仅main分支)
deploy (依赖test) → GitHub Pages
```

## 2. .github/workflows/rtd-preview.yml — RTD PR预览

触发条件：
```yaml
on:
  pull_request_target:
    types: [opened]
```

仅在PR**打开时**触发一次（不触发synchronize等事件）。
权限：`pull-requests: write`

### Job：binder

运行环境：`ubuntu-latest`

单一步骤：使用 `actions/github-script@v6` 在PR上发表评论，评论内容包含RTD预览徽章和链接：

```
[![lite-badge](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)]
(https://try-jupyter--{PR_NUMBER}.org.readthedocs.build/en/{PR_NUMBER})
:point_left: Try it on ReadTheDocs
```

预览URL格式：`https://try-jupyter--{PR_NUMBER}.org.readthedocs.build/en/{PR_NUMBER}`

## 3. .readthedocs.yml — ReadTheDocs构建配置

```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: mambaforge-latest
  commands:
    - mamba install -c conda-forge -c nodefaults pixi
    - pixi install
    - pixi run build
    - pixi run filter-kernels
    - pixi run readthedocs
```

### 构建环境

- OS：Ubuntu 22.04
- Python工具：`mambaforge-latest`（确保mamba在$PATH上）

### 构建命令（5步）

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1 | `mamba install -c conda-forge -c nodefaults pixi` | 安装pixi（使用conda-forge，禁用默认channel） |
| 2 | `pixi install` | 安装所有pixi依赖 |
| 3 | `pixi run build` | 构建JupyterLite站点 |
| 4 | `pixi run filter-kernels` | 过滤xeus内核 |
| 5 | `pixi run readthedocs` | 复制dist到RTD输出目录（$READTHEDOCS_OUTPUT/html） |

> **注意**：RTD构建不执行 `add-plausible` 步骤（RTD预览不需要分析追踪），也不执行测试步骤。

## 部署目标对比

| 部署目标 | 触发条件 | 构建步骤差异 | URL |
|---------|---------|------------|-----|
| GitHub Pages | main分支push | build + filter-kernels + add-plausible + test | `steps.deployment.outputs.page_url` → jupyter.org/try-jupyter |
| ReadTheDocs（PR预览） | PR opened | build + filter-kernels（无add-plausible，无test） | `try-jupyter--{PR}.org.readthedocs.build` |

## 相关信源

- [pyproject.toml 信源](pyproject-source.md)（pixi任务定义）
- [构建脚本信源](scripts-source.md)（后处理脚本逻辑）
