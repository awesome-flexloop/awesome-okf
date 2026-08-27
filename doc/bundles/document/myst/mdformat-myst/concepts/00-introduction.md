---
type: Concept
title: mdformat-myst 项目介绍与安装
description: mdformat-myst 是 mdformat 的 MyST Markdown 兼容性插件，提供 MyST 语法格式化支持。
tags: [introduction, installation, myst, markdown, mdformat]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-init
    resource: /references/source-init.md
    title: mdformat-myst 插件入口模块
---

## 什么是 mdformat-myst

mdformat-myst 是 [mdformat](https://github.com/executablebooks/mdformat) 的插件，为 [MyST（Markedly Structured Text）](https://myst-parser.readthedocs.io/) Markdown 语法提供格式化支持。MyST 是 Executable Books 项目推出的一种 Markdown 扩展语法，结合了 CommonMark 的简洁性和 reStructuredText 的强大表达能力，广泛用于技术文档和学术写作。

mdformat 本身只支持标准 CommonMark 和部分 GFM（GitHub Flavored Markdown）语法。安装 mdformat-myst 插件后，mdformat 能够正确解析和格式化 MyST 特有的语法元素，包括角色（role）、指令（directive）、注释、块中断、目标锚点和数学公式。

当前版本为 0.3.0。

## 安装

### 前置条件

- Python 3.10 或更高版本
- mdformat >= 0.7.0

### 使用 pip 安装

```bash
pip install mdformat-myst
```

安装后，mdformat 会自动通过 Python 入口点（entry point）机制发现该插件，无需额外配置。

### 依赖说明

安装 mdformat-myst 会自动安装以下依赖：

| 依赖包 | 最低版本 | 作用 |
|--------|---------|------|
| mdformat | 0.7.0 | Markdown 格式化引擎 |
| mdit-py-plugins | 0.3.0 | markdown-it-py 的 MyST 语法插件 |
| mdformat-front-matters | 1.0.0 | YAML front matter 格式化支持 |
| mdformat-footnote | 0.1.1 | 脚注语法支持 |
| mdformat-gfm | 1.0.0 | GFM 表格等语法支持 |
| ruamel.yaml | 0.16.0 | YAML 格式化（用于指令选项） |

## 使用方式

安装插件后，直接使用 mdformat 命令行格式化 MyST Markdown 文件即可：

```bash
mdformat document.md
```

插件通过 entry point 自动注册，mdformat 启动时会加载名称为 `myst` 的解析器扩展。

## 支持的 MyST 语法

mdformat-myst 支持格式化以下 MyST 语法元素：

- **角色（Role）**：`{role-name}`content`` 格式
- **指令（Directive）**：围栏代码块形式的指令，选项 YAML 自动格式化
- **行注释**：`%` 开头的注释行
- **块中断**：`+++` 标记
- **目标锚点**：`(target-name)=` 格式
- **数学公式**：`$inline$` 和 `$$block$$` 格式，支持带编号的公式块

## 相关概念

- [插件架构](01-plugin-architecture.md)
- [MyST 语法支持](02-myst-syntax-support.md)
