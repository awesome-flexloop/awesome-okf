---
type: Concept
title: 脚注渲染格式与缩进规则
description: mdformat-footnote 如何渲染脚注引用和定义，以及缩进处理逻辑。
tags: [footnote, rendering, indent, format, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /references/source-plugin.md
    title: mdformat-footnote 插件核心实现
---

## RENDERERS 映射

mdformat-footnote 注册了三个 token 类型的渲染器：

| Token 类型 | 渲染函数 | 说明 |
|-----------|---------|------|
| `footnote_ref` | `_footnote_ref_renderer` | 脚注引用标记 |
| `footnote` | `_footnote_renderer` | 脚注定义块 |
| `footnote_block` | `_render_children` | 脚注定义容器 |

## 脚注引用渲染

脚注引用（如 `[^1]`）由 `_footnote_ref_renderer` 处理：

```python
def _footnote_ref_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    return f"[^{node.meta['label']}]"
```

输出格式为 `[^label]`，标签从 `node.meta["label"]` 获取。在格式化后，标签通常是数字（由重排序逻辑分配），但保留原始标签名作为 label meta 值。

## 脚注定义渲染

脚注定义（如 `[^1]: content`）由 `_footnote_renderer` 处理，是最复杂的渲染函数。

### 输出结构

格式化后的脚注定义格式如下：

```markdown
[^label]: 首段首行内容
    首段其余行内容（4空格缩进）

    第二个块级元素（4空格缩进）
```

### 渲染逻辑

1. **过滤锚点节点**：排除 `footnote_anchor` 类型的子节点（这些是 markdown-it 内部的回溯锚点，不需要输出）

2. **首行缩进上下文**：首段首行使用特殊缩进——缩进宽度等于 `[^label]: ` 的长度（label长度+4）。这使得首行内容与后续内容视觉对齐：

   ```markdown
   [^1]: 首行内容跟在冒号后
         第二行也对齐到同一位置（在indented上下文中渲染）
   ```

3. **首段处理**：如果第一个子节点是 paragraph 类型：
   - 在与label等长+1的缩进上下文中渲染首段
   - 提取首段第一行（接在 `[^label]: ` 后面）
   - 首段其余行使用4空格缩进

4. **后续元素处理**：剩余子元素在4空格缩进上下文中渲染，用双换行分隔

5. **无首段情况**：如果第一个子节点不是 paragraph（如直接是列表、代码块等），所有内容都使用4空格缩进，从冒号后换行开始

### _render_children

footnote_block 容器使用简单的 `_render_children` 函数，将所有子节点用双换行 `\n\n` 连接。footnote_block 是所有 footnote 定义的父容器。

## 内联脚注禁用

在 `update_mdit` 中，插件先启用 footnote_plugin 紧接着禁用 `footnote_inline` 规则：

```python
mdit.use(footnote_plugin)
mdit.disable("footnote_inline")
```

这意味着 Pandoc 的内联脚注语法 `^[inline footnote text]` 不会被识别为脚注。注释明确说明这是因为"we don't have rendering support for them yet"——当前版本尚未实现内联脚注的渲染支持。

## 相关概念

- [脚注排序逻辑与分类机制](03-footnote-reordering.md)
- [插件配置与 CLI 选项](01-plugin-configuration.md)
