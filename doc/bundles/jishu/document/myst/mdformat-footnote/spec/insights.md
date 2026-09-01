---
type: spec
title: mdformat-footnote 架构洞察
description: mdformat-footnote 源码洞察记录
tags:
- mdformat-footnote
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: mdformat-footnote-source
  resource: /references/source-init.md
  title: mdformat-footnote source-init
- id: mdformat-footnote-source-1
  resource: /references/source-plugin.md
  title: mdformat-footnote source-plugin
- id: mdformat-footnote-source-2
  resource: /references/source-reorder.md
  title: mdformat-footnote source-reorder
---

# mdformat-footnote 架构洞察

## 洞察四元组

### 洞察 1：脚注编号按引用顺序重排而非定义顺序

- **陈述**：插件在 markdown-it 核心规则链的 `footnote_tail` 之前插入 `reorder_footnotes` 规则，将脚注定义按照它们在正文中被首次引用的顺序重新排列，并重新分配连续数字 ID。
- **证据**：F-010、F-023、F-028、F-029
- **反常识**：标准 markdown-it 脚注插件按定义顺序编号，但格式化后输出的脚注序号取决于引用顺序而非定义书写顺序——这意味着同一组脚注定义，改变正文引用顺序会导致编号完全变化。
- **行动**：在文档中不必在意脚注定义的排列顺序，mdformat-footnote 会自动按引用出现顺序重新编号并排列定义块。

### 洞察 2：四类脚注分类处理处理孤立脚注

- **陈述**：插件将脚注分为四类：正文引用（body_referenced）、仅嵌套引用（nested_only）、仅围栏引用（fence_only）、完全孤立（true_orphans），默认删除完全孤立的脚注。
- **证据**：F-024、F-028
- **反常识**：在代码块/fence中出现的 `[^label]` 也被识别为脚注引用（fence_only类别），即使它们不会被渲染为真正的脚注链接。这是因为重排序在AST层面操作，fence token的内容也被扫描。
- **行动**：使用 `--keep-footnote-orphans` 参数保留未引用的脚注定义；注意代码块中的脚注样式文本会影响排序结果。

### 洞察 3：内联脚注被显式禁用

- **陈述**：`update_mdit` 中先启用 footnote_plugin 紧接着调用 `mdit.disable("footnote_inline")`，禁用了内联脚注语法（`^[inline text]`）。
- **证据**：F-008、F-009
- **反常识**：插件不是"选择性启用"需要的功能，而是"先全量启用再禁用不支持的部分"——内联脚注被禁用是因为渲染器尚未支持（注释明确说明"for now"）。
- **行动**：当前版本不支持内联脚注的格式化，使用 `^[text]` 语法的脚注无法被正确处理，需使用标准的 `[^label]` + 定义块形式。

### 洞察 4：subId 重新分配实现多引用回溯支持

- **陈述**：`_reassign_subids` 函数在脚注重排后重新分配 subId（同一脚注多次引用时的出现序号），正文引用优先编号，定义内嵌套引用后编号。
- **证据**：F-031
- **反常识**：subId 的分配顺序影响 HTML 输出中 `fnref:label:N` 的回溯链接编号，但标准 Markdown 渲染中 subId 通常不可见。这个机制保证了即使脚注重排后，多引用的回溯链接仍然指向正确的引用位置。
- **行动**：普通用户无需关心 subId 机制；插件开发者在扩展脚注功能时需注意重排序后必须重新分配 subId。

## 知识地图

### 文档分组与学习路径

**入门组（2篇）**
1. `00-introduction.md` - 项目概述与安装
2. `01-plugin-configuration.md` - 插件配置与 CLI 选项

**核心组（2篇）**
3. `02-footnote-rendering.md` - 脚注渲染格式与缩进规则
4. `03-footnote-reordering.md` - 脚注排序逻辑与分类机制

### 事实-文档映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction | F-001, F-004, F-005 |
| 01-plugin-configuration | F-002, F-003, F-006, F-011, F-012, F-013, F-020, F-021, F-022 |
| 02-footnote-rendering | F-007, F-008, F-009, F-014, F-015, F-016, F-017, F-018, F-019 |
| 03-footnote-reordering | F-010, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032 |
