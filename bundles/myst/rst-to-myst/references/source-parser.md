---
type: Reference
title: rst-to-myst RST 解析器模块
description: parser.py 实现 LosslessRSTParser 和自定义 docutils Transforms。
tags: [source-code, parser, docutils, rst, ast]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-parser
    resource: /spec/facts.md
    title: rst-to-myst 事实清单
---

## 模块概览

`rst_to_myst/parser.py` 实现 RST 到 docutils AST 的无损解析（218行）。

## 核心类

### `LosslessRSTParser(Parser)`

定制的 RST 解析器，继承自 `docutils.parsers.rst.Parser`。与标准解析器的关键区别：
- `inliner` 设置为 `InlinerMyst()` 实例
- `state_classes` 通过 `get_state_classes()` 获取自定义状态类
- 注释明确说明"roles and directives are not run"——不执行指令的 run 方法，保留原始结构

### `IndirectHyperlinks(Transform)`

解析间接超链接目标，但不解析实际引用（不替换 refname）。

### `StripFootnoteLabel(Transform)`

遍历所有 footnote 和 citation 节点，移除第一个 label 子节点（脚注编号标签在转换中不需要）。

### `ResolveListItems(Transform)`

为 bullet_list 和 enumerated_list 的子 list_item 传播属性：
- bullet_list：设置 `style="bullet"` 和 `prefix="bullet_char "`
- enumerated_list：设置 `style="enumerated"` 和 `prefix="N. "`（支持 start 属性）

支持的枚举类型：arabic、lowerroman、upperroman、loweralpha、upperalpha。
TODO 注释表明 markdown-it 仅支持数字编号。

### `FrontMatter(Transform)`

将文档开头的 field_list 转换为 `FrontMatterNode`：
- 跳过 PreBibliographic 节点（如注释）
- 支持 section 内的 field_list
- 需要 `document.settings.front_matter = True` 才生效

## 核心函数

### `to_docutils_ast(...)`

将 RST 文本转换为 docutils AST 的主函数：

1. 创建 docutils 设置（report_level=2/warning, halt_level=4/severe）
2. 编译 namespace（指令/角色查找表），可通过参数传入预编译 namespace
3. 加载默认指令数据（directives.yml），合并自定义 conversions
4. 创建 LosslessRSTParser 并执行解析
5. 按顺序应用 Transforms：PropagateTargets → FrontMatter → AnonymousHyperlinks → Footnotes → StripFootnoteLabel → ResolveListItems
6. 返回 `(document, warning_stream)` 元组

### `_load_directive_data()`

使用 `@lru_cache` 缓存从 `rst_to_myst/data/directives.yml` 加载的指令转换映射数据。

## 源码位置

- 文件路径：`rst_to_myst/parser.py`
- 代码行数：218行

## 相关概念

- [三阶段转换流水线架构](/concepts/03-conversion-pipeline.md)
- [LosslessRSTParser 与自定义 Transform](/concepts/04-lossless-parser.md)
