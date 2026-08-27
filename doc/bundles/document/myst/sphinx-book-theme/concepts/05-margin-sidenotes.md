---
type: Concept
title: 05 - Margin 指令与边注旁注
description: margin 指令用法、SideNoteNode 机制、HandleFootnoteTransform 脚注转边注原理、sidenote 与 marginnote 区别
tags:
- sphinx-book-theme
- margin
- sidenote
- marginnote
- footnote
- directive
- transform
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/directives.py
- src/sphinx_book_theme/nodes.py
- src/sphinx_book_theme/_transforms.py
---

# Margin 指令与边注旁注

sphinx-book-theme 提供两种在右侧边距显示内容的方式：`margin` 指令（手动放置任意内容）和自动脚注转边注（通过 `use_sidenotes` 配置）。两者共享CSS样式体系，但实现机制不同。

## Margin 指令

`margin` 指令将任意内容放入右侧边距区域。它继承自 docutils 的 `Sidebar` 指令（F-090），添加了 `margin` CSS 类。

### 语法

**MyST（Markdown）**：

```markdown
```{margin} 可选标题
这里是边距内容，可以包含 **格式化文本**、列表、甚至图片。
```
```

**reStructuredText**：

```rst
.. margin:: 可选标题

   这里是边距内容，可以包含 **格式化文本**、列表、甚至图片。
```

### 无标题用法

不提供标题参数时，标题节点会被自动移除（F-094）：

```markdown
```{margin}
这是一个无标题的边距内容块。
```
```

### 实现原理

`Margin` 类的 `run()` 方法（F-090-F-094）：
1. 若无参数，设 `self.arguments = [""]`（避免父类报错）
2. 调用父类 `Sidebar.run()` 生成节点
3. 为根节点添加 `"margin"` CSS 类
4. 若无标题参数，移除第一个子节点（title节点）

## 边注与旁注（Sidenotes & Marginnotes）

边注/旁注功能通过 `use_sidenotes: True` 配置启用（F-104）。启用后，标准脚注自动从文档末尾迁移到引用位置旁的右侧边距。

### 两种边注类型

| 类型 | 语法 | 编号 | CSS类 | tagid前缀 |
|------|------|------|-------|-----------|
| Sidenote（旁注） | 标准脚注 `[^1]` | 保留编号上标 | `sidenote` | `sidenote-role-` |
| Marginnote（边注） | 脚注内容以 `{-} ` 开头 | 无编号 | `marginnote` | `marginnote-role-` |

（F-107-F-108、F-098-F-099）

### MyST 语法

```markdown
这是正文内容，这里有一个旁注[^1]和一个边注[^2]。

[^1]: 这是带编号的旁注，数字自动生成。
[^2]: {-} 这是无编号的边注，适合补充说明但不需要编号引用的场景。
```

### rST 语法

```rst
这是正文内容，这里有一个旁注[#note1]_和一个边注[#note2]_。

.. [#note1] 这是带编号的旁注。
.. [#note2] {-} 这是无编号的边注。
```

### HandleFootnoteTransform 工作原理

`HandleFootnoteTransform` 是一个 SphinxPostTransform（F-102），在HTML渲染前执行（priority=1, formats=("html",)）。其工作流程：

1. **检查开关**：若 `use_sidenotes` 为 False，直接返回（F-104）
2. **遍历引用**：遍历文档中所有 `footnote_reference` 节点（F-105）
3. **匹配脚注**：通过 `backrefs[0] == ids[0]` 匹配引用与脚注内容（F-106）
4. **提取内容**：脚注节点的第二个子节点（`children[1]`）是内容文本（F-108）
5. **判断类型**：检查内容首文本是否以 `"{-}"` 开头（F-042）
   - 是 → marginnote：移除 `{-}` 标记，添加 "marginnote" 类
   - 否 → sidenote：创建 superscript 编号节点，添加 "sidenote" 类
6. **处理嵌套**：若引用位于容器（如 admonition）内，执行双节点策略（见下文）
7. **替换节点**：将 `footnote_reference` 替换为 `SideNoteNode` + 内容节点（F-083）
8. **清理原脚注**：从原父节点移除 footnote 节点（F-086）

