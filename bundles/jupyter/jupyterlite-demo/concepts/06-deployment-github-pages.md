---
type: Concept
title: GitHub Pages 部署流水线
description: JupyterLite 站点的 CI/CD 构建部署流程、GitHub Actions 工作流配置、构建命令参数详解，以及本地构建预览方法
tags: [deployment, github-pages, ci-cd, github-actions, build, jupyter-lite-build]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: workflow
    resource: /references/deploy-workflow-source.md
    title: 部署流水线信源
  - id: requirements
    resource: /references/requirements-source.md
    title: 依赖配置信源
---

## 部署流程概览

JupyterLite Demo 使用 GitHub Actions 自动化构建和部署到 GitHub Pages，整个流程分为两个 Job：

```
┌──────────────┐     ┌──────────────┐
│   Push/PR    │────→│  build job   │
└──────────────┘     └──────┬───────┘
                            │ dist/ 产物
                            ▼
                     ┌──────────────┐
                     │ deploy job   │────→ GitHub Pages
                     │ (仅 main)    │
                     └──────────────┘
```

- **build job**：每次 push 和 PR 都执行，负责安装依赖和构建站点
- **deploy job**：仅 main 分支执行，负责将构建产物部署到 GitHub Pages

## build job 详解

### 触发条件

```yaml
on:
  push:
    branches:
      - main        # 推送到 main 分支时触发
  pull_request:
    branches:
      - '*'         # 所有 PR 都触发（用于测试构建是否成功）
```

PR 触发的 build 只验证构建能否成功，不会部署。

### 构建步骤

**步骤 1：检出代码**

```yaml
- uses: actions/checkout@v4
```

**步骤 2：设置 Python 环境**

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
```

使用 Python 3.11（JupyterLite 兼容版本）。

**步骤 3：安装依赖**

```yaml
- run: python -m pip install -r requirements.txt
```

安装 requirements.txt 中声明的所有 JupyterLite 包和扩展。

**步骤 4：构建站点**

```yaml
- run: |
    cp README.md content
    jupyter lite build --contents content --output-dir dist
```

关键操作：
1. `cp README.md content`：将 README 复制到内容目录，使其在站点内可访问
2. `jupyter lite build`：执行构建，核心参数：
   - `--contents content`：指定内容源目录
   - `--output-dir dist`：指定构建输出目录

**步骤 5：上传构建产物**

```yaml
- uses: actions/upload-pages-artifact@v3
  with:
    path: ./dist
```

将 dist/ 目录打包为 GitHub Pages artifact。

## deploy job 详解

### 条件与权限

```yaml
deploy:
  needs: build                    # 等待 build 完成
  if: github.ref == 'refs/heads/main'  # 仅在 main 分支
  permissions:
    pages: write                  # Pages 写入权限
    id-token: write               # OIDC 认证
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
```

### 部署步骤

```yaml
- uses: actions/deploy-pages@v4
  id: deployment
```

使用官方 action 将 artifact 部署到 GitHub Pages。部署成功后，站点可通过 `https://<username>.github.io/<repo>/` 访问。

## jupyter lite build 命令详解

```bash
jupyter lite build [OPTIONS]
```

### 常用参数

| 参数 | 说明 | Demo 是否使用 |
|------|------|:---:|
| `--contents` | 内容源目录路径 | ✅ `--contents content` |
| `--output-dir` | 构建输出目录 | ✅ `--output-dir dist` |
| `--lite-dir` | 包含 jupyter-lite.json 的目录 | ❌（默认当前目录） |
| `--apps` | 构建的应用列表 | ❌（默认全部：lab/repl/tree/retro） |
| `--piplite-url` | 自定义 PyPI 镜像 URL | ❌ |
| `--fed-lib-cdn` | 使用 CDN 加载第三方扩展 | ❌ |
| `--no-sourcemaps` | 不生成 sourcemaps | ❌ |
| `--debug` | 输出调试信息 | ❌ |

