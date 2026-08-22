---
type: Concept
title: 转义机制与后处理器原理
description: mdformat-myst 如何在渲染后自动转义 MyST 特殊字符，避免普通文本被误解析。
tags: [escaping, postprocessor, special-characters, paragraph, text]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /references/source-plugin.md
    title: mdformat-myst 插件核心实现
---

## 为什么需要转义

MyST 引入了多种特殊语法标记，如果普通文本中出现这些字符序列，Markdown 解析器会将它们误识别为 MyST 语法元素。mdformat-myst 通过 POSTPROCESSORS（后处理器）在渲染完成后对输出进行转义处理，确保字面量文本中的特殊字符被正确转义。

## 两层转义机制

mdformat-myst 实现了两个后处理器：

| 后处理器 | 处理节点 | 处理层级 | 转义内容 |
|---------|---------|---------|---------|
| `_escape_paragraph` | paragraph | 块级/行首 | `+++`、`%`、`(target)=`模式 |
| `_escape_text` | text | 行内 | `{role}`模式、`$`符号 |

## 段落级转义

`_escape_paragraph` 逐行检查并转义三种行首特殊模式：

1. **三个及以上连续+号**：在第一个`+`前加反斜杠（避免误识别为块中断）
2. **百分号开头的行**：在`%`前加反斜杠（避免误识别为注释）
3. **目标锚点模式**：匹配`^\s*\(.+\)=\s*$`正则的行，在第一个`(`前加反斜杠

## 行内级转义

`_escape_text` 处理行内特殊字符：

1. **MyST角色名**：用正则`({[a-zA-Z0-9_\-+:]+})`匹配花括号包裹的角色名模式，前缀反斜杠
2. **美元符号**：所有`$`转义为`\$`（避免误识别为数学公式）

注意：真正的角色和数学公式由专用渲染器处理，不会走到text后处理器。

## 相关概念

- [MyST 语法支持](/concepts/02-myst-syntax-support.md)
- [插件架构](/concepts/01-plugin-architecture.md)
