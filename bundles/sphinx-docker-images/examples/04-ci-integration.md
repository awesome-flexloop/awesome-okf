---
type: example
title: "CI 集成：在 GitHub Actions 中构建文档"
description: "在 GitHub Actions 中使用 Sphinx Docker 镜像自动构建和部署文档的完整配置"
tags: [example, ci, github-actions, deployment]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: build, resource: "/references/workflow-build.md", title: "版本发布工作流 build.yml" }
  - { id: build-ci, resource: "/references/workflow-build-ci.md", title: "CI 镜像工作流 build-ci.yml" }
---

# CI 集成：在 GitHub Actions 中构建文档

本示例演示如何在 GitHub Actions CI 流水线中使用 Sphinx Docker 镜像自动构建文档，可选部署到 GitHub Pages。

## 前置条件

- 项目托管在 GitHub 上
- 项目中有 Sphinx 文档目录（如 `docs/`）
- 可选：需要部署到 GitHub Pages

## 示例 1：基础 HTML 构建检查

创建 `.github/workflows/docs.yml`：

```yaml
name: Build Docs

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Build HTML with Sphinx Docker
        run: |
          cd docs
          docker run --rm -v "${{ github.workspace }}/docs:/docs" \
            sphinxdoc/sphinx:8.2.3 \
            sphinx-build -M html . _build -W

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: docs-html
          path: docs/_build/html/
```

**关键点**：
- `-W` 参数将警告视为错误，确保文档质量
- 使用 `github.workspace` 获取绝对路径
- 上传构建产物供下载查看

## 示例 2：构建 PDF 文档

```yaml
name: Build PDF Docs

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build PDF with Sphinx LaTeX image
        run: |
          cd docs
          docker run --rm -v "${{ github.workspace }}/docs:/docs" \
            sphinxdoc/sphinx-latexpdf:8.2.3 \
            sphinx-build -M latexpdf . _build

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: docs-pdf
          path: docs/_build/latex/*.pdf
```

## 示例 3：使用自定义依赖构建

如果文档需要额外的 Python 包，可以在 CI 中直接安装（无需自定义镜像）：

```yaml
name: Build Docs with Dependencies

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies and build
        run: |
          cd docs
          docker run --rm -v "${{ github.workspace }}/docs:/docs" \
            sphinxdoc/sphinx:8.2.3 \
            bash -c "pip install --no-cache-dir \
              sphinx-rtd-theme myst-parser \
              && sphinx-build -M html . _build -W"

      - uses: actions/upload-artifact@v4
        with:
          name: html-docs
          path: docs/_build/html/
```

## 示例 4：部署到 GitHub Pages

```yaml
name: Docs to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build HTML
        run: |
          cd docs
          docker run --rm -v "${{ github.workspace }}/docs:/docs" \
            sphinxdoc/sphinx:8.2.3 \
            bash -c "pip install --no-cache-dir -r requirements.txt \
              && sphinx-build -M html . _build"

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build/html/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## 示例 5：使用 docker-ci 镜像测试 Sphinx 扩展开发

如果你在开发 Sphinx 扩展，可以使用 CI 镜像：

```yaml
name: Test Sphinx Extension

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests in Sphinx CI image
        run: |
          docker run --rm \
            -v "${{ github.workspace }}:/sphinx" \
            sphinxdoc/docker-ci:latest \
            bash -c "
              cd /sphinx &&
              python3 -m venv /tmp/venv &&
              source /tmp/venv/bin/activate &&
              pip install -e '.[test]' &&
              pytest tests/
            "
```

## CI 最佳实践

1. **固定镜像版本**：使用 `sphinxdoc/sphinx:8.2.3` 而非 `:latest`，确保构建可复现
2. **-W 警告即错误**：构建时加上 `-W` 参数，防止文档警告积累
3. **缓存 pip 包**：对于需要频繁安装依赖的项目，使用 Docker 卷或 actions/cache 缓存 pip 包
4. **分离构建和部署**：build job 构建文档，deploy job 部署，失败时容易定位
5. **只在必要时构建 PDF**：PDF 构建慢且镜像大，只在 tag 发布时构建
6. **上传 artifact**：构建完成后上传 HTML 产物，方便预览和审查

## 从 GHCR 拉取镜像

如果 Docker Hub 访问不稳定，可以从 GHCR 拉取：

```yaml
docker run --rm -v "${{ github.workspace }}/docs:/docs" \
  ghcr.io/sphinx-doc/sphinx:8.2.3 \
  sphinx-build -M html . _build
```

## 相关概念

- [构建流水线详解](/concepts/06-build-pipeline.md)：官方镜像的 CI/CD 设计
- [CI 测试镜像详解](/concepts/05-ci-image.md)：docker-ci 镜像的用途
- [自定义镜像扩展](/examples/03-custom-image.md)：为 CI 创建专用自定义镜像
