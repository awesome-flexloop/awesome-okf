---
type: concept
title: "数学公式"
description: "math指令（块级）和math角色（行内）的LaTeX数学公式语法、Typst备用内容和数学排版"
tags: [myst-syntax, math, latex, typst, equations]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/math.ts"
    facts: [F-S023]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/math.ts"
    facts: [F-S050]
---

# 数学公式

MyST 支持 LaTeX 语法的数学公式，分为块级公式（`math` 指令）和行内公式（`math` 角色）。

## 行内公式

使用 `{math}` 角色在文本中插入行内公式：

```markdown
爱因斯坦质能方程 {math}`E=mc^2` 是最著名的物理公式之一。
```

也可以使用标准的 `$...$` 分隔符：

```markdown
爱因斯坦质能方程 $E=mc^2$ 是最著名的物理公式之一。
```

行内公式生成 `inlineMath` MDAST 节点。

### Typst 备用内容

行内公式支持 `:typst:` 选项提供 Typst 专用内容：

```markdown
{math}`\alpha`
:typst: alpha
```

如果未提供 typst 选项，LaTeX 内容会自动转换为 Typst。

## 块级公式

使用 `math` 指令插入块级（display）公式：

````markdown
```{math}
:label: eq-pythagorean

a^2 + b^2 = c^2
```
````

也可以使用 `$$...$$` 分隔符：

```markdown
$$
a^2 + b^2 = c^2
$$ (eq-pythagorean)
```

块级公式生成 `math` MDAST 节点，独立成行并居中显示。

### 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `:label:` / `:name:` | String | 公式标签，用于交叉引用 |
| `:class:` | String | CSS 类名 |
| `:typst:` | String | Typst 专用数学内容 |
| `:enumerated:` / `:numbered:` | Boolean | 是否编号 |
| `:enumerator:` / `:number:` | String | 显式编号值 |

### 公式编号和引用

带标签的公式会自动编号，可以通过 `{eq}` 或 `{ref}` 角色引用：

````markdown
```{math}
:label: eq-euler

e^{i\pi} + 1 = 0
```

欧拉恒等式（见公式 {eq}`eq-euler`）被称为"最美的数学公式"。
````

输出类似："欧拉恒等式（见公式 (1)）被称为..."。

### Typst 块级公式

````markdown
```{math}
:typst: alpha + beta = gamma

\alpha + \beta = \gamma
```
````

在 Typst 导出中使用 `:typst:` 指定的内容，其他格式使用 LaTeX 内容。这对于 LaTeX-to-Typst 自动转换不完美的情况很有用。

## 常用 LaTeX 数学语法

MyST 使用 MathJax/KaTeX 渲染数学公式，支持标准 LaTeX 数学命令：

### 基本运算

```markdown
行内：分数 $\frac{a}{b}$，根号 $\sqrt{x}$，上标 $x^2$，下标 $x_i$

块级：
$$
\frac{\partial f}{\partial x} = \lim_{\Delta x \to 0} \frac{f(x+\Delta x) - f(x)}{\Delta x}
$$
```

### 矩阵

```markdown
$$
A = \begin{pmatrix}
a_{11} & a_{12} \\
a_{21} & a_{22}
\end{pmatrix}
$$
```

### 求和与积分

```markdown
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

### 多行对齐（使用 aligned 环境）

````markdown
```{math}
:label: eq-align

\begin{aligned}
(x+y)^2 &= (x+y)(x+y) \\
&= x^2 + 2xy + y^2
\end{aligned}
```
````

## Tight 排版

math 指令的 `tight` 属性由解析器自动设置（来自围栏代码块的紧凑模式），影响公式上下间距。

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [交叉引用与引用](06-cross-references-citations.md)
