---
type: Concept
title: mdurl 简介
description: mdurl 是什么——Markdown URL处理工具库的定位、起源、核心API与在 Executable Books 生态中的角色
tags: [mdurl, markdown, url, introduction]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T01:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mdurl-source
    resource: /references/mdurl-source.md
    title: mdurl 源码路径映射
---

## 什么是 mdurl

mdurl 是一个专门用于处理 Markdown 中 URL 的 Python 工具库，提供 URL 的解析（parse）、格式化（format）、编码（encode）和解码（decode）四大核心功能。它是 JavaScript [mdurl](https://www.npmjs.com/package/mdurl) 包的 Python 端口，而 JavaScript mdurl 本身是 [markdown-it](https://github.com/markdown-it/markdown-it) Markdown 解析器的 URL 处理组件。

在 Executable Books 生态中，mdurl 是 [markdown-it-py](../../markdown-it-py/concepts/00-introduction.md) 的直接依赖——markdown-it-py 在解析链接（link）、自动链接（autolink）、图片（image）等 Markdown 元素时，需要对 URL 进行编码、解码、解析和格式化，这些操作全部由 mdurl 提供。

## 起源与设计背景

mdurl 的 URL 解析器并非从零实现，而是移植自 Joyent 的 Node.js 内置 `url` 模块，并做了 6 处针对 Markdown 场景的调整：

1. 路径不自动添加前导斜杠（如 `http://foo?bar` 的 pathname 为空字符串而非 `/`）
2. 反斜杠不替换为正斜杠（`http:\\example.org\` 被视为相对路径）
3. 尾部冒号作为路径的一部分（`http://example.org:foo` 的 pathname 为 `:foo`）
4. 解析结果中不做 URL 编码（Node.js 原始实现会对 auth 和 path 中部分字符编码）
5. 不提供 `parseQueryString` 参数
6. 移除了 `host`、`path`、`query` 等可由其他字段推导的冗余属性

这些差异使得 mdurl 的行为与 Python 标准库 `urllib.parse.urlparse` 也有所不同——mdurl 的解析规则是为 Markdown 规范（CommonMark/GFM）量身定制的。

## 核心 API 概览

mdurl 的公共 API 共导出 10 个名称，分为四类：

| 类别 | API | 说明 |
|------|-----|------|
| 数据结构 | `URL` | 不可变 namedtuple，包含 URL 的 8 个组件字段 |
| 解析/格式化 | `parse(url, *, slashes_denote_host=False)` | 将 URL 字符串解析为 `URL` namedtuple |
| | `format(url)` | 将 `URL` namedtuple 拼接回 URL 字符串 |
| 编码/解码 | `encode(string, exclude=..., *, keep_escaped=True)` | 百分号编码 URL 字符串 |
| | `decode(string, exclude=...)` | 解码百分号编码的 URL 字符串 |
| 编码常量 | `ENCODE_DEFAULT_CHARS` | encode 默认排除字符集（保留 URL 结构字符） |
| | `ENCODE_COMPONENT_CHARS` | encode 组件级排除字符集（仅保留非保留字符） |
| | `DECODE_DEFAULT_CHARS` | decode 默认排除字符集 |
| | `DECODE_COMPONENT_CHARS` | decode 组件级排除字符集（空字符串） |

## 环境要求

- Python 3.10+
- 无第三方运行时依赖（仅使用标准库 `urllib.parse`、`collections`、`re`、`functools`）
- MIT 许可证

## 设计哲学

mdurl 采用函数式设计风格：数据（`URL` namedtuple）是不可变的纯数据，所有操作都是独立函数，不依赖面向对象的方法调用。编码和解码内部使用预计算的 128 项 ASCII 查找表并缓存，对纯 ASCII URL 处理性能极高。

## 相关概念

- [URL 数据结构](01-url-data-structure.md)
- [URL 解析与格式化](02-parse-and-format.md)
- [URL 编码与解码](03-encode-and-decode.md)
- [基础使用示例](../examples/basic-usage.md)
