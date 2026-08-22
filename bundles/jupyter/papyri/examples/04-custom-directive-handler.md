---
type: Example
title: "自定义指令处理器"
description: "从零编写 RST 指令处理器，处理自定义指令并将其转换为 IR 节点，包括 Admonition、代码块、表格等输出类型"
tags: [directives, handlers, extensions, rst, custom, ir]
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: "/references/papyri-source.md"
    title: "Papyri Python 核心包源码信源"
  - id: nodes-src
    resource: "/references/ir-nodes-source.md"
    title: "Papyri IR 节点类型源码信源"
---

# 自定义指令处理器

本示例演示如何为 papyri 编写自定义 RST 指令处理器，将 docstring 中的自定义指令转换为 IR 节点。

## 背景：为什么需要处理器

当 papyri 解析 docstring 时，遇到 RST 指令（`.. directive-name::` 块）会：
1. 在 TOML 配置的 `[global.directives]` 中查找处理器
2. 找到 → 调用处理器，用返回的 IR 节点替换指令
3. 找不到 → 生成 `Directive` 节点，**序列化时强制报错**

这确保没有任何信息被静默丢弃。

## 示例1：最简单的处理器——丢弃指令

使用内置 `drop` 处理器：

```toml
[global.directives]
testsetup = 'papyri.directives:drop'
```

适用于不影响阅读的测试/设置指令。

## 示例2：保留为代码块

使用内置 `code_handler`：

```toml
[global.directives]
code-block = 'papyri.directives:code_handler'
literalinclude = 'papyri.directives:code_handler'
```

## 示例3：版本提示 Admonition

处理 `.. versionadded::`、`.. versionchanged::`、`.. deprecated::` 等版本提示指令：

```python
# mypackage/_papyri.py
from papyri.nodes import Admonition, Paragraph, Text


def _get_arg_and_body(directive):
    """从指令节点提取参数和体内容。
    
    注意：实际实现需要遍历 tree-sitter CST 节点。
    这里提供简化版本展示处理器的基本结构。
    """
    arg = ""
    body = ""
    for child in getattr(directive, "children", []):
        if hasattr(child, "text"):
            text = child.text
            if isinstance(text, bytes):
                text = text.decode()
            if not arg:
                arg = text.strip()
            else:
                body += text + "\n"
    return arg, body.strip()


def versionadded(directive):
    """处理 .. versionadded:: X.Y 指令。"""
    version, desc = _get_arg_and_body(directive)
    text = f"New in version {version}."
    if desc:
        text += f" {desc}"
    return Admonition(
        kind="versionadded",
        children=(Paragraph((Text(text),)),),
    )


def versionchanged(directive):
    """处理 .. versionchanged:: X.Y 指令。"""
    version, desc = _get_arg_and_body(directive)
    text = f"Changed in version {version}."
    if desc:
        text += f" {desc}"
    return Admonition(
        kind="versionchanged",
        children=(Paragraph((Text(text),)),),
    )


def deprecated(directive):
    """处理 .. deprecated:: X.Y 指令。"""
    version, desc = _get_arg_and_body(directive)
    text = f"Deprecated since version {version}."
    if desc:
        text += f" {desc}"
    return Admonition(
        kind="deprecated",
        children=(Paragraph((Text(text),)),),
    )
```

在 TOML 中注册：

```toml
[global.directives]
versionadded = 'mypackage._papyri:versionadded'
versionchanged = 'mypackage._papyri:versionchanged'
deprecated = 'mypackage._papyri:deprecated'
```

## 示例4：注意/警告框

处理 `.. note::`、`.. warning::`、`.. tip::` 等提示框：

```python
def note_directive(directive):
    """处理 .. note:: 指令。"""
    _, body = _get_arg_and_body(directive)
    return Admonition(
        kind="note",
        children=(Paragraph((Text(body),)),),
    )


def warning_directive(directive):
    """处理 .. warning:: 指令。"""
    _, body = _get_arg_and_body(directive)
    return Admonition(
        kind="warning",
        children=(Paragraph((Text(body),)),),
    )


def danger_directive(directive):
    """处理 .. danger:: 指令。"""
    _, body = _get_arg_and_body(directive)
    return Admonition(
        kind="danger",
        children=(Paragraph((Text(body),)),),
    )


def tip_directive(directive):
    """处理 .. tip:: 指令。"""
    _, body = _get_arg_and_body(directive)
    return Admonition(
        kind="tip",
        children=(Paragraph((Text(body),)),),
    )
```

注册：

```toml
[global.directives]
note = 'mypackage._papyri:note_directive'
warning = 'mypackage._papyri:warning_directive'
danger = 'mypackage._papyri:danger_directive'
tip = 'mypackage._papyri:tip_directive'
attention = 'mypackage._papyri:warning_directive'
important = 'mypackage._papyri:note_directive'
seealso = 'mypackage._papyri:note_directive'
```

> [!TIP]
> Admonition 的 `kind` 必须是已知类型：`note`、`tip`、`important`、`warning`、`danger`、`neutral`。未知 kind 会通过 `admonition_base_type()` 映射到基础类型，version 相关 kind 映射到 `neutral`。

## 示例5：返回多个节点

处理器可以返回 Node 列表，一个指令展开为多个 IR 节点：

```python
def seealso_handler(directive):
    """处理 .. seealso:: 指令，展开为段落 + SeeAlsoItem 列表。"""
    _, body = _get_arg_and_body(directive)
    # 可以返回多个节点
    return [
        Paragraph((Text("See Also:"),)),
        Paragraph((Text(body),)),
    ]
```

## 示例6：处理带选项的指令

某些指令带选项（`:option: value`）：

```python
def code_block_handler(directive):
    """处理 .. code-block:: python :linenos: 类指令。"""
    lang, body = _get_arg_and_body(directive)
    # 选项在 directive 的 children 中需要解析
    return Code(
        children=(Text(body),),
        language=lang or "text",
        execution_status=None,
        out=None,
    )
```

## Admonition kind 到样式映射

Papyri viewer 使用 6 种基础 Admonition 样式：

| kind | 基础样式 | 典型用途 |
|------|---------|---------|
| `note` | note | 一般性提示 |
| `tip` | tip | 实用技巧 |
| `important` | important | 重要信息 |
| `warning` | warning | 警告（可能出问题） |
| `danger` | danger | 危险（会出问题） |
| `neutral` | neutral | 版本信息等中性内容 |

非基础 kind 通过 `admonition_base_type()` 自动映射：

| 输入 kind | 映射到 |
|-----------|--------|
| `versionadded`/`versionchanged`/`deprecated` | `neutral` |
| `attention`/`caution` | `warning` |
| `error` | `danger` |
| `hint` | `tip` |
| 其他未知 | `note` |

## 关键点总结

1. **处理器签名**：接收一个指令节点参数，返回 `Node` 或 `list[Node]`
2. **必须注册**：在 `[global.directives]` 中用 `'module.path:func_name'` 格式注册
3. **drop 是最安全的兜底**：不确定如何处理的指令先 drop，避免序列化报错
4. **Admonition kind 有限制**：必须使用 6 种基础类型或可映射的已知类型
5. **可以返回多个节点**：返回列表即可展开为多个 IR 节点
6. **指令未注册会报错**：`Directive._reject_at_validate = True`，不会静默丢失信息

## 相关示例

- [自定义 TOML 配置](02-custom-config.md)
