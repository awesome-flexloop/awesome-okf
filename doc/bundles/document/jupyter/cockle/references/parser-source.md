---
type: reference
title: 解析器源码参考
description: Tokenizer 和 Parser 的源码参考，包括分词规则、AST 节点类型、别名展开和重定向处理
tags:
  - cockle
  - parser
  - tokenizer
  - ast
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: parse
    resource: /references/parser-source.md
    title: src/parse.ts
  - id: tokenize
    resource: /references/parser-source.md
    title: src/tokenize.ts
---

## 概述

Cockle 浏览器 Shell 的解析器（Parser）由分词器（Tokenizer）和语法分析器两部分组成。分词器将用户输入的原始字符串切分为词法单元（Token）序列，解析器再将 Token 序列组装为抽象语法树（AST，Abstract Syntax Tree）节点数组。解析过程同时处理别名（Alias）展开、管道（Pipe）连接和重定向（Redirect）识别，是命令行解释执行的前端核心。

## Token 类型

分词器输出的基本单元是 Token（词法单元）：

```typescript
type Token = {
  offset: number;
  value: string;
};
```

- **offset**：Token 在原始输入字符串中的起始偏移量（以字符为单位），用于错误定位和补全上下文计算
- **value**：Token 的实际文本内容

## AST 节点类型

解析器生成的所有节点均继承自 Node 抽象基类。

### Node 抽象基类

```typescript
abstract class Node {
  abstract lastToken(): [Token | null, boolean];
}
```

- **lastToken()**：返回节点的最后一个 Token 及一个布尔标志，用于补全时判断光标位置是否在此节点末尾

### CommandNode

CommandNode（命令节点）表示一条可执行命令：

```typescript
class CommandNode extends Node {
  name: Token;
  suffix: Token[];
  redirects?: RedirectNode[];
}
```

- **name**：命令名 Token（命令的第一个词）
- **suffix**：命令参数 Token 数组
- **redirects**：可选的重定向节点数组

一个 CommandNode 表示形如 `ls -la /tmp > output.txt` 的完整命令调用。

### PipeNode

PipeNode（管道节点）表示通过管道符 `|` 连接的命令序列：

```typescript
class PipeNode extends Node {
  commands: CommandNode[];
}
```

- **commands**：由管道连接的 CommandNode 数组，长度至少为 2（单个命令无需 PipeNode 包裹）

例如 `ls | grep txt | wc -l` 会生成包含 3 个 CommandNode 的 PipeNode。

### RedirectNode

RedirectNode（重定向节点）表示输入输出重定向：

```typescript
class RedirectNode extends Node {
  token: Token;
  target: Token;
}
```

- **token**：重定向操作符 Token（如 `>`、`>>`、`<`、`2>`、`2>>`）
- **target**：重定向目标文件名 Token

## 分词器 (Tokenizer)

分词器负责逐字符扫描输入字符串，根据字符类型（CharType）和分隔符规则生成 Token 序列。

### CharType 枚举

```typescript
enum CharType {
  None,
  Delimiter,
  DoubleQuote,
  SingleQuote,
  Whitespace,
  Other
}
```

### 分隔符与空白

- **分隔符（Delimiters）**：`;`、`&`、`|`、`>`、`<` 五个字符，各自或组合构成语法边界
- **空白字符（Whitespace）**：空格字符 `' '`，用于分隔 Token

### 特殊处理规则

**`2>` stderr 重定向**：分词器将字符序列 `2>` 识别为单个 Token（而非 `2` 和 `>` 两个 Token），用于标准错误输出重定向。`2>>` 同理被识别为追加重定向。

**引号处理**：
- 单引号（`'`）和双引号（`"`）内的内容被整体作为一个 Token
- 引号本身不作为 Token 值的一部分
- 引号内的分隔符和空白字符失去语法含义，作为普通文本处理

例如输入 `"hello world";foo` 会被分词为 `["hello world", ";", "foo"]`。

### 别名展开

别名展开在分词过程中实时发生，由 `_addToken()` 方法处理。当当前 Token 处于命令位置（即整条命令的第一个 Token，或紧跟在 `;`、`&`、`|` 之后）时，分词器通过 `aliases.getRecursive(value)` 执行递归别名查找：

1. 如果找到别名定义，用别名值替换原始输入
2. 替换后重新对新内容执行分词
3. 递归展开直到没有更多别名匹配或达到递归上限

这意味着别名可以引用其他别名，分词器会自动完成链式展开。

## 解析器 (Parser)

### parse 函数

```typescript
function parse(
  source: string,
  throwErrors?: boolean,
  aliases?: Aliases
): Node[]
```

解析入口函数，执行以下步骤：
1. 调用 `tokenize()` 生成 Token 序列
2. 按命令结束符 `;` 和 `&` 分割为独立命令段
3. 在每个命令段内按管道符 `|` 分割为命令链
4. 为每个命令构建 CommandNode，识别其中的重定向
5. 若命令链包含多个命令，包装为 PipeNode
6. 返回 Node 数组

### tokenize 函数

```typescript
function tokenize(
  source: string,
  throwErrors?: boolean,
  aliases?: Aliases
): Token[]
```

分词入口函数，逐字符扫描源字符串，根据当前 CharType 状态机产出 Token 列表。在命令位置触发别名递归展开。

### 识别的重定向类型

| 操作符 | 含义 |
|--------|------|
| `>` | 标准输出重定向（覆盖） |
| `>>` | 标准输出重定向（追加） |
| `2>` | 标准错误重定向（覆盖） |
| `2>>` | 标准错误重定向（追加） |
| `<` | 标准输入重定向 |

### 命令结束符

- **`;`**：顺序执行——前一条命令完成后执行下一条
- **`&`**：后台执行——前一条命令在后台运行，立即执行下一条

两个符号均可作为多条命令的分隔符，解析器遇到时结束当前命令节点的构建。

## 解析示例

对于输入字符串 `echo "hello world" | grep h >> output.txt & ls -la;`，解析过程如下：

1. 分词结果：`["echo", "hello world", "|", "grep", "h", ">>", "output.txt", "&", "ls", "-la", ";"]`
2. 按 `&` 和 `;` 分割为三段：管道段、`ls -la`、空段
3. 管道段按 `|` 分割为 `echo "hello world"` 和 `grep h >> output.txt`
4. 识别 `>> output.txt` 为追加重定向，附加到第二个 CommandNode
5. 生成 AST：`[PipeNode(CommandNode(echo), CommandNode(grep, redirect=>>)), CommandNode(ls)]`

```typescript
// 简化的解析结果示意
[
  PipeNode {
    commands: [
      CommandNode { name: Token("echo"), suffix: [Token("hello world")] },
      CommandNode {
        name: Token("grep"),
        suffix: [Token("h")],
        redirects: [RedirectNode { token: Token(">>"), target: Token("output.txt") }]
      }
    ]
  },
  CommandNode { name: Token("ls"), suffix: [Token("-la")] }
]
```

## 相关概念

- [命令系统源码参考](/references/command-source.md)：命令注册表与运行器接口
- [内置命令源码参考](/references/builtin-source.md)：alias 命令与别名管理
- [配置与环境源码参考](/references/config-source.md)：Aliases 类的递归解析 API
