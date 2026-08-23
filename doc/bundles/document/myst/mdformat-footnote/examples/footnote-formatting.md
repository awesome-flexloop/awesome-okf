---
type: Example
title: 脚注格式化与排序示例
description: 使用 mdformat-footnote 格式化脚注并自动按引用顺序排序。
tags: [example, footnote, formatting, ordering, cli]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-reorder
    resource: /references/source-reorder.md
    title: mdformat-footnote 脚注重排序逻辑
---

## 脚注自动排序

创建一个脚注定义顺序混乱的 Markdown 文件 `paper.md`：

```markdown
# 研究论文

爱因斯坦的质能方程[^emc2]是现代物理的基石。

牛顿运动定律[^newton]描述了经典力学。

[^third]: 这是一个从未被引用的脚注。

[^emc2]: 质能等价公式：$E = mc^2$，由爱因斯坦于1905年提出。
    这个公式表明质量和能量是等价的。

[^newton]: 牛顿三大运动定律是经典力学的基础。
```

运行格式化：

```bash
mdformat paper.md
```

格式化后，脚注将按引用顺序重新编号排列，未引用的孤立脚注 `[^third]` 默认被移除：

```markdown
# 研究论文

爱因斯坦的质能方程[^1]是现代物理的基石。

牛顿运动定律[^2]描述了经典力学。

[^1]: 质能等价公式：$E = mc^2$，由爱因斯坦于1905年提出。
    这个公式表明质量和能量是等价的。

[^2]: 牛顿三大运动定律是经典力学的基础。
```

## 保留孤立脚注

使用 `--keep-footnote-orphans` 选项保留未引用的脚注定义：

```bash
mdformat --keep-footnote-orphans paper.md
```

孤立脚注会排在所有被引用的脚注之后。

## 嵌套脚注处理

mdformat-footnote 能正确处理脚注内引用其他脚注的情况：

```markdown
这是正文[^main]。

[^main]: 主要脚注内容，引用了另一个来源[^nested]。

[^nested]: 被嵌套引用的脚注。
```

格式化后，被嵌套引用的脚注会紧跟在引用它的脚注之后排列。

## 代码块中的脚注引用

代码围栏中出现的 `[^label]` 也会被识别为脚注引用：

````markdown
正文引用[^a]。

```
这里有个脚注引用[^b]在代码块中。
```

[^a]: 正文引用的脚注。
[^b]: 代码块中引用的脚注。
````

这些仅在代码块中引用的脚注会归为 fence_only 类别，排在正文引用和嵌套引用之后。

## 与 mdformat-myst 配合

mdformat-myst 插件自动依赖 mdformat-footnote，因此在 MyST 项目中脚注功能默认启用。在 pyproject.toml 或 .mdformatrc 中可配置脚注选项。

## 相关概念

- [脚注渲染格式与缩进规则](/concepts/02-footnote-rendering.md)
- [脚注排序逻辑与分类机制](/concepts/03-footnote-reordering.md)
- [插件配置与 CLI 选项](/concepts/01-plugin-configuration.md)
