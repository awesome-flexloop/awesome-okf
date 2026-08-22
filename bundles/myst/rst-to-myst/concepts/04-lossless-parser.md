---
type: Concept
title: LosslessRSTParser 与自定义 Transform
description: rst-to-myst 的无损 RST 解析器和 docutils AST 变换机制。
tags: [parser, docutils, transform, lossless, ast]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-parser
    resource: /references/source-parser.md
    title: rst-to-myst RST 解析器模块
---

## 为什么需要无损解析

标准 docutils RST 解析器在解析过程中会执行指令的 `run()` 方法和角色的处理函数，将指令/角色替换为它们生成的 docutils 节点。这对于渲染是正确的，但对于格式转换来说是破坏性的——执行后会丢失原始的指令名称、选项和内容结构，无法还原为 MyST 指令语法。

`LosslessRSTParser` 的核心设计原则是"无损"：保留指令和角色的原始结构，不执行它们的 run 方法，使后续阶段能够将它们直接翻译为 MyST 的等价语法。

## LosslessRSTParser

`LosslessRSTParser` 继承自 `docutils.parsers.rst.Parser`，重写了初始化逻辑：

```python
class LosslessRSTParser(Parser):
    def __init__(self):
        self.initial_state = "Body"
        self.state_classes = get_state_classes()
        for state_class in self.state_classes:
            state_class.nested_sm_cache = []
        self.inliner = InlinerMyst()
```

### 与标准 Parser 的区别

1. **InlinerMyst**：使用自定义的 InlinerMyst 替代标准 Inliner，处理角色（role）的识别而不执行角色函数
2. **自定义状态类**：`get_state_classes()` 返回定制的状态类集合，用于指令的识别但不执行 run 方法
3. **缓存清除**：每次初始化时清空状态类的 `nested_sm_cache`，避免上次解析的残留状态

## 自定义节点类型

为了在 AST 中保留指令和角色的原始信息，rst-to-myst 定义了以下自定义节点类型：

| 节点类 | 继承自 | 用途 |
|--------|--------|------|
| `UnprocessedText` | `nodes.Text` | 不做转义处理的文本 |
| `EvalRstNode` | `nodes.Element` | eval-rst 替换内容 |
| `RoleNode` | `nodes.Element` | RST 角色 |
| `DirectiveNode` | `nodes.Element` | RST 指令（含 name/module/conversion/options_list 属性） |
| `ArgumentNode` | `nodes.Element` | 指令参数 |
| `ContentNode` | `nodes.Element` | 指令内容 |
| `FrontMatterNode` | `nodes.Element` | 文档 front matter |

### DirectiveNode 结构

`DirectiveNode` 是最重要的自定义节点，存储指令的完整信息：

```python
DirectiveNode(
    rawsource,
    name="directive-name",        # 指令名称
    module="full.module.path",    # 指令类的模块路径
    conversion="conversion-type", # 转换类型（来自 directives.yml）
    options_list=[("key", "val")], # 选项键值对列表
)
```

DirectiveNode 可以包含可选的 ArgumentNode 子节点（指令参数）和 ContentNode 子节点（指令内容）。

## 自定义 Transforms

docutils Transform 是在解析完成后对 AST 进行修改的机制。rst-to-myst 实现了 4 个自定义 Transform。

### StripFootnoteLabel

```python
class StripFootnoteLabel(Transform):
    def apply(self):
        for node in self.document.traverse(
            lambda n: isinstance(n, (nodes.footnote, nodes.citation))
        ):
            if node.children and isinstance(node.children[0], nodes.label):
                node.pop(0)
```

**作用**：移除脚注（footnote）和引用（citation）节点的第一个 label 子节点。RST 脚注可能以显式标签（如 `[1]`、`[#note]`）开头，转换时不需要这些标签（MyST 使用自动编号或标签引用）。

### ResolveListItems

```python
class ResolveListItems(Transform):
    def apply(self):
        # 为 bullet_list 的 list_item 设置 style="bullet", prefix="• "
        # 为 enumerated_list 的 list_item 设置 style="enumerated", prefix="1. "
        # 支持 start 属性（列表起始编号）
```

**作用**：为列表项传播样式和前缀属性。标准 docutils 列表项不直接存储前缀符号，此 Transform 计算并附加这些信息供渲染阶段使用。

支持的枚举编号类型：

| 类型 | 转换函数 | 示例 |
|------|---------|------|
| arabic | `lambda i: i` | 1, 2, 3 |
| lowerroman | `roman.toRoman(i).lower()` | i, ii, iii |
| upperroman | `roman.toRoman(i).upper()` | I, II, III |
| loweralpha | `chr(ord('a') + i - 1)` | a, b, c |
| upperalpha | 同上 `.upper()` | A, B, C |

> 注意：markdown-it 目前仅支持数字编号，非数字编号类型在 TODO 中标记为待支持。

### FrontMatter

```python
class FrontMatter(Transform):
    def apply(self):
        if not self.document.settings.front_matter:
            return
        # 跳过 PreBibliographic 节点（如注释）
        # 如果第一个非前置节点是 field_list
        # 或者 section 的第一个非前置子节点是 field_list
        # 将其替换为 FrontMatterNode
```

**作用**：将文档开头的 field_list（如 `:title: xxx`）提取为 FrontMatterNode，后续渲染为 YAML front matter（`---` 包裹）。这个行为可通过 `front_matter=False` 参数禁用。

### IndirectHyperlinks（未完全实现）

```python
class IndirectHyperlinks(Transform):
    def apply(self):
        for target in self.document.indirect_targets:
            if not target.resolved:
                self.resolve_indirect_target(target)
            # 不解析实际引用（self.resolve_indirect_references）
```

**作用**：解析间接超链接目标，但不解析引用本身（保留 refname 供后续处理）。

## Transform 执行顺序

`to_docutils_ast()` 按以下顺序应用 Transform（顺序重要）：

1. `PropagateTargets`（docutils 内置）- 传播空目标到后续元素
2. `FrontMatter`（自定义）- 提取 front matter
3. `AnonymousHyperlinks`（docutils 内置）- 链接匿名引用
4. `Footnotes`（docutils 内置）- 为自动编号脚注分配编号
5. `StripFootnoteLabel`（自定义）- 移除脚注标签
6. `ResolveListItems`（自定义）- 解析列表项属性

## 指令数据加载

默认指令转换映射从包数据文件 `rst_to_myst/data/directives.yml` 加载，使用 `@lru_cache` 缓存避免重复读取。用户可通过 `conversions` 参数覆盖或追加映射。

## 相关概念

- [三阶段转换流水线架构](/concepts/03-conversion-pipeline.md)
- [MarkdownItRenderer 与 AST→Token 遍历](/concepts/06-token-rendering.md)
- [指令转换机制与 directives.yml 映射](/concepts/05-directive-conversion.md)
