---
type: Concept
title: 快速上手
description: sphinx-design 的安装、启用、验证与常见问题
tags:
- sphinx
- extension
- design
- getting-started
- setup
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- pyproject.toml
- sphinx_design/__init__.py
- sphinx_design/extension.py
---

# 快速上手

## 安装

使用 pip 安装 sphinx-design：

```bash
pip install sphinx-design
```

依赖要求：
- Python >= 3.11
- Sphinx >= 7.2, < 10

## 启用扩展

在 Sphinx 项目的 `conf.py` 中，将 `sphinx_design` 添加到 `extensions` 列表：

```python
# conf.py
extensions = [
    # ... 其他扩展
    "sphinx_design",
]
```

启用后，所有指令和角色即可在文档中使用，无需额外配置。

## 最小验证示例

创建一个测试文档 `test.rst`（reStructuredText）：

```rst
Test sphinx-design
==================

.. grid:: 2

   .. grid-item-card:: 卡片 1

      这是第一张卡片的内容。

   .. grid-item-card:: 卡片 2

      这是第二张卡片的内容。

.. dropdown:: 点击展开

   这里是折叠的内容。
```

或使用 MyST Markdown（需要 myst-parser）：

````markdown
# Test sphinx-design

````{grid} 2

```{grid-item-card} 卡片 1

这是第一张卡片的内容。
```

```{grid-item-card} 卡片 2

这是第二张卡片的内容。
```
````

```{dropdown} 点击展开
这里是折叠的内容。
```
````

构建文档验证：

```bash
sphinx-build -b html . _build
```

打开 `_build/test.html`，应能看到两列网格卡片和一个可点击展开的折叠区域。

## 常用配置

### FontAwesome 图标

sphinx-design 自带 Octicon 和 Material Design 图标的内嵌 SVG，但 FontAwesome 图标需要额外加载 CSS。两种方式：

**方式一：CDN 加载（最简单）**

```python
# conf.py
sd_fontawesome_source = "cdn"
# 默认使用 cdnjs 的 FA 6.1.1，可自定义 URL：
# sd_fontawesome_cdn_url = "https://你的CDN地址/fontawesome/css/all.min.css"
```

**方式二：主题/手动引入**

```python
sd_fontawesome_source = "none"  # 默认值，自行在主题或模板中引入 FA CSS
```

控制 FontAwesome 版本的 CSS 类名方案：

```python
sd_fontawesome_version = "as-named"  # 默认，按角色名原样输出
# 可选值：
# "as-named" — :fas: 输出 "fas", :fa-solid: 输出 "fa-solid"
# "6"        — 所有角色映射到 FA6 类名（fa-solid/fa-brands/fa-regular）
# "5"        — 映射到 FA5 类名（fas/fab/far）
# "4"        — 映射到 FA4 类名（fa，无样式区分）
```

### Tab 持久化

默认情况下，Tab 的选中状态会通过 localStorage 跨页面保持。可自定义存储键前缀或禁用：

```python
sd_tabs_storage_prefix = "sphinx-design-tab-id-"  # 默认值
# 设置为空字符串禁用持久化：
# sd_tabs_storage_prefix = ""
```

### LaTeX 中的图标

在 LaTeX/PDF 输出中渲染 FontAwesome 图标：

```python
sd_fontawesome_latex = "fontawesome5"  # 使用 fontawesome5 包
# 可选值：
# False / "none"    — 不渲染（默认），发出警告
# True / "fontawesome" — 使用 fontawesome 包
# "fontawesome5"    — 使用 fontawesome5 包（推荐，支持brands/regular样式）
```

### 隐藏首页标题

在文档顶部的 docinfo 中添加 `:sd_hide_title:` 字段可隐藏第一个 section 标题（常用于 landing page）：

```rst
:sd_hide_title:

Landing Page
============
```

## MyST Markdown 使用提示

在 MyST Markdown 中使用 sphinx-design 指令时，注意：

1. **指令围栏**：使用三重反引号 + 大括号包裹指令名，如 ` ```{grid} 2 `
2. **嵌套指令**：嵌套的指令也需要各自的围栏，注意反引号数量递增或使用波浪号
3. **角色语法**：MyST 中角色使用 `{role}`text`` 格式，如 `{bdg-primary}`主要标签``
4. **徽章 tooltip**：MyST 中反斜杠转义直接传递，使用 `\;` 转义分号即可

## 常见问题

### Q: 组件样式与主题冲突？

确保你的 Sphinx 主题没有覆盖 `sd-` 前缀的 CSS 类。sphinx-design 的 CSS 已经使用 `sd-sphinx-override` 类做了基本样式重置。如果仍有冲突，可以通过自定义 CSS 覆盖特定类。

### Q: 非 HTML 输出（PDF/LaTeX）中组件长什么样？

dropdown 和 tab 在 LaTeX 中会降级为"标题+内容"的线性结构（rubric 标题 + 正常内容），卡片会显示为带框的内容块，徽章和按钮显示为普通文本，图标（非 FA）在非 HTML 输出中被跳过。

### Q: 如何自定义组件样式？

添加自定义 CSS 文件：

```python
# conf.py
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

然后在 `_static/custom.css` 中覆盖 `sd-` 前缀的类：

```css
/* 自定义卡片样式 */
.sd-card {
    border-radius: 1rem;
}
```

### Q: tab-set-code 不工作？

`tab-set-code` 的直接子元素必须是代码块（literal_block），不能是其他内容。确保代码块与指令之间没有空行导致被解析为段落。

## 相关概念

- [sphinx-design 简介](00-introduction.md) — 项目定位与特性概览
- [扩展架构](02-extension-architecture.md) — 组件注册与两阶段渲染
- [网格布局系统](04-grids.md) — 响应式网格详解
