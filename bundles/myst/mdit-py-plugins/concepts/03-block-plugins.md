---
type: Concept
title: 块级插件详解
description: front_matter、colon_fence、amsmath、container、deflist、fieldlist、admon等块级插件的语法和行为
tags:
- mdit-py-plugins
- block-plugins
- front-matter
- colon-fence
- amsmath
- container
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 01-plugin-basics
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins 源码路径映射
---

# 块级插件详解

块级插件在 `md.block.ruler` 注册规则，操作 StateBlock 识别和输出块级结构。

## front_matter

**语法**：文档开头 `---\nYAML\n---`

**注册位置**：before "table"，alt: paragraph/reference/blockquote/list

**关键行为**：
- 只在文档第一行匹配（`startLine == 0`）
- 起始标记最少3个连续 `-`
- 内容存为 `front_matter` Token（自闭合），content字段是YAML原文
- 插件本身不解析YAML，需要外部YAML库处理content
- 起始标记必须在行首（前导缩进0），后续内容不需要缩进

```python
from mdit_py_plugins.front_matter import front_matter_plugin
md = MarkdownIt().use(front_matter_plugin)
tokens = md.parse("---\ntitle: Hello\n---\n# Content")
# tokens[0].type == "front_matter"
# tokens[0].content == "title: Hello\n"
```

## colon_fence

**语法**：`:::lang\ncontent\n:::`

**注册位置**：before "fence"，alt: paragraph/reference/blockquote/list/footnote_def

**关键行为**：
- 与反引号围栏逻辑几乎相同，但使用 `:` 字符
- 最少3个 `:`
- 闭合标记长度必须 ≥ 起始标记
- 渲染为 `<pre><code class="block-{lang}">...</code></pre>`
- 适合在反引号围栏中嵌套围栏（避免标记冲突）

## amsmath

**语法**：`\begin{env}...\end{env}`

**注册位置**：before "blockquote"，alt: paragraph/reference/blockquote/list/footnote_def

**支持的环境**：equation, multline, gather, align, alignat, flalign, matrix, pmatrix, bmatrix, Bmatrix, vmatrix, Vmatrix, eqnarray（带*号变体也支持）

**关键行为**：
- 不自动闭合（必须找到 `\end{env}` 标记）
- 起始和结束可以在同一行
- 渲染为 `<div class="math amsmath">...</div>`
- 与dollarmath互补：amsmath处理LaTeX环境语法，dollarmath处理$分隔符语法

## container

**语法**：`:::name [params]\ncontent\n:::`

**参数**：name（容器名）、marker（标记字符，默认`:`）、validate（自定义验证函数）、render（自定义渲染函数）

**关键行为**：
- 标记最少3个
- 支持嵌套容器（不同长度标记匹配）
- 默认验证检查params第一个词是否等于name
- 默认渲染添加 `class="{name}"` 属性到开标签
- 内部递归调用 block.tokenize 解析内容
- 可多次use注册不同name的容器

## deflist

**语法**：
```
Term
: Definition

Term
~ Alternative definition marker
```

**注册位置**：block.ruler（具体before位置见源码）

**关键行为**：
- 定义标记支持 `:` 和 `~` 两种字符
- 标记后必须有空格
- 定义体支持多段落（缩进续行）
- 支持紧排（compact）和松排（loose）模式
- 渲染为 `<dl><dt>term</dt><dd>definition</dd></dl>`

## fieldlist

**语法**：`:fieldname: field body`（reST风格字段列表）

**注册位置**：before "paragraph"，alt: paragraph/reference/blockquote

**关键行为**：
- 字段名用 `:` 包裹（`:name:`）
- 字段名中不允许冒号
- 字段体缩进相对于字段名标记
- 支持字段体多段落（同缩进续行）
- 行内标记在字段名中解析
- 渲染为 `<dl class="field-list"><dt>name</dt><dd>body</dd></dl>`

## admon

**语法**：`!!! type "Title"\n    content`

**关键行为**：
- 类型标识（note/warning/tip/important/caution等）
- 可选标题在双引号中
- 内容缩进4空格
- 移植自 Python-Markdown admonitions 扩展

## 块级插件通用模式

所有块级插件遵循相同模式：
1. 开头检查 `is_code_block()`
2. 检测起始标记（字符/正则）
3. `silent=True` 时仅返回True/False（不输出Token）
4. 扫描结束标记/结束行
5. 输出开标签Token（nesting=1）
6. 递归调用 `state.md.block.tokenize()` 解析内容（如适用）
7. 输出闭标签Token（nesting=-1）
8. 设置 `state.line = nextLine`
9. 返回True
