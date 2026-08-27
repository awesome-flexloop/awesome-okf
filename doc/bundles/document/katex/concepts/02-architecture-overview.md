---
type: Concept
title: 架构总览
description: KaTeX 的三层消化管模型（Lexer→MacroExpander→Parser）与渲染管线（buildTree→buildHTML/buildMathML→输出）的整体架构。
tags: [katex, architecture, pipeline, digestive-model]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## 整体架构

KaTeX 的处理流程遵循 TeX 的 **消化管模型**（Digestive Model），将 LaTeX 字符串像食物一样逐层处理：

```
输入字符串
    │
    ▼
┌─────────┐  Token  ┌────────────────┐  Token  ┌─────────┐  ParseNode[]  ┌──────────┐  DomSpan  ┌──────┐
│  Lexer  │ ──────▶ │ MacroExpander  │ ──────▶ │ Parser  │ ────────────▶ │ buildTree│ ────────▶ │ 输出  │
│ (mouth) │         │   (gullet)     │         │(stomach)│               │          │           │      │
└─────────┘         └────────────────┘         └─────────┘               └──────────┘           └──────┘
   词法分析            宏展开                    语法解析                    构建渲染           DOM/字符串
```

### 四个核心阶段

| 阶段 | 类/函数 | 输入 | 输出 | TeX术语 |
|------|---------|------|------|---------|
| 词法分析 | `Lexer` | LaTeX字符串 | Token流 | mouth（口） |
| 宏展开 | `MacroExpander` | Token流 | 展开后的Token流 | gullet（食道） |
| 语法解析 | `Parser` | 展开后的Token流 | ParseNode[]（解析树） | stomach（胃） |
| 渲染构建 | `buildTree()` | ParseNode[] + Settings | DomSpan（虚拟DOM树） | — |

这个分层的关键设计点是：**每一层只和相邻层通信**，且数据流向是单向的。

## 数据流详解

### 1. 词法分析（Lexer）

Lexer 负责将原始字符串切分为 Token 序列。它使用一个大正则表达式 `tokenRegex` 识别以下内容：

- **空白字符**：空格、换行等
- **控制词（control word）**：反斜杠开头后跟字母序列，如 `\frac`、`\alpha`
- **控制符号（control symbol）**：反斜杠开头后跟单个非字母字符，如 `\{`、`\$`、`\+`
- **Unicode字符**：包括代理对（surrogate pair，处理emoji等）和组合变音符号
- **特殊命令**：`\verb` 和 `\verb*`（原样文本命令）有专门处理
- **注释**：`%` 开头的内容到行尾被忽略（catcode=14）

Lexer 还维护 `catcodes`（分类码）映射，控制某些字符的特殊行为。

### 2. 宏展开（MacroExpander）

MacroExpander 是一个 Token 转换器。它从 Lexer 获取 Token，但在返回 Token 给 Parser 之前，会检查当前 Token 是否是一个宏名：

- 如果是宏，就将宏的展开结果压入内部 Token 栈，然后递归继续展开
- 如果不是宏（普通Token），直接返回给 Parser

这个"展开直到不是宏"的过程通过 `expandNextToken()` 方法实现，带有展开次数计数防止无限递归。

MacroExpander 还维护：
- **分组栈**：`{...}` 和 `\begingroup...\endgroup` 创建新的作用域
- **命名空间**：`Namespace` 类实现宏定义的嵌套作用域

### 3. 语法解析（Parser）

Parser 是解析的核心。它从 MacroExpander 获取已展开的 Token，递归构建 ParseNode 树：

- **parseExpression()**：解析表达式序列，处理中缀运算符（如 `\over`）
- **parseAtom()**：解析单个原子（符号、函数调用、组），并处理紧随的上下标
- **parseGroup()**：解析分组（`{...}`、`\begingroup...\endgroup`）或单个符号/函数
- **parseFunction()**：查询函数注册表，调用对应handler构建ParseNode
- **parseArguments()**：根据函数签名消费指定数量和类型的参数

Parser 在解析过程中会切换模式（math/text），因为某些命令只在特定模式下可用。

### 4. 渲染构建（buildTree）

`buildTree()` 接收 ParseNode 树和 Settings，执行以下步骤：

1. 从 Settings 创建 Options 对象（包含当前样式、字号、颜色等渲染状态）
2. 根据 `settings.output` 选择输出格式：
   - `"mathml"`：仅生成 MathML
   - `"html"`：仅生成 HTML
   - `"htmlAndMathml"`（默认）：同时生成，MathML在前、HTML在后
3. 对于 HTML+MathML 双输出，使用 `combineMathMLAndHtml()` 将两者组合
4. 如果是 displayMode，用 `displayWrap()` 添加外层包裹span（处理编号和对齐）
5. 返回最终的 DomSpan 虚拟DOM节点

## 注册表架构

KaTeX 的核心引擎是"空壳"，所有具体的 LaTeX 命令都通过注册表插件式注册：

- **defineFunction**：注册 LaTeX 命令的解析handler、HTML builder、MathML builder
- **defineEnvironment**：注册 LaTeX 环境（如 `\begin{array}...\end{array}`）
- **defineMacro**：注册宏定义（简单的字符串替换或函数展开）
- **symbols.ts**：注册单个符号（Unicode字符→符号节点的映射）

`src/functions/` 目录下的43个文件和 `src/environments/` 下的2个文件就是通过这些注册函数将具体命令"插入"到核心引擎中。

## 模式系统

KaTeX 有两种解析模式：

- **math 模式**：数学模式，处理数学符号、运算符等
- **text 模式**：文本模式，通过 `\text{}` 等命令进入，按普通文本处理

渲染时的 **Style**（8种）独立于解析模式，控制的是视觉样式：
- display / text / script / scriptscript（行间/行内/上标/上上标）
- 每种又有 cramped（压缩）和非cramped两种变体

## 不可变状态传递

渲染阶段的 Options 对象是不可变的。当子节点需要不同的样式/颜色/字号时，通过 `options.havingStyle()`、`options.withColor()` 等方法创建新的 Options 实例传入，而非修改原对象。这避免了子树渲染对兄弟节点和父节点的状态污染。

## 虚拟DOM层

构建阶段不直接操作真实 DOM 或拼接字符串，而是构建一层轻量虚拟DOM树：
- `Span`：`<span>` 元素
- `Anchor`：`<a>` 元素（链接）
- `SymbolNode`：带有字体和位置信息的文本节点
- `SvgNode`/`PathNode`/`LineNode`：SVG元素（根号、分数线条等）

虚拟节点提供两个输出方法：
- `toNode()`：转为真实 DOM 元素（供 `render()` 使用）
- `toMarkup()`：序列化为 HTML 字符串（供 `renderToString()` 使用）

## 相关概念

- [词法分析器（Lexer）](03-lexer.md)
- [宏展开器（MacroExpander）](04-macro-expander.md)
- [解析器（Parser）](05-parser.md)
- [渲染管线](06-render-pipeline.md)
- [虚拟DOM树](07-dom-tree.md)
- [函数注册表](08-function-registry.md)
