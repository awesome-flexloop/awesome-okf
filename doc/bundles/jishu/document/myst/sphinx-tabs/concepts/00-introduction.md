---
type: Concept
title: sphinx-tabs 简介
description: sphinx-tabs 是什么——为 Sphinx 文档提供可切换标签页组件，支持多语言代码示例、分组同步和无障碍访问
tags: [sphinx, tabs, introduction, ui-component, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:22:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# sphinx-tabs 简介

sphinx-tabs 是 Executable Books 生态中的 Sphinx 标签页组件扩展，允许在文档中创建可切换的标签页视图，最常用于展示多语言代码示例、不同操作系统的命令、或分步内容。输出符合 WAI-ARIA 无障碍标准，支持键盘导航。

## 核心功能

- **基础标签页**：通过 `.. tabs::` 和 `.. tab::` 指令创建可切换内容面板
- **分组标签同步**：`.. group-tab::` 实现跨页面标签选中状态记忆（基于 sessionStorage）
- **代码标签页**：`.. code-tab::` 专为多语言代码示例设计，自动识别 Pygments lexer
- **键盘无障碍**：左右方向键导航标签，Tab 键聚焦，符合 WAI-ARIA Tabs 模式
- **条件资源加载**：仅在使用了标签页的页面加载 CSS/JS，不增加无页面的负担
- **嵌套支持**：标签页内可嵌套标签页
- **可关闭标签**：点击已选中标签可取消选中（可配置关闭）

## 四个指令一览

| 指令 | 用途 | 典型场景 |
|------|------|---------|
| `.. tabs::` | 标签页容器 | 包裹一组 tab 指令 |
| `.. tab:: 标题` | 普通标签页 | 分步教程、选项对比 |
| `.. group-tab:: 名称` | 分组同步标签 | 多页面统一的语言/OS选择 |
| `.. code-tab:: lexer` | 代码标签页 | 多语言代码示例（Python/R/Julia） |

## 设计特点

- 核心代码仅 348 行 Python（单个文件 `tabs.py`）
- 自定义 4 种 docutils 节点，通过 `tagname` 属性映射到 HTML 标签
- 标签按钮使用原生 `<button>` 元素而非 `<div>`，获得无障碍能力
- 标签 ID 通过 `env.temp_data` 栈式管理，支持嵌套
- 前端 JS 仅约 150 行，使用 sessionStorage 实现状态持久化

## 环境要求

- Python 3
- Sphinx
- Pygments（代码标签页的 lexer 识别依赖）

## 相关概念

- [快速开始](01-getting-started.md)
- [四个指令详解](02-directives.md)
- [分组标签与代码标签](03-group-and-code-tabs.md)
