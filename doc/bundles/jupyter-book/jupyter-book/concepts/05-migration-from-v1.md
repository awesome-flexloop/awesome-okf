---
type: concept
title: "从 v1 迁移"
description: "Jupyter Book v1 到 v2 的主要变化、配置迁移、命令差异和迁移策略"
tags: [jupyter-book, migration, v1, sphinx, upgrade]
generated: 2026-08-23
verified: false
status: exploratory
stale_after: 2027-06-30
sources:
  - path: "ts/index.ts"
    facts: [F-011]
  - path: "py/jupyter_book/__main__.py"
    facts: [F-001, F-002]
---

# 从 v1 迁移

Jupyter Book v2 是对 v1 的彻底重构，底层从 Sphinx 切换到 myst-cli。这意味着 v1 的配置文件、命令和扩展在 v2 中大多不再兼容。本文档概述主要变化和迁移策略。

> **注意**：本文档基于 v2 源码架构分析，具体迁移工具和兼容层可能随版本变化，请参考官方迁移指南获取最新信息。

## 架构变化总结

| 方面 | Jupyter Book v1 | Jupyter Book v2 |
|------|----------------|----------------|
| 构建引擎 | Sphinx (Python) | myst-cli (TypeScript) |
| Markdown 解析 | MyST-Parser (Python) | myst-parser (TypeScript/micromark) |
| 配置文件 | `_config.yml` + `_toc.yml` | `myst.yml` |
| CLI 框架 | click (Python) | commander (TypeScript) |
| 目录结构 | `_build/` (Sphinx 输出) | `_build/` (myst-cli 输出) |
| PDF 导出 | LaTeX via Sphinx | myst-to-tex + jtex + latexmk |
| HTML 导出 | Sphinx HTML 主题 | myst-to-html + myst-theme |
| 扩展机制 | Sphinx extensions | MyST directives/roles + plugins |
| 执行代码 | jupyter-sphinx / nbclient | myst-execute 内置 |
| Python 依赖 | Sphinx + 多个 Sphinx 扩展 | 仅 nodeenv（自动管理 Node.js） |

## 配置文件迁移

### v1: _config.yml

```yaml
# _config.yml (v1)
title: My Book
author: The Jupyter Book Community
logo: logo.png

execute:
  execute_notebooks: force

latex:
  latex_documents:
    targetname: book.tex

html:
  use_repository_button: true
  repository_url: https://github.com/executablebooks/jupyter-book
```

### v2: myst.yml

```yaml
# myst.yml (v2)
version: 1
project:
  title: My Book
  author: The Jupyter Book Community
  keywords: []
  github: https://github.com/executablebooks/jupyter-book
  # bibliography: references.bib

site:
  template: book-theme
  # options:
  #   logo: logo.png

build:
  exports:
    - format: pdf
      template: default
    - format: html
  execute:
    execute_notebooks: true  # 或 false / "auto"
```

### 关键配置映射

| v1 (_config.yml) | v2 (myst.yml) | 说明 |
|-----------------|---------------|------|
| `title` | `project.title` | 标题 |
| `author` | `project.author` | 作者 |
| `logo` | `site.options.logo` | Logo |
| `execute.execute_notebooks` | `build.execute.execute_notebooks` | 代码执行 |
| `repository_url` | `project.github` | 仓库链接 |
| `latex.*` | `build.exports` (format: pdf) | LaTeX/PDF 配置通过模板选项 |
| `html.*` | `site.options` | HTML 主题配置 |
| `sphinx.config` | 不适用 | v2 没有 Sphinx，需要转换 |
| `parse.*` | 内置（默认启用） | MyST 语法默认全部启用 |
| `bibtex_bibfiles` | `project.bibliography` | 参考文献文件 |

### TOC 迁移

v1 的 `_toc.yml` 使用自定义格式：

```yaml
# _toc.yml (v1)
format: jb-book
root: intro
chapters:
- file: markdown
- file: content
  sections:
  - file: content/citations
```

v2 的 TOC 直接在 myst.yml 中定义或使用自动生成：

```yaml
# myst.yml (v2)
project:
  toc:
    - file: intro
    - file: markdown
      children:
        - file: content/citations
```

或使用 `--write-toc` 选项自动从文件结构生成。

## 命令差异

| v1 命令 | v2 命令 | 说明 |
|---------|---------|------|
| `jupyter-book create mybook` | `jupyter-book init mybook` | 初始化项目 |
| `jupyter-book build mybook` | `jupyter-book build mybook` | 构建（命令名不变，底层完全不同）|
| `jupyter-book build mybook --builder pdfhtml` | `jupyter-book build mybook --pdf` | PDF 导出 |
| `jupyter-book build mybook --builder latex` | `jupyter-book build mybook --tex` | 仅生成 LaTeX |
| `jupyter-book clean mybook` | `jupyter-book clean mybook` | 清理 |
| 无 | `jupyter-book start` | 开发服务器（v2 新增）|
| 无 | `jupyter-book templates list/download` | 模板管理（v2 新增）|

### 启动开发服务器（v2 新增）

