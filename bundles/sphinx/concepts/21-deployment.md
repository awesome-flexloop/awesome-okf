---
type: "concept"
title: "部署到线上"
description: "Sphinx文档部署指南——Read the Docs、GitHub Pages、GitLab Pages、Netlify、自建服务器等部署方案，Docs as Code理念与CI/CD集成"
tags: [deployment, hosting, readthedocs, github-pages, netlify, ci-cd]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T10:45:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: official-deploy
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 Deploying 章节"
---

# 部署到线上

Sphinx 生成的 HTML 文档是纯静态文件，可以部署到几乎任何静态网站托管服务。本章介绍主流部署方案，遵循 "Docs as Code"（文档即代码）理念——将文档源码纳入版本控制，通过 CI/CD 自动构建和部署。

## 部署选项概览

| 方案 | 难度 | 版本管理 | 自定义域名 | 免费 | 适合场景 |
|------|------|---------|-----------|------|---------|
| **Read the Docs** | ⭐ 极简 | ✅ 内置多版本 | ✅ | ✅ | 开源项目文档首选 |
| **GitHub Pages** | ⭐⭐ 简单 | ⚠️ 需自己管理 | ✅ | ✅ | GitHub 项目 |
| **GitLab Pages** | ⭐⭐ 简单 | ⚠️ 需自己管理 | ✅ | ✅ | GitLab 项目 |
| **Netlify** | ⭐⭐ 简单 | ✅ Deploy Previews | ✅ | ✅ | 需要预览功能 |
| **自建服务器/Nginx** | ⭐⭐⭐ 复杂 | ❌ 手动 | ✅ | ❌ | 企业内网/私有部署 |

## Read the Docs（推荐开源项目）

