---
type: spec
title: sphinx-togglebutton 源码事实清单
description: sphinx-togglebutton 源码事实清单
tags:
- sphinx-togglebutton
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-togglebutton-source
  resource: /references/togglebutton-source.md
  title: sphinx-togglebutton togglebutton-source
---

# sphinx-togglebutton 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 版本号 `__version__ = "0.4.5"`
- F-002: 包名为 `sphinx-togglebutton`，作者 Chris Holdgraf
- F-003: 许可证为 MIT License
- F-004: setup.cfg 中声明依赖 `sphinx` 和 `docutils`
- F-005: 包数据包含 `_static/togglebutton.css`、`_static/togglebutton.js`、翻译文件
- F-006: 消息目录名 `MESSAGE_CATALOG_NAME = "togglebutton"`，支持 30+ 种语言国际化

## 核心 Python 模块（sphinx_togglebutton/__init__.py）

- F-007: `st_static_path(app)` 函数将包内 `_static` 目录追加到 `app.config.html_static_path`
- F-008: `initialize_js_assets(app, config)` 通过 `app.add_js_file(None, body=...)` 向页面注入内联 JS 变量：`toggleHintShow`、`toggleHintHide`、`toggleOpenOnPrint`，并加载 `togglebutton.js`
- F-009: `insert_custom_selection_config(app)` 读取 `app.config["togglebutton_selector"]` 配置，注入 JS 全局变量 `togglebuttonSelector`
- F-010: 定义 `class Toggle(Directive)`，继承自 `docutils.parsers.rst.Directive`
- F-011: Toggle 指令 `optional_arguments = 1`，`final_argument_whitespace = True`，`has_content = True`
- F-012: Toggle 指令选项规范：`{"id": directives.unchanged, "show": directives.flag}`
- F-013: Toggle.run() 创建 `nodes.container(classes=["toggle"])`，若有 `:show:` 选项则添加 `toggle-shown` 类
- F-014: Toggle.run() 使用 `self.state.nested_parse()` 解析指令内容到容器节点

## 配置项（setup 函数注册）

- F-015: `togglebutton_selector` 默认值为 `".toggle, .admonition.dropdown"`，重建类型为 `"html"`
- F-016: `togglebutton_hint` 默认值为国际化翻译后的 `"Click to show"`
- F-017: `togglebutton_hint_hide` 默认值为国际化翻译后的 `"Click to hide"`
- F-018: `togglebutton_open_on_print` 默认值为 `True`，控制打印时是否展开折叠内容

## setup 函数

- F-019: setup() 中通过 `app.add_message_catalog()` 注册翻译消息目录
- F-020: setup() 通过 `app.connect("builder-inited", st_static_path)` 连接静态路径事件
- F-021: setup() 通过 `app.add_css_file("togglebutton.css")` 添加样式表
- F-022: setup() 注册 4 个配置值（selector、hint、hint_hide、open_on_print）
- F-023: setup() 连接 `builder-inited` 到 `insert_custom_selection_config`
- F-024: setup() 连接 `config-inited` 到 `initialize_js_assets`
- F-025: setup() 通过 `app.add_directive("toggle", Toggle)` 注册 `.. toggle::` 指令
- F-026: setup() 返回 `{"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}`

## 前端 JavaScript（togglebutton.js）

- F-027: JS 定义内联 SVG chevron 图标 `toggleChevron`（右箭头折线）
- F-028: `initToggleItems()` 函数通过 `document.querySelectorAll(togglebuttonSelector)` 查找所有可折叠元素
- F-029: 对 admonition 类型元素：在 `.admonition-title` 内插入 `<button class="toggle-button">`，按钮含 `data-target`、`data-button`、`aria-expanded` 属性
- F-030: admonition 的整个标题栏（`.admonition-title`）都可点击触发折叠/展开
- F-031: 对非 admonition 元素：用 `<details class="toggle-details"><summary>` 原生 HTML 元素包装
- F-032: `toggleHidden(button)` 函数通过切换 `toggle-hidden` CSS 类控制显示/隐藏，同步更新 `aria-expanded` 和提示文本
- F-033: 非 admonition 折叠块的 summary 文本在展开/折叠间切换 `toggleHintShow`/`toggleHintHide`
- F-034: 打印事件处理：`beforeprint` 时展开所有折叠内容，`afterprint` 时恢复折叠状态
- F-035: 使用 MutationObserver 监听 `.toggle` 元素的 class 属性变化，同步按钮提示文本
- F-036: 提供全局函数 `syncAllToggleHints()` 供外部扩展调用同步按钮状态
