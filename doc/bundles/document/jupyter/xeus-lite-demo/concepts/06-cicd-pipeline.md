---
type: Concept
title: GitHub Actions CI/CD 流水线
description: deploy.yml 工作流详解，build 和 deploy 两个 job 的执行流程、配置选项和自定义方法
tags: [github-actions, cicd, build, deploy, github-pages, automation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: deploy-wf
    resource: /references/deploy-workflow-source.md
    title: CI/CD 流水线信源
---

## 工作流概览

`.github/workflows/deploy.yml` 定义了完整的 CI/CD 流水线，实现代码推送后的自动构建和部署。整个流程由两个 job 组成：

```
push/PR → build job（构建静态站点）→ deploy job（仅main分支，部署到Pages）
```

## 触发条件

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - '*'
```

| 事件 | 分支 | 执行的 Job |
|------|------|-----------|
| push | main | build + deploy |
| push | 其他分支 | 仅 build（如果直接push到非main分支） |
| pull_request | 任意分支 | 仅 build（验证构建是否成功） |

这种设计确保：
- main 分支的更新自动部署到生产站点
- PR 变更只验证不部署，避免未审查代码上线
- PR 中构建失败会阻止合并

## Build Job 详解

build job 负责将源码构建为静态站点产物。

### 运行环境

```yaml
runs-on: ubuntu-latest
```

使用 GitHub 提供的最新 Ubuntu 虚拟机。

### 步骤详解

#### 1. Checkout（检出代码）

```yaml
- name: Checkout
  uses: actions/checkout@v3
```

将仓库代码检出到虚拟机的工作目录。

#### 2. Setup Python（设置 Python）

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
```

安装 Python 3.12。micromamba 也会自带 Python，但这一步确保系统 Python 可用。

#### 3. Install mamba（安装 micromamba）

```yaml
- name: Install mamba
  uses: mamba-org/setup-micromamba@v1
  with:
    micromamba-version: '1.5.8-0'
    environment-file: .github/build-environment.yml
    cache-environment: true
```

这是关键步骤：
- 使用 micromamba（轻量 conda 实现）创建构建环境
- 根据 `.github/build-environment.yml` 安装依赖（jupyterlite-core、jupyterlite-xeus 等）
- `cache-environment: true` 缓存 conda 环境，避免每次重新下载包（显著加速构建）
- 缓存 key 基于 environment-file 的内容哈希，文件变更时自动重建缓存

#### 4. Build the JupyterLite site（构建站点）

```yaml
- name: Build the JupyterLite site
  shell: bash -l {0}
  run: |
    cp README.md content
    jupyter lite build --contents content --output-dir dist
```

核心构建步骤：
- `cp README.md content`：将 README.md 复制到 content 目录，使其在 JupyterLite 文件浏览器中可见
- `jupyter lite build`：执行构建命令
  - `--contents content`：指定内容目录（包含 Notebook 和 README）
  - `--output-dir dist`：输出到 dist/ 目录
- `shell: bash -l {0}`：使用 login shell，确保 conda/mamba 的初始化脚本被正确加载（否则 jupyter 命令可能找不到）

构建过程中 jupyterlite-xeus 插件会：
1. 读取根目录的 `environment.yml`
2. 从 emscripten-forge-dev 和 conda-forge 通道下载 WASM 包
3. 将 xeus 内核和用户包打包到静态站点
4. 编译 JupyterLab/Notebook 前端
5. 生成所有静态文件到 dist/

#### 5. Upload artifact（上传构建产物）

```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ./dist
```

将 dist/ 目录打包为 GitHub Pages artifact，供 deploy job 使用。

## Deploy Job 详解

deploy job 将 build job 产生的静态文件部署到 GitHub Pages。

### 依赖和条件

```yaml
deploy:
  needs: build
  if: github.ref == 'refs/heads/main'
```

- `needs: build`：等待 build job 成功完成
- `if: github.ref == 'refs/heads/main'`：仅在 main 分支执行（PR 不部署）

### 权限配置

```yaml
permissions:
  pages: write
  id-token: write
```

- `pages: write`：允许写入 GitHub Pages
- `id-token: write`：允许使用 OIDC 进行认证（无需手动配置 deploy token）

### 环境配置

```yaml
environment:
  name: github-pages
  url: ${{ steps.deployment.outputs.page_url }}
```

指定部署到 `github-pages` 环境，并记录部署后的 URL。

### 部署步骤

```yaml
steps:
  - name: Deploy to GitHub Pages
    id: deployment
    uses: actions/deploy-pages@v4
```

使用官方的 `actions/deploy-pages@v4` 将之前上传的 artifact 部署到 GitHub Pages。部署完成后，站点即可通过 `https://{user}.github.io/{repo}/` 访问。

## 自定义工作流

### 添加构建前步骤

如果需要在构建前执行额外操作（如预处理数据、下载额外文件），可以在 Build 步骤前添加：

```yaml
- name: Preprocess data
  shell: bash -l {0}
  run: |
    # 例如：下载数据集到 content/
    wget https://example.com/data.csv -O content/data.csv
```

### 自定义构建参数

修改 Build 步骤的 `jupyter lite build` 命令可以添加更多选项：

```yaml
- name: Build the JupyterLite site
  shell: bash -l {0}
  run: |
    cp README.md content
    jupyter lite build \
      --contents content \
      --output-dir dist \
      --mathjax-url "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
```

常用 `jupyter lite build` 选项：
- `--contents <dir>`：内容目录
- `--output-dir <dir>`：输出目录
- `--apps <apps>`：构建哪些应用（lab/notebook/retro）
- `--mathjax-url <url>`：自定义 MathJax CDN
- `--lite-dir <dir>`：JupyterLite 源目录

### 修改部署分支

如果需要部署到非 GitHub Pages 的位置（如 Netlify、Vercel、S3 等），可以替换 deploy job。但这超出了默认模板的范围。

### 添加构建状态徽章

在 README.md 中可以添加构建状态徽章：

```markdown
[![Build](https://github.com/{USER}/{REPO}/actions/workflows/deploy.yml/badge.svg)](https://github.com/{USER}/{REPO}/actions/workflows/deploy.yml)
```

## 监控构建

在仓库的 **Actions** 标签页可以查看：
- 每次构建的状态（成功/失败/进行中）
- 每个步骤的详细日志
- 构建耗时
- 历史构建记录

## 常见构建失败原因

| 失败步骤 | 可能原因 | 排查方法 |
|---------|---------|---------|
| Install mamba | environment.yml 语法错误或包不存在 | 检查 .github/build-environment.yml 语法 |
| Build | environment.yml 中的包无 WASM 版本 | 查看构建日志，确认包在 emscripten-forge 可用 |
| Build | jupyterlite-xeus 版本不兼容 | 尝试升级/降级 jupyterlite-xeus 版本 |
| Deploy | GitHub Pages 未启用 | 确认 Settings → Pages → Source = "GitHub Actions" |
| Deploy | 权限不足 | 确认 permissions 配置中 pages 和 id-token 为 write |

## 相关概念

- [GitHub 模板三步部署](03-github-template-deploy.md) — 部署流程入门
- [构建环境配置](05-build-env-config.md) — build-environment.yml 详解
- [双环境模型](02-dual-environment.md) — 两个环境文件的区别
