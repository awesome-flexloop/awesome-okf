---
type: Concept
title: 高级功能
description: sphinx-external-toc 的进阶用法——章节编号样式、glob 模式匹配、外部链接、CLI 工具、与 Jupyter Book 集成
tags: [sphinx, sphinx-extension, toctree, advanced, numbering, glob, cli, jupyter-book, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-source
    resource: /references/etoc-source.md
    title: sphinx-external-toc 源码路径映射
---

# 高级功能

本文档介绍 sphinx-external-toc 的高级功能：编号样式、glob 模式、外部链接、CLI 工具等。

## 章节编号样式

sphinx-external-toc 扩展了 Sphinx 原生的章节编号功能，支持多种编号样式。

### 启用编号

在 toctree 选项中设置 `numbered: true` 启用编号：

```yaml
root: index
subtrees:
  - numbered: true
    entries:
      - file: chapter1
      - file: chapter2
```

或使用 `defaults` 全局启用：

```yaml
root: index
defaults:
  numbered: true
subtrees:
  - entries:
      - file: chapter1
      - file: chapter2
```

`numbered` 也可以设为整数，表示最大编号深度：

```yaml
numbered: 2  # 只编号到2级标题
```

### 编号样式

通过 `style` 选项设置编号样式：

```yaml
root: index
subtrees:
  - numbered: true
    style: romanupper
    entries:
      - file: chapter1
      - file: chapter2
```

支持的样式：

| style | 效果 |
|-------|------|
| `numerical`（默认） | 1, 2, 3... |
| `romanupper` | I, II, III... |
| `romanlower` | i, ii, iii... |
| `alphaupper` | A, B, C... |
| `alphalower` | a, b, c... |

### 多级编号样式

`style` 可以是列表，为不同层级指定不同样式：

```yaml
style: [numerical, alphabetalower, romanlower]
```

这会产生类似 "1.a.i" 的多级编号。

### 重置编号

默认情况下（`use_multitoc_numbering: true`），多个 toctree 之间编号连续递增。设置 `restart_numbering: true` 让每个 toctree 从1重新开始：

```yaml
root: index
subtrees:
  - caption: 第一部分
    numbered: true
    restart_numbering: true
    entries:
      - file: part1/chapter1
      - file: part1/chapter2
  - caption: 第二部分
    numbered: true
    restart_numbering: true  # 从 1 重新开始
    entries:
      - file: part2/chapter3
```

也可以在 `conf.py` 中全局禁用连续编号：

```python
use_multitoc_numbering = False
```

## Glob 模式匹配

使用 `glob` 条目可以按模式匹配多个文档，无需逐个列出：

```yaml
root: index
subtrees:
  - entries:
      - file: intro
      - glob: chapters/*
      - file: appendix
```

`chapters/*` 会匹配 `chapters/` 目录下的所有文档文件，按文件名字母顺序排列。

### 反转顺序

使用 `reversed: true` 反转 glob 匹配的文档顺序（对按日期命名的博客文章等有用）：

```yaml
subtrees:
  - reversed: true
    entries:
      - glob: posts/*
```

### Glob 模式语法

Sphinx glob 使用标准 fnmatch 模式：

| 模式 | 匹配 |
|------|------|
| `*` | 单层目录内的任意文件 |
| `**` | 递归匹配子目录 |
| `?` | 单个字符 |
| `[seq]` | 字符集中的任意字符 |

注意：glob 条目不能包含子 entries（即不能嵌套）。

## 外部链接

使用 `url` 条目添加外部链接到导航栏：

```yaml
root: index
subtrees:
  - caption: 文档
    entries:
      - file: install
      - file: usage
  - caption: 链接
    entries:
      - url: https://github.com/your/repo
        title: GitHub
      - url: https://example.com
        title: 项目官网
```

外部链接在导航中显示为普通链接项，但不会作为文档构建。`title` 字段是推荐设置的，否则显示完整 URL。

## 多 TocTree 与 captions

一个文档可以包含多个 toctree，每个有独立的 caption 和选项：

```yaml
root: index
subtrees:
  - caption: 📖 用户指南
    titlesonly: true
    entries:
      - file: guide/install
      - file: guide/usage
  - caption: 🔧 API 参考
    hidden: true  # 不显示在正文中，只在侧边栏
    entries:
      - file: api/core
      - file: api/utils
  - caption: 🌐 外部资源
    entries:
      - url: https://github.com/your/repo
        title: GitHub
```

每个 subtree 对应一个独立的 `toctree` 节点，可以有不同的 caption、numbered、hidden 等设置。

## titlesonly 选项

`titlesonly: true` 让 toctree 只显示文档标题，不显示文档内的子章节标题。这在顶层导航中很常见，避免侧边栏过于冗长：

```yaml
defaults:
  titlesonly: true
```

## maxdepth 选项

控制导航树展开的最大深度：

```yaml
subtrees:
  - maxdepth: 2  # 只显示到2级
    entries:
      - file: chapter1
```

- `-1`（默认）：无限制，显示所有层级
- `1`：只显示顶级文档
- `2`：显示顶级+一级子文档
- 以此类推

## CLI 工具

sphinx-external-toc 提供命令行工具辅助开发。

### 解析验证 ToC 文件

```bash
# 解析 _toc.yml 并输出 JSON 格式的 sitemap
sphinx-etoc parse _toc.yml
```

输出包含 `root`、`documents`、`meta` 等字段的 JSON，可以验证 YAML 语法是否正确。

### 从 ToC 生成项目骨架

```bash
# 根据 _toc.yml 创建缺失的文档文件
sphinx-etoc to-project _toc.yml -e rst -p docs -o
```

选项：
- `-e, --extension`：文件扩展名（rst 或 md，默认 rst）
- `-p, --path`：目标目录（默认为 ToC 文件所在目录）
- `-o, --overwrite`：覆盖已存在的文件

### CLI 入口点

CLI 入口可能因安装方式不同而不同：

```bash
# 标准入口
sphinx-etoc --help
sphinx-external-toc --help

# Python 模块方式
python -m sphinx_external_toc.cli --help
```

## 与 Jupyter Book 集成

sphinx-external-toc 是 Jupyter Book 的核心组件。Jupyter Book 使用 `jb-book` 或 `jb-article` 格式：

### jb-book 格式

```yaml
format: jb-book
root: intro
parts:
  - caption: Get started
    chapters:
    - file: start/overview
    - file: start/install
  - caption: Guides
    chapters:
    - file: guides/01
      sections:
      - file: guides/01-1
      - file: guides/01-2
```

### jb-article 格式

```yaml
format: jb-article
root: index
sections:
- file: intro
- file: methods
- file: results
```

在 Jupyter Book 项目中，`_toc.yml` 由 Jupyter Book CLI 管理，用户通常不需要直接配置 Sphinx 扩展——Jupyter Book 会自动启用 sphinx-external-toc。

## 自动排除未引用文件

设置 `external_toc_exclude_missing = True` 可以自动将不在 `_toc.yml` 中的文档排除在构建之外：

```python
# conf.py
external_toc_exclude_missing = True
```

这确保只有 ToC 中引用的文件才会被构建，避免草稿文件或孤立页面意外出现在文档中。

实现机制：在 `config-inited` 时递归扫描源目录所有文档文件，对比 SiteMap 中的文档列表，将不在 SiteMap 中且不匹配任何 glob 模式的文件追加到 `exclude_patterns`。

## 相关概念

- [_toc.yml 语法详解](02-toc-yaml-syntax.md)
- [扩展工作机制](03-extension-mechanism.md)
- [基础 _toc.yml 示例](../examples/basic-toc.md)
