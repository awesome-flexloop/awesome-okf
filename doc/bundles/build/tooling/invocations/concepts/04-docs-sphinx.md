---
type: Concept
title: Sphinx 文档管理
description: 使用 docs 模块构建、清理、浏览 Sphinx 文档，多站点管理与文件监控自动重建
tags: [invocations, docs, sphinx, documentation, watch-docs, multi-site]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# Sphinx 文档管理

`invocations.docs` 模块提供 [Sphinx](https://www.sphinx-doc.org/) 文档构建、管理和文件监控自动重建任务。

## 快速使用

```python
# tasks.py
from invoke import Collection
from invocations.docs import ns as docs_ns

ns = Collection(docs_ns)
ns.configure({
    "sphinx": {
        "source": "docs",
        "target": "docs/_build",
        "target_file": "index.html",
    },
})
```

## 核心任务

### build：构建文档（默认任务）

```bash
# 默认构建
inv docs.build

# 构建前清理
inv docs.build --clean

# 构建后在浏览器中打开
inv docs.build --browse

# 严格模式（nitpick：警告转错误 + 完整 traceback）
inv docs.build --nitpick

# 传递额外 sphinx-build 选项
inv docs.build --opts="-b dirhtml"

# 指定源目录/输出目录（覆盖配置）
inv docs.build --source=custom-docs --target=custom-build
```

#### build 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `clean` | bool | False | 构建前清理 target 目录 |
| `browse` | bool | False | 构建完成后用 `open` 命令打开 index.html |
| `nitpick` | bool | False | 添加 `-n -W -T`（nitpicky + warnings-as-errors + full traceback） |
| `opts` | str | None | 额外 sphinx-build 选项 |
| `source` | str | None | 源目录，覆盖 `sphinx.source` 配置 |
| `target` | str | None | 输出目录，覆盖 `sphinx.target` 配置 |

构建命令格式为：`sphinx-build <opts> <source> <target>`。

### clean：清理构建目录

```bash
inv docs.clean
```

删除 `sphinx.target` 目录（通常是 `docs/_build`），确保下次构建从零开始。

### browse：打开文档

```bash
inv docs.browse
```

使用 `open` 命令在浏览器中打开构建产物的 `index.html`。

### doctest：运行文档测试

```bash
inv docs.doctest
```

运行 Sphinx 的 [doctest](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html) builder，测试文档中的代码示例。使用临时目录作为构建目标，测试完成后自动清理。

### tree：显示文档树

```bash
inv docs.tree
```

使用 `tree` 命令显示文档源目录结构，忽略 `.git`、`__pycache__`、`_build` 等目录。

## 默认配置

```python
ns.configure({
    "sphinx": {
        "source": "docs",
        "target": "docs/_build",
        "target_file": "index.html",
    },
})
```

## 多站点构建

对于维护多个文档站点的项目（如 API 文档站 `docs/` 和主网站 `www/`），`invocations.docs` 提供了多站点支持。模块内置了两个预定义子集合：

```python
from invocations.docs import docs, www  # 两个预配置的子集合
```

- `docs`：构建 `sites/docs/` → `sites/docs/_build/`（API 文档站）
- `www`：构建 `sites/www/` → `sites/www/_build/`（主网站）

期望目录结构：

```
project/
├── sites/
│   ├── docs/      # API 文档 Sphinx 源
│   │   ├── conf.py
│   │   └── index.rst
│   └── www/       # 主网站 Sphinx 源
│       ├── conf.py
│       └── index.rst
```

### sites：同时构建两个站点

```bash
inv docs.sites
```

`sites` 任务执行两轮构建：
1. **第一轮**（静默模式）：同时构建 docs 和 www，确保 intersphinx inventory 文件存在
2. **第二轮**（严格模式）：以 `nitpick=True` 严格构建两个站点

### watch-docs：文件监控自动重建

```bash
inv docs.watch-docs
```

`watch-docs` 使用 watchdog 监控文件变化并自动重建：

- **WWW 触发**：`./README.rst` 或 `./sites/www/` 目录变化 → 重建 www 站点
- **API 触发**：`./sites/docs/` 目录变化 → 重建 docs 站点
- **源码触发**：`./<package>/` 目录变化（通过 `packaging.package` 或 `tests.package` 配置确定包名）→ 重建 docs 站点

使用 `ignore_regexes` 忽略 `.swp` 文件和 `_build` 目录。

### 自定义站点

`_site(name, help_part)` 工厂函数可用于创建自定义站点子集合：

```python
from invocations.docs import _site
# 创建自定义站点子集合
api_docs = _site("api", "the API reference subsite.")
# 在自己的 tasks.py 中使用
ns = Collection(api_docs)
```

## 跨 Context 调用模式

docs.py 中展示了一个重要的 Invoke 模式——**在一个任务中调用另一个 Collection 的任务并使用其独立配置**：

```python
# sites 任务中的模式
from invoke import Context
docs_c = Context(config=c.config.clone())
www_c = Context(config=c.config.clone())
docs_c.update(**docs.configuration())
www_c.update(**www.configuration())
docs_c["run"].hide = True
docs["build"](docs_c, nitpick=True)  # 用独立 context 调用子集合任务
```

这种模式允许在单个任务中使用不同 Collection 的配置执行同一任务函数，实现多站点并行构建。

## 相关概念

- [快速上手](/concepts/01-getting-started.md)
- [工具函数与文件监控](/concepts/07-utilities-watchers.md)
- [组合模式：组装自己的任务集合](/concepts/10-composition-patterns.md)
- [多站点文档构建示例](/examples/multi-site-docs.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
