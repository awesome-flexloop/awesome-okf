---
type: spec
title: sphinx-tabs 源码事实清单
description: sphinx-tabs 源码事实清单
tags:
- sphinx-tabs
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-tabs-source
  resource: /references/tabs-source.md
  title: sphinx-tabs tabs-source
---

# sphinx-tabs 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 版本号 `__version__ = "3.6.0.dev"`
- F-002: 包名为 `sphinx-tabs`，属于 Executable Books 生态
- F-003: 核心源码仅 2 个 Python 文件：`__init__.py`（1行版本号）+ `tabs.py`（348行）
- F-004: 静态资源：`static/tabs.css` + `static/tabs.js`

## 自定义节点类型（tabs.py）

- F-005: `SphinxTabsContainer(nodes.container)` 继承自 container，tagname 为 `"div"`
- F-006: `SphinxTabsPanel(nodes.container)` 继承自 container，tagname 为 `"div"`
- F-007: `SphinxTabsTab(nodes.paragraph)` 继承自 paragraph，tagname 为 `"button"`
- F-008: `SphinxTabsTablist(nodes.container)` 继承自 container，tagname 为 `"div"`
- F-009: `visit()`/`depart()` 函数为自定义节点提供通用 HTML 渲染：通过 `node.tagname` 动态生成标签，复制属性，清理内部属性（classes/ids/names/dupnames/backrefs）

## TabsDirective（顶层容器指令）

- F-010: `class TabsDirective(SphinxDirective)`，`has_content = True`
- F-011: run() 创建 `nodes.container(type="tab-element")`，添加 CSS 类 `"sphinx-tabs"`
- F-012: 使用 `self.env.temp_data` 维护标签页状态：`next_tabs_id`（自增ID计数器）、`tabs_stack`（嵌套标签栈）
- F-013: 每个 tabs 块有唯一 `tabs_id`，状态存储在 `self.env.temp_data[f"tabs_{tabs_id}"]` 中
- F-014: 状态字典包含：`tab_ids`（已用标签ID列表）、`tab_titles`（(data_tab, tab_name) 元组列表）、`is_first_tab`（是否第一个标签标志）
- F-015: 解析完内容后，对兼容 builder 创建 `SphinxTabsTablist` 节点，设置 `role="tablist"` 和 `aria-label="Tabbed content"`
- F-016: 若 `sphinx_tabs_disable_tab_closing` 配置为 False（默认），tablist 添加 `"closeable"` 类
- F-017: 遍历 `tab_titles` 设置 ARIA 属性：`role="tab"`、`id`、`name`、`tabindex`、`aria-selected`、`aria-controls`
- F-018: 第一个标签 `tabindex="0"` 且 `aria-selected="true"`，其余为 `tabindex="-1"` 且 `aria-selected="false"`

## TabDirective（单个标签页指令）

- F-019: `class TabDirective(SphinxDirective)`，`has_content = True`
- F-020: 从 `tabs_stack[-1]` 获取当前 tabs_id，从 `self.env.temp_data[tabs_key]` 获取共享状态
- F-021: tab_id 处理：若未指定则调用 `self.env.new_serialno(tabs_key)` 生成序号；若重复则自动追加后缀 `-1`, `-2` 等
- F-022: 创建 `SphinxTabsTab` 节点，解析第一行内容为标签标题
- F-023: 创建 `SphinxTabsPanel` 节点，设置 `role="tabpanel"`、`id`、`tabindex=0`、`aria-labelledby`、CSS 类 `"sphinx-tabs-panel"`
- F-024: 第一个面板无 `hidden` 属性，其余面板设置 `hidden="true"`
- F-025: 非兼容 builder 降级：使用普通 docutils container 节点输出，不使用 ARIA 标签组件

## GroupTabDirective（分组标签指令）

- F-026: `class GroupTabDirective(TabDirective)` 继承自 TabDirective
- F-027: run() 添加 CSS 类 `"group-tab"`
- F-028: tab_id 从组名的 base64 编码生成：`base64.b64encode(group_name.encode("utf-8")).decode("utf-8")`
- F-029: 分组标签选中状态通过 `sessionStorage` 持久化，切换时同步所有同名标签页

## CodeTabDirective（代码标签指令）

- F-030: `class CodeTabDirective(GroupTabDirective)` 继承自 GroupTabDirective
- F-031: `required_arguments = 1`（lexer 名称），`optional_arguments = 1`（自定义标签名）
- F-032: option_spec 继承 CodeBlock 的选项：`force`、`linenos`、`dedent`、`lineno-start`、`emphasize-lines`、`caption`、`class`、`name`
- F-033: 标签名解析顺序：第二参数（自定义名）→ `lexer_classes` 中查 Pygments lexer 正式名称 → `LEXER_MAP` 中查短名映射
- F-034: LEXER_MAP 通过遍历 `pygments.lexers.get_all_lexers()` 构建，将所有 lexer 短名映射到正式名称
- F-035: 添加 CSS 类 `"code-tab"`，调用 `CodeBlock.run(self)` 解析代码内容
- F-036: 重置 content 数据调用父类 run() 生成面板节点，再将代码块追加到面板

## 辅助功能

- F-037: `get_compatible_builders(app)` 返回兼容 builder 列表：html、singlehtml、dirhtml、readthedocs 系列、spelling，并追加 `sphinx_tabs_valid_builders` 配置的自定义 builder
- F-038: `_FindTabsDirectiveVisitor` 是 NodeVisitor，通过 doctree 遍历来检测页面是否使用了 tabs 指令
- F-039: `update_context()` 连接 `html-page-context` 事件，若页面包含 tabs 指令才添加 CSS/JS 资源（条件加载）
- F-040: 条件加载受 `app.registry.html_assets_policy == "always"` 全局策略影响

## setup 函数配置

- F-041: `sphinx_tabs_valid_builders` 配置，默认 `[]`，追加自定义兼容 builder
- F-042: `sphinx_tabs_disable_css_loading` 配置，默认 `False`，设为 True 则不自动添加 CSS（用户自定义主题时使用）
- F-043: `sphinx_tabs_disable_tab_closing` 配置，默认 `False`，设为 True 则标签不可关闭（点击已选中标签不会取消选中）
- F-044: 注册 4 个自定义节点 + HTML visit/depart 方法
- F-045: 注册 4 个指令：`tabs`、`tab`、`group-tab`、`code-tab`
- F-046: 静态路径通过 `builder-inited` 事件插入到 `html_static_path` 最前面
- F-047: 返回 `parallel_read_safe: True, parallel_write_safe: True`

## 前端 JavaScript（tabs.js）

- F-048: 使用 WAI-ARIA 标签页模式（role="tablist"/"tab"/"tabpanel"）
- F-049: 键盘导航：左右方向键在标签间循环移动焦点
- F-050: 点击标签时 `deselectTabList()` 取消所有选中 → `selectTab()` 选中当前 → `selectNamedTabs()` 同步同名分组标签
- F-051: group-tab 的选中状态存入 `sessionStorage['sphinx-tabs-last-selected']`
- F-052: 切换标签时计算位置偏移量，调用 `window.scrollTo()` 防止页面跳动
- F-053: DOMContentLoaded 时从 sessionStorage 恢复上次选中的分组标签
