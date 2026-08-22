---
type: Example
title: CI集成与缓存策略
description: 在CI/CD流水线中使用jupyter-cache加速Notebook文档构建，包括GitHub Actions配置和缓存持久化策略
tags: [jupyter, cache, ci, cd, github-actions, build, example]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:54:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# CI集成与缓存策略

## 核心思路

CI构建Notebook文档的痛点：
- 每次CI运行都重新执行所有Notebook，耗时很长
- 大部分Notebook代码未变，重复执行浪费资源
- 数据Notebook执行可能需要数分钟甚至数小时

jupyter-cache解决思路：
1. 将缓存目录持久化到CI缓存系统
2. 构建时自动跳过已缓存的Notebook
3. 仅重新执行代码变更的Notebook

## GitHub Actions配置

```yaml
# .github/workflows/docs.yml
name: Build Docs

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install jupyter-cache jupyter-book
          pip install -r requirements.txt

      - name: Cache jupyter-cache
        uses: actions/cache@v4
        with:
          path: .jupyter_cache
          key: jcache-${{ github.run_id }}
          restore-keys: |
            jcache-

      - name: Add notebooks to cache
        run: |
          jcache -p .jupyter_cache notebook add docs/notebooks/*.ipynb || true

      - name: Execute notebooks (cached)
        run: |
          jcache -p .jupyter_cache notebook execute-all

      - name: Build documentation
        run: |
          jupyter-book build docs/

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/_build/html
```

### 关键点说明

1. **缓存持久化**：使用 `actions/cache@v4` 缓存 `.jupyter_cache` 目录
2. **restore-keys**：使用 `jcache-` 前缀恢复最近的缓存
3. **`|| true`**：添加Notebook时已存在则忽略错误
4. **execute-all**：仅执行未缓存的Notebook

## GitLab CI配置

```yaml
# .gitlab-ci.yml
variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  JCACHE_DIR: "$CI_PROJECT_DIR/.jupyter_cache"

cache:
  paths:
    - .cache/pip
    - .jupyter_cache

build_docs:
  image: python:3.11
  stage: build
  script:
    - pip install jupyter-cache jupyter-book
    - jcache notebook add docs/notebooks/*.ipynb || true
    - jcache notebook execute-all
    - jupyter-book build docs/
  artifacts:
    paths:
      - docs/_build/html/
```

## 缓存策略最佳实践

### 缓存大小控制

```bash
# 在CI构建前设置合理的缓存上限
jcache cache limit 200

# 定期清理（可选，LRU自动淘汰）
# 无需手动清理，超限自动删除最旧缓存
```

### 强制重新执行

当需要强制重新执行所有Notebook时（如依赖库版本更新）：

```bash
# 清除缓存
jcache cache clear

# 或在CI中通过commit message触发
# "[clear-cache]" 在commit message中时清空缓存
```

GitHub Actions示例：

```yaml
- name: Clear cache if requested
  run: |
    if [[ "${{ github.event.head_commit.message }}" == *"[clear-cache]"* ]]; then
      jcache cache clear
    fi
```

### 缓存键策略

根据Notebook内容变更设计缓存键：

```yaml
# 使用Notebook文件hash作为缓存键的一部分
- name: Compute notebook hash
  id: nb-hash
  run: |
    HASH=$(find docs/notebooks -name "*.ipynb" -exec md5sum {} \; | sort | md5sum | cut -d' ' -f1)
    echo "hash=$HASH" >> $GITHUB_OUTPUT

- name: Cache jupyter-cache
  uses: actions/cache@v4
  with:
    path: .jupyter_cache
    key: jcache-${{ steps.nb-hash.outputs.hash }}
    restore-keys: |
      jcache-
```

## 与MyST-NB/jupyter-book集成

jupyter-cache 可通过 myst_nb 配置直接集成：

```python
# _config.yml (jupyter-book)
sphinx:
  config:
    nb_execution_mode: cache
    nb_execution_cache_path: .jupyter_cache
```

或在 `conf.py`（Sphinx + MyST-NB）：

```python
# conf.py
extensions = ["myst_nb"]
nb_execution_mode = "cache"
nb_execution_cache_path = ".jupyter_cache"
```

MyST-NB 在 cache 模式下自动使用 jupyter-cache 管理Notebook执行缓存。

## 本地开发缓存策略

```bash
# 开发时使用全局缓存路径
export JCACHE_PATH=~/.cache/jupyter-cache/myproject

# 执行Notebook
jcache -p $JCACHE_PATH notebook add notebooks/*.ipynb || true
jcache -p $JCACHE_PATH notebook execute-all
```

这在多个项目间共享执行缓存，节省磁盘空间。

## 故障排查

### 缓存损坏

```bash
# 如果缓存数据库损坏，清除重建
jcache cache clear
jcache notebook add notebooks/*.ipynb
jcache notebook execute-all
```

### 缓存版本不兼容

升级jupyter-cache后可能需要清除旧缓存：

```bash
jcache project info
# 如果版本不匹配，清除缓存
jcache cache clear
```

### CI缓存未命中

1. 检查缓存路径是否正确
2. 检查 `restore-keys` 是否匹配
3. 检查Notebook文件路径是否一致（绝对/相对路径差异）

## 相关示例

- [基本CLI使用](/examples/basic-usage.md)
- [Python API编程](/examples/python-api.md)

## 相关概念

- [缓存架构设计](/concepts/02-architecture.md)
- [配置项参考](/concepts/07-configuration.md)
- [CLI命令详解](/concepts/05-cli-reference.md)
