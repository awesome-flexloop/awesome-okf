---
type: Concept
title: 宏展开器（MacroExpander）
description: KaTeX MacroExpander（gullet）的工作原理，包括Token栈、宏展开循环、参数消费、分组作用域和展开计数防护。
tags: [katex, macro, expansion, gullet, namespace]
generated: { by: "reference_agent/trae-cn", at: 2026-08-22T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T22:30:00+08:00 }
status: stable
stale_after: 2027-02-22
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
---

## MacroExpander 的角色

MacroExpander 位于 Lexer 和 Parser 之间，是 TeX 消化管模型中的 "gullet"（食道）。它的核心职责是在 Token 传递给 Parser 之前，递归展开所有宏定义。

MacroExpander 位于 [src/MacroExpander.ts](https://github.com/KaTeX/KaTeX/blob/main/src/MacroExpander.ts)。

## 为什么需要独立的宏展开层

宏在 TeX 中不仅仅是字符串替换。宏可以：
- 带参数（`#1`~`#9`）
- 改变后续解析行为
- 嵌套展开（宏的展开结果中可能包含另一个宏）
- 通过 `{...}` 分组控制作用域

如果将宏展开混入 Parser，会导致递归展开逻辑与语法解析逻辑深度耦合。独立的 MacroExpander 层让 Parser 看到的始终是"展开后"的 Token 流，简化了 Parser 的实现。

## 核心类

```typescript
class MacroExpander implements MacroContextInterface {
    lexer: LexerInterface;      // 底层词法分析器
    stack: Token[];             // Token栈（逆序存储）
    mode: Mode;                 // 当前模式："math" | "text"
    macros: Namespace<MacroDefinition>;  // 宏命名空间
    _expandCount: number;       // 展开计数（防无限递归）
    settings: Settings;
    globalMacros: GlobalMacros;

    expandNextToken(): Token;   // 核心方法：展开直到非宏Token
    fetch(): Token;             // 获取下一个已展开Token（Parser调用）
    consumeSpaces(): void;      // 消费连续空白
    consumeArg(allowGroup, argType): Token[];  // 消费宏/函数参数
    beginGroup(): void;         // 开始分组（{...}）
    endGroup(): void;           // 结束分组
}
```

## Token 栈机制

MacroExpander 维护一个内部 Token 栈 `stack: Token[]`，采用 **逆序存储**（最新压入的在数组末尾）：

- 当 Lexer 产出新 Token 时，push 到栈顶
- 当宏展开时，将展开结果的 Token 序列逆序 push 到栈顶（这样最先展开的内容最先被消费）
- `fetch()` 从栈顶 pop 取 Token；如果栈空，则从 Lexer 获取新 Token

逆序压栈的精妙之处：假设宏 `\a` 展开为 `xy`，展开后栈中 `[..., x, y]`（y在栈顶先被pop出），这样 x 在 y 之前被消费，得到正确顺序 `xy`。

## expandNextToken()：展开循环

这是宏展开的核心方法。它的循环逻辑：

```
while (true) {
    token = 从栈顶获取（pop或从lexer获取）;
    
    if token是可展开的宏:
        查询宏定义;
        如果有参数:
            消费参数（处理#1~#9占位符）;
        将展开结果逆序push到栈;
        _expandCount++;
        if _expandCount > maxExpand: 抛出错误;
        continue;  // 继续循环，展开结果中可能还有宏
    
    if token是 \noexpand 标记:
        返回下一个token（标记为不展开）;
    
    if token是 \expandafter:
        跳过一个token，展开再下一个;
    
    return token;  // 非宏Token，返回给Parser
}
```

### 展开计数防护

`_expandCount` 初始为 0，每次展开一次宏加 1。当超过 `settings.maxExpand`（默认 1000）时抛出异常，防止恶意或错误输入导致的无限宏递归（如 `\def\a{\a}\a`）。

## 宏定义类型

宏定义存储在 `macros: Namespace<MacroDefinition>` 中，支持两种形式：

### 字符串宏（简单替换）

```javascript
// 例如 \def\RR{\mathbb{R}}
"\\RR": { tokens: toString("\\mathbb{R}"), numArgs: 0 }
```

字符串宏在展开时，通过 `_getExpansion()` 将字符串转换为 Token 数组，压入栈中。

### 函数宏（动态展开）

```javascript
// 例如 \newcommand 的展开器是一个函数
"\\@ifstar": function(context) {
    // 动态决定展开内容
    return expandedTokens;
}
```

函数宏在展开时被调用，接收 MacroExpander 作为上下文，可以执行复杂的动态展开逻辑。

## 参数消费

`consumeArg()` 方法用于消费宏或函数的参数。它支持：

- **花括号组**：`{...}` 作为一个参数（剥去外层花括号）
- **单个Token**：如果参数没有花括号包裹，取单个Token
- **指定类型**：根据 argType（color/size/url/raw/hbox等）进行特殊解析
- **原始模式**：某些参数类型（如url、raw）会进行特殊字符处理

参数中的 `#1`~`#9` 占位符在展开时被替换为实际参数的 Token 序列，`##` 转义为单个 `#`。

## 分组作用域

MacroExpander 通过 `beginGroup()` 和 `endGroup()` 实现分组：

- `beginGroup()` 调用 `macros.beginGroup()`，将当前宏表压栈
- 在分组内定义的宏（通过 `\def`、`\newcommand` 等）只在分组内有效
- `endGroup()` 调用 `macros.endGroup()`，弹出宏表，恢复外层作用域

花括号 `{...}` 和 `\begingroup...\endgroup` 都创建新分组。

### Namespace 类

Namespace 实现了嵌套作用域：
- 外层：全局/外层宏定义
- 内层：当前分组内的宏定义（查找时先查内层，再查外层）
- endGroup 时丢弃内层定义，恢复外层可见性

## \noexpand 和 \expandafter

这两个特殊的 TeX 原语在 MacroExpander 中处理：

- **\noexpand**：紧随其后的 Token 被标记为 `noexpand: true`，在本次展开中不被展开
- **\expandafter**：跳过下一个 Token，先展开再后面的一个 Token，然后再处理跳过的 Token

这些原语为高级宏编程提供了精确的展开时序控制。

## 与 Parser 的交互

Parser 通过以下方式与 MacroExpander 交互：

| Parser调用 | 作用 |
|-----------|------|
| `gullet.fetch()` | 获取下一个已展开的Token |
| `gullet.consumeSpaces()` | 跳过连续空白Token |
| `gullet.consumeArg()` | 消费一个参数 |
| `gullet.beginGroup()` | 开始分组 |
| `gullet.endGroup()` | 结束分组 |
| `gullet.expandNextToken()` | 显式触发一次展开 |
| `gullet.switchMode(mode)` | 切换 math/text 模式 |

Parser 不直接与 Lexer 通信，所有 Token 都通过 MacroExpander 获取。

## 内置宏

内置宏定义在 [src/macros.ts](https://github.com/KaTeX/KaTeX/blob/main/src/macros.ts) 中，包括：
- 简单别名：`\to` → `\rightarrow`
- 带参数宏：`\textbf` → 模式切换+参数
- 控制结构：`\newcommand`、`\def`、`\let` 等
- TeX 原语：`\relax`、`\expandafter`、`\noexpand` 等

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [词法分析器（Lexer）](/concepts/03-lexer.md)
- [解析器（Parser）](/concepts/05-parser.md)
- [宏系统](/concepts/09-macro-system.md)
- [函数注册表](/concepts/08-function-registry.md)
