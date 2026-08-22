---
type: spec
title: sphinx-copybutton 源码事实清单
description: sphinx-copybutton 源码事实清单
tags:
- sphinx-copybutton
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-copybutton-source
  resource: /references/copybutton-source.md
  title: sphinx-copybutton copybutton-source
---

# sphinx-copybutton 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: `__version__ = "0.5.2"` 定义于 `sphinx_copybutton/__init__.py` L5
- F-002: `setup.py` 声明 `python_requires=">=3.7"`
- F-003: `setup.py` 声明 `install_requires=["sphinx>=1.8"]`
- F-004: 许可证为 MIT License
- F-005: 作者为 Executable Book Project
- F-006: 通过 `extensions = ['sphinx_copybutton']` 方式注册为 Sphinx 扩展（非 entry point）
- F-007: `setup(app)` 返回字典 `{"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}`

## 核心 Python 模块（sphinx_copybutton/__init__.py）

- F-008: `scb_static_path(app)` 函数将 `_static` 目录的绝对路径追加到 `app.config.html_static_path`
- F-009: `add_to_context(app, config)` 函数将配置值注入到 `config.html_context` 字典
- F-010: `setup(app)` 连接 `builder-inited` 事件到 `scb_static_path`
- F-011: `setup(app)` 连接 `config-inited` 事件到 `add_to_context`

## 配置项注册（add_config_value）

- F-012: `copybutton_prompt_text` 默认值 `""`，重建条件 `"html"`
- F-013: `copybutton_prompt_is_regexp` 默认值 `False`，重建条件 `"html"`
- F-014: `copybutton_only_copy_prompt_lines` 默认值 `True`，重建条件 `"html"`
- F-015: `copybutton_remove_prompts` 默认值 `True`，重建条件 `"html"`
- F-016: `copybutton_copy_empty_lines` 默认值 `True`，重建条件 `"html"`
- F-017: `copybutton_line_continuation_character` 默认值 `""`，重建条件 `"html"`
- F-018: `copybutton_here_doc_delimiter` 默认值 `""`，重建条件 `"html"`
- F-019: `copybutton_image_svg` 默认值 `""`，重建条件 `"html"`
- F-020: `copybutton_selector` 默认值 `"div.highlight pre"`，重建条件 `"html"`
- F-021: `copybutton_exclude` 默认值 `".linenos"`，重建条件 `"html"`
- F-022: `copybutton_image_path` 默认值 `""`，重建条件 `"html"`（已废弃）

## 静态资源注册

- F-023: `setup(app)` 调用 `app.add_css_file("copybutton.css")` 注册样式表
- F-024: `setup(app)` 调用 `app.add_js_file("clipboard.min.js")` 注册 ClipboardJS 库
- F-025: `setup(app)` 调用 `app.add_js_file("copybutton.js")` 注册主脚本

## 静态文件清单（package_data）

- F-026: `_static/copybutton.css` — 复制按钮样式
- F-027: `_static/copybutton_funcs.js` — 文本过滤与格式化函数（ES Module，使用 `export function`）
- F-028: `_static/copybutton.js_t` — Jinja2 模板化主脚本
- F-029: `_static/copy-button.svg` — 复制图标
- F-030: `_static/check-solid.svg` — 成功状态图标
- F-031: `_static/clipboard.min.js` — ClipboardJS 第三方库（通过 git submodule 引入）

## JavaScript 模板变量注入

- F-032: `copybutton_prompt_text` 通过 `{!r}` 格式化为 JavaScript 字符串字面量注入模板
- F-033: `copybutton_prompt_is_regexp`、`copybutton_only_copy_prompt_lines`、`copybutton_remove_prompts`、`copybutton_copy_empty_lines` 通过 `| lower` 过滤器转为 JavaScript 布尔值（true/false）
- F-034: `copybutton_line_continuation_character` 和 `copybutton_here_doc_delimiter` 通过 `{!r}` 格式化为字符串字面量
- F-035: `copybutton_image_svg` 直接作为 SVG 字符串注入（用户自定义图标）
- F-036: `copybutton_selector` 直接作为 CSS 选择器字符串注入
- F-037: `copybutton_format_func` 读取 `copybutton_funcs.js` 文件内容，将 `export function` 替换为 `function` 后注入模板
- F-038: `copybutton_exclude` 作为 CSS 选择器字符串注入

## 废弃处理

