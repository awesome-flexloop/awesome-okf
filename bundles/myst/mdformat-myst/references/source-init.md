---
type: Reference
title: mdformat-myst 插件入口模块
description: mdformat_myst 包的 __init__.py 入口，定义版本号和文档字符串。
tags: [source-code, myst, markdown, mdformat]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-init
    resource: /spec/facts.md
    title: mdformat-myst 事实清单
---

## 模块概览

`mdformat_myst/__init__.py` 是包的入口文件，包含：

- **文档字符串**：`"""Mdformat plugin for MyST compatibility."""`
- **版本号**：`__version__ = "0.3.0"`

## 导出接口

该模块不显式导出任何函数或类，插件入口点通过 `pyproject.toml` 中的 entry points 配置指向 `mdformat_myst.plugin` 模块。

## 源码位置

- 文件路径：`mdformat_myst/__init__.py`
- 代码行数：3行（含文档字符串）

## 相关概念

- [插件架构](/concepts/01-plugin-architecture.md)
