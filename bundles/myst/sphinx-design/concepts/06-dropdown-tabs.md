---
type: concept
title: 折叠与标签页
description: dropdown（折叠容器）和 tab-set/tab-item/tab-set-code（标签页）的用法、选项、同步机制
tags:
- sphinx
- design
- dropdown
- tabs
- interactive
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/dropdown.py
- sphinx_design/tabs.py
- sphinx_design/static/design-tabs.js
---

# 折叠与标签页

折叠（dropdown）和标签页（tab）是 sphinx-design 的两个交互组件，它们都采用两阶段渲染架构。

## 折叠容器（dropdown）

dropdown 使用 HTML5 原生 `<details>/<summary>` 元素实现，**零 JavaScript 依赖**。

### 基本用法

```rst
.. dropdown:: 点击展开/折叠

   折叠的内容，可以包含任意 reStructuredText 内容。
```

标题是可选参数，无标题时显示三个点（kebab-horizontal octicon）作为默认图标：

```rst
.. dropdown::
   :open:

   无标题、默认展开的折叠内容。
```

### 选项详解

| 选项 | 值 | 默认 | 说明 |
|---|---|---|---|
| `open` | flag | 无 | 默认展开状态 |
| `color` | 语义色名 | 无 | summary 背景色 |
| `icon` | octicon 名称 | 无 | 标题前缀图标 |
| `chevron` | right-down/down-up | right-down | 状态图标方向 |
| `animate` | fade-in/fade-in-slide-down | 无 | 展开动画 |
| `margin` | 1或4个值 0-5/auto | sd-mb-3 | 外边距 |
| `name` | 文本 | 无 | 引用锚点名称 |
| `class-container` | CSS类 | 无 | details 额外类 |
| `class-title` | CSS类 | 无 | summary 额外类 |
| `class-body` | CSS类 | 无 | 内容区额外类 |

### 带颜色的折叠

```rst
.. dropdown:: 注意事项
   :color: warning
   :icon: alert
   :animate: fade-in

   请注意以下事项...
```

### chevron 方向

- `right-down`（默认）：折叠时 chevron 朝右，展开时朝下（右→下）
- `down-up`：折叠时朝下，展开时朝上（下→上）

### 渲染结构

转换后的 HTML 结构为：

```html
<details class="sd-sphinx-override sd-dropdown sd-card {container_classes}">
  <summary class="sd-summary-title sd-card-header {title_classes}">
    <span class="sd-summary-icon">{icon SVG}</span>
    <span class="sd-summary-text">标题文本</span>
    <span class="sd-summary-state-marker sd-summary-chevron-right">{chevron SVG}</span>
  </summary>
  <div class="sd-summary-content sd-card-body {body_classes}">
    内容
  </div>
</details>
```

dropdown 默认使用 card 样式（`sd-card`），提供视觉上的卡片外观。

## 标签页（tab-set）

tab 组件使用 CSS `:checked` 伪类 + 隐藏的 radio input 实现切换，配合少量 JavaScript 实现跨标签组同步和 localStorage 持久化。

### 基本用法

```rst
.. tab-set::

   .. tab-item:: 标签一

      标签一的内容。

   .. tab-item:: 标签二
      :selected:

      标签二的内容（默认选中）。
```

### tab-set 选项

| 选项 | 值 | 默认 | 说明 |
|---|---|---|---|
| `sync-group` | 字符串 | "tab" | 同步组名，同组标签跨页面联动 |
| `class` | CSS类 | 无 | 额外CSS类 |

### tab-item 选项

| 选项 | 值 | 默认 | 说明 |
|---|---|---|---|
| `selected` | flag | 无 | 默认选中（第一个未标记selected的tab-item默认选中） |
| `sync` | 字符串 | 无 | 同步ID，同组同ID的标签同步选中 |
| `name` | 文本 | 无 | 引用锚点 |
| `class-container` | CSS类 | 无 | 面板容器类 |
| `class-label` | CSS类 | 无 | 标签类 |
| `class-content` | CSS类 | 无 | 内容区类 |

### 标签同步

`sync-group` 和 `sync` 配合实现跨 tab-set 的标签联动：

```rst
.. tab-set::
   :sync-group: language

   .. tab-item:: Python
      :sync: python

      Python 代码...

   .. tab-item:: JavaScript
      :sync: javascript

      JavaScript 代码...
```

页面上其他 `sync-group: language` 的 tab-set 中，如果有 `sync: python` 的 tab-item，当用户选择 Python 标签时，所有同组的 Python 标签都会被选中。选择状态通过 localStorage 持久化（可配置 `sd_tabs_storage_prefix` 控制）。

### 代码标签页（tab-set-code）

`tab-set-code` 是一个便捷指令，自动将子代码块按语言生成标签页：

````rst
.. tab-set-code::

   .. code-block:: python

      print("Hello")

   .. code-block:: javascript

      console.log("Hello")
````

自动生成的效果等同于：

````rst
.. tab-set::
   :sync-group: code

   .. tab-item:: Python
      :sync: python

      .. code-block:: python

         print("Hello")

   .. tab-item:: JavaScript
      :sync: javascript

      .. code-block:: javascript

         console.log("Hello")
````

**tab-set-code 选项**：

| 选项 | 值 | 默认 | 说明 |
|---|---|---|---|
| `no-sync` | flag | 无 | 禁用自动同步 |
| `sync-group` | 字符串 | "code" | 同步组名 |
| `class-set` | CSS类 | 无 | tab-set 额外类 |
| `class-item` | CSS类 | 无 | tab-item 额外类 |

标签名自动取代码块语言的大写形式（如 `python` → `PYTHON`）。

### JavaScript 增强

`design-tabs.js` 提供三个增强功能：

1. **跨 tab-set 同步**：同 `sync-group` + `sync-id` 的标签联动切换
2. **localStorage 持久化**：选中状态跨页面保持（可通过 `sd_tabs_storage_prefix = ""` 禁用）
3. **URL 支持**：
   - 查询参数：`?code=python` 可直接选中指定同步ID的标签
   - URL hash：`#anchor` 可定位到标签内元素并自动展开父级标签（支持嵌套tab）

JS 使用 `document.currentScript` 在脚本加载时获取 `data-sd-tabs-storage-prefix` 属性（通过 `app.add_js_file("design-tabs.js", **js_attributes)` 注入）。

### 非 HTML 降级

在 LaTeX/PDF/man 等非 HTML 输出中：
- dropdown：summary 作为标题（rubric），内容跟随其后线性展示
- tab：tab-label 作为标题（rubric），tab-content 作为内容，所有标签按顺序展开显示

### 锚点处理

tab-item 支持 `:name:` 选项创建锚点，tab-set 会保留 `nodes.target`（超链接目标）到重建结构前部，确保其他文档对 tab 内锚点的引用仍然有效。同时，ids 通过 PropagateTargets 机制传播到 label 节点，保证 anchor 链接正确解析。

## 相关概念

- [扩展架构与两阶段渲染](/concepts/02-extension-architecture.md) — PostTransform 机制详解
- [快速上手](/concepts/01-getting-started.md) — 配置 tab 持久化
- [图标系统](/concepts/08-icons-article-info.md) — dropdown icon 选项使用的 octicon 图标
