---
type: concept
title: "Typst 导出"
description: "myst-to-typst 将 MDAST 转换为 Typst 标记语言的 TypstSerializer 架构、宏命令收集和与 LaTeX 导出的对称设计"
tags: [myst-exporters, typst, serializer, macros, myst-to-typst]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-typst/src/index.ts"
    facts: [F-021, F-022, F-023, F-024]
  - path: "jtex/src/typst/imports.ts"
    facts: [F-031]
---

# Typst 导出

Typst 导出由 `myst-to-typst` 包提供。Typst 是一个新一代的标记语言和排版系统，设计上比 LaTeX 更简洁现代。myst-to-typst 的架构与 myst-to-tex 高度对称，但针对 Typst 的语法特性做了适配。

## Typst 语法简介

```typst
= 一级标题
== 二级标题

普通段落文本，*粗体*，_斜体*，`行内代码`。

$ E = m c^2 $ 是行内公式。

$
  integral_0^infinity e^(-x^2) dif x = sqrt(pi)/2
$ 是块级公式。

#figure(image("path.png"), caption: [图片标题]) <fig:label>

@fig:label 引用图片。

#table(
  columns: (auto, 1fr),
  [表头1], [表头2],
  [单元格], [内容],
)
```

核心语法特征：
- 标题用 `=` 前缀（数量对应层级）
- 命令用 `#` 前缀（如 `#figure`、`#image`、`#table`）
- 内容块用 `[]` 包裹
- 标签用 `<label>` 定义，用 `@label` 引用
- 宏/自定义函数用 `#let name = ...`
- 导入用 `#import "path": *`

## TypstSerializer 架构

```typescript
class TypstSerializer implements ITypstSerializer {
  file: VFile;
  options: Options;
  stack: boolean[];     // 环境栈（数学模式等）
  text: string[];       // 输出文本行
  imports: Set<string>; // macros 集合
  commands: Record<string, any>; // 自定义命令
  macros: Set<string>;  // 需导出到 myst-imports.typ 的宏定义
  headingIdentifiers: Record<string, number>; // 标题去重计数
  references: References;
  footnotes: Record<string, FootnoteDefinition>;
  glossary: Record<string, [string, string]>;
  abbreviations: Record<string, [string, string]>;
  handlers: Record<string, TypstHandler>;
}
```

### 核心方法

| 方法 | 说明 |
|------|------|
| `write(value)` | 追加字符串到当前行 |
| `text(value)` | 转义 Typst 特殊字符后写入（`#`、`$`、`[`、`]`、`<`、`>`、`\`、`*`、`_`）|
| `renderChildren(node, opts?)` | 遍历子节点，按 type 查 handler 分发 |
| `renderBlock(node, fn)` | 渲染块级元素（前后确保换行） |
| `newline()` | 添加换行 |
| `renderCommand(cmd, args)` | 输出 `#cmd(args)` 或 `#cmd[content]` |
| `renderList(body, opts?)` | 渲染列表 |
| `inMathMode()` | 判断当前是否在数学模式 |
| `addMacro(name, definition)` | 注册宏到 macros 集合 |

### 数学模式追踪

`stack` 数组用于追踪嵌套上下文：
- 进入数学块时 push `true`，退出时 pop
- `inMathMode()` 检查栈顶是否为数学模式
- 这影响转义行为（数学模式下 `{`、`}`、`#` 不需要转义，而文本模式下需要）

## TypstResult 输出结构

```typescript
type TypstResult = {
  value: string;                 // Typst 正文内容
  imports: Set<string>;          // 需要 #import 的宏包
  commands: Record<string, any>; // 自定义命令定义
  macros: Set<string>;           // 需要写入 myst-imports.typ 的宏
};
```

与 LatexResult 对称：
- `value` → 正文
- `macros` 对应 LaTeX 的 `commands`（数学宏/自定义函数）
- `imports` 对应 LaTeX 的 `imports`（usepackage 等价于 #import）
- Typst 没有显式的 preamble 概念，所有宏定义通过 `myst-imports.typ` 文件引入

## jtex Typst 路径整合

jtex 对 Typst 的处理与 LaTeX 对称：

1. **renderImports**（kind='typst'）：
   - macros 不为空时，生成 `#import "myst-imports.typ": *`
   - commands 生成 `#let \name = $definition$` 格式
   - preamble 直接追加到内容前面

2. **myst-imports.typ 文件**：
   - macros 集合的内容写入独立的 `.typ` 文件
   - 内容包含数学函数定义、自定义 helper 函数
   - 主模板通过 `#import` 引入

3. **模板变量**：Typst 模板使用相同的 Nunjucks 语法（`[-CONTENT-]`、`[-doc.title-]` 等），但文件扩展名为 `.typ`

## 节点映射要点

| MyST 节点 | Typst 输出 | 说明 |
|----------|-----------|------|
| heading(1) | `= Title` | 一级标题 |
| heading(2) | `== Title` | 二级标题 |
| paragraph | 普通文本 | 段落间空行 |
| strong | `*text*` | 粗体 |
| emphasis | `_text_` | 斜体 |
| inlineCode | `` `code` `` | 行内代码 |
| code | ```` ```lang\ncode\n``` ```` | 代码块（Typst 的 raw 语法） |
| list(ul) | `- item` | 无序列表 |
| list(ol) | `+ item` | 有序列表 |
| link | `#link("url")[text]` | 链接 |
| image | `#image("path")` | 图片 |
| container/figure | `#figure(image("path"), caption: [cap]) <label>` | 图片+标题 |
| math/display | `$ formula $`（单独段落） | 块级公式 |
| math/inline | `$formula$`（行内） | 行内公式 |
| crossReference | `@label` | 引用（Typst 自动处理编号） |
| cite | `@key` | 参考文献引用 |
| table | `#table(columns: ..., ...)` | 表格 |
| raw/typst | 直接透传 | Typst 原生代码透传 |
| footnote | `#footnote[content]` | 脚注 |

### 数学转换

LaTeX 数学语法与 Typst 数学语法有差异，myst-to-typst 的数学 handler 需要做转换：
- `\frac{a}{b}` → `(a)/(b)` 或 `frac(a, b)`
- `\sum_{i=1}^{n}` → `sum_(i=1)^n`
- `\alpha`、`\beta` 等希腊字母保留（Typst 支持相同的转义序列）
- `\textbf{}` → `bold()`、`\textit{}` → `italic()`
- `\begin{bmatrix}...\end{bmatrix}` → `mat(...; ...)`

### 标题去重

`headingIdentifiers: Record<string, number>` 跟踪已使用的标题标识符。如果两个标题文本相同，Typst 会自动添加数字后缀（如 `label`、`label-1`、`label-2`），Serializer 模拟此行为。

### 引用处理

- 文档内交叉引用：直接 `@label`
- 文档间引用：`#link("path")` 或根据配置处理
- 参考文献：`@citationkey`，需要 BibTeX/Typst 原生引用配置

## PDF 编译

Typst 原生支持 PDF 输出（无需 LaTeX 工具链）：

```bash
typst compile output.typ output.pdf
```

myst-cli 的 build 层在 Typst 模板渲染完成后，调用 typst CLI 编译为 PDF。Typst 编译速度比 LaTeX 快（秒级），且自动处理多次编译（无需 latexmk 循环）。

## 相关概念

- [00-exporter-architecture](00-exporter-architecture.md)：统一导出架构
- [02-latex-export](02-latex-export.md)：LaTeX 导出（对称对比）
- [03-pdf-export](03-pdf-export.md)：PDF 生成
- [08-jtex-template-engine](08-jtex-template-engine.md)：jtex 模板引擎
