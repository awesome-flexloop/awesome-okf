---
type: Concept
title: "部署：GitHub Pages与ReadTheDocs双渠道"
description: "详解Try Jupyter的部署体系：GitHub Actions三阶段流水线（build→test→deploy）、GitHub Pages正式部署、ReadTheDocs PR预览、部署条件与权限配置。"
tags: [deployment, github-pages, readthedocs, github-actions, ci-cd, preview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ci-source
    resource: "/references/ci-source.md"
    title: "CI/CD工作流信源"
  - id: scripts
    resource: "/references/scripts-source.md"
    title: "构建脚本信源"
---

# 部署：GitHub Pages与ReadTheDocs双渠道

Try Jupyter 采用**双渠道部署策略**：GitHub Pages 作为正式生产环境，ReadTheDocs 提供PR预览环境。两套部署共享同一套构建逻辑，但执行步骤略有差异。

## 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    代码推送/PR                           │
│  push to main / pull_request (任意分支)                 │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions (deploy.yml)                │
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌──────────────────────┐ │
│  │  build  │───→│  test   │───→│ deploy (仅main分支)   │ │
│  │ 构建站点 │    │ E2E测试 │    │ GitHub Pages部署      │ │
│  └─────────┘    └─────────┘    └──────────────────────┘ │
│       ↓              ↓                                  │
│  artifact:      失败时上传                                │
│  jupyterlite-   截图+视频                                 │
│  dist          HTML报告（总是）                           │
└──────────────────────┬──────────────────────────────────┘
                       │ main分支
                       ↓
              ┌─────────────────┐
              │  GitHub Pages   │
              │ jupyter.org/    │
              │  try-jupyter    │
              └─────────────────┘

┌─────────────────────────────────────────────────────────┐
│           PR opened → RTD Preview (rtd-preview.yml)     │
│                                                         │
│  PR打开时自动评论，提供RTD预览链接                         │
│  RTD实际构建在.readthedocs.yml配置中执行                   │
└──────────────────────┬──────────────────────────────────┘
                       ↓
              ┌─────────────────────────────┐
              │ ReadTheDocs PR预览           │
              │ try-jupyter--{PR}.org.       │
              │ readthedocs.build            │
              └─────────────────────────────┘
```

## GitHub Actions 主工作流（deploy.yml）

### 触发条件

| 事件 | 分支 | 执行的Jobs |
|------|------|-----------|
| `push` | `main` | build → test → deploy |
| `pull_request` | 任意分支（`*`） | build → test（不部署） |

### 权限配置

```yaml
permissions:
  actions: write
  contents: write
  deployments: write
  pages: write
```

deploy job额外需要：`pages: write` 和 `id-token: write`（用于GitHub Pages OIDC认证）。

### Job 1：build — 构建

运行环境：`ubuntu-latest`

| 步骤 | 操作 | 说明 |
|------|------|------|
| Checkout | `actions/checkout@v4` | 检出代码 |
| Setup pixi | `prefix-dev/setup-pixi@v0.9.3` | 安装pixi v0.71.0，启用缓存 |
| 准备内容 | `cp README.md content` | 将README复制到content目录（使其在站点中可访问） |
| 构建站点 | `pixi run build` | 执行 `jupyter lite build` |
| 过滤内核 | `pixi run filter-kernels` | 精简xeus内核列表为5个 |
| 注入分析 | `pixi run add-plausible` | 添加Plausible分析脚本 |
| 上传测试artifact | `actions/upload-artifact@v4` | 保存为 `jupyterlite-dist`，供test job下载 |
| 上传Pages artifact | `actions/upload-pages-artifact@v4` | 保存为GitHub Pages部署artifact |

> **关键细节**：`cp README.md content` 在构建前执行，将README作为站点内容的一部分。这意味着README中的说明文字在站点中也可以访问。

### Job 2：test — 测试

依赖：`needs: build`
运行环境：`ubuntu-latest`
超时：`timeout-minutes: 30`

| 步骤 | 操作 | 说明 |
|------|------|------|
| Checkout | `actions/checkout@v4` | 检出代码（测试代码在仓库中） |
| Setup pixi | `prefix-dev/setup-pixi@v0.9.3` | 安装pixi |
| 下载构建产物 | `actions/download-artifact@v4` | 从build job下载dist |
| 安装浏览器 | `pixi run playwright install --with-deps chromium` | 安装Playwright和Chromium |
| 运行测试 | `pixi run test` | 执行pytest，包含所有notebook |
| 上传失败证据 | `actions/upload-artifact@v4`（`if: failure()`） | 截图 + 视频 |
| 上传测试报告 | `actions/upload-artifact@v4`（`if: always()`） | HTML报告 + 测试结果 |

**Artifact上传策略**：
- 失败截图和视频仅在失败时上传（节省存储空间）
- HTML测试报告总是上传（无论成功失败，便于审查）
- 使用 `if-no-files-found: ignore` 防止文件不存在时action失败

### Job 3：deploy — 部署

依赖：`needs: test`
条件：`if: github.ref == 'refs/heads/main'`（仅main分支push触发）
环境：`github-pages`（GitHub Pages部署环境）
URL：`${{ steps.deployment.outputs.page_url }}`

| 步骤 | 操作 | 说明 |
|------|------|------|
| Deploy to GitHub Pages | `actions/deploy-pages@v4` | 部署到GitHub Pages |

使用官方 `actions/deploy-pages@v4` 处理部署，不需要自定义脚本。

### 三阶段流水线的防护机制

```
build（所有PR和push）
  ↓ artifact传递
test（必须通过才能部署）
  ↓ 仅main分支
deploy（自动部署到GitHub Pages）
```

- **build→test通过artifact传递**：test job不重新构建，直接使用build产物，确保测试的是即将部署的代码
- **test是部署的门禁**：`needs: test` 确保只有测试通过才能部署
- **main分支保护**：deploy job仅在main分支执行，PR不会触发部署

## ReadTheDocs PR预览

### PR预览工作流（rtd-preview.yml）

触发条件：
```yaml
on:
  pull_request_target:
    types: [opened]
```

仅在PR**首次打开**时触发（不在每次push更新时重复评论）。使用 `pull_request_target` 事件（而非 `pull_request`），因为需要write权限来评论PR。

### 执行逻辑

使用 `actions/github-script@v6` 在PR上自动发表评论：

```javascript
var PR_NUMBER = context.issue.number
github.rest.issues.createComment({
  issue_number: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  body: `[![lite-badge](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)]
(https://try-jupyter--${PR_NUMBER}.org.readthedocs.build/en/${PR_NUMBER}) 
:point_left: Try it on ReadTheDocs`
})
```

评论包含一个徽章和RTD预览链接。

### RTD预览URL格式

```
https://try-jupyter--{PR_NUMBER}.org.readthedocs.build/en/{PR_NUMBER}
```

例如PR #123的预览地址为：`https://try-jupyter--123.org.readthedocs.build/en/123`

### ReadTheDocs构建配置（.readthedocs.yml）

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

RTD构建与GitHub Actions的差异：

| 步骤 | GitHub Actions | ReadTheDocs |
|------|---------------|-------------|
| 包管理器安装 | `prefix-dev/setup-pixi` action | `mamba install pixi` |
| README复制 | `cp README.md content` | ❌ 无 |
| 构建 | `pixi run build` | `pixi run build` |
| 内核过滤 | `pixi run filter-kernels` | `pixi run filter-kernels` |
| 分析注入 | `pixi run add-plausible` | ❌ 无（预览不需要） |
| 测试 | `pixi run test` | ❌ 无（预览不阻塞合并） |
| 部署 | `actions/deploy-pages@v4` | `pixi run readthedocs`（复制到$READTHEDOCS_OUTPUT） |

**关键差异说明**：
1. **不复制README**：RTD预览中README不作为内容（RTD有自己的文档系统）
2. **不注入分析**：PR预览不需要追踪用户行为
3. **不运行测试**：预览环境不阻塞PR合并，测试在GitHub Actions中执行
4. **部署方式不同**：RTD通过 `pixi run readthedocs` 将dist复制到 `$READTHEDOCS_OUTPUT/html`

`pixi run readthedocs` 命令：
```bash
rm -rf $READTHEDOCS_OUTPUT/html && cp -r dist $READTHEDOCS_OUTPUT/html
```

## 环境变量与安全

### deploy job所需权限

```yaml
permissions:
  pages: write      # 创建GitHub Pages部署
  id-token: write   # OIDC token认证（用于GitHub Pages）
```

### RTD构建环境变量

`pixi run readthedocs` 使用 `$READTHEDOCS_OUTPUT` 环境变量，这是ReadTheDocs构建系统自动设置的，指向RTD的输出目录。

## 本地预览 vs 部署

| 环境 | 构建命令 | 访问方式 | 用途 |
|------|---------|---------|------|
| 本地 | `pixi run build && pixi run filter-kernels` | `python -m http.server` → localhost:8000 | 开发调试 |
| PR预览 | RTD自动构建 | RTD预览链接 | PR审查、功能预览 |
| 正式 | GHA build→test→deploy | jupyter.org/try-jupyter | 生产环境 |

## 部署检查清单

每次部署前（main分支push时自动执行）：

- [ ] 所有notebook执行无未预期错误（Playwright测试）
- [ ] Python内核（Pyodide+Xeus）正常工作
- [ ] C++/R/SQLite内核正常工作
- [ ] 可视化库（matplotlib/plotly/bqplot等）正常显示
- [ ] 交互式Widget（ipywidgets/ipyleaflet）正常交互
- [ ] 终端可用
- [ ] GeoJSON/FASTA文件查看器正常
- [ ] 语言切换（中/法/英）正常

## 相关概念

- [构建管线](05-build-pipeline.md)
- [UI测试框架](07-ui-testing.md)
- [快速开始](01-getting-started.md)
