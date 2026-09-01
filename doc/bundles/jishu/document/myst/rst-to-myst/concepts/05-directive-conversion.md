---
type: Concept
title: 指令转换机制与 directives.yml 映射
description: rst-to-myst 如何通过 directives.yml 和自定义转换映射将 RST 指令转为 MyST 指令。
tags: [directive, conversion, directives.yml, mapping, fence]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-parser
    resource: /references/source-parser.md
    title: rst-to-myst RST 解析器模块
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 指令转换原理

RST 指令（directive）是块级扩展机制，格式为 `.. directive-name:: argument`。在标准 docutils 解析中，指令的 `run()` 方法会被调用生成具体节点。但 rst-to-myst 的 `LosslessRSTParser` 不执行 `run()` 方法，而是将指令保留为 `DirectiveNode`，包含指令名称、模块路径、选项列表和内容。

这意味着转换是"语法级"的：工具不理解指令的语义，而是根据指令的模块路径查找转换类型，然后输出对应的 MyST 语法。

## directives.yml 映射文件

默认的指令转换规则存储在 `rst_to_myst/data/directives.yml` 中，通过 `_load_directive_data()` 函数加载并使用 `@lru_cache` 缓存。

映射格式为：
```yaml
module.path.ClassName: conversion_type
```

用户可通过 `conversions` 参数（CLI 中为 `--conversions` 选项）覆盖或追加映射。

## 指令渲染输出

MyST 指令使用代码围栏（fence）语法，支持三种围栏字符：

| 围栏字符 | 触发条件 | 语法 |
|---------|---------|------|
| 反引号 `` ` `` | 默认 | `````{name} arg``` `` |
| 冒号 `:` | `colon_fences=True` 且指令有内容 | `:::{name} arg` |
| 波浪号 `~` | 参数/信息串中含反引号或波浪号 | `~~~{name} arg~~~` |

冒号围栏（colon fence）是 MyST 的特有语法，允许围栏内容中包含反引号而不冲突。

## _directive_render 函数

`_directive_render` 是指令渲染的核心函数，输出结构如下：

```
{fence_str}{{name}}{argument}
{option_block}
{content}
{fence_str}
```

### 特殊指令处理

两种特殊指令有硬编码处理：

1. **`misc.Replace`**：如果指令模块以 `misc.Replace` 结尾且有子节点，直接输出最后一个子节点（替换指令的内容）
2. **`misc.Date`**：输出替换引用 `{sub-ref}\`today\``

### 参数渲染

如果有 `directive_arg` 子节点，将其内容渲染并压缩为单行（换行符合并为空格），前面加空格作为 info 字符串的一部分。

### 选项渲染

如果 `options_list` 非空，将选项键值对序列化为 YAML，然后用 `textwrap.indent` 以冒号缩进：

```
:key1: value1
:key2: value2
```

值的类型处理：
- `None` → `true`（布尔标志选项）
- 数字字符串 → 转为整数
- 其他 → 保持字符串

### 内容渲染

如果有 `directive_content` 子节点，渲染其子内容。选项块和内容之间用双换行分隔。如果没有选项块但内容以 `:` 开头，前面添加空行避免被误识别为选项。

### 围栏长度计算

围栏长度为内容中围栏字符的最长连续出现次数 + 1（最小为 3），确保围栏标记不会与内容中的字符序列冲突。

## 指令选项格式

RST 指令有两种选项格式，转换后统一为 MyST 兼容格式：

### RST 冒号选项格式

```rst
.. image:: picture.png
   :alt: 示例图片
   :width: 300px
```

转换后保持冒号格式（冒号缩进）：

````markdown
```{image} picture.png
:alt: 示例图片
:width: 300px
```
````

### 枚举类型支持

`ResolveListItems` Transform 支持五种枚举编号类型，但 markdown-it 目前仅完整支持数字（arabic）编号。其他类型（roman/alpha）的支持在代码中标记为 TODO。

## 转换扩展推断

`get_myst_extensions()` 函数扫描输出 tokens 推断所需的 MyST 扩展。指令相关的规则：
- 使用冒号围栏的指令（`token.markup` 含 `:`）→ 需要 `colon_fence` 扩展

转换完成后 CLI 输出所需扩展列表，用户需在 MyST 配置中启用。

## 自定义转换

通过 `--conversions` 选项（CLI）或 `conversions` 参数（Python API）指定自定义映射：

```yaml
# my-conversions.yml
mypackage.mydirective: eval_rst
```

```bash
rst2myst stream --conversions my-conversions.yml input.rst
```

```python
from rst_to_myst import rst_to_myst
result = rst_to_myst(rst_text, conversions={"mypackage.mydirective": "eval_rst"})
```

## 相关概念

- [三阶段转换流水线架构](03-conversion-pipeline.md)
- [LosslessRSTParser 与自定义 Transform](04-lossless-parser.md)
- [mdformat 渲染集成与自定义渲染器](07-mdformat-integration.md)
