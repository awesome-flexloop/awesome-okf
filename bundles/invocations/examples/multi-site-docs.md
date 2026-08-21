---
type: Example
title: 多站点文档构建配置
description: 配置 docs 模块管理多个 Sphinx 文档站点（API 文档 + 主网站），包括双站构建和文件监控自动重建
tags: [invocations, example, docs, sphinx, multi-site, watch-docs]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# 多站点文档构建配置

本示例展示如何配置 Invocations 的 docs 模块来管理多个 Sphinx 文档站点，适用于同时维护 API 文档和项目主网站的项目。

## 场景

你的项目需要维护两个文档站点：
- **API 文档**（`sites/docs/`）：技术 API 参考，使用 Sphinx autodoc 从源码生成
- **主网站**（`sites/www/`）：项目介绍、README、changelog 等营销内容

期望目录结构：

```
myproject/
├── sites/
│   ├── docs/           # API 文档 Sphinx 源
│   │   ├── conf.py
│   │   ├── index.rst
│   │   ├── api.rst
│   │   └── _build/     # 构建输出（gitignore）
│   └── www/            # 主网站 Sphinx 源
│       ├── conf.py
│       ├── index.rst
│       ├── changelog.rst
│       └── _build/     # 构建输出（gitignore）
├── myproject/          # 源码包
├── README.rst
├── tasks.py
└── pyproject.toml
```

## 配置 tasks.py

### 使用内置 docs 和 www 子集合

Invocations 的 `docs.py` 模块内置了 `docs` 和 `www` 两个预配置子集合，期望 `sites/docs/` 和 `sites/www/` 目录结构：

```python
from invoke import Collection
from invocations.docs import docs, www, sites, watch_docs

# 直接使用内置子集合
ns = Collection(docs, www, sites, watch_docs)
ns.configure({
    "packaging": {
        "package": "myproject",  # watch_docs 监控源码目录用
    },
})
```

使用方式：

```bash
# 单独构建 API 文档
inv docs.build

# 单独构建主网站
inv www.build

# 同时构建两个站点（含 nitpick 严格模式）
inv docs.sites

# 监控文件变化自动重建两个站点
inv docs.watch-docs
```

### 自定义站点配置

如果内置的 `docs`/`www` 命名不符合你的需求，可以使用 `_site()` 工厂函数创建自定义站点：

```python
from invoke import Collection
from invocations.docs import _site, build, tree, watch_docs

# 创建自定义站点
api = _site("api", "the API reference documentation.")
guide = _site("guide", "the user guide documentation.")

@task
def build_all(c):
    """构建所有文档站点"""
    from invoke import Context
    for site_coll in [api, guide]:
        ctx = Context(config=c.config.clone())
        ctx.update(**site_coll.configuration())
        site_coll["build"](ctx, nitpick=True)

ns = Collection(api, guide, build_all, watch_docs)
```

期望目录结构对应调整为：

```
sites/
├── api/
│   ├── conf.py
│   └── index.rst
└── guide/
    ├── conf.py
    └── index.rst
```

### 单站点配置（简单项目）

如果你的项目只有一个文档源（标准 `docs/` 目录），使用默认配置：

```python
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

## 关键配置说明

### 自动源码监控

`watch_docs` 通过配置确定要监控的源码目录：

```python
ns.configure({
    "packaging": {"package": "myproject"},  # 优先使用
    # 或者
    "tests": {"package": "myproject"},       # 备选
})
```

配置后，`watch_docs` 会监控：
- `./README.rst` → 触发 www 重建
- `./sites/www/` → 触发 www 重建
- `./sites/docs/` → 触发 docs 重建
- `./myproject/` → 触发 docs 重建（源码变化时 API 文档需要更新）

### sites 任务的两轮构建

`sites` 任务执行两轮构建：
1. **第一轮（静默）**：同时构建 docs 和 www，`hide=True` 抑制输出。这一轮的目的是生成 intersphinx inventory 文件，解决跨站引用问题。
2. **第二轮（严格）**：以 `nitpick=True`（`-n -W -T`）构建，将警告转为错误并显示完整 traceback。

### 构建选项

```bash
# 构建并清理
inv docs.build --clean

# 构建后在浏览器打开
inv docs.build --browse

# 严格模式
inv docs.build --nitpick

# 指定额外 sphinx-build 选项
inv docs.build --opts="-b dirhtml -t production"
```

## 完整示例 tasks.py

```python
from invoke import Collection, task
from invocations.docs import docs, www, sites, watch_docs
from invocations.pytest import test, coverage
from invocations import checks
from invocations.console import confirm
import os

@task
def docs_serve(c, port=8000):
    """本地预览文档（Python http.server）"""
    target = docs.configuration()["sphinx"]["target"]
    with c.cd(target):
        c.run(f"python -m http.server {port}")

ns = Collection(
    docs, www, sites, watch_docs, docs_serve,
    test, coverage, checks,
)

ns.configure({
    "sphinx": {
        "source": "sites/docs",  # 默认 docs 源
        "target": "sites/docs/_build",
        "target_file": "index.html",
    },
    "packaging": {
        "package": "myproject",
        "wheel": True,
    },
    "blacken": {
        "folders": ["myproject", "tests"],
    },
})
```

## 注意事项

- 两个站点的 `conf.py` 中建议配置 intersphinx 以实现交叉引用
- `sites` 任务需要两个站点都能成功构建（第一轮静默失败不会显示错误）
- `watch_docs` 依赖 watchdog 库（`pip install watchdog`）
- 监控模式使用 `r".*/\..*\.swp"` 忽略 vim 临时文件
- 多站点模式下每个站点有独立的 `_build/` 目录

## 相关概念

- [Sphinx 文档管理](/concepts/04-docs-sphinx.md)
- [工具函数与文件监控](/concepts/07-utilities-watchers.md)
- [组合模式：组装自己的任务集合](/concepts/10-composition-patterns.md)

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
