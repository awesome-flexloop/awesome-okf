---
okf_version: "0.2"
type: bundle
title: "sphinx-external-toc — 外部目录导航"
description: "sphinx-external-toc 用单一 _toc.yml 文件定义 Sphinx 站点导航结构，支持集中式目录管理、多种编号样式和 Jupyter Book 格式"
tags: [sphinx, sphinx-extension, toctree, navigation, yaml, jupyter-book, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-repo
    resource: https://github.com/executablebooks/sphinx-external-toc
    title: sphinx-external-toc GitHub Repository
    author: team:executablebooks
  - id: etoc-docs
    resource: https://sphinx-external-toc.readthedocs.io/
    title: sphinx-external-toc Documentation
---

# sphinx-external-toc — 外部目录导航

sphinx-external-toc 是 [Executable Book Project](https://executablebooks.org/) 开发的 Sphinx 扩展，通过项目根目录的单一 `_toc.yml` 文件定义整个站点的导航结构（toctrees），替代 Sphinx 原生分散在各文档中的 `.. toctree::` 指令。它是 Jupyter Book 的核心导航组件。

> **核心特点**：集中式 YAML 导航定义、兼容所有 Sphinx 主题（注入标准 toctree 节点）、支持数字/罗马/字母等多种编号样式、三种文件格式（default/jb-book/jb-article）、glob 自动匹配。

## 知识地图

```
sphinx-external-toc/
├── 📖 concepts/       概念文档（5 篇）
│   ├── 入门：简介、快速开始
│   ├── 核心：_toc.yml语法、扩展工作机制
│   └── 进阶：编号样式、glob、CLI工具
├── 💡 examples/       实战示例（1 篇）
│   └── 基础 _toc.yml 示例（8个场景）
└── 📚 references/     信源参考（1 篇）
    └── 源码路径映射
```

## 推荐学习路径

### 20 分钟快速上手

1. [简介](concepts/00-introduction.md) → 了解定位和核心概念（5分钟）
2. [快速开始](concepts/01-getting-started.md) → 安装、创建第一个 _toc.yml（10分钟）
3. [基础 _toc.yml 示例](examples/basic-toc.md) → 复制示例配置，迁移现有项目（5分钟）

### 深入理解（30-60 分钟）

4. [_toc.yml 语法详解](concepts/02-toc-yaml-syntax.md) → 三种格式、条目类型、选项配置
5. [扩展工作机制](concepts/03-extension-mechanism.md) → Collector替换、Transform注入、执行流程
6. [高级功能](concepts/04-advanced-features.md) → 编号样式、glob、外部链接、CLI工具

## 核心洞察

| # | 洞察 | 一句话总结 |
|---|------|-----------|
| 1 | 替换而非增强 | 通过gc禁用内置Collector，替换为自定义子类实现旁路接管 |
| 2 | 集中式站点地图 | _toc.yml 解析为SiteMap对象，单一YAML管理全局导航 |
| 3 | 多格式键名映射 | FileFormat类按深度选择键名，兼容default/jb-book/jb-article |
| 4 | 兼容式Transform注入 | priority=100注入标准toctree节点，主题无需修改即可兼容 |

## 与原生 toctree 对比

| 特性 | 原生 toctree | sphinx-external-toc |
|------|-------------|---------------------|
| 定义位置 | 分散在各文档中 | 集中在 _toc.yml |
| 全局结构查看 | 需要打开多个文件 | 一个文件一目了然 |
| Jupyter Book 兼容 | 需要适配 | 原生支持 |
| 编号样式 | 仅数字 | 数字/罗马/字母 |
| 学习曲线 | Sphinx 基础 | 需要学习 YAML 语法 |
| 适合规模 | 小型项目 | 中大型文档站点 |

## 相关知识包

| 知识包 | 关系 |
|--------|------|
| [sphinx-book-theme](https://github.com/executablebooks/sphinx-book-theme) | Jupyter Book 主题——sphinx-external-toc 的主要使用场景 |
| [sphinx-copybutton](https://github.com/executablebooks/sphinx-copybutton) | 代码复制按钮——Executable Books 生态常用扩展 |
| [MyST Parser](https://github.com/executablebooks/MyST-Parser) | MyST Markdown——Executable Books 生态核心 |

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
