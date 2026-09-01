---
type: Concept
title: 5分钟快速上手
description: 在 GitHub Actions 中集成 Sphinx Problem Matcher 的完整步骤、workflow 配置示例与注意事项
tags: [github-problem-matcher, getting-started, github-actions, workflow, ci]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T14:50:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: gpm-source
    resource: /references/github-problem-matcher-source.md
---

# 5分钟快速上手

## 前置条件

使用 Sphinx Problem Matcher 需要：

1. 项目使用 [Sphinx](https://www.sphinx-doc.org/) 构建文档（reStructuredText 或 MyST Markdown）
2. 项目托管在 GitHub 上并使用 GitHub Actions 作为 CI 平台
3. CI workflow 中包含文档构建步骤（如 `make html` 或 `sphinx-build`）

## 最小配置

在你的 GitHub Actions workflow 文件（通常是 `.github/workflows/docs.yml`）中，在 Sphinx 构建步骤**之前**添加一行 `uses`：

```yaml
name: Build Docs
on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install sphinx
          # 安装你的文档依赖

      - name: Activate Sphinx Problem Matcher
        uses: sphinx-doc/github-problem-matcher@master

      - name: Build docs
        run: |
          cd docs
          make html
```

就是这么简单。添加 `uses: sphinx-doc/github-problem-matcher@master` 这一步之后，后续的 Sphinx 构建输出中的警告就会被自动捕获并显示为 PR 注解。

## 关键注意事项

### Matcher 必须在构建之前注册

`::add-matcher::` 命令只影响命令执行**之后**的日志输出。因此必须确保：

```yaml
# ✅ 正确：先注册 matcher，再构建
- uses: sphinx-doc/github-problem-matcher@master
- run: make html

# ❌ 错误：先构建，再注册 matcher（matcher 看不到之前的输出）
- run: make html
- uses: sphinx-doc/github-problem-matcher@master
```

### Action 不构建文档

README 特别强调：

> **Note: This action does not handle actually building your docs.**

这个 Action 只注册 Problem Matcher，不安装 Sphinx、不执行构建命令。你需要自己负责文档构建的所有步骤。

### 版本固定

生产环境建议固定版本而非使用 `@master`：

```yaml
# 推荐：固定到特定 commit SHA（最安全）
- uses: sphinx-doc/github-problem-matcher@<commit-sha>

# 或者使用 release tag（如有）
- uses: sphinx-doc/github-problem-matcher@v1
```

`@master` 跟随主分支，可能在未来更新中引入不兼容变更。

## 配合 -W 选项实现质量门禁

Sphinx 支持 `-W`（`--warnings-as-errors`）选项将警告转为错误。配合 Problem Matcher，可以实现文档质量门禁：

```yaml
- name: Build docs (warnings as errors)
  run: |
    cd docs
    sphinx-build -W -b html . _build/html
```

这样当存在任何文档警告时：
1. PR 中显示内联警告注解（来自 Problem Matcher）
2. CI 构建失败（来自 `-W` 选项）
3. 阻止有问题的文档合入主分支

## 效果预览

注册 matcher 后，当 Sphinx 输出警告时，PR 的 Files changed 视图中会在对应的文件和行号上显示警告标记。开发者点击注解可以直接看到警告消息，无需在构建日志中搜索。

匹配的警告格式包括：

```
# 标准格式（文件:行号: 级别: 消息）
docs/index.rst:16: WARNING: Error in "code-block" directive: ...

# 宽松格式（/绝对路径.rst: 级别: 消息，无行号）
/path/to/docs/notintoc.rst: WARNING: document isn't included in any toctree

# 兜底格式（文件.rst:行号:消息，无级别标识）
docs/config.rst:42:Undefined label or reference target
```

## 完整 workflow 示例

以下是一个生产级文档 CI 配置：

```yaml
name: Documentation
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install Sphinx and dependencies
        run: |
          pip install sphinx sphinx-rtd-theme myst-parser
          pip install -e .  # 安装项目本身（如需要 autodoc）

      - name: Activate Sphinx Problem Matcher
        uses: sphinx-doc/github-problem-matcher@master

      - name: Build HTML documentation
        run: |
          sphinx-build -W -b html docs/ docs/_build/html

      - name: Deploy to GitHub Pages (on main branch)
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/_build/html
```

## 相关概念

- [Action 结构解析](02-action-structure.md)
- [Problem Matcher JSON 格式](03-matcher-json.md)
- [三种正则模式详解](04-regex-patterns.md)
- [基础使用示例](../examples/basic-usage.md)
- [源码信源登记](../references/github-problem-matcher-source.md)
