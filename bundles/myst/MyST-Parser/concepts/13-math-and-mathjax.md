---
type: Concept
title: 数学公式与 MathJax
description: dollarmath/amsmath 扩展的数学公式语法、MathJax 配置自动调整
tags: [myst, sphinx, math, mathjax, dollarmath, amsmath, latex, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 数学公式与 MathJax

MyST-Parser 通过 `dollarmath` 和 `amsmath` 扩展支持 LaTeX 数学公式，并自动配置 MathJax 以避免双重处理冲突。

## 启用数学扩展

```python
# conf.py
myst_enable_extensions = ["dollarmath", "amsmath"]
```

## dollarmath 语法

### 行内公式

使用单个 `$` 包裹：

```markdown
质能方程 $E = mc^2$ 是物理学的基础公式。

欧拉公式 $e^{i\pi} + 1 = 0$ 被称为最美的公式。
```

### 块级公式

使用双 `$$` 包裹：

```markdown
$$
\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
$$
```

块级公式可以带标签（用于交叉引用）：

```markdown
$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$ (quadratic-formula)
```

### dollarmath 配置项

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `myst_dmath_allow_labels` | True | 允许 `$$...$$ (label)` 标签语法 |
| `myst_dmath_allow_space` | True | 允许 `$ x $` 首尾有空格 |
| `myst_dmath_allow_digits` | True | 允许 `1$x$2` 首尾有数字 |
| `myst_dmath_double_inline` | False | 允许行内 `$$x$$`（默认 $$ 仅用于块级） |

### allow_space 注意

`dmath_allow_space=True`（默认）时，`$ x $` 是合法的行内公式。如果需要在文本中使用 `$` 作为货币符号，可以：

1. 使用反斜杠转义：`\$100`
2. 设置 `myst_dmath_allow_space = False`（此时只有 `$x$` 无空格才识别为公式）

## amsmath 扩展

`amsmath` 扩展支持 LaTeX AMS 数学环境，需同时启用 `dollarmath`：

### align 环境

```markdown
$$
\begin{align}
a &= b + c \\
  &= d + e + f \\
  &= g + h
\end{align}
$$
```

### gather 环境

```markdown
$$
\begin{gather}
a = b + c \\
d = e + f
\end{gather}
$$
```

### multline 环境

```markdown
$$
\begin{multline}
a + b + c + d + e + f + g + h + i \\
+ j + k + l + m + n
\end{multline}
$$
```

### 其他支持的环境

- `equation`、`equation*`
- `alignat`、`alignat*`
- `cases`
- `split`

## MathJax 自动配置

MyST-Parser 通过 `override_mathjax()` 函数在 `builder-inited` 事件中自动调整 MathJax 配置：

1. **移除 `$` 定界符**：Sphinx 内置的 MathJax 配置默认将 `$...$` 识别为行内数学，但 MyST-Parser 的 dollarmath 扩展已经将 `$...$` 解析为 math 节点，MathJax 不应再处理。因此 `override_mathjax()` 将 `$` 从 MathJax 的 `inlineMath` 配置中移除，避免双重渲染。

2. **添加 CSS 类**：将 `myst_mathjax_classes`（默认 `"tex2jax_process|mathjax_process|math|output_area"`）添加到 MathJax 的 `processClass` 中。

3. **控制开关**：通过 `myst_update_mathjax = False` 可以禁用此自动配置（当你需要自定义 MathJax 设置时）。

## 数学节点渲染

dollarmath 插件将数学公式解析为 markdown-it Token，渲染器生成 docutils math 节点：

- 行内公式 → `nodes.math`（行内）
- 块级公式 → `nodes.math_block`（块级，带 label/number 属性）

这些节点由 Sphinx/各 builder 的 math 扩展处理（HTML 输出为 MathJax `<span class="math">`，LaTeX 输出为原生 `\( \)`/`\[ \]`）。

## 相关概念

- [扩展语法系统](/concepts/05-extension-system.md)
- [配置系统](/concepts/04-config-system.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
- [启用扩展实战](/examples/02-enable-extensions.md)
