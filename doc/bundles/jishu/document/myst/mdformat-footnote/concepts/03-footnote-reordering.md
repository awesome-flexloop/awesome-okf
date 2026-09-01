---
type: Concept
title: 脚注排序逻辑与分类机制
description: mdformat-footnote 如何将脚注按引用顺序重排、处理嵌套引用和孤立脚注。
tags: [footnote, reordering, classification, dependency-graph, orphans]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-reorder
    resource: /references/source-reorder.md
    title: mdformat-footnote 脚注重排序逻辑
---

## 为什么需要重排序

标准 markdown-it 脚注插件按照脚注定义在文档中出现的顺序分配数字编号。但在实际写作中，作者可能不按引用顺序书写脚注定义，或者在修改文档时插入/删除引用导致编号混乱。mdformat-footnote 在解析阶段之后、渲染阶段之前，通过 core ruler 规则插入重排序逻辑，确保输出的脚注始终按正文中首次引用的顺序编号。

## 规则插入位置

重排序规则通过以下方式插入到 markdown-it 的核心规则链中：

```python
mdit.core.ruler.before("footnote_tail", "reorder_footnotes", reorder_fn)
```

这表示在 `footnote_tail` 规则（markdown-it 脚注插件自带的后处理规则）之前执行 `reorder_footnotes` 规则。`reorder_fn` 是 `reorder_footnotes_by_definition` 函数的 partial，绑定了 `keep_orphans` 参数。

## 脚注四分类

重排序的第一步是将所有脚注引用分为四类，这由 `_categorize_footnotes` 函数实现：

| 分类 | 条件 | 排序位置 |
|------|------|---------|
| **body_referenced** | old_id >= 0（正文中直接引用） | 最优先，按首次引用位置排序 |
| **nested_only** | old_id < 0，仅在其他脚注定义内被引用 | 正文引用之后 |
| **fence_only** | old_id < 0，仅在代码围栏内被引用 | nested_only 之后，按围栏中出现顺序 |
| **true_orphans** | 从未被任何地方引用 | 最后（或删除） |

### old_id 的含义

在 markdown-it 脚注插件中，`old_id >= 0` 表示该引用出现在正文（非脚注定义内、非围栏内），`old_id < 0` 表示该引用的首次出现不在正文流中。

### 依赖图构建

`_build_dependency_graph` 函数遍历 tokens，构建脚注间的嵌套引用关系：
- 进入 `footnote_reference_open` token 时记录当前脚注标签
- 在该脚注定义内遇到 `footnote_ref` 时，记录依赖关系（脚注A引用了脚注B）
- 退出 `footnote_reference_close` 时结束当前脚注上下文

依赖图类型为 `dict[str, set[str]]`，键是脚注标签，值是该脚注直接引用的其他脚注标签集合。

### 围栏引用收集

`_collect_refs_in_fences` 函数扫描所有 fence 类型 token 的内容，用正则 `\[\^([^\]]+)\]` 匹配脚注引用，收集仅在代码块中出现的脚注标签。

## 重排序流程

`_build_reordered_list` 函数按照以下顺序构建新的脚注列表：

1. **正文引用的脚注**：按首次在正文中出现的顺序（body_referenced 已按 old_id 排序）
   - 每添加一个正文引用的脚注，立即递归处理它嵌套引用的脚注（深度优先）
2. **仅嵌套引用的脚注**：nested_only 集合中的脚注
3. **仅围栏引用的脚注**：fence_only 列表中的脚注（按围栏中出现顺序）
4. **孤立脚注**：如果 `keep_orphans=True`，追加 true_orphans

### 嵌套脚注处理

`_process_nested_for_parent` 函数递归处理脚注的嵌套引用：当一个脚注被加入新列表后，它所引用的其他脚注（不在 skip_labels 中的）也会被立即添加。这确保了如果脚注 A 引用了脚注 B，B 会紧跟在 A 之后出现。

skip_labels 包含 body_labels（正文引用的脚注，已在主循环处理）和 true_orphans（孤立脚注不需要嵌套处理）。

## ID 和 subId 更新

重排后需要更新 token 中存储的 ID 引用：

### _update_token_ids

递归遍历所有 token，更新 `footnote_ref` 和 `footnote_anchor` 类型 token 的 `meta["id"]` 字段，将旧 ID 映射为新 ID。

### _reassign_subids

subId 用于同一脚注被多次引用时区分回溯链接。重排后需要重新分配：

1. 先将所有引用分为正文引用（body_refs）和定义内引用（def_refs）
2. 按输出顺序为正文引用分配连续 subId（从0开始）
3. 然后为各脚注定义内的引用分配 subId
4. 更新脚注的 `count` 属性为总引用次数

这种分配方式确保正文引用的 subId 优先，符合阅读顺序。

## 重排序状态管理

`_ReorderState` 数据类管理重排序过程中的可变状态：

- `old_list`/`refs`：原始脚注数据
- `new_list`：重排后的脚注定义
- `old_to_new_id`：旧ID到新ID的映射表
- `processed`：已处理的标签集合（防重复）
- `new_id`：下一个可用的新ID（从0递增）

## 相关概念

- [脚注渲染格式与缩进规则](02-footnote-rendering.md)
- [插件配置与 CLI 选项](01-plugin-configuration.md)
