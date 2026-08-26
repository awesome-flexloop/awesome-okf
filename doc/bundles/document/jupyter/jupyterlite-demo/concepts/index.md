---
type: Index
title: 概念文档索引
description: JupyterLite Demo 概念文档目录，包含8篇从入门到进阶的概念讲解
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
---

# JupyterLite Demo 概念文档

本目录包含 JupyterLite Demo 的核心概念文档，从入门到进阶系统化讲解 JupyterLite 站点的结构、配置和定制方法。

## 文档列表

### 入门层

| 文档 | 说明 |
|------|------|
| [00-JupyterLite Demo 简介](00-introduction.md) | 是什么、核心特性、与传统 Jupyter 的区别、生态位置 |
| [01-Demo 仓库结构与三件套模式](01-demo-overview.md) | 目录结构、依赖+内容+CI 三件套模式、三层笔记本结构 |

### 核心层

| 文档 | 说明 |
|------|------|
| [02-站点配置详解](02-site-configuration.md) | jupyter-lite.json 配置文件、扩展管理、常用高级配置 |
| [03-三大内核生态对比](03-kernel-ecosystem.md) | Pyodide/JavaScript/p5 内核特性、能力边界、选择策略 |
| [04-内容目录与数据文件组织](04-content-and-data.md) | content/ 目录布局、数据文件共享、MIME 渲染器 |
| [05-Pyodide 生态库与 %pip 安装](05-pyodide-libraries.md) | %pip 工作原理、预装 vs 按需、可视化库使用模式 |

### 进阶层

| 文档 | 说明 |
|------|------|
| [06-GitHub Pages 部署流水线](06-deployment-github-pages.md) | CI/CD 工作流、构建命令参数、本地预览、其他部署方式 |
| [07-自定义 Demo 站点指南](07-customization-guide.md) | 添加内容、扩展、主题、语言包、品牌定制 |

## 推荐阅读顺序

1. 入门了解 → [00-简介](00-introduction.md) → [01-仓库结构](01-demo-overview.md)
2. 动手部署 → [从零部署](../examples/01-first-deployment.md)
3. 理解核心 → [02-站点配置](02-site-configuration.md) → [03-内核生态](03-kernel-ecosystem.md) → [05-Pyodide库](05-pyodide-libraries.md)
4. 进阶定制 → [06-部署流水线](06-deployment-github-pages.md) → [07-自定义指南](07-customization-guide.md)

```{toctree}
:maxdepth: 7

00-introduction
01-demo-overview
02-site-configuration
03-kernel-ecosystem
04-content-and-data
05-pyodide-libraries
06-deployment-github-pages
07-customization-guide
```
