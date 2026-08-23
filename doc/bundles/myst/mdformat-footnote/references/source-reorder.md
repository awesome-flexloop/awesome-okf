---
type: Reference
title: mdformat-footnote 脚注重排序逻辑
description: _reorder.py 实现脚注分类、依赖图构建、重排序和 ID 重新分配。
tags: [source-code, footnote, reordering, algorithm]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-reorder
    resource: /spec/facts.md
    title: mdformat-footnote 事实清单
---

## 模块概览

`mdformat_footnote/_reorder.py` 实现脚注 ID 规范化和重排序逻辑（285行）。

## 核心数据类

### `_FootnoteCategories`

脚注四分类容器：
- `body_referenced: list[tuple[int, str, str]]` - 正文中引用的脚注（old_id, label_key, label）
- `nested_only: set[str]` - 仅在其他脚注定义内引用的脚注
- `fence_only: list[str]` - 仅在代码围栏中引用的脚注（按出现顺序）
- `true_orphans: list[str]` - 从未被引用的真正孤立脚注

### `_ReorderState`

重排序过程的可变状态：
- `old_list: dict` - 原始脚注定义字典
- `refs: dict` - 原始引用字典
- `new_list: dict` - 重排后的脚注定义字典
- `old_to_new_id: dict[int, int]` - 旧ID到新ID的映射
- `processed: set[str]` - 已处理的标签集合
- `new_id: int` - 下一个可用的新ID

## 核心函数

### `reorder_footnotes_by_definition(state, keep_orphans=False)`

入口函数，执行完整重排序流程：
1. 从 `state.env["footnotes"]` 提取 refs 和 list
2. 构建脚注间嵌套引用依赖图
3. 收集代码围栏中的脚注引用
4. 将脚注分类为四类
5. 若不保留孤立脚注，删除 true_orphans
6. 按顺序构建新列表：body_referenced → 嵌套引用 → nested_only → fence_only → orphans
7. 更新 token 中的脚注 ID
8. 重新分配 subId（多次引用序号）

### `_build_dependency_graph(tokens)`

构建脚注间的依赖图：遍历 tokens，在 footnote_reference_open/close 之间收集嵌套的 footnote_ref，记录哪个脚注引用了哪些其他脚注。

### `_categorize_footnotes(refs, footnote_deps, refs_in_fences)`

分类逻辑：
- `old_id >= 0`：body_referenced（正文引用）
- `old_id < 0` 且在其他脚注中被引用：nested_only
- `old_id < 0` 且仅在围栏中引用：fence_only
- 其余：true_orphans

### `_reassign_subids(tokens, refs, footnote_list)`

重新分配 subId：
1. 将引用分为正文引用（body_refs）和定义内引用（def_refs）
2. 先为正文引用分配连续 subId（按出现顺序）
3. 再为各脚注定义内的嵌套引用分配 subId
4. 更新脚注的 `count` 属性

## 正则表达式

- `_FOOTNOTE_REF_PATTERN = re.compile(r"\[\^([^\]]+)\]")` - 匹配脚注引用

## 源码位置

- 文件路径：`mdformat_footnote/_reorder.py`
- 代码行数：285行

## 相关概念

- [脚注排序逻辑与分类机制](/concepts/03-footnote-reordering.md)
