---
type: Reference
title: "myst.yml 配置解析"
description: "MyST文档站点配置文件myst.yml的源码级解析：项目元数据、插件配置、目录树(TOC)、book-theme主题选项。"
tags: ["myst", "myst.yml", "配置", "TOC", "主题", "listing"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/docs/myst.yml"
    lines: "1-25"
    description: "MyST站点配置"
---

# myst.yml 配置解析

## 概述

myst.yml 是MyST Markdown文档引擎的站点配置文件，定义了项目元数据、插件、目录结构和主题选项。该文件位于`docs/`目录下，是文档站点的核心配置。

## 完整配置结构

### version：配置版本

```yaml
version: 1
```

MyST配置格式版本，当前为v1。

### project：项目元数据

```yaml
project:
  title: Jupyter Surveys
  github: https://github.com/jupyter/surveys
  license:
    code: CC0-1.0
    content: CC0-1.0
  plugins:
    - jupyterlab-myst
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `title` | Jupyter Surveys | 站点标题 |
| `github` | 仓库URL | 在页面显示GitHub链接和编辑按钮 |
| `license.code/content` | CC0-1.0 | 代码和内容均使用CC0公共领域贡献 |
| `plugins` | jupyterlab-myst | 启用JupyterLab MyST插件，支持交互式单元格 |

### site：站点配置

```yaml
site:
  domains:
    - jupyter.github.io/surveys
  options:
    logo: surveys/logo.png
    logo_text: Jupyter Surveys
  nav: []
  actions:
    - title: Learn More
      url: https://jupyter.org
```

- **domains**：配置GitHub Pages域名（`jupyter.github.io/surveys`）
- **options.logo**：站点Logo图片路径（相对于docs/目录）
- **actions**：导航栏操作按钮，链接到jupyter.org

### toc：目录树（Table of Contents）

```yaml
  toc:
    - file: index.md
    - title: Survey Datasets
      children:
        - pattern: "surveys/*/index.md"
        - pattern: "surveys/*/*/index.md"
```

| 条目 | 类型 | 说明 |
|------|------|------|
| `index.md` | file | 首页 |
| Survey Datasets | title | 数据集分组标题 |
| `surveys/*/index.md` | pattern | 一级数据集目录README（glob匹配） |
| `surveys/*/*/index.md` | pattern | 二级子目录README（glob匹配） |

**glob模式的优势**：新增数据集目录后无需手动更新TOC，自动发现新内容。

### theme：主题配置

```yaml
  template: book-theme
  options:
    show_footer: false
```

- 使用`book-theme`模板（书籍风格文档主题）
- `show_footer: false`隐藏页脚，保持页面简洁

## 关键设计模式

### Glob驱动的TOC自动发现

使用`pattern` glob模式而非显式文件列表，让文档结构随文件系统自动扩展。这是开源项目文档的常见模式——贡献者只需在正确位置添加文件，无需修改配置。

### 插件化扩展

通过`plugins`字段启用`jupyterlab-myst`，让MyST文档支持Jupyter单元格的交互式渲染。这是MyST区别于传统静态站点生成器的核心优势。

## 相关概念

- [MyST文档系统](../concepts/04-myst-docs-system.md)：MyST的完整功能介绍
- [仓库结构](../concepts/02-repository-structure.md)：docs/目录的位置与作用
- [本地构建文档](../examples/01-build-docs-locally.md)：构建站点的实战步骤
