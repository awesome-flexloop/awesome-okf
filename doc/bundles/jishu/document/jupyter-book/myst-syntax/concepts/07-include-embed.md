---
type: concept
title: "包含与嵌入"
description: "include/literalinclude指令的文件包含、行范围过滤和embed指令的内容复用机制"
tags: [myst-syntax, include, embed, literalinclude, file-inclusion, content-reuse]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/include.ts"
    facts: [F-S025]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/embed.ts"
    facts: [F-S026]
---

# 包含与嵌入

MyST 提供两种内容复用机制：`include`（文件包含）和 `embed`（内容嵌入/复制）。

## Include 指令

`include` 指令将外部文件内容包含到当前文档中，支持行范围过滤和代码块模式。

### 基本语法

```markdown
:::{include} sections/intro.md
:::
```

这会将 `sections/intro.md` 的内容解析为 MyST 并插入当前位置。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | String | ✅ | 相对于当前文件的路径 |

### 代码块模式（Literal Include）

三种方式启用代码块模式：
1. 使用 `literalinclude` 别名
2. 设置 `:literal: true`
3. 设置 `:lang:`（或 `:language:`/`:code:`）指定语言

````markdown
```{literalinclude} src/hello.py
```

:::{include} src/hello.py
:lang: python
:::

:::{include} src/hello.py
:literal: true
:::
````

代码块模式自动：
- 将文件内容作为代码块显示
- 推断语言（从文件扩展名：.py→python, .ts→typescript, .js→javascript, .tex→latex, .md→markdown, .yml→yaml）
- 默认显示文件名标签（可用 `:filename: false` 关闭）
- 继承所有代码块选项（linenos、emphasize-lines 等）

### 行过滤选项

Include 提供精细的行选择机制：

| 选项 | 类型 | 互斥组 | 说明 |
|------|------|--------|------|
| `:start-line:` | Number | start组 | 从指定行开始（0索引，负数从末尾计数） |
| `:start-at:` | String | start组 | 从第一次出现指定文本的行开始（含该行） |
| `:start-after:` | String | start组 | 从第一次出现指定文本之后开始 |
| `:end-line:` | Number | end组 | 到指定行结束（不含该行） |
| `:end-at:` | String | end组 | 到第一次出现指定文本结束（含该行） |
| `:end-before:` | String | end组 | 到第一次出现指定文本之前结束 |
| `:lines:` | String | 独占 | 精确选择行号 |

**互斥规则**：
- start 组（start-line/start-at/start-after/lines）只能选一个
- end 组（end-line/end-at/end-before/lines）只能选一个
- 同时使用多个会产生警告

#### 行号过滤示例

```markdown
:::{include} src/app.py
:lang: python
:start-line: 10
:end-line: 20
:::
```

包含第 10-19 行（0-indexed，start-line=10 → 第11行，end-line=20 → 到第20行之前）。

#### 文本标记过滤

```markdown
:::{include} src/app.py
:lang: python
:start-after: // START_CONCEPT
:end-before: // END_CONCEPT
:::
```

包含标记之间的内容，适合从源文件中提取文档相关的代码段。

#### lines 选项

lines 选项提供最灵活的行选择：

```markdown
:lines: 1,3,5-10,20-
```

- `1`：第1行（注意：lines 使用1-based索引，与 start-line 的0-based不同）
- `3`：第3行
- `5-10`：第5到10行
- `20-`：第20行到文件末尾

### 代码块选项（代码模式下可用）

代码模式下支持所有 CODE_DIRECTIVE_OPTIONS：

| 选项 | 说明 |
|------|------|
| `:caption:` | 代码标题 |
| `:linenos:` | 显示行号 |
| `:lineno-start:` | 行号起始值 |
| `:lineno-match:` | 匹配源文件行号（对连续行范围有效） |
| `:emphasize-lines:` | 高亮行（基于包含后的行号） |
| `:filename:` | 文件名标签（默认自动设置为文件名） |
| `:class:` / `:label:` | 通用选项 |

### 自动语言映射

```ts
function extToLanguage(ext) {
  return {
    ts: 'typescript', js: 'javascript', mjs: 'javascript',
    tex: 'latex', py: 'python', md: 'markdown', yml: 'yaml',
  }[ext] ?? ext;
}
```

## Embed 指令

`embed` 指令复用文档中已标记标签的内容，类似"引用并展开"：

```markdown
:::{embed} #fig-my-chart
:::
```

这会将标签为 `fig-my-chart` 的图表（或其他已标记元素）的内容复制到当前位置。

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| label | String | ✅ | 目标元素的标签（支持 `#` 前缀） |

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:remove-input:` | Boolean | 嵌入 Notebook 单元格时移除输入 |
| `:remove-output:` | Boolean | 嵌入 Notebook 单元格时移除输出 |
| `:class:` / `:label:` | - | 通用选项 |

### Embed vs Include vs Ref

| 机制 | 用途 | 来源 |
|------|------|------|
| `{ref}`label`` | 生成引用链接/编号 | 同项目内标签 |
| `:::{include}file` | 包含文件内容 | 外部文件 |
| `:::{embed}#label` | 复制展开标签内容 | 同项目内标签的内容 |

embed 最适合的场景：
- 在多个位置重复展示同一个图表
- 将 Notebook 输出的图表嵌入到文档正文中
- 创建摘要/概览页面，复用关键内容

```markdown
# 摘要

:::{embed}#fig-main-result
:::

:::{embed}#tbl-summary
:::
```

## Div 指令

`div` 指令是通用块级容器，用于添加 CSS 类名或分组内容：

```markdown
:::{div}
:class: custom-box

这一段内容被包裹在自定义容器中。
:::
```

输出为 `<div>` HTML 元素，常用于自定义样式。

## 相关概念

- [代码块](02-code-blocks.md) — literalinclude 使用的代码块选项
- [指令与角色基础](00-directive-role-basics.md)
