---
type: bundle
title: mdformat-myst
description: mdformat 的 MyST Markdown 语法格式化插件，支持角色、指令、数学公式、注释、目标锚点等 MyST 语法。
okf_version: "0.2"
tags: [myst, markdown, mdformat, formatter, plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
---

# mdformat-myst

mdformat-myst 是 [mdformat](https://github.com/executablebooks/mdformat) 的 MyST（Markedly Structured Text）Markdown 兼容性插件。安装后 mdformat 可以正确格式化 MyST 特有的语法元素。

- **版本**：0.3.0
- **Python 要求**：≥ 3.10
- **源码**：`mdformat_myst/`

## 快速开始

```bash
pip install mdformat-myst
mdformat document.md
```

## 文档导航

### [概念文档](/concepts/index.md)

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [项目介绍与安装](/concepts/00-introduction.md) | 安装、基本使用和支持的语法范围 |
| 01 | [插件架构与 mdformat-myst 组成](/concepts/01-plugin-architecture.md) | mdformat 插件机制和本插件的组合式设计 |
| 02 | [MyST 语法支持范围](/concepts/02-myst-syntax-support.md) | 角色、注释、块中断、目标、数学公式的渲染格式 |
| 03 | [指令选项 YAML 格式化机制](/concepts/03-directive-formatting.md) | MyST 指令识别和选项 YAML 自动格式化 |
| 04 | [转义机制与后处理器原理](/concepts/04-escaping-and-postprocessors.md) | 自动转义 MyST 特殊字符的双层机制 |

### [示例文档](/examples/index.md)

| 文档 | 说明 |
|------|------|
| [MyST 文档格式化示例](/examples/formatting-myst-documents.md) | 格式化包含各种 MyST 语法的文档 |

### [信源参考](/references/index.md)

| 文档 | 说明 |
|------|------|
| [插件入口模块](/references/source-init.md) | `__init__.py` 模块 |
| [插件核心实现](/references/source-plugin.md) | `plugin.py` 模块 |
| [指令格式化模块](/references/source-directives.md) | `_directives.py` 模块 |

### 规范文档

- [事实清单](/spec/facts.md) - R阶段零推断事实采集
- [架构洞察](/spec/insights.md) - I阶段核心洞察四元组与知识地图
