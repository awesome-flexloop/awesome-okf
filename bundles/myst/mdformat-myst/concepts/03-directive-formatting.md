---
type: Concept
title: 指令选项 YAML 格式化机制
description: mdformat-myst 如何识别并自动格式化 MyST 指令的选项 YAML 块。
tags: [directive, yaml, formatting, fence, ruamel]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-directives
    resource: /references/source-directives.md
    title: mdformat-myst 指令格式化模块
---

## MyST 指令语法

MyST 指令（Directive）是一种扩展 Markdown 语法，用于插入复杂内容块（如图片、警告框、代码块等）。指令使用代码围栏语法，info 字符串被花括号包裹：

````markdown
```{directive-name} argument
:option1: value1
:option2: value2

指令内容
```
````

或者使用 YAML 围栏形式的选项：

````markdown
```{directive-name} argument
---
option1: value1
option2: value2
---

指令内容
```
````

## 指令识别方式

mdformat-myst 的 fence 渲染函数通过一个简单的规则区分普通代码块和 MyST 指令：

> 如果 fence 的 info 字符串以 `{` 开头且以 `}` 结尾，则识别为 MyST 指令。

这个判断逻辑在 `fence` 函数中实现，是相对于 mdformat 上游 fence 渲染代码的唯一修改（注释明确标记为"the *only* thing added to the upstream fence implementation"）。

## 两种选项格式解析

`parse_opts_and_content` 函数能解析两种指令选项格式：

### 1. YAML 围栏格式（---分隔）

````markdown
```{note}
---
class: warning
---
这是一条警告。
```
````

解析规则：
- 第一行必须是≥3个连续连字符
- 后续行直到下一个≥3连字符行都是 YAML 内容
- 之后的行为正文内容
- 空行（YAML和正文之间的一个空行）会被自动跳过

### 2. 冒号选项格式（:key: value）

````markdown
```{image} picture.png
:alt: 示例图片
:width: 300px
```
````

解析规则：
- 第一行以 `:` 开头（去除前导空白后），去除首字符作为 YAML 的第一行
- 后续连续以 `:` 开头的行都作为选项行
- 第一个不以 `:` 开头的行之后为正文内容

## YAML 格式化流程

识别为指令后，`format_directive_content` 函数执行以下步骤：

1. **解析分离**：调用 `parse_opts_and_content` 将原始内容分离为未格式化的 YAML 字符串和正文内容
2. **YAML 解析**：使用 ruamel.yaml 加载 YAML 字符串（加载失败时保留原始内容并输出警告）
3. **YAML 序列化**：使用配置好的 ruamel.yaml YAML 实例重新序列化，实现缩进规范化
4. **清理结束标记**：ruamel.yaml 会自动在文档末尾添加 `\n...\n` 结束标记，需要移除
5. **空值处理**：如果序列化结果为 `null\n`（表示空 YAML），替换为空字符串
6. **重组**：用 `---\n` 包裹格式化后的 YAML，追加正文内容

## YAML 缩进配置

ruamel.yaml 配置为：
- **mapping 缩进**：2 空格
- **sequence 缩进**：4 空格
- **offset**：2（序列项相对于父键的偏移）

这意味着格式化后的选项 YAML 会统一为以下风格：

```yaml
---
key1: value1
key2:
  - item1
  - item2
---
```

## 围栏字符选择

fence 渲染函数根据 info 字符串内容选择围栏字符：
- 如果 info 字符串包含反引号（`` ` ``）或波浪号（`~`），使用波浪号 `~` 作为围栏字符
- 否则使用反引号 `` ` ``

围栏长度通过 `longest_consecutive_sequence` 函数计算：围栏字符在内容中的最长连续出现次数 + 1（最小为 3），确保围栏标记不会与内容冲突。

## 格式化示例

### 输入（格式不规范）

````markdown
```{image} /img/fun-fish.png
---
alt: fish
width: 200px
---
```
````

### 输出（格式化后）

````markdown
```{image} /img/fun-fish.png
---
alt: fish
width: 200px
---
```
````

在这个例子中，YAML 选项本身格式正确，输出保持不变。如果 YAML 缩进不规范，ruamel.yaml 会自动修正缩进。

## 相关概念

- [插件架构](/concepts/01-plugin-architecture.md)
- [MyST 语法支持](/concepts/02-myst-syntax-support.md)
- [转义机制与后处理器](/concepts/04-escaping-and-postprocessors.md)
