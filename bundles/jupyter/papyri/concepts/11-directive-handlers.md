---
type: Concept
title: 指令处理器扩展
description: 如何为 papyri 编写自定义 RST 指令处理器，包括内置处理器和注册机制
tags: [papyri, directives, extensions, handlers, rst]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: config-src
    resource: /references/config-source.md
    title: Papyri 配置系统源码信源
---

## 指令处理机制

RST 指令（`.. directive-name:: arguments` 块）是 docstring 中的扩展标记。Papyri 默认不认识任意指令——遇到未注册的指令会生成 `Directive` 节点，而 `Directive._reject_at_validate = True` 会在验证阶段抛出错误。

要支持自定义指令，必须在 TOML 配置中注册处理器。

## 内置处理器

### papyri.directives:drop

静默丢弃指令及其全部内容。适用于不影响文档语义的指令（如测试设置指令）：

```toml
[global.directives]
testsetup = 'papyri.directives:drop'
testcleanup = 'papyri.directives:drop'
```

### papyri.directives:code_handler

将指令体保留为代码块。适用于 `code-block`、`literalinclude` 等代码类指令：

```toml
[global.directives]
code-block = 'papyri.directives:code_handler'
ipython = 'papyri.directives:code_handler'
```

## 注册自定义处理器

在 TOML 配置文件的 `[global.directives]` 节注册：

```toml
[global.directives]
directive-name = 'module.path:handler_function'
```

处理器函数的格式是 `'模块路径:函数名'`，使用与限定名相同的冒号分隔符。

## 处理器函数签名

指令处理器函数接收一个参数并返回一个或多个 IR 节点：

```python
def my_handler(directive_node) -> Node | list[Node]:
    """
    处理一个 RST 指令节点。

    参数:
        directive_node: tree-sitter 解析出的指令 CST 节点，
                       可提取指令名、参数和体内容

    返回:
        一个 IR Node 或 Node 列表，替换原 Directive 节点在 IR 树中的位置
    """
    ...
```

### 可用的上下文

处理器可以通过 directive_node 访问：

- **指令名**：`directive_node.type` 或通过 child 节点获取
- **参数**：`directive_node.children` 中的 argument 节点
- **选项**：`.. directive:: :option: value` 格式的选项
- **体内容**：缩进块中的文本/CST 节点

处理器可以使用 `papyri/tree.py` 中的工具解析体内容，或者直接构造 IR 节点。

## 常见场景

### 场景 1：丢弃测试相关指令

```toml
[global.directives]
testsetup = 'papyri.directives:drop'
testcleanup = 'papyri.directives:drop'
doctest = 'papyri.directives:drop'
```

### 场景 2：将特定指令转换为 Admonition

```python
def version_added_handler(directive_node):
    # 提取版本号参数
    version = extract_argument(directive_node)
    # 提取描述文本
    body_text = extract_body_text(directive_node)
    # 返回 Admonition 节点
    return Admonition(
        kind="versionadded",
        children=[Paragraph([Text(f"New in version {version}. {body_text}")])]
    )
```

注册：
```toml
[global.directives]
versionadded = 'mypackage.directives:version_added_handler'
versionchanged = 'mypackage.directives:version_changed_handler'
deprecated = 'mypackage.directives:deprecated_handler'
```

### 场景 3：处理图像指令

```python
def plot_handler(directive_node):
    # 提取图像路径参数
    image_path = extract_argument(directive_node)
    return Image(
        reference=RefInfo(kind="assets", path=image_path),
        options={}
    )
```

## Directive 节点的调试

如果忘记注册某个指令的处理器，错误信息会明确指出指令名：

```
NotImplementedError: 遇到未注册的指令 "mydirective"。
请在配置文件的 [global.directives] 中注册处理器，或使用 papyri.directives:drop 丢弃。
```

在开发过程中，可以使用 `@debug(tag)` 标记的节点类型（如 `UnprocessedDirective`）来检查哪些指令尚未被处理。

## 相关概念

- [RST 解析](10-rst-parsing.md)
- [IR 节点类型体系](04-ir-node-types.md)
- [配置系统](07-config-system.md)
