---
type: Reference
title: GitHub Actions 工作流解析
description: pages.yml CI/CD 工作流的完整结构、触发条件、构建矩阵、部署步骤的源码级登记
tags: [github-actions, ci-cd, deployment, github-pages, pages.yml]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pages-yml
    resource: /references/ci-workflow-source.md
    title: .github/workflows/pages.yml
---

## GitHub Actions 工作流解析

本信源文档登记 `.github/workflows/pages.yml` 的完整工作流结构。

## 工作流基本信息

| 属性 | 取值 |
|------|------|
| `name` | `"Build and Deploy"` |
| 运行环境 | `ubuntu-latest` |
| Shell | `bash` |

## 触发条件

| 触发事件 | 配置 | 说明 |
|----------|------|------|
| `push` | branches: `main` | 推送到 main 分支时触发 |
| `pull_request` | 无额外配置 | 所有 PR 触发 |
| `workflow_dispatch` | 无额外配置 | 手动触发 |
| `schedule` | cron: `"0 0 * * *"` | 每日 UTC 00:00 定时构建 |

## 全局环境变量

| 变量 | 取值 | 说明 |
|------|------|------|
| `FORCE_COLOR` | `3` | 强制终端彩色输出 |
| `SPHINXOPTS` | `"-W --keep-going -j auto -D jupyterlite_silence=0"` | Sphinx 构建选项 |

SPHINXOPTS 拆解：
- `-W`：将警告视为错误
- `--keep-going`：遇到错误继续构建（尽量多地发现问题）
- `-j auto`：并行构建（自动检测 CPU 核心数）
- `-D jupyterlite_silence=0`：覆盖 conf.py 中的 silence 设置，显示 JupyterLite 构建日志

## 并发控制

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

同一 PR/分支的多次推送会取消前一次构建，避免队列堆积。

## Job 1: build-sites（并行构建双站点）

### 矩阵策略

```yaml
strategy:
  fail-fast: false
  matrix:
    site: [[pyodide-kernel-example, pyodide], [xeus-kernel-example, xeus]]
```

| site[0]（目录名） | site[1]（artifact名/URL路径） | 内核类型 |
|-------------------|-------------------------------|---------|
| `pyodide-kernel-example` | `pyodide` | Pyodide (WebAssembly CPython) |
| `xeus-kernel-example` | `xeus` | Xeus (emscripten-forge) |

`fail-fast: false` 确保一个站点构建失败不影响另一个。

### 构建步骤

| 步骤 | 条件 | 说明 |
|------|------|------|
| Checkout | 始终 | 使用 actions/checkout@v5，persistCredentials=false |
| Set up uv | 始终 | astral-sh/setup-uv@v6，Python 3.12，自动激活环境 |
| Install micromamba | 仅 Xeus | mamba-org/setup-micromamba@v2，WASM 环境求解需要 |
| Install dependencies | 始终 | `uv pip install -r requirements.txt`（工作目录：{site}） |
| Build Sphinx site | 始终 | `make html`（工作目录：{site}/docs） |
| Upload site artifacts | 始终 | 上传 {site}/docs/build/html，保留7天，无文件时报错 |

### Xeus 构建特殊需求

Xeus 内核需要 micromamba 来求解 emscripten-forge 的 WASM 包依赖（通过 environment.yml），因此在 Install micromamba 步骤有条件判断：
```yaml
if: matrix.site[0] == 'xeus-kernel-example'
```

## Job 2: deploy（部署到 GitHub Pages）

### 运行条件

```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
```

仅在推送到 main 分支或手动触发时部署。

### 权限

| 权限 | 级别 |
|------|------|
| `contents` | `write` |
| `pages` | `write` |
| `deployments` | `write` |

### 部署步骤

| 步骤 | 说明 |
|------|------|
| Checkout | 拉取代码（需要根目录的 index.html 和 switcher.json） |
| Download artifacts | 下载所有 build-sites 的 artifact 到 dist/ 目录 |
| Move base files | `mv index.html dist/index.html` + `mv switcher.json dist/switcher.json` |
| Sanity check | `tree dist` 验证目录结构 |
| Deploy to GitHub Pages | 使用 peaceiris/actions-gh-pages@v4 |

### 部署配置

```yaml
- uses: peaceiris/actions-gh-pages@v4
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_branch: gh-pages
    force_orphan: true
    publish_dir: ./dist
    user_name: "github-actions[bot]"
    user_email: "github-actions[bot]@users.noreply.github.com"
```

关键配置：
- `publish_branch: gh-pages`：部署到 gh-pages 分支
- `force_orphan: true`：每次部署创建全新的孤立提交（不保留历史）
- `publish_dir: ./dist`：包含 pyodide/、xeus/、index.html、switcher.json 的目录

## 部署后站点结构

```
https://jupyterlite.github.io/sphinx-demo/
├── index.html           # 内核选择落地页
├── switcher.json        # 版本切换器配置
├── pyodide/             # Pyodide 内核站点
│   ├── index.html
│   ├── lite/            # JupyterLite 构建产物
│   └── ...
└── xeus/                # Xeus 内核站点
    ├── index.html
    ├── lite/
    └── ...
```

## 相关概念

- [09-ci-deployment](../concepts/09-ci-deployment.md)
- [04-kernel-comparison](../concepts/04-kernel-comparison.md)