### 构建过程

执行 `jupyter lite build` 时，内部执行以下操作：

1. **发现包**：扫描当前 Python 环境中安装的 jupyterlite 相关包（内核、扩展、主题）
2. **收集前端资源**：将各包的 JupyterLab 扩展（JS/CSS/WASM）收集到构建目录
3. **复制内容**：将 `--contents` 指定目录的文件复制到 files/
4. **生成配置**：生成运行时 jupyter-lite.json，合并用户配置
5. **生成应用**：为每个应用（lab/repl/tree）生成 HTML 和配置
6. **生成 Service Worker**：生成离线缓存的 service-worker.js
7. **打包 Pyodide**：复制 Pyodide WASM 文件和预安装包

### 构建输出结构

```
dist/
├── index.html              # 入口重定向页面
├── jupyter-lite.json       # 运行时配置（构建生成）
├── service-worker.js       # Service Worker（离线缓存）
├── lab/                    # JupyterLab 应用
│   ├── index.html
│   ├── packages/           # JupyterLab 扩展包
│   └── themes/             # 主题资源
├── repl/                   # REPL 应用
├── tree/                   # 文件浏览器
├── Pyodide/                # Pyodide WASM 运行时
│   ├── pyodide.js
│   ├── pyodide.asm.wasm
│   └── pyodide_py.tar      # Python 标准库
├── @jupyterlite/           # JupyterLite 内核资源
│   ├── pyodide-kernel/
│   ├── javascript-kernel/
│   └── p5-kernel/
├── files/                  # 用户内容文件（从 content/ 复制）
│   ├── python.ipynb
│   ├── data/
│   └── README.md
└── api/                    # Jupyter Server API 模拟
```

## GitHub Pages 前置设置

要让部署工作流生效，仓库需要配置：

1. 进入仓库 **Settings → Pages**
2. **Source** 选择 **GitHub Actions**（而非 Deploy from branch）
3. 确保仓库的 Actions 权限允许 Pages 写入（Settings → Actions → General → Workflow permissions）

## 本地构建与预览

在本地开发时，可以跳过 CI 直接构建和预览：

```bash
# 安装依赖
pip install -r requirements.txt

# 构建站点
cp README.md content
jupyter lite build --contents content --output-dir dist

# 启动本地预览服务器
jupyter lite serve --output-dir dist
# 或者使用任意静态文件服务器
python -m http.server 8000 --directory dist
# 访问 http://localhost:8000
```

本地预览注意事项：
- `jupyter lite serve` 会自动检测文件变化并重新构建
- 需要使用 HTTP 服务器访问（不能用 file:// 协议），因为 Service Worker 和 WASM 需要 HTTP(S)
- 某些浏览器扩展可能会干扰 Service Worker，建议使用无痕模式测试

## 其他部署方式

除了 GitHub Pages，构建产物（dist/）可以部署到任何支持静态文件托管的服务：

| 平台 | 方法 |
|------|------|
| Vercel | 导入仓库，配置构建命令和输出目录 |
| Netlify | 类似 Vercel，拖拽 dist/ 目录即可部署 |
| S3 + CloudFront | 上传 dist/ 到 S3 bucket，配置 CloudFront CDN |
| 自有服务器 | 将 dist/ 放到 Nginx/Apache 的静态文件目录 |
| IPFS | 上传 dist/ 到 IPFS，通过网关访问 |

部署到子路径时（如 `https://example.com/jupyterlite/`），需要在 jupyter-lite.json 中配置 `baseUrl`。

## 相关概念

- [站点配置详解](/concepts/02-site-configuration.md)
- [Demo 仓库结构与三件套模式](/concepts/01-demo-overview.md)
- [自定义 Demo 站点指南](/concepts/07-customization-guide.md)
- [从零部署实战](/examples/01-first-deployment.md)
- [自定义 Demo 站点实战](/examples/07-custom-demo-site.md)
