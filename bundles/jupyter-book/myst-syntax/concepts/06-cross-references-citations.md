---
type: concept
title: "交叉引用与引用"
description: "ref角色、cite角色族、doc/download/term角色的交叉引用和文献引用机制"
tags: [myst-syntax, cross-reference, citation, cite, ref, bibliography]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/reference.ts"
    facts: [F-S049]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/cite.ts"
    facts: [F-S046, F-S047, F-S048]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/bibliography.ts"
    facts: [F-S027]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/glossary.ts"
    facts: [F-S028]
---

# 交叉引用与引用

MyST 提供了强大的交叉引用和学术引用系统，支持标签引用、文献引用、文档间引用和术语引用。

## 交叉引用（Ref 角色）

使用 `{ref}` 角色引用已标记标签的元素：

```markdown
如 {ref}`fig-architecture` 所示，系统由三个模块组成。
```

引用格式为 `{ref}`label``，标签通过 `:label:` 选项在指令中定义。

### 别名

| 角色名 | 用途 |
|--------|------|
| `ref` | 通用引用 |
| `eq` | 公式引用（输出 (1) 格式） |
| `numref` | 编号引用（Sphinx 兼容） |
| `prf:ref` / `proof:ref` | 证明环境引用 |

### 自定义显示文本

可以覆盖引用的显示文本，使用尖括号语法：

```markdown
如 {ref}`架构图 <fig-architecture>` 所示。
```

格式：`{ref}`显示文本 <label>``

这在公式引用中特别有用：

```markdown
根据 {eq}`欧拉公式 <eq-euler>`，我们可以得出...
```

### 可引用的元素

任何带 `:label:` 选项的指令都可以被引用：

| 元素 | 标签选项 | 引用输出示例 |
|------|----------|-------------|
| figure | `:label: fig-x` | "Figure 1" |
| table | `:label: tbl-x` | "Table 1" |
| code | `:label: code-x` | "Code 1" |
| math | `:label: eq-x` | "(1)" |
| section 标题 | 隐式 | 标题文本 |
| admonition | `:label: note-x` | 提示框标题 |

## 文献引用（Cite 角色）

`{cite}` 角色用于引用 BibTeX 参考文献：

```markdown
这一方法最早由 {cite}`knuth1984texbook` 提出。
```

多引用用逗号分隔：

```markdown
多项研究 {cite}`knuth1984texbook, lamport1994latex` 表明...
```

### 引用风格（CiteKind）

通过不同的角色别名控制引用风格：

#### Parenthetical 引用（括号式）

| 角色 | 效果 | 输出示例 |
|------|------|----------|
| `cite:p` | 括号引用 | (Knuth 1984) |
| `cite:ps` | 括号引用（短格式） | (Knuth, 1984) |
| `cite:ct` | 括号引用（大写） | (Knuth 1984) |
| `cite:cts` | 括号引用（大写+短格式） | (Knuth, 1984) |
| `cite:alp` / `cite:alps` | Alpha 风格 | [Knu84] |
| `cite:label` / `cite:labelpar` | 标签引用 | [1] |

#### Narrative 引用（叙述式）

| 角色 | 效果 | 输出示例 |
|------|------|----------|
| `cite` 或 `cite:t` | 叙述引用 | Knuth (1984) |
| `cite:ts` | 叙述引用（短格式） | Knuth, 1984 |

默认的 `{cite}`key`` 使用 narrative 风格。

#### 部分引用

| 角色 | 输出 |
|------|------|
| `cite:year` / `cite:yearpar` | 仅年份：(1984) |
| `cite:author` / `cite:authors` | 仅作者：Knuth |
| `cite:authorpar` / `cite:authorpars` | 作者（括号）：(Knuth) |
| `cite:cauthor` / `cite:cauthors` | 作者（大写） |

### 前缀和后缀

支持在引用键前后添加文本：

```markdown
如 {cite:p}`{see}knuth1984texbook{p. 1166}` 所述。
```

输出：(see Knuth 1984, p. 1166)

格式：`{prefix}key{suffix}`

### 引用分组

多引用自动分组在 CiteGroup 中，确保样式一致：

```markdown
{cite:p}`knuth1984, lamport1994`
→ (Knuth 1984; Lamport 1994)
```

`cite:alp` 风格例外，不分组（每个引用独立显示为 [Knu84] 格式）。

## 参考文献列表

`bibliography` 指令在文档中插入参考文献列表：

```markdown
:::{bibliography}
:::
```

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:filter:` | String | 过滤引用（如只显示特定类型） |

BibTeX 文件在 myst.yml 中配置：

```yaml
project:
  bibliography:
    - references.bib
```

或自动发现项目目录中的所有 .bib 文件。

## 术语引用（Term 角色）

`{term}` 角色链接到 glossary 中定义的术语：

```markdown
{term}`Markdown` 是一种轻量级标记语言。
```

术语在 `glossary` 指令中定义：

```markdown
:::{glossary}
Markdown
  一种轻量级标记语言，由 John Gruber 于 2004 年创建。

MyST
  Markedly Structured Text，Markdown 的扩展语法。
:::
```

## 文档引用（Doc 角色）

`{doc}` 角色链接到项目中的其他文档：

```markdown
参见 {doc}`getting-started` 了解安装方法。
```

## 下载链接（Download 角色）

`{download}` 角色创建文件下载链接：

```markdown
下载 {download}`示例文件 <examples/sample.pdf>`。
```

## 缩写（Abbr 角色）

`{abbr}` 或 `{abbreviation}` 角色创建缩写，鼠标悬停显示全称：

```markdown
{abbr}`CSS (Cascading Style Sheets)` 用于网页样式。
```

格式：`{abbr}`缩写(全称)``，使用正则 `/^(.+?)\(([^()]+)\)$/` 匹配。

输出为 `<abbr title="全称">缩写</abbr>` HTML 元素。

## 引用工作流总结

```
1. 在文档中定义标签：
   :::{figure} image.png
   :label: fig-my-figure
   图标题
   :::

2. 在需要处引用：
   如 {ref}`fig-my-figure` 所示...

3. 参考文献：
   - 在 myst.yml 中声明 bibliography: [refs.bib]
   - 使用 {cite}`key` 引用
   - 使用 :::{bibliography}::: 插入文献列表

4. 术语：
   - 在 :::{glossary}::: 中定义术语
   - 使用 {term}`术语名` 引用
```

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [图片与图表](03-figures-images.md)
- [代码块](02-code-blocks.md)
