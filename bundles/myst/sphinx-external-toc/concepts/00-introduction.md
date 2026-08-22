---
type: Concept
title: sphinx-external-toc 简介
description: sphinx-external-toc 是什么——用单一 _toc.yml 文件定义 Sphinx 站点导航结构，替代分散在各文档中的 toctree 指令
tags: [sphinx, sphinx-extension, toctree, navigation, introduction, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-source
    resource: /references/etoc-source.md
    title: sphinx-external-toc 源码路径映射
---

# sphinx-external-toc 简介

sphinx-external-toc 是 [Executable Book Project](https://executablebooks.org/) 开发的 Sphinx 扩展，允许在项目根目录的单一 `_toc.yml` 文件中定义整个站点的导航结构（目录树/toctree），替代 Sphinx 原生的"每个文档中使用 `.. toctree::` 指令声明子文档"的分散式导航定义方式。它是 Jupyter Book 的核心导航组件。

## 核心问题与定位

Sphinx 原生的 toctree 机制采用**分布式定义**——每个文档通过 `.. toctree::` 指令声明它包含哪些子文档：

```rst
.. toctree::
   :maxdepth: 2

   install
   usage
   api
```

这种方式对于小型文档很自然，但对于大型文档站点存在以下问题：

- **导航结构分散**：要了解站点整体结构，需要打开多个文件查看各处的 toctree 指令
- **全局调整困难**：调整文档层级关系需要修改多个文件中的 toctree
- **与 Jupyter Book 的需求不匹配**：Jupyter Book 需要"书籍式"的 parts/chapters/sections 层级结构

sphinx-external-toc 通过**集中式导航定义**解决了这些问题：所有导航关系在一个 YAML 文件中声明，文档本身只包含内容，不声明导航关系。

## 核心特点

- **集中式导航**：整个站点的目录结构定义在单一 `_toc.yml` 文件中
- **兼容 Sphinx 生态**：在文档变换阶段注入标准 `toctree` 节点，主题无需修改即可工作
- **多种格式支持**：default（subtrees/entries）、jb-book（parts/chapters/sections）、jb-article（sections）三种 YAML 格式
- **三种条目类型**：文件引用（file）、glob 模式匹配（glob）、外部 URL 链接（url）
- **编号样式扩展**：支持数字、大写/小写罗马数字、大写/小写字母等多种章节编号样式
- **自动排除**：可自动将不在 ToC 中的文件加入排除列表
- **CLI 工具**：提供命令行工具验证 ToC 文件、生成项目骨架
- **多 toctree 编号**：支持多个 toctree 间的连续编号或独立编号

## 与 Sphinx 原生 toctree 的关系

sphinx-external-toc 不是独立实现导航系统，而是**替换**了 Sphinx 内置的 toctree 收集机制：

1. 禁用内置 `TocTreeCollector`
2. 解析 `_toc.yml` 构建内存中的 `SiteMap` 对象
3. 在文档变换阶段（Transform priority=100），将标准 `toctree` 节点注入文档树
4. 自定义 `TocTreeCollectorWithStyles` 处理这些节点（包括扩展的编号样式）
5. 后续 Sphinx 流程（侧边栏、面包屑、上/下页）正常工作

这种"兼容式替换"设计确保了与所有 Sphinx 主题的兼容性。

## 适用场景

sphinx-external-toc 适合以下场景：

- **Jupyter Book 项目**：作为 Jupyter Book 的核心导航组件自动启用
- **大型文档站点**：需要全局把控导航结构的项目
- **书籍式文档**：需要 parts/chapters/sections 多级结构的文档
- **自动生成文档**：导航结构需要程序化生成或批量调整的场景

对于小型项目（几个文档页面），原生 `.. toctree::` 更简单直接，sphinx-external-toc 可能是过度工程。

## 环境要求

- Python（setup.py 中未指定最低版本，但根据依赖推断 Python 3.7+）
- Sphinx（核心依赖）
- PyYAML（解析 `_toc.yml`）
- click（CLI 工具）
- sphinx-multitoc-numbering（依赖扩展，处理多 toctree 编号）

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [_toc.yml 语法详解](/concepts/02-toc-yaml-syntax.md)
- [扩展工作机制](/concepts/03-extension-mechanism.md)
- [基础 _toc.yml 示例](/examples/basic-toc.md)
