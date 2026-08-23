---
type: Concept
title: CI/CD 与 GitHub Pages 部署
description: GitHub Actions 双站点并行构建、artifact 上传、gh-pages 部署的完整工作流
tags: [github-actions, deployment, github-pages, ci-cd, gh-pages]
difficulty: advanced
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ci-workflow
    resource: /references/ci-workflow-source.md
    title: .github/workflows/pages.yml 源码
---

## 部署架构概述

sphinx-demo 的 CI/CD 采用"并行构建→聚合部署"的模式：

```
                    ┌─────────────────────┐
                    │  Push to main / PR   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  build-sites (Job 1) │
                    │  strategy.matrix     │
                    ├───┬─────────────┬────┤
                    │   │             │    │
              ┌─────▼─┐ ┌─────▼─────┐     │
              │Pyodide│ │  Xeus     │     │
              │ build │ │  build    │     │
              └───┬───┘ └─────┬─────┘     │
                  │            │           │
                  └─────┬──────┘           │
                        │                   │
              ┌─────────▼─────────┐        │
              │  Upload artifacts │        │
              └─────────┬─────────┘        │
                        │                  │
              ┌─────────▼─────────┐        │
              │  deploy (Job 2)   │ ← 仅main分支
              │  Download all     │
              │  + index.html     │
              │  + switcher.json  │
              │  → gh-pages       │
              └───────────────────┘
```

## 触发条件

工作流在以下场景触发：

| 事件 | 条件 | 是否部署 |
|------|------|---------|
| `push` | main 分支 | ✅ 构建+部署 |
| `pull_request` | 任何 PR | ❌ 仅构建（不部署） |
| `workflow_dispatch` | 手动触发 | ✅ 构建+部署 |
| `schedule` | 每日 UTC 00:00 | ❌ 仅构建（验证依赖兼容性） |

每日定时构建的目的是及时发现依赖更新导致的构建问题，而非部署。

## 矩阵并行构建

```yaml
strategy:
  fail-fast: false
  matrix:
    site:
      - [pyodide-kernel-example, pyodide]
      - [xeus-kernel-example, xeus]
```

`fail-fast: false` 确保即使一个站点构建失败，另一个站点的构建仍然继续完成，便于一次性发现所有问题。

### 每个构建步骤详解

1. **Checkout**：拉取代码（`persistCredentials: false`，构建不需要写权限）
2. **Setup uv**：安装 Python 3.12 和 uv 包管理器
3. **Install micromamba**（仅 Xeus）：安装 micromamba 用于求解 WASM 包依赖
4. **Install dependencies**：`uv pip install -r requirements.txt`（在站点目录下执行）
5. **Build Sphinx site**：`make html`（在 `docs/` 目录下执行）
6. **Upload artifact**：上传构建产物，保留7天

### SPHINXOPTS 构建选项

工作流中设置了严格的构建选项：

```bash
SPHINXOPTS="-W --keep-going -j auto -D jupyterlite_silence=0"
```

| 选项 | 作用 |
|------|------|
| `-W` | 将警告视为错误（保证文档质量） |
| `--keep-going` | 遇到错误继续构建（尽量多地发现问题） |
| `-j auto` | 并行构建（利用所有 CPU 核心） |
| `-D jupyterlite_silence=0` | 显示 JupyterLite 详细构建日志（CI 排错需要） |

## 部署步骤

部署 Job 仅在 main 分支推送或手动触发时运行。

### 权限配置

```yaml
permissions:
  contents: write
  pages: write
  deployments: write
```

这三个权限分别用于：
- `contents: write`：推送到 gh-pages 分支
- `pages: write`：配置 GitHub Pages
- `deployments: write`：创建部署状态

### 部署流程

1. **Checkout**：拉取代码（需要根目录的 index.html 和 switcher.json）
2. **Download artifacts**：下载所有构建站点的 artifact 到 `dist/` 目录
3. **Move base files**：将根目录的 index.html 和 switcher.json 移动到 dist/
4. **Sanity check**：运行 `tree dist` 验证目录结构
5. **Deploy**：使用 `peaceiris/actions-gh-pages` 部署到 gh-pages 分支

### gh-pages 配置

```yaml
- uses: peaceiris/actions-gh-pages@v4
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_branch: gh-pages
    force_orphan: true
    publish_dir: ./dist
```

关键选项：
- `force_orphan: true`：每次部署创建全新的孤立提交，不保留历史（保持 gh-pages 分支干净）
- `publish_dir: ./dist`：部署目录包含 pyodide/、xeus/、index.html、switcher.json

## 部署后站点结构

```
https://YOUR_USERNAME.github.io/YOUR_REPO/
├── index.html              # 内核选择落地页
├── switcher.json           # 版本切换器配置
├── pyodide/                # Pyodide 站点
│   ├── index.html
│   ├── lite/               # JupyterLite 构建产物
│   ├── jupyterlite/demo.html
│   └── ...
└── xeus/                  # Xeus 站点
    ├── index.html
    ├── lite/
    └── ...
```

### 版本切换器工作原理

PyData 主题的版本切换器不是单页应用路由——它通过跳转到不同 URL 路径实现版本切换：
- 选择 "Pyodide kernel" → 跳转到 `/pyodide/`
- 选择 "Xeus kernel" → 跳转到 `/xeus/`

每个路径下是一个完全独立的 Sphinx 静态站点。

## 本地验证部署

在本地模拟部署构建：

```bash
# 构建 Pyodide 站点
cd pyodide-kernel-example/docs
make html

# 构建 Xeus 站点（需要安装 micromamba）
cd ../../xeus-kernel-example/docs
make html

# 组装部署目录
mkdir -p dist/pyodide dist/xeus
cp -r ../../pyodide-kernel-example/docs/build/html/* dist/pyodide/
cp -r ../../xeus-kernel-example/docs/build/html/* dist/xeus/
cp ../../index.html dist/
cp ../../switcher.json dist/

# 本地预览
cd dist && python -m http.server 8000
```

## 常见部署问题

### 构建时间过长

首次构建需要下载 Pyodide（~20MB）和 JupyterLite 资源。CI 中可通过缓存 pip 依赖加速：

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ matrix.site[0] }}-${{ hashFiles('*/requirements.txt') }}
```

### Xeus 构建失败

Xeus 需要 micromamba 来解析 WASM 包依赖。确保 CI 中使用 `mamba-org/setup-micromamba@v2` 且在 Xeus 构建步骤前安装。

### 页面 404

GitHub Pages 需要在仓库 Settings → Pages 中将 Source 设置为 `gh-pages` 分支。首次部署后需要等待 1-2 分钟生效。

### 版本切换器不工作

确保 `switcher.json` 在部署根目录（与 index.html 同级），且 `json_url` 路径配置正确。注意 Sphinx 构建时 switcher.json 的路径和部署时的路径可能不同——demo 中 conf.py 使用相对路径，CI 部署时将 switcher.json 放到 dist/ 根目录。

## 完整工作流源码

完整的 GitHub Actions YAML 见 [/references/ci-workflow-source.md](/references/ci-workflow-source.md)。

## 相关内容

- [01-project-structure](/concepts/01-project-structure.md)
- [04-kernel-comparison](/concepts/04-kernel-comparison.md)
- [08-customization](/concepts/08-customization.md)
- [/references/ci-workflow-source.md](/references/ci-workflow-source.md)
