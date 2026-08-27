---
type: Concept
title: 词法分析器（Lexer）
description: KaTeX Lexer 的工作原理，包括正则分词、Token结构、分类码（catcodes）、注释处理和\verb命令。
tags: [katex, lexer, token, catcode, regex]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## Lexer 的角色

Lexer（词法分析器）是 KaTeX 处理管线的第一层（TeX 术语中的 "mouth"）。它的职责是将原始的 LaTeX 字符串切分为 Token 流，供下游的 MacroExpander 消费。

Lexer 位于 [src/Lexer.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Lexer.ts)。

## 核心类

```typescript
export default class Lexer implements LexerInterface {
    input: string;           // 输入字符串
    settings: Settings;      // 全局设置
    tokenRegex: RegExp;      // 分词正则
    catcodes: Record<string, number>;  // 分类码映射

    constructor(input: string, settings: Settings);
    lex(): Token;            // 获取下一个Token（核心方法）
}
```

## Token 结构

每个 Token 是 [src/Token.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Token.ts) 中定义的类实例：

```typescript
class Token {
    text: string;           // Token的文本内容
    loc: SourceLocation | null;  // 源码位置（start/end偏移）
    noexpand: boolean | null;    // 是否禁止展开（\noexpand标记）
    treatAsRelax: boolean | null;  // 是否视为\relax
}
```

- `text` 是 Token 的实际文本，对于控制序列如 `\frac`，text 就是 `"\\frac"`
- `loc` 记录了 Token 在原始输入中的位置范围，用于错误提示
- `noexpand` 和 `treatAsRelax` 是宏展开控制标志

## 分词正则

Lexer 的核心是一个大正则表达式 `tokenRegex`，它通过 `tokenRegexString` 构建，按以下优先级匹配：

| 优先级 | 模式 | 匹配内容 |
|--------|------|----------|
| 1 | `[\u0020\u00a0\n\r\t]` | 空白字符（空格、不换行空格、换行、回车、制表符） |
| 2 | `\\\\[ \t]*\n?[\u0020\u00a0\n\r\t]*` | 行尾反斜杠（续行符，消耗后续空白） |
| 3 | `%[^\n]*` | 注释（`%` 到行尾） |
| 4 | `\\\\verb\\*?([^a-zA-Z])((?:[\\S\\s])*?)(?:\\s*)\\1` | `\verb` 命令（任意定界符包裹的原样文本） |
| 5 | `\\\\verb\\*?\\s(?:[\\S])*?\\s` | `\verb` 命令（空格作为定界符） |
| 6 | `\\\\[a-zA-Z@]+` | 控制词（反斜杠+字母序列） |
| 7 | `\\\\[^a-zA-Z\\uD800-\\uDFFF]` | 控制符号（反斜杠+单个非字母非代理对字符） |
| 8 | `[\\uD800-\\uDBFF][\\uDC00-\\uDFFF][\\u0300-\\u036F\\u0483-\\u0487]*` | Unicode代理对+组合变音符号 |
| 9 | `[` 加上 specialCatcodes + `]` | 特殊分类码字符 |
| 10 | `[\\u0000-\\uD7FF\\uE000-\\uFFFF]` | 单个Unicode BMP字符 |
| 11 | `[\\uD800-\\uDFFF]` | 单个代理项（代理对不匹配时的回退） |
| 12 | `[\\u0300-\\u036F\\u0483-\\u0487]+` | 组合变音符号序列 |

**关键设计点**：正则的优先级决定了匹配顺序。例如 `\verb` 命令必须在控制词之前匹配，否则 `\verb` 中的 `\v` 会被当作控制符号 `\v`（accent命令）匹配。

## 分类码（catcodes）

TeX 的 catcode（category code）系统为每个字符分配一个类别，控制其行为。Lexer 中默认设置：

```typescript
this.catcodes = {
    "%": 14,  // 注释符
    "~": 13,  // 活动字符（active character，类似单字符宏）
};
```

catcode 14 的字符（`%`）触发注释处理，catcode 13 的字符（`~`）作为活动字符由 MacroExpander 处理。其他字符使用默认分类。

`\catcode` 命令可以在运行时改变字符的 catcode，但 Lexer 通过 `catcodes` 对象动态维护这些映射。

## \verb 命令的特殊处理

`\verb` 和 `\verb*` 命令用于原样输出文本（类似代码中的引号），其定界符可以是任意字符。例如：

- `\verb|a+b|` — 用 `|` 作定界符
- `\verb"hello"` — 用 `"` 作定界符
- `\verb* x ` — 用空格作定界符（星号版本保留空格）

正则中的模式4和5专门处理这两种定界符情况，确保定界符之间的所有字符（包括反斜杠和特殊字符）都被原样捕获，不被分词。

## lex() 方法工作流程

`lex()` 方法是 Lexer 的主要入口，由 MacroExpander 调用。它的基本逻辑：

1. 检查是否还有输入（`this.pos` 未到达末尾）
2. 使用 `tokenRegex` 匹配下一个Token
3. 如果匹配到注释（`%`），跳过该行（`this.catcode('%') === 14`）
4. 如果匹配到 `\verb`，按原样文本处理
5. 对于普通Token，跳过前导空白（根据当前模式决定是否保留）
6. 返回构造的 Token 对象（包含 text 和 loc 信息）

## 与 MacroExpander 的接口

Lexer 实现了 `LexerInterface` 接口，这是 MacroExpander 对 Lexer 的唯一依赖：

```typescript
interface LexerInterface {
    input: string;
    settings: Settings;
    tokenRegex: RegExp;
    catcodes: Record<string, number>;
    lex(): Token;
}
```

MacroExpander 通过 `lexer.lex()` 逐个获取 Token，这是 Lexer 与外部的唯一交互点。

## 注意事项

- Lexer **不理解** LaTeX 语法，它只做字符级别切分。例如 `\frac{1}{2}` 被切分为 `\frac`、`{`、`1`、`}`、`{`、`2`、`}`，而不会理解分数结构
- Lexer **不展开宏**，宏展开是 MacroExpander 的职责
- 空白字符在数学模式下通常被忽略，在文本模式下会被保留为间距Token
- 续行符（行尾的 `\`）会被Lexer消耗掉（匹配模式2），不会传递给下游

## 相关概念

- [架构总览](02-architecture-overview.md)
- [宏展开器（MacroExpander）](04-macro-expander.md)
- [解析器（Parser）](05-parser.md)
