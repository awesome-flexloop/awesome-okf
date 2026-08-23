---
type: Concept
title: 解析器（Parser）
description: KaTeX Parser 的工作原理，包括表达式解析、原子解析、上下标处理、函数调度、参数解析和模式切换。
tags: [katex, parser, ast, parse-node, mode]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## Parser 的角色

Parser 是 KaTeX 消化管模型的第三层（"stomach"/胃），负责将 MacroExpander 输出的已展开 Token 流解析为抽象语法树（AST，即 ParseNode 数组）。

Parser 位于 [src/Parser.ts](https://github.com/KaTeX/KaTeX/blob/main/src/Parser.ts)。

## 核心类

```typescript
class Parser {
    mode: Mode;                // 当前模式："math" | "text"
    gullet: MacroExpander;     // 宏展开器（获取Token的唯一通道）
    settings: Settings;
    leftrightDepth: number;    // \left...\right 嵌套深度
    nextToken: Token;          // 前瞻Token

    parse(): AnyParseNode[];   // 解析完整表达式，返回AST根节点
}
```

## 解析流程概览

Parser 的解析过程是递归下降的：

```
parse()                          // 入口
  └─ parseExpression()           // 解析表达式序列
       ├─ parseAtom()            // 解析单个原子
       │    ├─ parseGroup()      // 解析组（{...}或函数调用）
       │    │    ├─ parseFunction()  // 查询并调用注册的函数handler
       │    │    └─ 处理花括号组
       │    ├─ 处理上下标（^、_、'）
       │    └─ 处理limits控制
       └─ handleInfixNodes()     // 处理中缀运算符（\over等）
```

## parse()：入口方法

```typescript
parse(): AnyParseNode[] {
    this.gullet.beginGroup();
    const parse = this.parseExpression(false);
    this.expect("EOF");
    this.gullet.endGroup();
    return parse;
}
```

关键点：
- 解析前创建一个隐式分组（保护全局状态）
- 调用 `parseExpression(false)` 解析主体，参数 `false` 表示不在中缀运算符处中断
- `expect("EOF")` 确认所有Token已消费
- 结束隐式分组

## parseExpression()：表达式序列

`parseExpression(breakOnInfix, breakOnTokenText?)` 循环解析 atom，直到遇到终止符：

终止条件：
- 遇到 `}` 或 `\endgroup`（花括号组/分组结束）
- 遇到 `\end`（环境结束）
- 遇到 `\right`（匹配的\left结束）
- 遇到 `&`（表格对齐标记）
- 遇到指定的 breakOnTokenText
- 遇到 EOF

解析完成后，如果 `breakOnInfix` 为 true，调用 `handleInfixNodes()` 处理中缀运算符。

## parseAtom()：原子与上下标

每个 atom 代表一个不可再分割的排版单元（符号、函数结果、组），其后可能跟随上下标：

```
parseAtom() 流程:
1. base = parseGroup()         // 解析基础原子
2. while (下一个Token是 ^ 或 _ 或 ')  // 处理上下标
3. 处理 \limits / \nolimits    // 控制大算符的上下标位置
4. return 组装好的节点（带sup/sub的原子）
```

### 上下标处理

- `^` 引入上标（superscript）
- `_` 引入下标（subscript）
- `'`（单引号）是 `^{\prime}` 的简写
- 连续的 `^` 或 `_` 会报错（如 `x^2^3`）
- 同一原子可以同时有上标和下标，顺序无关

## parseGroup()：分组与函数调度

`parseGroup()` 处理 Token 流中的一个组：

```
parseGroup() 流程:
1. 前瞻一个Token
2. switch (token.text):
   case "{":
     消费 {，递归 parseExpression()，消费 }
     返回 ordgroup 节点
   case "\begingroup":
     消费 \begingroup，递归 parseExpression()，消费 \endgroup
     返回 ordgroup 节点
   case "\color", "\colorbox":
     特殊处理（颜色切换在组解析时执行）
   default:
     如果是注册函数:
       return parseFunction()
     如果是符号/字符:
       返回符号节点
```

## parseFunction()：函数调度

当遇到已注册的控制序列时，Parser 调用函数注册表中对应的 handler：

```typescript
parseFunction(): AnyParseNode {
    const token = this.fetch();
    const func = _functions[token.text];  // 查询注册表
    
    // 检查模式允许性
    if (this.mode === "text" && !func.allowedInText) 抛出错误;
    if (this.mode === "math" && !func.allowedInMath) 抛出错误;
    
    // 解析参数
    const args = this.parseArguments(func);
    
    // 调用handler
    return func.handler(this, token, args);
}
```

### parseArguments()：参数解析

根据 FunctionSpec 的 `numArgs`、`argTypes`、`numOptionalArgs` 解析参数：

- **必选参数**：通过 `consumeArg()` 消费
- **可选参数**：`[...]` 包裹的参数，向前查看是否存在
- **类型化参数**：根据 argType 进行特殊解析：
  - `"color"`：解析颜色值
  - `"size"`：解析尺寸值（如 `1em`、`10pt`）
  - `"url"`：解析URL（转义特殊字符）
  - `"raw"`：原样文本（含嵌套花括号）
  - `"hbox"`：在文本模式下解析的组
  - `"primitive"`：TeX原始命令参数
  - `"math"`/`"text"`：在指定模式下解析
  - `"original"`：保持当前模式解析

## handleInfixNodes()：中缀运算符

TeX 中有一些中缀运算符（不是函数调用语法），最典型的是 `\over`（分数）：

```
{a \over b}    等价于    \frac{a}{b}
```

`handleInfixNodes()` 在 parseExpression 完成后扫描结果中是否包含中缀节点，如果有，将其重写为对应的函数形式（如将 `\over` 转换为 `\frac` 节点）。

这种设计的原因是 TeX 的 `\over` 是在解析完两侧后才"回头"构建分数节点，属于后处理。

## 模式切换

Parser 在 `math` 和 `text` 两种模式间切换：

- **math 模式**：默认模式，字符被解释为数学符号
- **text 模式**：由 `\text{}`、`\hbox{}` 等命令进入，字符被解释为普通文本

模式切换通过 `this.gullet.switchMode("text")` 和 `this.switchMode()` 实现。切换模式影响：
- 符号的解释（如 `-` 在数学模式中是减号/二元运算符，在文本模式中是连字符）
- 哪些函数可用（部分函数只在特定模式下注册）
- 空白的处理（文本模式保留空格，数学模式忽略空格）

## ParseNode 类型

解析结果是 `AnyParseNode[]`，即 ParseNode 数组。每个 ParseNode 是一个对象，至少包含：

```typescript
{
    type: NodeType;     // 节点类型，如 "frac"、"sqrt"、"mathord"、"op"
    mode: Mode;         // 创建该节点时的模式
    loc?: SourceLocation;  // 源码位置
    // ... 类型特定的字段
}
```

所有节点类型定义在 [src/types/nodes.ts](https://github.com/KaTeX/KaTeX/blob/main/src/types/nodes.ts) 中。

## 错误处理

Parser 在遇到语法错误时抛出 `ParseError`，包含：
- 错误消息（如 "Expected 'EOF' after '"
- 错误位置（SourceLocation）
- 当前 Token 信息

parseTree 入口函数（[src/parseTree.ts](https://github.com/KaTeX/KaTeX/blob/main/src/parseTree.ts)）捕获 ParseError 并附加位置信息。

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [宏展开器（MacroExpander）](/concepts/04-macro-expander.md)
- [函数注册表](/concepts/08-function-registry.md)
- [渲染管线](/concepts/06-render-pipeline.md)
- [配置系统](/concepts/10-settings-options.md)
