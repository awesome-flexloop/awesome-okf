---
type: Concept
title: RST 解析与 IR 转换
description: Papyri 使用 tree-sitter-rst 解析 reStructuredText，通过 GenVisitor 将解析树转换为 IR 节点
tags: [papyri, rst, tree-sitter, parsing, visitor]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: nodes-src
    resource: /references/ir-nodes-source.md
    title: Papyri IR 节点类型源码信源
---

## 解析架构

Papyri 使用 tree-sitter-rst（通过 py-tree-sitter-rst 包）解析 RST 格式的 docstring。解析过程分为两个层次：

1. **numpydoc 分节**：使用 `numpydoc_compat.NumpyDocString` 将 docstring 分割为标准节（Parameters/Returns/Examples 等）
2. **tree-sitter 解析**：对每个节的文本内容，使用 tree-sitter-rst 解析为 CST（具体语法树），再通过 Visitor 模式转换为 IR 节点树

## tree.py：Tree-sitter RST 模块

`papyri/tree.py` 是 tree-sitter-rst 的 Python 绑定和查询系统。核心组件：

### Language 和 Parser

- `RST_LANGUAGE`：加载的 tree-sitter-rst 语言对象
- `parse(text_bytes)`：将字节串解析为 tree-sitter Tree
- `ts.parse(text)`：便捷函数，接收 str 并返回 Tree

### GenVisitor：CST→IR 转换器

`GenVisitor` 是 tree-sitter CST 到 IR 节点的主要转换器，基于 tree-sitter 查询驱动。它遍历 CST 节点，使用预定义的查询模式匹配不同的 RST 结构，生成对应的 IR 节点。

Visitor 处理的主要 RST 结构：

| RST 结构 | IR 节点 |
|----------|---------|
| 段落 | Paragraph(Text(...)) |
| `**粗体**` | Strong(Text(...)) |
| `*斜体*` | Emphasis(Text(...)) |
| `` `代码` `` | InlineCode(Text(...)) |
| 链接 `` `文本 <url>`_ `` | Link(Text(...), reference=...) |
| 代码块 `.. code-block::` | Code(...) |
| 列表（有序/无序） | BulletList(ListItem(...)) |
| 引用块 | Blockquote(...) |
| 表格 | Table(TableRow(TableCell(...))) |
| 提示框 `.. note::` 等 | Admonition(...) |
| 数学 `.. math::` | Math(...) / InlineMath(...) |
| 指令 `.. directive::` | Directive（未注册）或自定义处理器结果 |
| 解释文本角色 ``:role:`text``` | InlineRole(...) → CrossRef(...) |
| 替换引用 `|sub|` | SubstitutionRef（@debug） |

### IngestVisitor（TypeScript 端）

TypeScript 端也有一个类似的 Visitor（`ingest/visitor.ts`），但它的目标是在摄取后对 IR 做后处理（如解析 to-resolve 引用），而非从 RST 解析。

## 分节：numydoc 风格

NumPy docstring 风格将文档分为固定的节标题。`numpydoc_compat.py` 是 numpydoc 库的兼容层，负责：

1. 识别节标题（如 `Parameters`、`Returns`、`Examples` 等）
2. 将 docstring 分割为节名→节内容的映射
3. 处理 NumPy 特有的参数列表格式（`name : type` 后跟缩进描述）
4. 处理 See Also 节（`func_name : 描述` 或 `func_name, func2` 格式）

### 标准节顺序

GeneratedDoc 的标准节顺序定义在 `generated_doc_order` 中：

```
Signature → Summary → Extended Summary → Parameters → Returns →
Yields → Receives → Raises → Warns → Other Parameters → Attributes →
Methods → See Also → Notes → Warnings → References → Examples
```

## 指令（Directives）

RST 指令（`.. directive-name::` 块）是扩展机制。Papyri 处理指令的方式：

1. tree-sitter 将指令解析为 `block_directive` CST 节点
2. GenVisitor 提取指令名、参数和体内容
3. 在 TOML 配置的 `[global.directives]` 中查找处理器
4. 找到 → 调用处理器函数，返回 IR 节点替换
5. 未找到 → 生成 `Directive` 节点（`_reject_at_validate = True`，序列化时强制报错）

> [!IMPORTANT]
> 未注册的指令会在验证阶段（`node.validate()`）抛出错误，而不是静默忽略。这确保开发者知道哪些指令需要处理，避免信息丢失。

## 解释文本角色（Interpreted Text Roles）

RST 的解释文本角色（``:role:`content```）用于标记行内语义。常见的 Python 文档角色：

- ``:func:`name``` → 函数引用
- ``:class:`name``` → 类引用
- ``:meth:`name``` → 方法引用
- ``:mod:`name``` → 模块引用
- ``:attr:`name``` → 属性引用
- ``:data:`name``` → 数据引用
- ``:const:`name``` → 常量引用
- ``:exc:`name``` → 异常引用
- ``:obj:`name``` → 任意 Python 对象引用
- ``:ref:`name``` → 交叉引用标签
- ``:doc:`name``` → 文档引用
- ``:math:`formula``` → 数学公式

这些角色在 gen 阶段：
1. 被解析为 `InlineRole` 节点
2. GenVisitor 尝试解析为 `CrossRef`（LocalRef 或 RefInfo）
3. 外部/未解析的保持为 `RefInfo(kind="to-resolve")`

## 代码块与执行

`.. code-block:: python` 指令生成 `Code` 节点。当 `--exec` 启用时，Examples 节中的代码块通过 `BlockExecutor` 执行：

1. `doctest.DocTestParser` 解析 Examples 节
2. 每个代码片段在隔离命名空间中执行
3. stdout/stderr 捕获到 `Code.out`
4. matplotlib 图形保存为 assets，通过 `Figure` 节点引用
5. 执行结果与期望输出对比（如果是 doctest 格式）

## 语法高亮

`gen.py` 中使用 Pygments 进行语法高亮：
- `highlight()` 函数对代码字符串进行词法分析
- 输出 token 流（token type → text 对）
- 这些 token 在 IR 中表示为 `GenToken`（UnserializableNode，中间态）
- 最终转换为 `Code` 节点的 `token` 字段（或保持纯文本）

## 相关概念

- [IR 节点类型体系](04-ir-node-types.md)
- [gen 管线](05-gen-pipeline.md)
- [指令处理器扩展](11-directive-handlers.md)
- [限定名与交叉引用](06-qualified-names.md)
