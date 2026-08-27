---
type: Example
title: CI Diff检查集成
description: 使用rediraffecheckdiff构建器在CI/CD流水线中检查删除/重命名文件是否都有重定向配置
tags: [sphinxext-rediraffe, ci, cd, github-actions, diff-checker, rediraffecheckdiff]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# CI Diff检查集成

本示例演示如何将 `rediraffecheckdiff` 构建器集成到CI/CD流水线中，自动检测PR中删除或重命名的文件是否都配置了重定向。

## 工作原理

`rediraffecheckdiff` 通过Git命令检测文件变更：

1. `git diff --name-status --diff-filter=R <branch>` — 检测重命名文件（R状态），获取相似度和新旧路径
2. `git diff --diff-filter=D --name-only <branch>` — 检测删除文件（D状态）
3. 将检测到的变更文件与 `rediraffe_redirects` 配置对比
4. 未配置重定向的文件输出error日志，构建以非零退出码失败

## 前置条件

- 项目使用Git进行版本控制
- CI环境中可以执行git命令
- `rediraffe_redirects` 已配置（dict或文件方式均可）
- `rediraffe_branch` 设置为对比基准分支

## GitHub Actions 集成

### 基础配置

在 `.github/workflows/docs.yml` 中添加重定向检查步骤：

```yaml
name: Documentation

on:
  pull_request:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 需要完整git历史进行diff比较

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install sphinx sphinxext-rediraffe

      - name: Check redirects
        run: |
          sphinx-build -b rediraffecheckdiff \
            -D rediraffe_branch=origin/${{ github.base_ref }} \
            docs docs/_build/redirect-check
```

### 关键点说明

1. **`fetch-depth: 0`**：必须获取完整git历史，否则git diff无法对比分支差异
2. **`rediraffe_branch=origin/main`**：对比PR的目标分支（通常是main）
3. **退出码非零**表示有遗漏的重定向，CI自动标记失败

### 完整工作流示例

```yaml
name: Documentation Check

on:
  pull_request:
    branches: [main, develop]

jobs:
  check-redirects:
    name: Check redirects
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Sphinx and rediraffe
        run: pip install sphinx>=6.0 sphinxext-rediraffe

      - name: Fetch base branch
        run: |
          git fetch origin ${{ github.base_ref }}:${{ github.base_ref }}

      - name: Run redirect checker
        run: |
          sphinx-build -b rediraffecheckdiff \
            -D rediraffe_branch=${{ github.base_ref }} \
            docs docs/_build/redirect-check

      - name: Build docs (only if redirect check passes)
        run: sphinx-build -b html docs docs/_build/html
```

## ReadTheDocs 集成

在 ReadTheDocs 的 `.readthedocs.yml` 中添加构建前检查：

```yaml
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.12"
  jobs:
    pre_build:
      - pip install sphinxext-rediraffe
      - git fetch origin main:main
      - sphinx-build -b rediraffecheckdiff -D rediraffe_branch=main docs docs/_build/check
```

注意：ReadTheDocs默认进行shallow clone，需要在构建中执行 `git fetch` 获取目标分支。

## 本地验证

在提交PR之前，本地运行检查：

```bash
# 检查相对于main分支的变更
git fetch origin main
sphinx-build -b rediraffecheckdiff -D rediraffe_branch=origin/main docs docs/_build/check

# 检查最近1个提交的变更
sphinx-build -b rediraffecheckdiff -D rediraffe_branch=HEAD~1 docs docs/_build/check

# 检查工作区未提交的变更
sphinx-build -b rediraffecheckdiff docs docs/_build/check
```

## 检查输出解读

### 通过检查的输出

```
Running Sphinx...
# 正常的Sphinx初始化日志...
deleted file docs/old-page.rst redirects to docs/new-page.rst.
renamed file docs/old-tutorial.rst redirects to docs/tutorial.rst.

build succeeded.
```

- `deleted file ... redirects to ...`：删除的文件有重定向配置 ✅
- `renamed file ... redirects to ...`：重命名的文件有重定向配置 ✅

### 检查失败的输出

```
(broken) docs/forgotten-page.rst was deleted but is not redirected!
(broken) docs/moved-page.rst was deleted but is not redirected! Hint: This file was renamed to docs/new-page.rst with a similarity of 95%.

Extension error...
```

- `was deleted but is not redirected!`：删除的文件缺少重定向配置 ❌
- `was renamed to ... with a similarity of N%`：重命名的文件缺少重定向配置，并给出提示目标 ❌

## 修复流程

当CI检查失败时，按以下步骤修复：

### 场景1：删除文件

如果文件确实应该删除且不需要重定向（如废弃的API页面被完全移除），不需要处理。但更好的做法通常是添加重定向到替代页面：

```python
# conf.py（dict方式）
rediraffe_redirects = {
    'api/deprecated.rst': 'api/index.rst',  # 将废弃页面重定向到API索引
}
```

或在 `redirects.txt` 中添加：

```text
api/deprecated.rst api/index.rst
```

### 场景2：重命名文件

根据CI提示的相似度信息，添加重定向：

```text
# CI提示：moved-page.rst was renamed to new-page.rst with a similarity of 95%
moved-page.rst new-page.rst
```

### 场景3：批量修复

当有大量重命名时，可以使用 `rediraffewritediff` 自动补全：

```bash
# 自动将相似度>=90%的重命名追加到redirects.txt
sphinx-build -b rediraffewritediff \
  -D rediraffe_branch=HEAD~1 \
  -D rediraffe_auto_redirect_perc=90 \
  docs docs/_build/write

# 审查自动添加的条目
cat docs/redirects.txt

# 手动补充未自动添加的条目后，再次运行检查
sphinx-build -b rediraffecheckdiff -D rediraffe_branch=HEAD~1 docs docs/_build/check
```

## 相关概念

- [Builder体系详解](../concepts/05-builders.md)
- [配置项详解](../concepts/04-configuration.md)
- [自动重定向写入示例](auto-redirect-writer.md)