[Read the Docs](https://readthedocs.org/) 是专门为技术文档（尤其是 Sphinx/MkDocs）设计的托管服务，免费用于开源项目。

### 核心特性

- **多版本文档**：自动为每个分支/标签构建不同版本的文档
- **拉取请求预览**：PR提交时自动构建预览
- **PDF/EPUB导出**：自动生成PDF和EPUB格式
- **搜索分析**：内置搜索和流量统计
- **自定义域名与HTTPS**：免费提供
- **Python/conda环境**：自动安装依赖

### 快速配置

1. 在 [Read the Docs](https://readthedocs.org/) 注册账号
2. 导入 GitHub/GitLab/Bitbucket 仓库
3. 在项目根目录添加 `.readthedocs.yaml` 配置文件：

```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.12"

sphinx:
  configuration: docs/conf.py
  # 如果Sphinx源码在docs/目录下
  # fail_on_warning: true  # 警告转错误（可选）

python:
  install:
    - requirements: docs/requirements.txt
    - method: pip
      path: .

# 可选：构建其他格式
formats:
  - pdf
  - epub
```

创建 `docs/requirements.txt`：

```txt
sphinx>=9.0
furo  # 或你使用的主题
myst-parser  # 如果用Markdown
```

提交推送后，Read the Docs 会自动构建并在 `<项目名>.readthedocs.io` 上发布。

## GitHub Pages

GitHub Pages 是 GitHub 提供的静态网站托管服务，通常通过 GitHub Actions 自动构建。

### 使用 GitHub Actions 自动部署

在仓库中创建 `.github/workflows/sphinx.yml`：

```yaml
name: "Sphinx: Render docs"

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        pip install sphinx furo myst-parser
        # 或 pip install -r docs/requirements.txt
    
    - name: Build HTML
      run: |
        cd docs
        make html
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: html-docs
        path: docs/_build/html/
    
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v4
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: docs/_build/html
```

### 配置 GitHub Pages

1. 仓库 Settings → Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 `gh-pages` / `/(root)`
4. Save

推送到 main 分支后，文档将在 `<用户名>.github.io/<仓库名>/` 上发布。

### 使用 sphinx.ext.githubpages 扩展

启用 `sphinx.ext.githubpages` 扩展，Sphinx 会自动生成 `.nojekyll` 文件（防止GitHub用Jekyll处理）和 `CNAME` 文件（自定义域名时使用）：

```python
# conf.py
extensions = ['sphinx.ext.githubpages']
```

## GitLab Pages

GitLab Pages 通过 `.gitlab-ci.yml` 配置：

```yaml
# .gitlab-ci.yml
stages:
  - deploy

pages:
  stage: deploy
  image: python:3.12-slim
  before_script:
    - apt-get update && apt-get install make --no-install-recommends -y
    - pip install sphinx furo myst-parser
  script:
    - cd docs && make html
    - mv docs/_build/html/ ./public/
  artifacts:
    paths:
      - public
  only:
    - main
```

推送到 main 分支后，文档将在 `<用户名>.gitlab.io/<仓库名>/` 发布。

## Netlify

[Netlify](https://www.netlify.com/) 提供了简单的拖拽部署和Git集成，支持Deploy Previews（每次PR生成预览URL）。

### 方法一：连接Git仓库

1. Netlify → Add new site → Import an existing project
2. 选择 GitHub/GitLab 仓库
3. 配置构建设置：
   - Build command: `sphinx-build -b html docs docs/_build/html`
   - Publish directory: `docs/_build/html`
4. 添加 `runtime.txt`（指定Python版本）：
   ```
   3.12
   ```
5. 添加 `requirements.txt`：
   ```
   sphinx>=9.0
   furo
   myst-parser
   ```

### 方法二：netlify.toml

```toml
[build]
command = "sphinx-build -b html docs docs/_build/html"
publish = "docs/_build/html"

[build.environment]
PYTHON_VERSION = "3.12"
```

## 自建服务器（Nginx）

如果需要完全控制部署环境，可以用Nginx/Apache托管静态文件：

### 步骤

1. **构建HTML文档**：
   ```bash
   sphinx-build -b html docs/ /var/www/docs/
   ```

2. **Nginx配置**：
   ```nginx
   server {
       listen 80;
       server_name docs.example.com;
       root /var/www/docs;
       index index.html;
       
       location / {
           try_files $uri $uri/ =404;
       }
       
       # 静态资源缓存
       location ~* \.(css|js|png|jpg|gif|ico|svg|woff2?)$ {
           expires 30d;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

3. **使用rsync自动同步**：
   ```bash
   #!/bin/bash
   sphinx-build -b html docs/ /tmp/docs-build/
   rsync -avz --delete /tmp/docs-build/ user@server:/var/www/docs/
   ```

### Docker部署

```dockerfile
FROM python:3.12-slim

RUN pip install sphinx furo myst-parser

WORKDIR /docs
COPY docs/ .

RUN sphinx-build -b html . _build/html

FROM nginx:alpine
COPY --from=0 /docs/_build/html /usr/share/nginx/html
EXPOSE 80
```

## "Docs as Code" 最佳实践

### 1. 文档依赖管理

将文档构建依赖固定在 `docs/requirements.txt`：

```txt
# docs/requirements.txt
sphinx==9.1.1
furo==2024.8.6
myst-parser==4.0.0
sphinxext-opengraph==0.9.1
```

或使用 `pyproject.toml` 的可选依赖组：

```toml
[project.optional-dependencies]
docs = [
    "sphinx>=9.0",
    "furo",
    "myst-parser",
]
```

安装：`pip install -e ".[docs]"`

### 2. CI/CD 检查清单

- [ ] 每次推送自动构建（无错误）
- [ ] 使用 `-W`（sphinx-build -W）将警告转为错误
- [ ] 链接检查（`sphinx-build -b linkcheck`）
- [ ] 拼写检查（使用 sphinxcontrib-spelling）
- [ ] PR预览（Read the Docs / Netlify 自动支持）

### 3. 不要提交构建产物

在 `.gitignore` 中添加：

```gitignore
# Sphinx构建产物
docs/_build/
docs/_static/
docs/_templates/
```

### 4. 文档版本管理策略

| 策略 | 适用场景 | 工具 |
|------|---------|------|
| 最新版文档 | 快速迭代的项目 | 任何部署方案 |
| 多版本文档 | 有长期支持版本的库 | Read the Docs / sphinx-multiversion |
| 每PR预览 | 协作开发 | Read the Docs / Netlify |

## sphinx-build 部署相关选项

```bash
# 基础HTML构建
sphinx-build -b html docs/ _build/html/

# 构建时将警告视为错误（CI推荐）
sphinx-build -b html -W docs/ _build/html/

# 链接检查（检查所有外部链接是否可达）
sphinx-build -b linkcheck docs/ _build/linkcheck/

# 构建PDF（需LaTeX环境）
sphinx-build -b latex docs/ _build/latex/
cd _build/latex && make

# 构建EPUB
sphinx-build -b epub docs/ _build/epub/

# 干净构建（清除缓存）
sphinx-build -b html -E docs/ _build/html/
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [HTML构建器详解](11-html-builder.md)
- [主题系统](13-theme-system.md)
- [Intersphinx跨项目引用](14-intersphinx.md)
