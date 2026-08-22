---
type: Concept
title: 通用工具函数
description: escapeHtml、unescapeAll、isWhiteSpace、isMdAsciiPunct、normalizeReference 等通用工具函数
tags:
- markdown-it-py
- utils
- entity
- escape
- helper
difficulty: 高级
estimated_time: 10分钟
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# 通用工具函数

`markdown_it/common/utils.py` 提供了一系列工具函数，主要用于 HTML 处理和文本操作。

## HTML 转义与实体

### escapeHtml(html)

转义 HTML 特殊字符：`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#x27;`

```python
from markdown_it.common.utils import escapeHtml
escapeHtml("<script>alert('xss')</script>")
# "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
```

### unescapeAll(str)

解码所有 HTML 实体（命名实体和数字实体）：
- `&amp;` → `&`
- `&#65;` / `&#x41;` → `A`
- `&lt;` → `<`

### isValidEntityCode(code)

检查 Unicode 码点是否为有效 HTML 实体字符（排除控制字符、代理对等）。

### fromCodePoint(code)

将 Unicode 码点转为字符（处理超过 0xFFFF 的码点，使用代理对）。

## 字符分类

### isWhiteSpace(code)

判断字符码是否为空白字符：空格(0x20)、Tab(0x09)、换行(0x0A)、回车(0x0D)、换页(0x0C)。

### isMdAsciiPunct(code)

判断是否为 Markdown ASCII 标点字符：`! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~`

### isPunctChar(ch)

判断是否为 Unicode 标点字符（使用 Unicode 正则属性 `P`）。

## 引用规范化

### normalizeReference(str)

规范化链接引用标签：
1. 折叠空白（多个空白合并为一个）
2. 去除首尾空白
3. 小写化

```python
normalizeReference("  Google  Search  ")  # "google search"
```

这确保 `[Google][google search]` 和 `[GOOGLE SEARCH]` 能匹配同一引用定义。

## 其他工具

### read_fixture_file(path)

读取 CommonMark 测试用例文件（.txt 格式），返回 `(text, expected_html, msg)` 元组列表。用于运行 CommonMark 兼容性测试。

## HTML 实体映射

`markdown_it/common/entities.py` 包含完整的 HTML 命名实体映射字典，key 是实体名（如 `"amp"`），value 是对应字符（如 `"&"`）。

## HTML 块判断

`markdown_it/common/html_blocks.py` 定义了 HTML 块级元素的判断规则，用于 html_block 规则判断哪些 HTML 标签应该作为块级处理。

## HTML 标签正则

`markdown_it/common/html_re.py` 预编译了 HTML 标签相关的正则表达式，用于 html_inline 和 html_block 规则匹配标签。
