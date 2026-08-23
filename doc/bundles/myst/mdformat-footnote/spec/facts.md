---
type: spec
title: mdformat-footnote 事实清单
description: mdformat-footnote 源码事实清单
tags:
- mdformat-footnote
- spec
- facts
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

# mdformat-footnote 事实清单

> 零推断事实采集，所有事实可在源码中直接验证。

## 包元数据

- **F-001**: 包版本为 `0.1.3`，定义于 `mdformat_footnote/__init__.py:3`
- **F-002**: 插件名称为 `footnote`，定义于 `__plugin_name__`，位于 `__init__.py:4`
- **F-003**: 模块入口点注册为 `mdformat.parser_extension` 组下的 `footnote = "mdformat_footnote"`，定义于 `pyproject.toml:33-34`
- **F-004**: 要求 Python 版本 `>=3.10`，定义于 `pyproject.toml:21`
- **F-005**: 运行时依赖包含 `mdformat >=0.7.0`、`mdit-py-plugins >=0.4.0`，定义于 `pyproject.toml:22-24`
- **F-006**: `__init__.py` 导出 `RENDERERS`、`add_cli_argument_group`、`update_mdit` 三个名称，位于 `__init__.py:6`

## 插件接口实现

- **F-007**: 定义 `update_mdit(mdit: MarkdownIt) -> None` 函数，位于 `plugin.py:39-49`
- **F-008**: `update_mdit` 中调用 `mdit.use(footnote_plugin)` 启用脚注插件，位于 `plugin.py:41`
- **F-009**: `update_mdit` 中调用 `mdit.disable("footnote_inline")` 禁用内联脚注，位于 `plugin.py:44`
- **F-010**: `update_mdit` 中通过 `mdit.core.ruler.before("footnote_tail", "reorder_footnotes", reorder_fn)` 在 `footnote_tail` 规则前插入脚注重排序规则，位于 `plugin.py:49`

## CLI 参数

- **F-011**: 定义 `add_cli_argument_group(group: argparse._ArgumentGroup) -> None` 函数，位于 `plugin.py:22-36`
- **F-012**: 添加 `--keep-footnote-orphans` 命令行参数，`action="store_const"`，`const=True`，`dest="keep_orphans"`，位于 `plugin.py:27-36`
- **F-013**: 默认行为是移除未引用的脚注定义，位于 `plugin.py:33-34`

## 渲染器映射

- **F-014**: `RENDERERS` 字典映射以下 token 类型，位于 `plugin.py:90-94`：
  - `footnote` → `_footnote_renderer`
  - `footnote_ref` → `_footnote_ref_renderer`
  - `footnote_block` → `_render_children`

## 渲染函数实现

- **F-015**: `_footnote_ref_renderer` 输出格式为 `[^label]`，位于 `plugin.py:52-53`
- **F-016**: `_footnote_renderer` 输出首行格式为 `[^label]:`，后续内容缩进 4 空格，位于 `plugin.py:56-83`
- **F-017**: `_footnote_renderer` 中排除 `footnote_anchor` 类型子节点，位于 `plugin.py:60`
- **F-018**: `_footnote_renderer` 对首段首行使用与 label 等长+1 的缩进上下文，其余元素使用 4 空格缩进，位于 `plugin.py:63-76`
- **F-019**: `_render_children` 函数将子节点用双换行 `\n\n` 连接，位于 `plugin.py:86-87`

## 配置辅助

- **F-020**: `get_conf(options: ContextOptions, key: str) -> bool | str | int | None` 函数读取配置，位于 `_helpers.py:13-16`
- **F-021**: 配置读取优先级：先从 `options["mdformat"][key]` 读取，再从 `options["mdformat"]["plugin"][__plugin_name__][key]` 读取，位于 `_helpers.py:15-16`
- **F-022**: `_keep_orphans(options: ContextOptions) -> bool` 函数返回是否保留孤立脚注，默认 `False`，位于 `plugin.py:17-19`

## 脚注重排序逻辑

- **F-023**: `reorder_footnotes_by_definition(state: StateCore, keep_orphans: bool = False) -> None` 是核心重排序函数，位于 `_reorder.py:263-285`
- **F-024**: `_FootnoteCategories` 数据类包含 `body_referenced`、`nested_only`、`fence_only`、`true_orphans` 四个分类，位于 `_reorder.py:13-24`
- **F-025**: `_ReorderState` 数据类维护 `old_list`、`refs`、`new_list`、`old_to_new_id`、`processed`、`new_id` 状态，位于 `_reorder.py:27-65`
- **F-026**: `_collect_refs_in_fences(tokens: list) -> list[str]` 收集代码围栏中引用的脚注标签，位于 `_reorder.py:68-80`
- **F-027**: `_build_dependency_graph(tokens: list) -> dict[str, set[str]]` 构建脚注间的嵌套引用依赖图，位于 `_reorder.py:83-99`
- **F-028**: 脚注分类逻辑：正文引用的→body_referenced、仅在其他脚注内引用的→nested_only、仅在围栏内引用的→fence_only、从未引用的→true_orphans，位于 `_reorder.py:110-146`
- **F-029**: 重排序顺序：body_referenced（按出现顺序）→每个脚注的嵌套引用→nested_only→fence_only→true_orphans（如保留），位于 `_reorder.py:161-186`
- **F-030**: `_update_token_ids(tokens: list, old_to_new_id: dict[int, int])` 递归更新 token 中的脚注 ID 映射，位于 `_reorder.py:189-196`
- **F-031**: `_reassign_subids(tokens: list, refs: dict, footnote_list: dict)` 按输出顺序重新分配 subId（正文引用优先，其次定义内引用），位于 `_reorder.py:229-243`
- **F-032**: `_FOOTNOTE_REF_PATTERN = re.compile(r"\[\^([^\]]+)\]")` 用于匹配脚注引用，位于 `_reorder.py:10`
