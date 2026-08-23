---
type: Concept
title: 徽章与按钮
description: bdg/bdg-link/bdg-ref 徽章角色和 button-link/button-ref 按钮指令的用法、tooltip、富文本Stash/Graft机制
tags:
- sphinx
- design
- badge
- button
- role
- directive
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/badges_buttons.py
---

# 徽章与按钮

sphinx-design 提供了行内徽章（badge role）和块级按钮（button directive）两种交互行内组件。

## 徽章（Roles）

徽章是行内元素，使用 role 语法（rST 中 `` :role:`text` ``，MyST 中 `{role}`text` `）。

### 徽章角色类型

| 角色模式 | 类型 | 说明 |
|---|---|---|
| `:bdg:`text`` | 纯文本 | 无色徽章 |
| `:bdg-{color}:`text`` | 纯文本 | 语义色填充徽章 |
| `:bdg-{color}-line:`text`` | 纯文本 | 语义色轮廓徽章 |
| `:bdg-link:`text <url>`` | 外部链接 | 链接到 URL |
| `:bdg-link-{color}:`text <url>`` | 外部链接 | 彩色外部链接 |
| `:bdg-link-{color}-line:`text <url>`` | 外部链接 | 彩色轮廓外部链接 |
| `:bdg-ref:`text <target>`` | 内部引用 | 链接到文档内目标 |
| `:bdg-ref-{color}:`text <target>`` | 内部引用 | 彩色内部引用 |
| `:bdg-ref-{color}-line:`text <target>`` | 内部引用 | 彩色轮廓内部引用 |

### 语义色

徽章可用的语义色：primary, secondary, success, info, warning, danger, light, muted, dark, white, black。

### 使用示例

```rst
版本 :bdg-primary:`3.0` 已发布。
状态: :bdg-success:`稳定` :bdg-warning:`实验性` :bdg-danger:`已弃用`

:bdg-link-primary:`文档 <https://example.com/docs>`
:bdg-ref-info:`API参考 <api-reference>`
```

MyST Markdown:

```markdown
版本 {bdg-primary}`3.0` 已发布。
{bdg-link-primary}`文档 <https://example.com/docs>`
```

### 轮廓变体

添加 `-line` 后缀创建轮廓（outline）样式徽章：

```rst
:bdg-primary-line:`轮廓徽章`
```

轮廓徽章使用透明背景 + 彩色边框和文本，视觉上更轻量。

### Tooltip 语法

徽章支持 tooltip 提示文本，语法为 `text;tooltip`（分号分隔）：

```rst
:bdg-info:`Python;3.11+`
```

渲染为带有 `title` 属性的徽章，鼠标悬停时显示 "3.11+"。

分号可用 `\;` 转义（在文本中使用字面量分号）：

```rst
:bdg:`语法规则\;注意事项;点击查看详情`
```

这会显示文本 "语法规则;注意事项"，tooltip 为 "点击查看详情"。

**链接徽章的 tooltip 限制**：`bdg-link` 和 `bdg-ref` 的 tooltip 只在显式 `title <target>` 形式后才接受分号，因为 URL 和引用目标中 `;` 是合法字符：

```rst
:bdg-link-primary:`文档 <https://example.com>;点击访问`  ✅
:bdg-ref:`<my-target>;这是提示`                       ❌ (bare form不支持tooltip)
```

### 非 HTML 渲染

徽章在 LaTeX/text/man/texinfo 输出中使用 passthrough 模式——直接渲染子文本，不输出 `<span>` 包装器，不会产生空标签。

## 按钮（Directives）

按钮是块级元素，使用指令语法。

### 按钮指令类型

| 指令 | 用途 | 链接类型 |
|---|---|---|
| `button-link` | 外部链接按钮 | URL（外部网站/文件） |
| `button-ref` | 内部引用按钮 | Sphinx 交叉引用（ref/doc/any/myst） |

### button-link 用法

```rst
.. button-link:: https://example.com
   :color: primary
   :expand:

   访问官网
