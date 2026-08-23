---
type: reference
title: "错误面板源码（src/error.tsx）"
description: "LaTeX 编译错误面板 ErrorPanel（Lumino Widget）和 LatexError React 组件，支持过滤/未过滤/JSON 三种日志查看模式"
tags: [error, panel, react, log-filter, error-display, latex-error]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: error-tsx
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/src/error.tsx"
    title: "src/error.tsx"
---

# 错误面板源码（src/error.tsx）

本信源登记 `src/error.tsx`（约114行），实现 LaTeX 编译错误的显示面板，包含 Lumino Widget 封装和 React 渲染组件。

## CSS 类常量

| 常量 | 值 | 用途 |
|------|-----|------|
| `LATEX_ERROR_PANEL` | `'jp-LatexErrorPanel'` | 错误面板 Widget CSS 类 |
| `LATEX_ERROR_CONTAINER` | `'jp-LatexErrorContainer'` | 错误消息容器 CSS 类 |
| `TOOLBAR_CELLTYPE_CLASS` | `'jp-Notebook-toolbarCellType'` | 复用 Notebook 工具栏样式 |
| `TOOLBAR_CELLTYPE_DROPDOWN_CLASS` | `'jp-Notebook-toolbarCellTypeDropdown'` | 下拉选择器样式 |

## ErrorPanel 类

继承自 `@lumino/widgets` 的 `Widget`，承载 LaTeX 编译错误信息的面板。

### constructor()

- 调用 `super()`
- 添加 CSS 类：`LATEX_ERROR_PANEL` 和 `TOOLBAR_CELLTYPE_CLASS`

### set text(value)

设置错误文本：
1. 使用 `ReactDOM.render()` 将 `<LatexError text={value} node={this} />` 渲染到 `this.node`
2. 回调中调用 `this.update()` 触发更新请求

### onUpdateRequest(msg)

更新时自动滚动到底部：
- 获取 `this.node.children[2].children[0]`（即 `<pre>` 容器元素）
- 设置 `el.scrollTop = el.scrollHeight`

### onCloseRequest(msg)

关闭时调用 `this.dispose()`。

## ILatexProps 接口

| 属性 | 类型 | 说明 |
|------|------|------|
| `text` | `string` | JSON 格式的错误消息字符串 |
| `node` | `ErrorPanel` | 所属 ErrorPanel 实例引用 |

## LatexError 类（React.Component）

React 组件，渲染错误日志和日志级别选择器。

### 构造函数

1. `JSON.parse(props.text)` 解析后端返回的 JSON
2. 提取并存储三种消息：
   - `this.fullMessage`：完整 LaTeX 输出
   - `this.errorOnlyMessage`：过滤后的错误消息
   - `this.displayedMessage`：当前显示消息（初始为 errorOnlyMessage）

### 实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `selectedValue` | `string \| undefined` | 下拉选择器当前值 |
| `fullMessage` | `string` | 完整未过滤的编译输出 |
| `errorOnlyMessage` | `string` | 经 filter_output 过滤的错误消息 |
| `displayedMessage` | `string` | 当前界面显示的消息 |

### handleChange(event)

下拉选择器变更处理：

| 选项值 | displayedMessage 设置为 |
|--------|------------------------|
| `'Filtered'` | `this.errorOnlyMessage`（过滤后错误） |
| `'Unfiltered'` | `this.fullMessage`（完整输出） |
| `'JSON'` | `this.props.text`（原始 JSON 字符串） |

选择后调用 `this.setState({})` 强制重渲染，然后 `this.props.node.update()` 触发滚动更新。

### render()

JSX 结构：
1. `<label>`："Log Level:" 标签
2. `<HTMLSelect>`：下拉选择器（JupyterLab UI 组件）
   - options: `['Filtered', 'Unfiltered', 'JSON']`
   - onChange: `this.handleChange`
   - aria-label: `"Log level"`
3. `<div>`（高度 `calc(100% - 3em)`）：
   - `<pre className={LATEX_ERROR_CONTAINER}>`：
     - `<code>{this.displayedMessage}</code>`

## 数据流

1. 后端 build.py 的 `run_latex()` 在编译失败时返回 JSON：`{"fullMessage": "...", "errorOnlyMessage": "..."}`
2. index.ts 的 `errorPanelInit(err)` 将 `err.message` 设置为 ErrorPanel 的 text
3. ErrorPanel.text setter 将 JSON 传给 LatexError React 组件
4. LatexError 解析 JSON，默认显示 Filtered 模式
5. 用户可切换到 Unfiltered 查看完整输出或 JSON 查看原始数据
