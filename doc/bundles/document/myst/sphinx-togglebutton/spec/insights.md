---
type: spec
title: sphinx-togglebutton 架构洞察
description: sphinx-togglebutton 源码洞察记录
tags:
- sphinx-togglebutton
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-togglebutton-source
  resource: /references/togglebutton-source.md
  title: sphinx-togglebutton togglebutton-source
---

# sphinx-togglebutton 架构洞察

> I 阶段产出：基于事实清单提炼的核心洞察四元组。

## 洞察 I-001：CSS 类驱动的折叠范式——两种 DOM 策略的智能分发

- **陈述**：sphinx-togglebutton 对 admonition 提示框和普通容器采用截然不同的 DOM 操作策略——admonition 通过添加/移除 CSS 类 `toggle-hidden` 实现折叠，并在标题栏插入按钮；普通容器则用原生 `<details>/<summary>` HTML 元素包装。两种策略由 JS 运行时自动判断元素类型（是否含 `admonition` 类）。
- **证据**：F-028~F-031（JS 中 if/else 分支分别处理 admonition 和非 admonition）、F-013（Toggle 指令创建 `.toggle` 类容器）
- **反常识**：扩展并没有统一使用一种折叠机制。admonition 不能简单用 `<details>` 包装是因为 admonition 有复杂的标题栏结构和 Pygments 语法高亮样式，直接包装会破坏 CSS 布局；而普通内容块用 `<details>` 则获得原生无障碍支持（键盘导航、屏幕阅读器）和无需 JS 的渐进增强。
- **行动**：为 Sphinx 扩展添加折叠功能时，应区分 admonition 和普通内容块分别处理；admonition 类元素适合用 CSS 类切换方案，普通内容适合 `<details>` 原生方案。

## 洞察 I-002：选择器驱动的自动折叠——零标记即可工作

- **陈述**：默认选择器 `".toggle, .admonition.dropdown"` 意味着两种触发方式：（1）使用 `.. toggle::` 指令显式创建折叠块；（2）给任意 admonition 添加 `:class: dropdown` 即可自动折叠，无需额外指令。这是通过 JS 端的 `querySelectorAll(togglebuttonSelector)` 全局扫描实现的，不依赖 Python 端对 admonition 的修改。
- **证据**：F-015（默认选择器配置）、F-028（JS 运行时 querySelectorAll 全局查找）、F-009（选择器可通过配置自定义）
- **反常识**：admonition 的折叠完全由前端 JS 驱动，Python 端不需要为 note/warning/tip 等 admonition 做任何定制。Sphinx 构建阶段 admonition 就像普通 admonition 一样输出 HTML，折叠行为是纯 JS 运行时增强——这意味着即使 JS 加载失败，内容也完全可见（渐进增强）。
- **行动**：使用折叠功能最简单的方式是给 admonition 加 `:class: dropdown`，无需使用 `.. toggle::` 指令；`.. toggle::` 指令适用于任意内容块（如图片、代码块组合）的折叠场景。

## 洞察 I-003：打印友好设计——beforeprint/afterprint 状态快照与恢复

- **陈述**：扩展在 `beforeprint` 事件中展开所有折叠内容（同时记录原始状态到 `dataset`），在 `afterprint` 事件中恢复原始折叠状态。对 `<details>` 元素设置 `el.open = true`，对 admonition 则程序化点击按钮触发展开，并通过 `dataset.toggle_after_print` 标记需要恢复的元素。
- **证据**：F-034（beforeprint/afterprint 事件处理）、F-018（togglebutton_open_on_print 配置开关）
- **反常识**：很多折叠 UI 组件忽略打印场景，导致打印出来的文档缺少折叠的内容。sphinx-togglebutton 通过配置项 `togglebutton_open_on_print`（默认 True）确保打印/导出 PDF 时所有内容可见，且打印后精确恢复用户的浏览状态——不是简单地全部展开不管恢复。
- **行动**：在文档构建中，始终保持 `togglebutton_open_on_print = True`（默认值）；如果需要打印时仍保持折叠状态，才设置为 False。

## 洞察 I-004：内联 JS 配置注入——Python 到 JS 的配置桥接模式

- **陈述**：Python 端的配置值（hint 文本、选择器、打印行为）通过 `app.add_js_file(None, body="let toggleHintShow = '...';")` 以 `<script>` 内联方式注入到 HTML 页面头部，在 `togglebutton.js` 加载前定义全局变量。这避免了 JS 端硬编码文本，支持国际化和运行时配置。
- **证据**：F-008（initialize_js_assets 注入内联 JS 变量）、F-009（insert_custom_selection_config 注入选择器变量）、F-016/F-017（hint 文本使用 get_translation 国际化）
- **反常识**：Sphinx 扩展的 JS 配置传递不是通过 AJAX 请求或 data 属性，而是在构建阶段将配置值序列化为 JS 变量字面量内联到 HTML 中。这是零运行时开销的配置传递方式——JS 文件本身完全静态，配置值在 HTML 中内联。
- **行动**：开发需要配置的 Sphinx JS 扩展时，采用"构建时内联配置变量 + 静态 JS 文件"模式，比 data 属性或 hidden input 更简洁、更易维护。

## 知识地图

```
sphinx-togglebutton/
├── 入门层
│   ├── 00-introduction.md     → I-001 两种折叠策略定位
│   └── 01-getting-started.md  → 安装配置 + dropdown类使用
├── 核心层
│   ├── 02-toggle-directive.md → I-001 toggle指令详解
│   └── 03-configuration.md    → I-004 配置项与JS桥接
└── 实践层
    └── examples/
        ├── basic-usage.md     → admonition折叠+toggle指令
        └── print-and-i18n.md  → I-003 打印+i18n配置
```
