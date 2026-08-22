---
type: Concept
title: 行内插件详解
description: dollarmath行内、sub/superscript、myst_role、gfm_autolink等行内插件
tags:
- mdit-py-plugins
- inline-plugins
- dollarmath
- subscript
- superscript
difficulty: 核心
estimated_time: 15分钟
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

# 行内插件详解

行内插件在 `md.inline.ruler` 注册规则，操作 StateInline 识别和输出行内 Token。

## dollarmath 行内数学

**语法**：`$x^2$`（行内）、`$$x^2$$`（双美元行内，double_inline=True时）

**注册位置**：before "escape"（在转义规则之前处理$）

**关键行为**：
- `is_escaped()` 检测 `\$` 转义，奇数个反斜杠则跳过
- `allow_space=False` 时 `$ a $` 不匹配（避免误匹配货币$ 100）
- `allow_digits=False` 时 `1$` 或 `$2` 不匹配（避免货币）
- 内容为空（`$$`）不匹配
- 双美元匹配需要两个$配对，内容在两对$之间
- 支持 `\` 转义$符号
- Token类型：`math_inline`（单$）、`math_inline_double`（双$）

## subscript 下标

**语法**：`~H~2~O` → H<sub>2</sub>O

**注册位置**：after "emphasis"

**关键行为**：
- 标记字符 `~`
- 内容中不允许未转义空白
- 使用 `skipToken()` 跳过嵌套的行内元素（如emphasis在sub内）
- 支持 `\~` 转义
- UNESCAPE_RE 用于反转义内容中的反斜杠
- Token类型：`sub_open`/`sub_close`（tag="sub"）

## superscript 上标

**语法**：`2^10^` → 2<sup>10</sup>

**注册位置**：inline.ruler（具体位置见源码）

与subscript类似，标记字符 `^`，Token类型 `sup_open`/`sup_close`（tag="sup"）。

## myst_role MyST角色

**语法**：`` {role}`content` ``

MyST（Markedly Structured Text）的角色语法，用于标记行内语义。例如 `` {math}`x^2` ``、`` {abbr}`HTML (HyperText Markup Language)` ``。

**注册位置**：inline.ruler

**关键行为**：
- 匹配 `{name}`text`` 模式
- role名称存在 `{` 和 `` ` `` 之间
- 内容在反引号中（类似行内代码，但支持更长的反引号序列）
- Token类型包含role信息

## gfm_autolink GFM自动链接

**语法**：纯文本中的URL（如 `https://example.com`）和邮箱地址自动转为链接

**注册位置**：inline.ruler

**关键行为**：
- 不需要 `<>` 包裹（与markdown-it内置autolink规则不同）
- 识别 http://、https://、ftp://、www. 开头的URL
- 识别邮箱地址
- 使用 `_match.py` 模块的匹配逻辑
- Token类型：`link_open`/`text`/`link_close`（与普通链接相同）
- 支持 www. 前缀自动添加 https://

## attrs 行内属性

**语法**：`text{.class #id key=value}`

为行内容器添加HTML属性。

## texmath TeX数学

**语法**：`\(x^2\)`（行内）、`\[x^2\]`（块级）

与dollarmath类似，但使用LaTeX风格的 `\(\)` 和 `\[\]` 分隔符。

## 行内插件通用模式

1. 检查当前位置字符是否为起始标记
2. 检查转义（`\`前缀）
3. 扫描找到结束标记（处理嵌套、转义）
4. `silent=True` 时仅返回True/False
5. `pushPending()` 刷新文本缓冲区
6. 输出 Token（开标签→text内容→闭标签，或单个自闭合Token）
7. 更新 `state.pos` 到匹配结束位置
8. 返回True