```

第一个参数是 URL（必填），内容是按钮文本。

### button-ref 用法

```rst
.. button-ref:: installation-guide
   :ref-type: ref
   :color: success
   :outline:

   前往安装指南
```

第一个参数是引用目标（必填），内容是按钮文本。无内容时自动使用目标的标题作为按钮文本。

### 按钮选项

| 选项 | 值 | 说明 |
|---|---|---|
| `color` | 语义色名 | 按钮颜色 |
| `outline` | flag | 使用轮廓样式 |
| `align` | left/right/center | 对齐方式（按钮所在段落的对齐） |
| `expand` | flag | 按钮撑满父容器宽度 |
| `click-parent` | flag | 父元素区域也可点击（stretched-link） |
| `tooltip` | 文本 | 悬停提示文本 |
| `shadow` | flag | 添加小阴影 |
| `ref-type` | any/ref/doc/myst | 仅button-ref：引用类型，默认any |
| `class` | CSS类列表 | 额外CSS类 |

### 按钮样式示例

```rst
.. button-link:: https://example.com
   :color: primary
   主要按钮

.. button-link:: https://example.com
   :color: danger
   :outline:
   危险轮廓按钮

.. button-link:: https://example.com
   :color: success
   :expand:
   :shadow:
   全宽成功按钮带阴影

.. button-ref:: getting-started
   :align: center
   :tooltip: 开始使用教程
   居中对齐按钮带提示
```

### 按钮 CSS 类模式

- 填充按钮：`sd-btn-{color}`（如 `sd-btn-primary`）
- 轮廓按钮：`sd-btn-outline-{color}`（如 `sd-btn-outline-primary`）
- 基础类：`sd-sphinx-override sd-btn sd-text-wrap`
- 阴影：`sd-shadow-sm`（shadow flag）
- 扩展点击区域：`sd-stretched-link`（click-parent flag）
- 全宽：外层 `sd-d-grid` 包装器（expand flag）

### button-ref 的富文本保留机制

`button-ref` 允许按钮文本包含富内容（加粗、斜体、图标等），但 Sphinx 标准域的交叉引用解析器会将内容扁平化为纯文本。sphinx-design 通过 **Marker-Class Stash/Graft** 模式解决此问题：

1. **ButtonRefContentStash**（PostTransform priority=8）：在 resolver 运行前，深拷贝每个有内容的 button-ref 的富文本子节点到 `document.sd_button_ref_content` 字典，key 为唯一 marker class（`sd-button-ref-content-{n}`），marker class 添加到 pending_xref 的 classes。
2. **Resolvers 运行**（priority 9-10）：Sphinx/myst-parser 的 resolver 将 pending_xref 替换为 reference 节点，class 属性被复制。
3. **ButtonRefContentGraft**（PostTransform priority=11）：遍历文档，找到带 marker class 的 reference 节点，用暂存的富文本替换扁平化内容，移除 marker。

类似地，`BadgeRefTooltipStash`（priority=5）和 `BadgeRefTooltipGraft`（priority=12）处理 bdg-ref 的 tooltip（因为 resolver 不复制自定义属性如 `sd_tooltip`，但复制 classes）。

### 可翻译按钮文本

按钮内容通过 `nodes.inline(translatable=True)` 标记为可翻译，Sphinx 的 gettext 构建会提取按钮文本进行翻译。这通过嵌套 inline 节点实现——外层 inline 保持引用结构完整，内层 translatable inline 被翻译后展开。

### 按钮与段落

按钮总是被包裹在 `nodes.paragraph` 中返回，因为 Sphinx 的 HTML writer 要求 reference 节点必须在 TextElement（如段落）内才能正确渲染。段落使用 align 选项的 CSS 类（`sd-text-left/right/center`）控制对齐。

## 相关概念

- [扩展架构与两阶段渲染](/concepts/02-extension-architecture.md) — Stash/Graft 模式深度解析
- [设计系统与CSS类名体系](/concepts/03-design-system.md) — 按钮/徽章的色彩和样式类
- [图标系统](/concepts/08-icons-article-info.md) — 在按钮/徽章中使用图标
