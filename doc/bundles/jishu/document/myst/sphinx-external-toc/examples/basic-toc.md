---
type: Example
title: 基础 _toc.yml 示例
description: 多种场景的 _toc.yml 完整示例——小型项目、多章节书籍、Jupyter Book 格式、含外部链接和glob
tags: [sphinx, sphinx-extension, toctree, example, yaml, configuration, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-source
    resource: /references/etoc-source.md
    title: sphinx-external-toc 源码路径映射
---

# 基础 _toc.yml 示例

本文档提供从简单到复杂的 `_toc.yml` 配置示例，覆盖常见使用场景。

## 示例1：最小项目

3个页面的简单文档：

```yaml
# _toc.yml
root: index
entries:
  - file: install
  - file: usage
```

对应目录结构：

```
docs/
├── _toc.yml
├── conf.py
├── index.rst
├── install.rst
└── usage.rst
```

conf.py 最小配置：

```python
# conf.py
project = 'My Project'
extensions = ['sphinx_external_toc']
exclude_patterns = ['_build']
```

## 示例2：带 Caption 和选项

带分组标题和最大深度控制：

```yaml
# _toc.yml
root: index
options:
  caption: 目录
  maxdepth: 2
entries:
  - file: intro
  - file: install
  - file: usage
    entries:
      - file: usage/basic
      - file: usage/advanced
```

## 示例3：多 Subtree（多分组导航）

侧边栏显示多个分组：

```yaml
# _toc.yml
root: index
subtrees:
  - caption: 📖 入门
    titlesonly: true
    entries:
      - file: intro
      - file: install
      - file: quickstart
  - caption: 📚 用户指南
    titlesonly: true
    entries:
      - file: guide/basics
      - file: guide/advanced
      - file: guide/faq
  - caption: 🔧 API 参考
    hidden: true
    entries:
      - file: api/core
      - file: api/utils
  - caption: 🔗 链接
    entries:
      - url: https://github.com/your/repo
        title: GitHub
      - url: https://pypi.org/project/your-package
        title: PyPI
```

## 示例4：带章节编号

罗马数字编号的多部分书籍：

```yaml
# _toc.yml
root: index
defaults:
  numbered: true
  titlesonly: true
subtrees:
  - caption: 第一部分：基础
    style: romanupper
    restart_numbering: true
    entries:
      - file: part1/intro
      - file: part1/concepts
  - caption: 第二部分：进阶
    style: romanupper
    restart_numbering: true
    entries:
      - file: part2/patterns
      - file: part2/best-practices
  - caption: 附录
    numbered: false
    entries:
      - file: appendix/changelog
      - file: appendix/acknowledgements
```

## 示例5：使用 Glob 自动匹配

自动包含目录中的所有文档：

```yaml
# _toc.yml
root: index
subtrees:
  - caption: 博客文章
    reversed: true
    entries:
      - file: blog/index
      - glob: blog/posts/*
  - caption: 文档
    entries:
      - file: docs/readme
      - glob: docs/**/*
```

注意：glob 按文件名字母顺序匹配，`reversed: true` 可以反转顺序（适用于日期命名的文章如 `2024-01-01-post.md`）。

## 示例6：Jupyter Book 格式（jb-book）

书籍格式，使用 parts/chapters/sections 层级：

```yaml
# _toc.yml
format: jb-book
root: intro
parts:
  - caption: 开始学习
    chapters:
    - file: start/overview
    - file: start/install
    - file: start/quickstart
  - caption: 核心教程
    chapters:
    - file: tutorials/basics
      sections:
      - file: tutorials/basics/setup
      - file: tutorials/basics/first-steps
    - file: tutorials/intermediate
      sections:
      - file: tutorials/intermediate/configuration
      - file: tutorials/intermediate/customization
  - caption: 参考
    chapters:
    - file: reference/api
    - file: reference/cli
    - url: https://github.com/your/repo
      title: GitHub
```

## 示例7：Jupyter Article 格式（jb-article）

单篇文章格式：

```yaml
# _toc.yml
format: jb-article
root: index
sections:
- file: intro
- file: background
- file: methods
  sections:
  - file: methods/data
  - file: methods/analysis
- file: results
- file: discussion
- file: conclusion
```

## 示例8：完整项目 conf.py

```python
# conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'My Python Package'
copyright = '2024, Your Name'
author = 'Your Name'
release = '2.0.0'
version = '2.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_external_toc',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'zh_CN'

# -- sphinx-external-toc 配置
external_toc_path = "_toc.yml"
external_toc_exclude_missing = True  # 自动排除不在ToC中的文件

# HTML 输出
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
```

## 项目目录结构

```
my-project/
├── docs/
│   ├── _toc.yml              # 导航定义
│   ├── conf.py               # Sphinx配置
│   ├── index.rst             # 根文档
│   ├── intro.rst
│   ├── install.rst
│   ├── guide/
│   │   ├── basics.rst
│   │   └── advanced.rst
│   └── api/
│       ├── core.rst
│       └── utils.rst
├── mypackage/
│   └── __init__.py
└── pyproject.toml
```

## 文档中使用 tableofcontents

在需要显示子文档列表的位置（通常是 index 文档），添加 `.. tableofcontents::` 指令：

```rst
.. index.rst

欢迎使用 My Package
====================

这是项目介绍...

.. tableofcontents::
```

如果不在任何文档中添加 `.. tableofcontents::`，toctree 节点会自动追加到每个有子文档的文档末尾。

## 验证 ToC 语法

使用 CLI 工具验证 `_toc.yml` 语法是否正确：

```bash
# 解析并输出JSON（有错误会显示）
sphinx-etoc parse _toc.yml

# 从ToC生成缺失的文档文件
sphinx-etoc to-project _toc.yml -e rst
```

## 常见问题

**Q: 如何让某些文档出现在侧边栏但不出现在正文目录中？**

A: 使用 `hidden: true` 选项：

```yaml
subtrees:
  - hidden: true
    entries:
      - file: internal/notes  # 仅侧边栏，正文不显示
```

**Q: 如何给文档自定义导航标题？**

A: 在 file 条目中添加 `title` 字段：

```yaml
- file: path/to/doc
  title: 自定义标题
```

**Q: glob 匹配的文档顺序不对？**

A: glob 按文件名字母顺序排序。可以通过文件命名控制顺序（如 `01-intro.md`、`02-install.md`），或在文件名前加数字前缀。

## 相关概念

- [_toc.yml 语法详解](../concepts/02-toc-yaml-syntax.md)
- [高级功能](../concepts/04-advanced-features.md)
- [快速开始](../concepts/01-getting-started.md)
