---
type: Concept
title: 支持的函数
description: KaTeX 官网 Supported Functions 页面的 14 个分类体系说明，涵盖重音、分隔符、环境、HTML 扩展、字母与 Unicode、布局、逻辑与集合论、宏、运算符、关系符、特殊记号、样式/颜色/字号/字体、符号与标点、单位，以及 HTML 扩展的 trust/strict 安全要求。
tags: [katex, supported-functions, reference, tex-commands, categories]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-supported
    resource: /references/katex-website.md#web-supported
    title: KaTeX 官网 Supported Functions 页面
  - id: web-options
    resource: /references/katex-website.md#web-options
    title: KaTeX 官网 Options 页面
  - id: facts
    resource: /spec/facts.md
    title: KaTeX 事实清单
---

## 概述

KaTeX 官网 [Supported Functions](https://katex.org/docs/supported) 页面按逻辑分组列出 KaTeX 支持的 TeX 函数，共 **14 个 H2 分类**[^web-supported]。本文档说明各分类的内容范围、使用要点和安全注意事项，作为查找命令的导航；完整的函数清单以官网页面为准，字母序索引见 [支持表](20-support-table.md)。

从源码视角看，这些函数的实现位于 `src/functions/` 目录（共 43 个 .ts 文件），通过 `defineFunction` 注册到全局表中[^src]。注册表机制详见 [函数注册表](08-function-registry.md)。

## 分类体系

### 1. Accents（重音）

重音命令用于在字符上方添加变音符号。KaTeX 支持的重音命令包括[^web-supported]：

- 单字符重音：`\tilde`、`\hat`、`\vec`、`\bar`、`\dot`、`\ddot`、`\acute`、`\grave`、`\breve`、`\check`、`\mathring`
- 宽体重音：`\widetilde`、`\widehat`
- 多点重音：`\dddot`、`\ddddot`
- 上下延伸重音：`\overgroup`、`\undergroup`

### 2. Delimiters（分隔符）

分隔符包括各种括号及其尺寸控制：

- **自动尺寸**：`\left` ... `\right`、`\middle`，根据内容自动调整括号大小
- **手动尺寸**：`\big`、`\Big`、`\bigg`、`\Bigg` 及其 l/m/r 变体（如 `\bigl`、`\Bigr`）
- **常见分隔符**：圆括号 `()`、方括号 `[]`、花括号 `\{\}`、绝对值 `|`、范数 `\|`、角括号 `\langle\rangle`、上取整 `\lceil\rceil`、下取整 `\lfloor\rfloor`

### 3. Environments（环境）

KaTeX 支持多种数学环境[^web-supported]：

- **矩阵类**：`matrix`、`pmatrix`（圆括号）、`bmatrix`（方括号）、`Bmatrix`（花括号）、`vmatrix`（竖线）、`Vmatrix`（双竖线）
- **对齐类**：`aligned`、`gathered`
- **cases**：`cases`（分段函数）
- **数组**：`array`

> **注意**：KaTeX 不支持 LaTeX 的 `align` 环境（因为 LaTeX 不在数学模式中支持 `align`），应使用数学模式中的 `aligned` 环境[^facts]。详见 [常见问题](21-common-issues.md)。

### 4. HTML（HTML 扩展）

KaTeX 提供非标准的 HTML 扩展命令，可直接生成 HTML 属性和元素[^web-supported]：

- 链接：`\url{url}`、`\href{url}{text}`
- 图片：`\includegraphics{url}`
- CSS 类/ID/样式：`\htmlClass{class}{content}`、`\htmlId{id}{content}`、`\htmlStyle{style}{content}`
- 数据属性：`\htmlData{key=value}{content}`

**安全要求**：

1. HTML 扩展命令对不可信输入有潜在危险，默认禁用（`trust: false`），尝试使用时命令名以 `errorColor` 渲染（红色）[^web-supported]
2. 完全信任输入需传 `trust: true`；推荐使用 trust 函数仅启用部分命令或 URL
3. `\html` 前缀命令（`\htmlClass` 等）是非标准扩展，还需放宽 `strict` 选项中的 `htmlExtension` 设置[^web-supported]

trust 控制的七类命令及 context 结构详见 [安全与错误处理](18-security-and-errors.md#trust)。

### 5. Letters and Unicode（字母与 Unicode）

KaTeX 对 Unicode 字符的支持策略[^web-supported]：

- 在 `strict` 为 `false` 或 `"warn"`（默认）时，KaTeX 在文本和数学模式下接受所有 Unicode 字母
- 未识别字符按文本模式处理
- 任何字符可通过 `\char"HHHH` 写入（十六进制 Unicode 码点）
- 希腊字母、希伯来字母等通过命令（如 `\alpha`、`\aleph`）输入

### 6. Layout（布局）

布局类命令控制公式的水平和垂直排列：

- 分数：`\frac`、`\dfrac`、`\tfrac`、`\cfrac`（连分数）
- 二项式系数：`\binom`、`\dbinom`、`\tbinom`
- 上下线：`\overline`、`\underline`、`\overbrace`、`\underbrace`
- 堆叠：`\stackrel`、`\overset`、`\underset`
- 换行与间距：`\\`、`\newline`、`\cr`、`\,`、`\:`、`\;`、`\quad`、`\qquad`
- 上下划线：`\rule`、`\hline`、`\hdashline`
- 盒子：`\boxed`、`\fbox`、`\fcolorbox`

### 7. Logic and Set Theory（逻辑与集合论）

逻辑与集合论符号，包括：

- 逻辑运算符：`\land`（∧）、`\lor`（∨）、`\lnot`（¬）、`\implies`（⇒）、`\iff`（⇔）
- 集合符号：`\in`（∈）、`\notin`（∉）、`\subset`（⊂）、`\supset`（⊃）、`\subseteq`（⊆）、`\cup`（∪）、`\cap`（∩）、`\emptyset`（∅）
- 量词：`\forall`（∀）、`\exists`（∃）

### 8. Macros（宏）

宏命令支持在 KaTeX 中定义和使用自定义命令：

- 定义：`\def`、`\newcommand`、`\renewcommand`、`\gdef`、`\global\def`
- 赋值：`\let`、`\global\let`
- 展开控制：`\expandafter`、`\noexpand`、`\relax`
- 参数占位符：`#1`~`#9`，`##` 转义为 `#`

宏也可通过 `settings.macros` 选项或 `__defineMacro` API 注册。宏系统的完整说明见 [宏系统](09-macro-system.md)；持久宏的安全边界见 [安全与错误处理](18-security-and-errors.md)。

### 9. Operators（运算符）

运算符分类：

- **二元运算符**：`+`、`-`、`\pm`（±）、`\times`（×）、`\div`（÷）、`\cdot`（·）、`\ast`（∗）、`\star`（⋆）
- **大算符**：`\sum`（∑）、`\int`（∫）、`\prod`（∏）、`\bigcup`、`\bigcap`、`\lim`、`\oint`
- **函数名**：`\sin`、`\cos`、`\tan`、`\log`、`\ln`、`\exp`、`\max`、`\min` 等（罗马体直立显示）

大算符在显示模式（`displayMode: true`）下使用大号字形，上下标位于正上方/正下方。

### 10. Relations（关系符）

关系符包括：

- **比较**：`=`、`\neq`（≠）、`<`、`>`、`\leq`（≤）、`\geq`（≥）、`\ll`（≪）、`\gg`（≫）
- **等价**：`\approx`（≈）、`\sim`（∼）、`\equiv`（≡）、`\cong`（≅）、`\propto`（∝）
- **箭头**：`\rightarrow`（→）、`\leftarrow`（←）、`\Rightarrow`（⇒）、`\Leftarrow`（⇐）、`\leftrightarrow`（↔）、`\Leftrightarrow`（⇔）
- **集合关系**：`\in`、`\ni`、`\subset`、`\supset`、`\subseteq`、`\supseteq`

### 11. Special Notation（特殊记号）

特殊记号包括：

- 微积分：`\partial`（∂）、`\nabla`（∇）、`\mathrm{d}`（微分 d）
- 省略号：`\cdots`（⋯）、`\ldots`（…）、`\vdots`（⋮）、`\ddots`（⋱）
- 角度：`\angle`（∠）、`\perp`（⊥）、`\parallel`（∥）
- 无穷：`\infty`（∞）
- 正负：`\pm`（±）、`\mp`（∓）

### 12. Style / Color / Size / Font（样式/颜色/字号/字体）

控制公式外观的命令：

- **颜色**：`\color{color}`（切换开关模式）、`\textcolor{color}{text}`、`\colorbox{color}{text}`、`\fcolorbox{border}{bg}{text}`
- **字号**：`\tiny`、`\scriptsize`、`\footnotesize`、`\small`、`\normalsize`、`\large`、`\Large`、`\LARGE`、`\huge`、`\Huge`（共 11 级）
- **字体样式**：`\mathbf`（粗体）、`\mathit`（斜体）、`\mathrm`（罗马体）、`\mathsf`（无衬线）、`\mathtt`（打字机体）、`\mathbb`（黑板粗体）、`\mathcal`（花体）、`\mathfrak`（Fraktur）、`\mathscr`（脚本体）
- **模式切换**：`\text`、`\textrm`、`\textbf`、`\textit` 等（文本模式）

> **注意**：`colorIsTextColor` 选项可改变 `\color` 的行为——默认为切换开关模式（匹配 LaTeX），设为 `true` 时恢复旧版参数式行为（匹配 MathJax）[^web-options]。

### 13. Symbols and Punctuation（符号与标点）

各类符号和标点：

- 标点：`,`、`;`、`!`、`?`、`:`（数学冒号）
- 特殊符号：`\%`（%）、`\#`（#）、`\&`（&）、`\_`（_）、`\$`（$）、`\S`（§）、`\P`（¶）
- 箭头与装饰：`\prime`（′）、`\dag`（†）、`\ddag`（‡）
- 空格与间距：`\ `（反斜杠空格）、`\!`（负间距）、`\,`、`\:`、`\;`、`\quad`、`\qquad`

### 14. Units（单位）

KaTeX 支持所有 TeX 单位，用于 `\kern`、`\rule`、`\hspace` 等命令：

- **相对单位**：`em`、`ex`、`mu`（数学单位，1mu = 1/18 em）
- **绝对单位**：`pt`、`pc`、`in`、`cm`、`mm`、`bp`、`dd`、`cc`、`sp`

绝对单位相对于默认 TeX 字号 10pt 缩放，例如 `\kern1cm` 等价于 `\kern2.845275em`。完整的单位换算说明见 [字体与单位](17-fonts-and-units.md#tex-单位与绝对长度)。

## 源码对应关系

从源码视角看，官网 Supported Functions 页面列出的命令主要由以下位置实现[^src]：

| 源码位置 | 内容 |
|---------|------|
| `src/functions/*.ts`（43 个文件） | 各命令的 handler + htmlBuilder + mathmlBuilder 实现 |
| `src/macros.ts` | 内置宏定义（通过宏而非函数实现的命令） |
| `src/symbols.ts` | 内置符号注册表（math/text 模式下的单字符符号） |
| `src/environments/` | array、cd 环境实现 |

部分符号通过宏而非 `\DeclareMathSymbol` 定义，展开时可能展开为多个 token 并受 `\expandafter` 和 `\noexpand` 影响[^facts]。

## 查阅建议

1. **知道分类，浏览命令**：在本文档或官网 Supported Functions 页面按分类查找
2. **知道形状，不知名称**：使用字母序的 [支持表](20-support-table.md)，或使用 [Detexify](https://detexify.kirelabs.org/classify.html) 手写识别
3. **确认是否支持**：查阅 [Support Table](https://katex.org/docs/support_table)，该页面同时列出支持和不支持的函数
4. **深入实现**：根据命令名称在 `src/functions/` 目录找到对应源文件

## 相关概念

- [支持表](20-support-table.md) — 字母序支持表与 Detexify 工具
- [函数注册表](08-function-registry.md) — defineFunction 机制与 FunctionSpec
- [宏系统](09-macro-system.md) — 宏定义与展开机制
- [配置系统](10-settings-options.md) — strict、trust、colorIsTextColor 等选项
- [安全与错误处理](18-security-and-errors.md) — HTML 扩展的 trust 安全要求
- [常见问题](21-common-issues.md) — align vs aligned、MathJax 差异等

[^web-supported]: 官网 Supported Functions 页面，https://katex.org/docs/supported
[^web-options]: 官网 Options 页面，https://katex.org/docs/options
[^src]: KaTeX 源码信源，`src/functions/` 目录含 43 个函数实现文件（F-012）
[^facts]: KaTeX 事实清单，W-137（align vs aligned）
