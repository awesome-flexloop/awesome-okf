---
type: bundle
title: mdformat-footnote
description: mdformat 的脚注语法支持插件，提供脚注自动排序、格式化和孤立脚注处理功能。
okf_version: "0.2"
tags: [footnote, markdown, mdformat, formatter, plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
---

# mdformat-footnote

mdformat-footnote 是 [mdformat](https://github.com/executablebooks/mdformat) 的脚注（Pandoc 风格）语法插件，提供脚注的解析、验证、自动排序和格式化功能。

- **版本**：0.1.3（Beta）
- **Python 要求**：≥ 3.10
- **源码**：`mdformat_footnote/`

## 快速开始

```bash
pip install mdformat-footnote
mdformat document.md
```

## 核心功能

- 按引用顺序自动重排脚注编号
- 规范化脚注定义块缩进（4空格）
- 处理脚注嵌套引用
- 识别代码围栏中的脚注引用
- 自动移除未引用的孤立脚注（可配置保留）

## 文档导航

### [概念文档](/concepts/index.md)

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [项目介绍与安装](/concepts/00-introduction.md) | 安装、基本使用和脚注语法 |
| 01 | [插件配置与 CLI 选项](/concepts/01-plugin-configuration.md) | --keep-footnote-orphans 选项和配置读取机制 |
| 02 | [脚注渲染格式与缩进规则](/concepts/02-footnote-rendering.md) | 脚注引用和定义的渲染输出格式 |
| 03 | [脚注排序逻辑与分类机制](/concepts/03-footnote-reordering.md) | 四分类、依赖图、重排序和ID重分配算法 |

### [示例文档](/examples/index.md)

| 文档 | 说明 |
|------|------|
| [脚注格式化与排序示例](/examples/footnote-formatting.md) | 自动排序、保留孤立脚注、嵌套脚注处理 |

### [信源参考](/references/index.md)

| 文档 | 说明 |
|------|------|
| [插件入口模块](/references/source-init.md) | `__init__.py` 模块 |
| [插件核心实现](/references/source-plugin.md) | `plugin.py` 模块（渲染器和CLI） |
| [脚注重排序逻辑](/references/source-reorder.md) | `_reorder.py` 模块（分类、排序算法） |

### 规范文档

- [事实清单](/spec/facts.md) - R阶段零推断事实采集
- [架构洞察](/spec/insights.md) - I阶段核心洞察四元组与知识地图
