---
type: reference
title: "页码控件源码（src/pagenumber.tsx）"
description: "PDF 查看器页码导航 React 组件 PageNumberComponent 和 Lumino 封装 PageNumberWidget"
tags: [pagenumber, react, widget, pagination, pdf-navigation, page-labels]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pagenumber-tsx
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/src/pagenumber.tsx"
    title: "src/pagenumber.tsx"
---

# 页码控件源码（src/pagenumber.tsx）

本信源登记 `src/pagenumber.tsx`（约199行），实现 PDF 查看器工具栏中的页码导航控件，支持页码输入、跳转和页码标签显示。

## PageNumberComponent 类（React.Component）

### IProps 接口

| 属性 | 类型 | 说明 |
|------|------|------|
| `widget` | `PDFJSViewer` | PDF 查看器实例引用 |

### IState 接口

| 属性 | 类型 | 说明 |
|------|------|------|
| `currentPageLabel` | `string \| undefined` | 当前页码标签（如罗马数字、自定义标签） |
| `currentPageNumber` | `number` | 当前页码（1-based 数字） |
| `pagesCount` | `number` | 总页数 |
| `userInput` | `string \| null` | 用户在输入框中输入的文本（未提交时） |

初始状态：`{ currentPageNumber: 0, pagesCount: 0, userInput: null }`

### 生命周期方法

| 方法 | 功能 |
|------|------|
| `componentDidMount()` | viewer ready 后监听 eventBus 的 `firstpage`、`pagechanging`、`pagelabels` 事件 |
| `componentWillUnmount()` | 取消事件监听 |

### 事件处理

| 方法 | 触发时机 | 功能 |
|------|---------|------|
| `handleChange(evt)` | input 内容变化 | 保存用户输入到 state.userInput |
| `handleFocus(evt)` | input 获得焦点 | 选中全部文本（`evt.target.select()`） |
| `handleBlur(evt)` | input 失去焦点 | 调用 setCurrentPage 跳转 |
| `handleKeyDown(evt)` | 按键 | Enter 键时调用 setCurrentPage 跳转 |
| `handlePageDataChange()` | PDF 页面事件 | 更新 currentPageLabel/Number、pagesCount，重置 userInput |

### setCurrentPage(pageLabel)

设置当前页：
- `widget.viewer.currentPageLabel = pageLabel`
- 重置 `userInput` 为 null

### render()

渲染结构：
```
<div className="jp-PDFJSPageNumber">
  <span>
    <input value={...} onBlur={onChange} onFocus onKeyDown />
    <span>{pageInfoText}</span>
  </span>
</div>
```

页码文本显示逻辑：
- 有 currentPageLabel：`" (N of M)"` 格式
- 无 currentPageLabel：`" of M"` 格式

输入框值：userInput 非空时显示用户输入，否则显示 currentPageLabel 或 currentPageNumber。

## PageNumberWidget 类

继承自 `ReactWidget`（`@jupyterlab/apputils`），将 React 组件包装为 Lumino Widget。

- 构造函数接收 `PageNumberComponent.IProps`，存储到 `this._props`
- `render()` 方法返回 `<PageNumberComponent {...this._props} />`

## 事件绑定

在 pdf.ts 的 `Private.createToolbar()` 中创建，传入 PDFJSViewer 实例：
```typescript
toolbar.addItem('PageNumber', new PageNumberWidget({ widget: content }));
```
