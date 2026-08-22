---
type: Concept
title: MyST 语法支持范围
description: mdformat-myst 支持的 MyST 语法元素及其渲染输出格式。
tags: [myst-syntax, role, comment, block-break, target, math]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /references/source-plugin.md
    title: mdformat-myst 插件核心实现
---

## 渲染器映射总览

mdformat-myst 通过 `RENDERERS` 字典注册了 9 种 token 类型的渲染函数，覆盖 MyST 扩展引入的所有新 token 类型以及对 blockquote 的特殊处理。

## 角色（Role）

角色是 MyST 中用于行内语义标记的语法，格式为 `{role-name}`content``。

**Token 类型**：`myst_role`

**渲染函数**：`_role_renderer`

**输出格式**：

```
{角色名}`内容`
```

角色名从 `node.meta["name"]` 获取，内容用反引号包裹。

## 行注释（Line Comment）

MyST 支持以 `%` 开头的注释行。

**Token 类型**：`myst_line_comment`

**渲染函数**：`_comment_renderer`

**输出格式**：

```
% 注释内容
% 多行注释每行行首加%
```

多行注释的换行符会被替换为 `\n%`，确保每行行首都有 `%` 前缀。

## 块中断（Block Break）

块中断用 `+++` 标记，用于在文档中创建显式的块分隔。

**Token 类型**：`myst_block_break`

**渲染函数**：`_blockbreak_renderer`

**输出格式**：

```
+++
```

如果 token 带有内容（block break 可以附带元数据），则输出为 `+++ content`。

## 目标锚点（Target）

目标锚点用于为文档中的位置创建可引用的标签，格式为 `(target-name)=`。

**Token 类型**：`myst_target`

**渲染函数**：`_target_renderer`

**输出格式**：

```
(target-name)=
```

## 行内数学

行内数学公式用单个美元符号包裹。

**Token 类型**：`math_inline`

**渲染函数**：`_math_inline_renderer`

**输出格式**：

```
$E = mc^2$
```

## 块级数学

块级数学公式用双美元符号包裹，可以独立成段。

**Token 类型**：`math_block`

**渲染函数**：`_math_block_renderer`

**输出格式**：

```
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$
```

当数学块位于缩进上下文中（indent_width > 0），会先对内容调用 `textwrap.dedent()` 去除公共缩进。

## 带标签的块级数学

块级数学公式可以附带编号/标签，用于交叉引用。

**Token 类型**：`math_block_label`

**渲染函数**：`_math_block_label_renderer`

**输出格式**：

```
$$
E = mc^2
$$ (eq:energy)
```

标签从 `node.info` 获取，追加在块级数学闭合 `$$` 之后的括号中。

## 数学块安全引用

当数学块出现在 blockquote（`>` 引用）中时，需要特殊处理以确保引用标记正确应用于多行数学内容。

**Token 类型**：`blockquote`

**渲染函数**：`_math_block_safe_blockquote_renderer`

该渲染函数遍历子节点，对 math_block 和 math_block_label 类型的子节点直接渲染，其他子节点渲染后按行拆分，每行前添加 `> ` 前缀，空行也保留 `>` 标记。

## Fence（代码/指令围栏）

fence 类型的渲染委托给 `_directives.py` 中的 `fence` 函数，该函数在标准 fence 渲染基础上增加了 MyST 指令的识别和格式化。详见[指令选项 YAML 格式化](/concepts/03-directive-formatting.md)。

## 相关概念

- [插件架构](/concepts/01-plugin-architecture.md)
- [指令选项 YAML 格式化](/concepts/03-directive-formatting.md)
- [转义机制与后处理器](/concepts/04-escaping-and-postprocessors.md)