### 嵌套场景的双节点策略

当脚注引用位于 admonition、quote 等容器内时，边注内容无法直接"跳出"容器显示在右侧边距。Transform 采用双节点策略（F-110-F-112）：

```
原始结构:
    <admonition>
        <paragraph>正文<footnote_reference id="1"/></paragraph>
    </admonition>
    <footnote backrefs="1">脚注内容</footnote>

转换后:
    <sidenote-node/>
    <inline class="sidenote">编号+内容</inline>  ← 容器外的可见副本
    <admonition>
        <paragraph>正文<sidenote-node/></paragraph>
    </admonition>
    <inline class="sidenote d-n">编号+内容</inline>  ← 容器内的隐藏副本
```

- 在容器**之前**插入可见的边注内容
- 在容器**内**引用位置旁插入一个 `d-n`（display:none）副本
- CSS媒体查询根据屏幕宽度决定显示哪个版本：
  - 宽屏（侧边栏可见）：显示容器外的副本，隐藏内部副本
  - 窄屏（移动端）：隐藏容器外的副本，显示内部副本（在正文流中展开）

向上遍历父节点时，遇到 paragraph 或 footnote 继续向上，遇到其他容器（非 paragraph/footnote/section/document）则执行替换（F-111-F-077）。

## SideNoteNode 与纯CSS交互

`SideNoteNode` 生成的HTML结构利用了 `<label> + <input type="checkbox">` 的纯CSS交互模式，**无需JavaScript**即可实现移动端点击展开/收起：

### Sidenote 生成的HTML

```html
<label for='sidenote-role-1' class='margin-toggle'>
    <span>1</span>  <!-- 上标编号 -->
</label>
<!-- 边注内容（由 <inline class="sidenote"> 渲染） -->
</span>
<input type='checkbox' id='sidenote-role-1' name='sidenote-role-1' class='margin-toggle'>
```

### Marginnote 生成的HTML

```html
<label for='marginnote-role-2' class='margin-toggle marginnote-label'>
</label>
<!-- 边注内容（由 <inline class="marginnote"> 渲染） -->
</label>
<input type='checkbox' id='marginnote-role-2' name='marginnote-role-2' class='margin-toggle'>
```

（F-098-F-101）

交互原理：
- 宽屏：checkbox 隐藏，边注内容始终显示在右侧边距
- 窄屏：label 显示为一个小标记，点击后 checkbox 被选中，CSS通过 `:checked +` 选择器显示边注内容在正文下方

## 移动端响应式行为

边注/旁注的响应式行为由CSS和JavaScript共同管理：

1. **CSS媒体查询**：宽屏（>992px）时边距内容显示在右侧；窄屏时隐藏在侧边，点击label展开
2. **TOC智能隐藏**：JavaScript IntersectionObserver 监听边注内容进入视口，自动隐藏右侧TOC避免重叠（F-170-F-173）
3. **选择器兼容**：JS同时监听 `marginnote/sidenote/margin/popout` 等类名的三种命名变体（驼峰/下划线/tag_前缀），兼容历史版本（F-171-F-172）

## 使用建议

| 场景 | 推荐方式 | 理由 |
|------|---------|------|
| 学术引用注释 | Sidenote（标准脚注） | 保留编号，可交叉引用 |
| 补充说明、旁白 | Marginnote（`{-}` 前缀） | 不打断阅读流，无编号 |
| 图片、表格、代码块 | `margin` 指令 | 支持任意复杂内容 |
| 术语定义 | Marginnote | 轻量，不占用编号 |
| 警告/注意事项 | 不使用边距，用 admonition | 重要内容不应放在边距 |

## 相关概念

- [主题概述](00-introduction.md)
- [配置系统详解](03-configuration.md)
- [交互功能（全屏/TOC隐藏/Thebe）](06-interactive-features.md)
- [样式定制与第三方扩展适配](08-customization.md)
- [源码路径映射与配置速查](../references/sbt-source.md)
