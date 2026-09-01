---
type: concept
title: "提示框与标注"
description: "admonition指令的11种类型、dropdown折叠面板、aside边栏、blockquote引用块"
tags: [myst-syntax, admonition, callout, dropdown, aside, blockquote]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/admonition.ts"
    facts: [F-S013]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/dropdown.ts"
    facts: [F-S034]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/aside.ts"
    facts: [F-S033]
---

# 提示框与标注

提示框（Admonition）是技术文档中最常用的标注元素，用于突出显示注意事项、警告、提示等内容。

## Admonition 类型

admonition 指令通过 11 个别名提供不同语义的提示框：

| 指令名 | 语义 | 典型用途 |
|--------|------|----------|
| `note` | 备注 | 普通说明、补充信息 |
| `tip` | 提示 | 有用的技巧、建议 |
| `hint` | 提示 | 更明显的提示 |
| `important` | 重要 | 重要信息提醒 |
| `warning` | 警告 | 需要注意的潜在问题 |
| `caution` | 小心 | 轻微警告 |
| `attention` | 注意 | 需要关注的内容 |
| `danger` | 危险 | 可能导致严重问题的操作 |
| `error` | 错误 | 错误情况说明 |
| `seealso` | 另见 | 相关参考链接 |
| `admonition` | 通用 | 自定义标题的提示框 |

### 基本语法

```markdown
:::{note}
这是一条备注。
:::

:::{warning}
请注意这个操作可能导致数据丢失！
:::

:::{tip}
使用 `myst start` 可以启动热重载开发服务器。
:::
```

### 自定义标题

使用通用 `admonition` 指令可以自定义标题（在参数位置）：

```markdown
:::{admonition} 自定义标题
这是一个自定义标题的提示框。
:::
```

使用具体类型名加参数也是自定义标题（与 Sphinx 行为不同，Sphinx 不允许命名类型有自定义标题）：

```markdown
:::{note} 我的标题
这个 note 有自定义标题。
:::
```

如果没有显式标题且 body 以粗体或标题开头，该内容会被自动用作标题。

### Admonition 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:class:` | String | CSS 类名。特殊值：`dropdown`（变为折叠面板）、`simple`（简单样式）、类型名（覆盖样式） |
| `:icon: false` | Boolean | 隐藏图标 |
| `:open:` | Boolean | 变为折叠面板并设置展开状态 |
| `:label:` | String | 添加交叉引用标签 |

### 可折叠 Admonition

```markdown
:::{note} 点击展开
:open: false

这里是折叠的内容。
:::
```

设置 `:class: dropdown` 也可以将任何提示框变为折叠面板。

## Dropdown 折叠面板

`dropdown` 指令专门用于创建可折叠的 details 元素：

```markdown
:::{dropdown} 点击展开查看答案
这是被折叠的答案内容，可以包含 **Markdown** 格式。
:::
```

| 选项 | 类型 | 说明 |
|------|------|------|
| `:open:` | Boolean | 初始展开状态（默认折叠） |
| `:label:` | String | 交叉引用标签 |

输出为 HTML `<details>` 元素：
- 参数内容放入 `<summary>` 子元素
- body 内容为折叠的详情
- `open` 选项控制 HTML open 属性

## Aside 边栏

`aside` 指令创建边栏/旁注内容，别名包括 `margin`、`sidebar`、`topic`：

```markdown
:::{sidebar} 边栏标题
这是出现在页边的内容，用于补充说明。
:::

:::{margin}
这是没有标题的边注。
:::
```

- `aside`/`margin`：无特殊 kind，输出为 `<aside>` 元素
- `sidebar`/`topic`：kind 设为指令名，主题可以区分样式
- 参数为可选标题（输出为 admonitionTitle 节点）
- body 为 MyST 内容

## Blockquote 引用块

`blockquote` 指令创建块引用，与标准 Markdown `>` 引用语法类似但支持选项和标签：

```markdown
:::{blockquote}
这是一段引用内容。
:::
```

## 对比：Admonition vs Dropdown vs Aside

| 特征 | Admonition | Dropdown | Aside |
|------|-----------|----------|-------|
| 默认样式 | 彩色边框提示框 | 折叠箭头 | 边栏/页边 |
| 可折叠 | `:open:` 或 `:class: dropdown` | 原生折叠 | 不可折叠 |
| 类型 | 11种语义类型 | 无类型 | sidebar/topic/margin |
| 典型用途 | 注意/警告/提示 | FAQ、答案、可选内容 | 边注、旁注、补充 |
| 标题 | 可选参数/自动 | 参数为必须（summary） | 可选参数 |

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [代码块](02-code-blocks.md)
- [高级指令](08-advanced-directives.md)
