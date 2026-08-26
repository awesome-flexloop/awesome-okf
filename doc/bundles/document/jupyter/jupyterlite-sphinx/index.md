---
okf_version: v0.2
title: JupyterLite-Sphinx Bundle
description: >
  jupyterlite-sphinx 0.23.0 源码学习教程——在 Sphinx 文档中嵌入 JupyterLite 的扩展库。
  基于源码事实生成，无虚构 API，提供从安装到深度定制的完整学习路径。
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T20:00:00+08:00
tags:
  - sphinx-extension
  - jupyterlite
  - documentation
  - interactive
stale_after: 2027-02-22
---

# jupyterlite-sphinx

> 版本：0.23.0 | Python ≥3.10 | Sphinx ≥4

**jupyterlite-sphinx** 是一个 Sphinx 扩展，用于在文档网站中嵌入 JupyterLite——一个完全在浏览器中运行的 Jupyter 环境，无需服务器端计算。通过五个 RST 指令（`jupyterlite`、`notebooklite`、`replite`、`voici`、`try_examples`），文档作者可以嵌入交互式 Notebook、REPL 控制台、Voici 仪表板，并为代码示例添加"Try It Live"交互按钮。

## 快速导航

- 🚀 **快速开始**：[快速上手](concepts/02-quick-start.md)
- 📖 **概念文档**：[Concepts 总览](concepts/index.md)
- 💡 **示例代码**：[Examples 总览](examples/index.md)
- 🔍 **源码参考**：[References 总览](references/index.md)
- ⚙️ **配置选项**：[配置参考](concepts/09-configuration.md)

## 学习路径

### 入门篇（30分钟掌握）
1. [介绍](concepts/00-introduction.md) — 什么是 jupyterlite-sphinx，核心功能概览
2. [安装](concepts/01-installation.md) — pip 安装和 conf.py 基础配置
3. [快速上手](concepts/02-quick-start.md) — 5分钟在文档中嵌入 JupyterLab
4. [指令总览](concepts/03-directive-overview.md) — 五个指令对比和通用选项

### 核心篇（1小时深入）
5. [jupyterlite 指令](concepts/04-jupyterlite-directive.md) — 嵌入完整 JupyterLab
6. [notebooklite 指令](concepts/05-notebooklite-directive.md) — 嵌入经典 Notebook
7. [replite 指令](concepts/06-replite-directive.md) — 嵌入交互式 REPL
8. [voici 指令](concepts/07-voici-directive.md) — 嵌入 Voici 仪表板
9. [try_examples 指令](concepts/08-try-examples-directive.md) — 交互式文档示例
10. [配置参考](concepts/09-configuration.md) — 所有 conf.py 选项详解

### 高级篇（深度理解）
11. [构建流程详解](concepts/10-build-process.md) — Sphinx 钩子和 jupyter lite build 流程
12. [节点类层次](concepts/11-node-hierarchy.md) — docutils 自定义节点继承体系
13. [前端 JS 交互](concepts/12-frontend-js.md) — 懒加载、移动端检测、运行时配置

## 核心能力

| 指令 | 嵌入内容 | 典型场景 |
|------|---------|---------|
| `.. jupyterlite::` | JupyterLab 完整界面 | 交互式教程、演示环境 |
| `.. notebooklite::` | 经典 Notebook 界面 | 打开指定 Notebook |
| `.. replite::` | 交互式 REPL 控制台 | 代码片段即时运行 |
| `.. voici::` | Voici 静态仪表板 | 数据可视化展示 |
| `.. try_examples::` | doctest 转交互式 Notebook | API 文档示例自动交互化 |

## 依赖关系

- **核心依赖**：sphinx≥4、jupyterlite-core≥0.2,<0.9
- **可选依赖**：jupytext（Markdown Notebook 支持）、voici（仪表板渲染）
- **建议搭配**：sphinx.ext.autodoc + numpydoc/napoleon（自动为 docstring 示例添加交互）

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
facts
insights
log
```
