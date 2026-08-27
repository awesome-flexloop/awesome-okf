---
type: Concept
title: _toc.yml 语法详解
description: _toc.yml 文件的完整语法——三种格式（default/jb-book/jb-article）、条目类型、选项配置、shorthand 语法
tags: [sphinx, sphinx-extension, toctree, yaml, syntax, jupyter-book, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-source
    resource: /references/etoc-source.md
    title: sphinx-external-toc 源码路径映射
---

# _toc.yml 语法详解

`_toc.yml` 是 sphinx-external-toc 的核心配置文件，定义整个文档站点的导航结构。本文档详细介绍其完整语法。

## 文件格式概述

sphinx-external-toc 支持三种文件格式，通过顶层 `format` 键指定：

| 格式 | format 值 | 键名结构 | 适用场景 |
|------|----------|---------|---------|
| 默认格式 | 不指定或 `default` | `subtrees` / `entries` | 通用 Sphinx 项目 |
| Jupyter Book 书籍 | `jb-book` | `parts` / `chapters` / `sections` | 多章节书籍式文档 |
| Jupyter Book 文章 | `jb-article` | `sections` | 单篇文章式文档 |

三种格式在数据模型层面是等价的，只是键名不同，最终都解析为相同的 `SiteMap` 结构。

## 默认格式（default）

默认格式使用 `subtrees` 和 `entries` 作为键名，是最通用的格式。

### 基本结构

```yaml
root: <根文档名>
defaults:
  <全局默认选项>
subtrees:
  - caption: <子树标题>
    <toctree选项>
    entries:
      - file: <文档路径>
      - file: <文档路径>
        entries:
          - file: <子文档路径>
      - glob: <glob模式>
      - url: <外部URL>
        title: <链接标题>
```

### 顶层键

| 键 | 必需 | 说明 |
|----|------|------|
| `root` | 是 | 根文档名（POSIX 路径，不带扩展名） |
| `format` | 否 | 文件格式：`default`、`jb-book`、`jb-article` |
| `defaults` | 否 | 所有 toctree 的默认选项 |
| `meta` | 否 | 元数据字典（不影响导航） |
| `subtrees` | 是 | 子树列表（根文档的 toctree） |

### 条目类型（entries 中的项）

每个条目必须且只能包含 `file`、`glob`、`url` 三者之一。

#### file 条目——引用文档

```yaml
- file: path/to/document
  title: 可选标题（覆盖文档标题）
```

- 路径使用 POSIX 格式（`/` 分隔），相对于源目录
- 可带或不带文件扩展名（`.rst`/`.md`）
- `title` 可选，覆盖文档自身的标题
- file 条目可以包含 `entries` 定义子文档（嵌套 toctree）

#### glob 条目——模式匹配

```yaml
- glob: pattern/*
```

- 使用 Sphinx 的标准 glob 模式匹配多个文档
- 匹配的文档按字母顺序排列
- glob 条目不能包含子 entries

#### url 条目——外部链接

```yaml
- url: https://example.com
  title: 示例网站
```

- `title` 是可选项但推荐设置，否则链接文本为 URL 本身
- url 条目不能包含子 entries

### Shorthand 语法（单 subtree 简写）

如果文档只有一个 subtree（大多数情况），可以省略 `subtrees` 包裹，直接使用 `entries`：

```yaml
root: index
entries:
  - file: doc1
  - file: doc2
  - file: doc3
```

这等价于：

```yaml
root: index
subtrees:
  - entries:
      - file: doc1
      - file: doc2
      - file: doc3
```

使用 shorthand 时，toctree 选项放入 `options` 键：

```yaml
root: index
options:
  caption: 目录
  maxdepth: 2
entries:
  - file: doc1
  - file: doc2
```

### TocTree 选项

每个 subtree（或 shorthand 的 `options`）支持以下选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `caption` | str | None | toctree 标题（显示在导航中） |
| `hidden` | bool | True | 是否在文档正文中隐藏 toctree（注意默认值为 True，与 Sphinx 默认不同） |
| `maxdepth` | int | -1 | 最大导航深度（-1 表示无限制） |
| `numbered` | bool/int | False | 是否编号章节（True/False 或最大编号深度） |
| `reversed` | bool | False | 是否反转条目顺序（对 glob 有用） |
| `titlesonly` | bool | False | 只显示文档标题，不显示子章节标题 |
| `style` | str/List[str] | `"numerical"` | 编号样式 |
| `restart_numbering` | bool | None | 是否重置编号计数器 |

### defaults——全局默认选项

`defaults` 键为所有 toctree 设置默认选项：

```yaml
root: index
defaults:
  titlesonly: true
  numbered: true
subtrees:
  - caption: 第一部分
    entries:
      - file: chapter1
  - caption: 第二部分
    entries:
      - file: chapter2
```

## Jupyter Book 格式（jb-book）

`jb-book` 格式使用更语义化的键名，适合书籍式文档：

```yaml
format: jb-book
root: index
parts:
  - caption: 第一部分
    chapters:
      - file: chapter1
      - file: chapter2
        sections:
          - file: chapter2a
          - file: chapter2b
  - caption: 第二部分
    chapters:
      - file: chapter3
```

键名映射：
- 第0层（根级别）：`parts`（对应 default 的 `subtrees`）
- 第1层（part 内）：`chapters`（对应 default 的 `entries`）
- 第2层及以下：`sections`（对应 default 的 `entries`）

jb-book 格式默认 `titlesonly: true`。

## Jupyter Book 文章格式（jb-article）

`jb-article` 格式更简单，适合单篇长文：

```yaml
format: jb-article
root: index
sections:
  - file: intro
  - file: methods
  - file: results
```

- 不使用 `parts`/`chapters` 层级
- 直接在根文档下使用 `sections` 定义章节
- 默认 `titlesonly: true`

## 嵌套结构深度

YAML 支持任意深度的嵌套。每个 `file` 条目可以包含 `entries`（或 `sections`，取决于格式和深度）来定义子文档：

```yaml
root: index
subtrees:
  - entries:
      - file: part1
        entries:
          - file: chapter1
            entries:
              - file: section1-1
              - file: section1-2
          - file: chapter2
      - file: part2
```

对应文档层级：

```
index
├── part1
│   ├── chapter1
│   │   ├── section1-1
│   │   └── section1-2
│   └── chapter2
└── part2
```

## 多 Subtree（多 toctree）

一个文档可以包含多个 toctree，对应侧边栏中的多个分组：

```yaml
root: index
subtrees:
  - caption: 用户指南
    entries:
      - file: install
      - file: usage
  - caption: API 参考
    entries:
      - file: api
  - caption: 外部链接
    entries:
      - url: https://github.com/your/repo
        title: GitHub
```

## 文档中使用 tableofcontents 指令

在文档正文中，使用 `.. tableofcontents::` 指令标记 toctree 渲染位置：

```rst
欢迎使用我的项目
================

这里是介绍文字...

.. tableofcontents::

更多内容...
```

如果不使用此指令，toctree 节点会自动追加到文档的最后一个 section 末尾。

## 相关概念

- [快速开始](01-getting-started.md)
- [扩展工作机制](03-extension-mechanism.md)
- [高级功能](04-advanced-features.md)
- [基础 _toc.yml 示例](../examples/basic-toc.md)
