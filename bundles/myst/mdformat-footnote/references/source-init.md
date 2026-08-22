---
type: Reference
title: mdformat-footnote 插件入口模块
description: mdformat_footnote 包的 __init__.py 入口，定义版本、插件名和导出接口。
tags: [source-code, footnote, markdown, mdformat]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-init
    resource: /spec/facts.md
    title: mdformat-footnote 事实清单
---

## 模块概览

`mdformat_footnote/__init__.py` 是包入口文件（6行），包含：

- **文档字符串**：`"""An mdformat plugin for parsing/validating footnotes"""`
- **版本号**：`__version__ = "0.1.3"`
- **插件名称**：`__plugin_name__ = "footnote"`
- **导出**：从 `.plugin` 导入 `RENDERERS`、`add_cli_argument_group`、`update_mdit`

## 导出接口

| 名称 | 来源 | 用途 |
|------|------|------|
| `RENDERERS` | `.plugin` | Token 渲染器映射字典 |
| `add_cli_argument_group` | `.plugin` | CLI 参数组添加函数 |
| `update_mdit` | `.plugin` | markdown-it 解析器配置函数 |

## 源码位置

- 文件路径：`mdformat_footnote/__init__.py`
- 代码行数：6行

## 相关概念

- [插件配置与 CLI 选项](/concepts/01-plugin-configuration.md)