v2 的 `jupyter-book start` 是一个强大的新功能：
- 启动本地 HTTP 服务器（默认端口 3000）
- 文件变化时自动重新构建
- 浏览器实时预览
- 支持交叉引用解析
- 这在 v1 中需要 `sphinx-autobuild`，v2 内置支持

## 内容兼容性

### 大多数 MyST Markdown 语法兼容

v1 和 v2 都使用 MyST Markdown，核心语法（标题/段落/列表/链接/图片/代码块/数学/表格）完全兼容。大多数 v1 的 `.md` 文件在 v2 中可以直接使用。

### 指令（Directives）

| v1 指令 | v2 状态 | 说明 |
|--------|--------|------|
| `{note}`/`{warning}`/`{admonition}` | ✅ 兼容 | 提示框 |
| `{figure}` | ✅ 兼容 | 图片 |
| `{table}` | ✅ 兼容 | 表格 |
| `{code-cell}` | ✅ 兼容 | 代码单元格 |
| `{toctree}` | ❌ 不支持 | v2 不使用 Sphinx toctree |
| `{eval-rst}` | ❌ 不支持 | v2 不支持 reStructuredText |
| `{glue}` | 需检查 | 变量替换，方式不同 |
| `{cite}` | ✅ 兼容 | 引用（语法可能略有差异）|
| `{math}` | ✅ 兼容 | 数学公式 |

### 角色（Roles）

| v1 角色 | v2 状态 |
|--------|--------|
| `{doc}` | ✅ 兼容 |
| `{ref}` | ✅ 兼容 |
| `{eq}` | ✅ 兼容 |
| `{numref}` | ✅ 兼容 |
| `{cite}` | ✅ 兼容 |
| `{download}` | 需检查 |

## Sphinx 扩展不兼容

v1 依赖 Sphinx 扩展生态，v2 不支持 Sphinx 扩展。常见的扩展替代方案：

| v1 Sphinx 扩展 | v2 替代方案 |
|---------------|-----------|
| `sphinxcontrib-bibtex` | 内置 bibliography 支持 |
| `sphinx-proof` | 内置 proof/定理环境 |
| `sphinx-togglebutton` | 内置（使用 details HTML 元素）|
| `sphinx-copybutton` | 内置（代码块复制按钮）|
| `sphinx-exercise` | myst-exercise 插件 |
| `nbsphinx` | 内置笔记本执行 |
| `myst_nb` | 内置（myst-execute）|
| `ablog` | myst-blog 插件 |
| 自定义 Sphinx 扩展 | 需要重写为 MyST 插件 |

## HTML 主题

v1 使用 Sphinx 主题（`sphinx-book-theme` 等），v2 使用 myst-theme 或自定义站点模板：

```yaml
# v2 myst.yml
site:
  template: book-theme  # myst 提供的书籍主题
  # 或自定义主题路径
  # template: ./my-custom-theme
```

myst-theme 提供了现代化的响应式设计，支持深色模式、侧边栏导航、搜索等功能。

## PDF 导出变化

v1 的 PDF 导出路径：
- `--builder pdfhtml`：HTML→PDF（通过 Chrome/Print）
- `--builder latex`：LaTeX→PDF（通过 Sphinx LaTeX builder）

v2 的 PDF 导出路径：
- `--pdf`：自动选择 LaTeX 路径（myst-to-tex + jtex 模板 + latexmk）
- `--typst`：Typst 路径（新功能，编译更快）
- 支持多种 LaTeX 模板（arXiv、IEEE 等）
- 模板可自定义下载

## 迁移策略

### 渐进式迁移

1. **安装 v2**：`pip install jupyter-book>=2.0`
2. **备份配置**：备份 `_config.yml` 和 `_toc.yml`
3. **运行 init**：`jupyter-book init` 在现有项目目录运行，生成 myst.yml
4. **手动调整配置**：将 `_config.yml` 中的设置映射到 myst.yml
5. **测试构建**：`jupyter-book build .` 检查输出
6. **逐个修复问题**：遇到不兼容的指令/角色时逐个处理
7. **删除旧配置**：确认一切正常后删除 `_config.yml` 和 `_toc.yml`

### 并行运行

如果需要过渡，可以在同一个项目中同时保留 v1 和 v2 的配置文件（`_config.yml` + `myst.yml`），但通常建议一次性迁移。

### 常见问题

1. **`{eval-rst}` 指令**：将 reST 语法转换为 MyST 语法
2. **自定义 CSS/JS**：v2 通过 `site.options.assets` 配置自定义静态资源
3. **intersphinx**：v2 通过 `project.references` 配置跨项目引用
4. **多语言**：检查 v2 是否支持所需的 LaTeX/Typst 语言配置
5. **发布到 GitHub Pages**：使用 `--gh-pages` 选项自动配置

## 相关概念

- [00-v2-architecture](/concepts/00-v2-architecture.md)：v2 双层架构
- [03-myst-cli-relationship](/concepts/03-myst-cli-relationship.md)：与 myst-cli 的关系
- [02-build-publish](/examples/02-build-publish.md)：构建与发布示例
