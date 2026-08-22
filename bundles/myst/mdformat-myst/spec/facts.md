---
type: spec
title: mdformat-myst 事实清单
description: mdformat-myst 源码事实清单
tags:
- mdformat-myst
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdformat-myst-source
  resource: /references/source-directives.md
  title: mdformat-myst source-directives
- id: mdformat-myst-source-1
  resource: /references/source-init.md
  title: mdformat-myst source-init
- id: mdformat-myst-source-2
  resource: /references/source-plugin.md
  title: mdformat-myst source-plugin
---

# mdformat-myst 事实清单

> 零推断事实采集，所有事实可在源码中直接验证。

## 包元数据

- **F-001**: 包版本为 `0.3.0`，定义于 `mdformat_myst/__init__.py:3`
- **F-002**: 模块入口点注册为 `mdformat.parser_extension` 组下的 `myst = "mdformat_myst.plugin"`，定义于 `pyproject.toml:38-39`
- **F-003**: 要求 Python 版本 `>=3.10`，定义于 `pyproject.toml:21`
- **F-004**: 运行时依赖包含 `mdformat >=0.7.0`、`mdit-py-plugins >=0.3.0`、`mdformat-front-matters >= 1.0.0`、`mdformat-footnote >=0.1.1`、`mdformat-gfm >=1.0.0`、`ruamel.yaml >=0.16.0`，定义于 `pyproject.toml:22-29`

## 插件接口实现

- **F-005**: 定义 `update_mdit(mdit: MarkdownIt) -> None` 函数，位于 `plugin.py:19-53`
- **F-006**: `update_mdit` 函数中启用 mdformat 内置插件：tables、front_matters、footnote，位于 `plugin.py:21-36`
- **F-007**: `update_mdit` 函数中调用 `mdit.use(myst_role_plugin)` 启用 MyST 角色扩展，位于 `plugin.py:39`
- **F-008**: `update_mdit` 函数中调用 `mdit.use(myst_block_plugin)` 启用 MyST 块扩展（含 LineComment、BlockBreak、Target 语法），位于 `plugin.py:43`
- **F-009**: `update_mdit` 函数中调用 `mdit.use(dollarmath_plugin)` 启用美元数学公式扩展，位于 `plugin.py:46`
- **F-010**: `update_mdit` 函数中调用 `mdit.add_render_rule("fence", render_fence_html)` 和 `mdit.add_render_rule("code_block", render_fence_html)` 覆盖 fence 和 code_block 的 HTML 渲染，位于 `plugin.py:52-53`

## 渲染器映射

- **F-011**: `RENDERERS` 字典映射以下 token 类型到渲染函数，位于 `plugin.py:147-157`：
  - `blockquote` → `_math_block_safe_blockquote_renderer`
  - `myst_role` → `_role_renderer`
  - `myst_line_comment` → `_comment_renderer`
  - `myst_block_break` → `_blockbreak_renderer`
  - `myst_target` → `_target_renderer`
  - `math_inline` → `_math_inline_renderer`
  - `math_block_label` → `_math_block_label_renderer`
  - `math_block` → `_math_block_renderer`
  - `fence` → `fence`（从 `_directives.py` 导入）
- **F-012**: `POSTPROCESSORS` 字典映射 `paragraph` → `_escape_paragraph` 和 `text` → `_escape_text`，位于 `plugin.py:158`

## 渲染函数实现

- **F-013**: `_role_renderer` 输出格式为 `{角色名}` + 反引号包裹的内容，位于 `plugin.py:56-59`
- **F-014**: `_comment_renderer` 输出格式为 `%` + 内容，换行符替换为 `\n%`，位于 `plugin.py:62-63`
- **F-015**: `_blockbreak_renderer` 输出格式为 `+++`，如有内容则追加空格和内容，位于 `plugin.py:66-70`
- **F-016**: `_target_renderer` 输出格式为 `(内容)=`，位于 `plugin.py:73-74`
- **F-017**: `_math_inline_renderer` 输出格式为 `$内容$`，位于 `plugin.py:77-78`
- **F-018**: `_math_block_renderer` 输出格式为 `$$内容$$`，缩进宽度>0时调用 `textwrap.dedent` 处理，位于 `plugin.py:81-85`
- **F-019**: `_math_block_label_renderer` 在 `_math_block_renderer` 输出后追加 ` (标签)`，位于 `plugin.py:88-89`

## 转义处理

- **F-020**: 正则表达式 `_TARGET_PATTERN = re.compile(r"^\s*\(.+\)=\s*$")` 用于匹配目标语法行，位于 `plugin.py:15`
- **F-021**: 正则表达式 `_ROLE_NAME_PATTERN = re.compile(r"({[a-zA-Z0-9_\-+:]+})")` 用于匹配角色名，位于 `plugin.py:16`
- **F-022**: `_escape_paragraph` 函数转义三种情况：三个及以上 `+` 开头行、`%` 开头行、匹配 `_TARGET_PATTERN` 的行，位于 `plugin.py:116-134`
- **F-023**: `_escape_text` 函数转义两种情况：MyST 角色名（前缀反斜杠）、美元符号 `$`，位于 `plugin.py:137-144`

## 指令（Directive）处理

- **F-024**: `_directives.py` 中定义 `fence` 渲染函数，位于 `_directives.py:30-71`
- **F-025**: `fence` 函数中，当 info 字符串以 `{` 开头且以 `}` 结尾时，调用 `format_directive_content` 格式化指令内容，位于 `_directives.py:63-64`
- **F-026**: `format_directive_content(raw_content: str) -> str` 函数使用 `ruamel.yaml` 格式化指令选项 YAML，位于 `_directives.py:74-99`
- **F-027**: `parse_opts_and_content(raw_content: str) -> tuple[str, str] | None` 函数解析两种选项格式：`---` 包裹的 YAML 块和 `:` 开头的选项行，位于 `_directives.py:102-133`
- **F-028**: `render_fence_html` 函数返回空字符串，用于绕过 mdformat 的 AST 验证，位于 `_directives.py:136-139`
- **F-029**: `longest_consecutive_sequence(seq: str, char: str) -> int` 函数返回字符串中指定字符的最长连续序列长度，位于 `_directives.py:14-27`
- **F-030**: ruamel.yaml 配置为 mapping 缩进 2、sequence 缩进 4、offset 2，位于 `_directives.py:10-11`