- F-039: `add_to_context()` 中若 `copybutton_image_path` 非空，发出 warning："copybutton_image_path is deprecated, use copybutton_image_svg"
- F-040: 废弃路径下会验证文件是否存在且后缀为 `.svg`，不存在或非 SVG 则抛出 `ValueError`

## CSS 样式（copybutton.css）

- F-041: `button.copybtn` 使用 `position: absolute; top: .3em; right: .3em;` 定位
- F-042: 按钮默认 `opacity: 0`，悬停或成功状态 `opacity: 1`
- F-043: 按钮尺寸 `width: 1.7em; height: 1.7em;`，SVG 图标 `width: 1.5em; height: 1.5em;`
- F-044: 成功状态 `button.copybtn.success` 使用绿色边框和文字 `#22863a`
- F-045: 默认配色：边框 `#1b1f2426`、背景 `#f6f8fa`、文字 `#57606a`（GitHub 风格）
- F-046: `div.highlight` 设置 `position: relative` 作为按钮定位的参照容器
- F-047: 悬停显示：`.highlight:hover button.copybtn, button.copybtn.success { opacity: 1; }`
- F-048: 打印媒体查询 `@media print` 隐藏按钮 `display: none`
- F-049: 包含 CSS-only tooltip 样式 `.o-tooltip--left`，左侧显示提示文字

## JavaScript 核心逻辑（copybutton.js_t）

- F-050: 支持 7 种语言本地化：en、es、de、fr、ru、zh-CN、it
- F-051: 语言检测通过 `document.documentElement.lang` 属性
- F-052: 本地化消息包含 `copy`、`copy_to_clipboard`、`copy_success`、`copy_failure` 四个键
- F-053: 默认复制图标为 Tabler Icons 的 copy SVG（双矩形）
- F-054: 成功图标为 Tabler Icons 的 check SVG（绿色对勾）
- F-055: `runWhenDOMLoaded(cb)` 函数处理 DOM 加载完成事件（兼容 `DOMContentLoaded` 和 `onreadystatechange`）
- F-056: 按钮 HTML 为 `<button class="copybtn o-tooltip--left" data-tooltip="复制" data-clipboard-target="#codecellN">`
- F-057: 使用 `codeCell.insertAdjacentHTML('afterend', ...)` 在代码块后面插入按钮
- F-058: ClipboardJS 初始化使用 `new ClipboardJS('.copybtn', {text: copyTargetText})`，自定义文本获取函数
- F-059: 成功回调调用 `clearSelection()`、`temporarilyChangeTooltip()`、`temporarilyChangeIcon()`
- F-060: 失败回调调用 `temporarilyChangeTooltip()` 显示失败消息
- F-061: 成功图标显示 2000ms 后恢复（`timeoutIcon = 2000`），success class 在 1500ms 后移除（`timeoutSuccessClass = 1500`）
- F-062: 若 ClipboardJS 未加载，使用 `setTimeout(addCopyButtonToCodeCells, 250)` 轮询等待
- F-063: 代码块 ID 格式为 `codecell{N}`（N 为索引）

## 文本处理函数（copybutton_funcs.js）

- F-064: `escapeRegExp(string)` 函数转义正则表达式特殊字符 `[.*+?^${}()|[\]\\]`
- F-065: `filterText(target, exclude)` 函数克隆目标节点，移除匹配 `exclude` CSS 选择器的子节点，返回 `innerText`
- F-066: `formatCopyText(textContent, copybuttonPromptText, isRegexp, onlyCopyPromptLines, removePrompts, copyEmptyLines, lineContinuationChar, hereDocDelim)` 为核心文本格式化函数
- F-067: 正则构建：`isRegexp` 为 true 时直接使用 `copybuttonPromptText`，否则调用 `escapeRegExp()` 转义
- F-068: 逐行处理逻辑：匹配 prompt 的行、行续接字符（`lineContinuationChar`）、HERE 文档（`hereDocDelim`）
- F-069: `onlyCopyPromptLines = true` 时只复制含 prompt 的行（空行除外）
- F-070: `removePrompts = true` 时从匹配行中移除 prompt 前缀
- F-071: `copyEmptyLines = true` 时保留空行
- F-072: 行续接逻辑：行以 `lineContinuationChar` 结尾时标记 `gotLineCont = true`，下一行也被视为 prompt 行
- F-073: HERE 文档逻辑：行包含 `hereDocDelim` 时切换 `gotHereDoc` 状态，其间的行也被处理
- F-074: 若没有任何行匹配 prompt，直接返回原始文本（不做任何处理）
- F-075: 返回前移除末尾换行符，避免粘贴时自动执行
