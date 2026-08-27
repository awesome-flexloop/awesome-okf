---
type: concept
title: "04 - 命令解析管线"
description: Tokenizer 词法分析和 Parser 语法分析——分词、别名展开、AST构建、管道和重定向解析
tags: [parsing, tokenizer, parser, ast, alias, redirect, pipe]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: parser-source
    resource: /references/parser-source.md
    title: 解析器参考
---

## 解析管线概述

命令解析管线（Parsing Pipeline）是 Cockle 将用户输入的原始字符串转化为可执行命令结构的核心过程。整个管线分为两个阶段：**词法分析（Tokenizer/分词器）** 和 **语法分析（Parser/解析器）**，最终输出抽象语法树（AST，Abstract Syntax Tree）。

```
原始字符串 "ls -la *.txt | grep err > result.txt 2>&1"
    │
    ▼
┌─────────────────────────────────────────────────┐
│  Tokenizer（分词器）                             │
│  • 逐字符扫描，基于 CharType 状态机              │
│  • 识别分隔符、空白、引号                        │
│  • 命令位置别名展开（递归）                      │
│  • 特殊合并 2> / 2>>                             │
│  • 输出: Token[] 流                              │
└────────────────────┬────────────────────────────┘
                     │ Token[]
                     ▼
┌─────────────────────────────────────────────────┐
│  Parser（解析器）                                │
│  • 按 ; / & 分割为独立命令段                     │
│  • 按 | 分割为管道链                             │
│  • 识别重定向（>/>>/</2>/2>>）                   │
│  • 构建 CommandNode / PipeNode / RedirectNode   │
│  • 输出: Node[] (AST)                           │
└────────────────────┬────────────────────────────┘
                     │ AST
                     ▼
         ShellImpl 遍历 AST 执行命令
```

ShellImpl 在执行命令前，调用 `parse(cmdText, aliases, throwErrors=true)` 完成整个解析过程 [F-174]。解析器入口函数签名如下：

```typescript
function parse(
  source: string,       // 原始命令行字符串
  throwErrors?: boolean, // 是否在解析错误时抛出异常
  aliases?: Aliases     // 别名表，用于分词时的别名展开
): Node[];              // 返回 AST 节点数组
```

## Tokenizer 词法分析

### Token 结构

分词器输出的基本单元是 Token（词法单元），包含两个字段 [F-220-F232]：

```typescript
type Token = {
  offset: number;  // Token 在原始输入中的起始偏移量（字符位置）
  value: string;   // Token 的实际文本内容
};
```

`offset` 字段用于错误定位和 Tab 补全时计算光标上下文，`value` 是分词后的文本。

### CharType 状态机

分词器使用基于 `CharType`（字符类型）的有限状态机逐字符扫描输入：

```typescript
enum CharType {
  None,         // 初始/无状态
  Delimiter,    // 分隔符（; & | > <）
  DoubleQuote,  // 双引号内
  SingleQuote,  // 单引号内
  Whitespace,   // 空白字符（空格）
  Other,        // 普通字符
}
```

分词器维护一个"当前字符类型"状态，根据状态决定如何处理下一个字符：

- **Whitespace 状态**：遇到空格时，若当前正在累积 Token 则结束当前 Token，跳过连续空白
- **Delimiter 状态**：遇到分隔符字符（`;`、`&`、`|`、`>`、`<`）时，结束当前 Token，将分隔符作为独立 Token（或组合 Token 如 `>>`、`2>`、`2>>`）
- **DoubleQuote / SingleQuote 状态**：进入引号后，所有字符（包括空白和分隔符）都作为普通文本累积，直到遇到匹配的闭合引号
- **Other 状态**：普通字符累积到当前 Token

### 分隔符处理

分词器识别五种分隔符字符：`;`、`&`、`|`、`>`、`<`。这些字符构成 Shell 语法的边界，各自或组合产生独立 Token：

| 字符序列 | Token 值 | 含义 |
|----------|----------|------|
| `;` | `;` | 命令顺序分隔符 |
| `&` | `&` | 后台执行分隔符 |
| `\|` | `\|` | 管道符 |
| `>` | `>` | 标准输出覆盖重定向 |
| `>>` | `>>` | 标准输出追加重定向 |
| `<` | `<` | 标准输入重定向 |
| `2>` | `2>` | 标准错误覆盖重定向 |
| `2>>` | `2>>` | 标准错误追加重定向 |

**`2>` 的特殊处理**：分词器将字符序列 `2>` 和 `2>>` 识别为单个 Token（而非数字 `2` 加重定向符 `>` 两个 Token），这是 Shell 语法中 stderr 重定向的特殊表示 [F-220-F232]。当分词器遇到字符 `2` 后面紧跟 `>` 时，会将它们合并为一个 Token。

### 引号处理

引号在分词中有特殊的语义——引号内的内容作为整体处理，分隔符和空白在引号内失去语法含义：

- **单引号（`'...'`）**：单引号内所有字符（包括双引号、空格、`|`、`>` 等）都作为普通文本，不进行任何展开
- **双引号（`"..."`）**：双引号内的分隔符和空白也作为普通文本（Cockle 当前不实现 Bash 中的 `$变量展开` 和 `` `命令替换` `` 在双引号内的特殊处理，但保留引号整体分词的语义）
- 引号本身不作为 Token 值的一部分——Token 的 value 是引号内的文本，不包含引号字符

示例：

```
输入: echo "hello world" 'foo|bar'
分词: ["echo", "hello world", "foo|bar"]
```

注意 `"hello world"` 中的空格不会导致分词，`'foo|bar'` 中的 `|` 不会被识别为管道符。

### 空白处理

空格字符 `' '` 是 Token 分隔符。连续的多个空格等效于单个空格。分词器在遇到空白时，如果正在累积一个非空 Token，则将该 Token 加入结果列表，然后跳过所有连续空白。

### 别名展开

别名（Alias）展开在分词过程中实时进行，这是 Cockle 解析器的一个重要特性——别名展开发生在**分词阶段**而非执行阶段 [F-220-F232]。

**展开时机**：当分词器识别出当前正在累积的 Token 处于**命令位置**时（即整条命令行的第一个 Token，或者紧跟在 `;`、`&`、`|` 分隔符之后的第一个 Token），会查找别名表。

**展开过程**：

1. 分词器通过 `aliases.getRecursive(value)` 对命令名执行递归别名查找
2. 如果找到别名定义（例如 `ll` 定义为 `ls -la`），则用别名值替换原始输入中的命令名
3. 替换后，分词器**回退**并对替换后的新文本重新执行分词
4. 递归展开直到没有更多别名匹配或达到递归上限（防止无限递归）
5. 非命令位置的 Token（参数、文件名等）不进行别名展开

示例：

```bash
# 假设已定义别名: alias ll='ls -la'
# 输入: ll /tmp
# 分词过程:
#   1. 识别 "ll" 在命令位置
#   2. 查找别名 → "ls -la"
#   3. 将输入替换为 "ls -la /tmp"
#   4. 重新分词 → ["ls", "-la", "/tmp"]
```

递归别名支持：如果别名 A 引用了别名 B，分词器会递归展开所有层级。例如 `alias gs='git status'` 和 `alias g='gs'`，输入 `g` 会展开为 `git status`。

## AST 节点类型

解析器将 Token 序列组装为 AST，所有节点继承自 `Node` 抽象基类：

```typescript
abstract class Node {
  abstract lastToken(): [Token | null, boolean];
}
```

`lastToken()` 方法返回节点的最后一个 Token 和一个布尔标志，用于 Tab 补全时判断光标位置是否在该节点末尾。

### CommandNode（命令节点）

`CommandNode` 表示一条可执行命令 [F-220-F232]：

```typescript
class CommandNode extends Node {
  name: Token;           // 命令名
  suffix: Token[];       // 命令参数列表
  redirects?: RedirectNode[];  // 关联的重定向节点
}
```

- **name**：命令名 Token，是命令的第一个词（在别名展开后）
- **suffix**：命令参数 Token 数组，包含所有选项和操作数
- **redirects**：可选的重定向数组，记录该命令的所有 I/O 重定向

例如 `ls -la /tmp > out.txt` 生成一个 CommandNode，name 为 `ls`，suffix 为 `["-la", "/tmp"]`，redirects 包含一个 `RedirectNode(">", "out.txt")`。

### PipeNode（管道节点）

`PipeNode` 表示通过管道符 `|` 连接的命令链 [F-175]：

```typescript
class PipeNode extends Node {
  commands: CommandNode[];  // 管道连接的命令数组
}
```

`commands` 数组长度至少为 2——单个命令不需要 PipeNode 包裹，直接作为 CommandNode 存在。管道中前一个命令的 stdout 通过 Pipe 对象连接到后一个命令的 stdin。

例如 `ls | grep txt | wc -l` 生成一个 PipeNode，包含三个 CommandNode：ls、grep、wc。

### RedirectNode（重定向节点）

`RedirectNode` 表示一个 I/O 重定向 [F-220-F232]：

```typescript
class RedirectNode extends Node {
  token: Token;   // 重定向操作符（>, >>, <, 2>, 2>>）
  target: Token;  // 重定向目标文件名
}
```

RedirectNode 总是作为 CommandNode 的 `redirects` 数组元素存在，不会独立出现在 AST 顶层。

## 命令分隔与管道

### 多命令分隔（; 和 &）

解析器按命令结束符 `;` 和 `&` 将 Token 序列分割为独立的命令段 [F-220-F232]：

- **`;`（顺序执行）**：前一条命令执行完毕后才执行下一条
- **`&`（后台执行）**：前一条命令在后台运行（ShellImpl 中当前实现为顺序执行，保留语法兼容性），不等待完成即执行下一条

例如 `echo a; echo b & echo c` 被分割为三段：`echo a`、`echo b`、`echo c`，生成三个独立节点。

### 管道连接（|）

在每个命令段内，解析器按管道符 `|` 分割为命令链 [F-175]：

- 如果命令段中只有一个命令（无 `|`），直接生成 CommandNode
- 如果命令段中有多个命令（包含 `|`），为每个命令创建 CommandNode，然后包裹在 PipeNode 中

管道链中的数据流：第一个命令的 stdout → Pipe → 第二个命令的 stdin → Pipe → ... → 最后一个命令的 stdout → 终端。

## 重定向解析

解析器在构建 CommandNode 时，会扫描 suffix Token 序列，识别重定向操作符及其目标文件 [F-176][F-177]。识别出的重定向从 suffix 中移除，创建对应的 RedirectNode 添加到 CommandNode 的 redirects 数组。

支持的五种重定向类型 [F-220-F232]：

| 操作符 | 类型 | 含义 | 实现 |
|--------|------|------|------|
| `>` | stdout 覆盖 | 将标准输出写入文件，覆盖已有内容 | 创建 FileOutput，truncate 模式 |
| `>>` | stdout 追加 | 将标准输出追加到文件末尾 | 创建 FileOutput，append 模式 |
| `<` | stdin | 从文件读取标准输入 | 创建 FileInput |
| `2>` | stderr 覆盖 | 将标准错误写入文件，覆盖已有内容 | 创建 FileOutput（stderr），truncate 模式 |
| `2>>` | stderr 追加 | 将标准错误追加到文件末尾 | 创建 FileOutput（stderr），append 模式 |

重定向可以出现在命令的任意位置——命令前、参数中间、命令后均可。解析器会将所有重定向收集到 redirects 数组中，剩余 Token 作为命令参数。

例如：

```bash
# 输入
> output.txt grep pattern < input.txt 2>> error.log

# 解析结果
CommandNode {
  name: "grep",
  suffix: ["pattern"],
  redirects: [
    RedirectNode(">", "output.txt"),
    RedirectNode("<", "input.txt"),
    RedirectNode("2>>", "error.log")
  ]
}
```

ShellImpl 在执行命令时（`_runCommand` 方法），根据 redirects 数组创建对应的 FileInput/FileOutput 对象，替换默认的 stdin/stdout/stderr [F-177]。

## 文件名通配符

文件名通配符展开（Glob Expansion）不在分词和语法分析阶段处理，而是在**命令执行阶段**由 `_filenameExpansion` 方法处理 [F-178]。但理解解析管线需要知道通配符的处理位置。

当 ShellImpl 执行 `_runCommand` 时，在设置好 IO 重定向后、调用命令 runner 之前，会对命令参数执行文件名展开：

- `*`：匹配任意长度的任意字符（正则 `.*`）
- `?`：匹配单个任意字符（正则 `.`）

展开过程：
1. 遍历命令的每个参数 Token
2. 如果参数包含 `*` 或 `?`，将通配符模式转为正则表达式
3. 对当前工作目录调用 `FS.readdir` 获取文件列表
4. 用正则匹配文件名，过滤掉隐藏文件（以 `.` 开头的文件，除非模式以 `.` 开头）
5. 匹配到的文件列表替换原始参数；若无匹配，保留原始通配符字符串作为字面值参数

例如 `ls *.md` 在包含 `README.md` 和 `CHANGELOG.md` 的目录中展开为 `ls README.md CHANGELOG.md`。

## 引号处理详解

引号是分词阶段的重要机制，以下通过更多示例说明引号对分词的影响：

```bash
# 基本引号
echo "hello world"        # → ["echo", "hello world"]
echo 'hello world'        # → ["echo", "hello world"]

# 引号内分隔符不生效
echo "a|b"                # → ["echo", "a|b"]  (| 在引号内，不是管道)
echo "a;b"                # → ["echo", "a;b"]  (; 在引号内，不是分隔符)
echo "a>b"                # → ["echo", "a>b"]  (> 在引号内，不是重定向)

# 引号拼接（相邻引号合并为一个 Token）
echo "hello"'world'       # → ["echo", "helloworld"]

# 引号与非引号混合
echo hello"world"foo      # → ["echo", "helloworldfoo"]

# 空引号产生空字符串 Token
echo ""                   # → ["echo", ""]
```

## 解析示例

通过几个完整示例理解解析管线的输出：

### 示例 1：简单命令

输入：`ls -la /home/user`

```
Token 流: [ls, -la, /home/user]
AST:
  CommandNode {
    name: ls,
    suffix: [-la, /home/user],
    redirects: undefined
  }
```

### 示例 2：管道加重定向

输入：`cat input.txt | grep error | wc -l > count.txt`

```
Token 流: [cat, input.txt, |, grep, error, |, wc, -l, >, count.txt]
AST:
  PipeNode {
    commands: [
      CommandNode { name: cat, suffix: [input.txt] },
      CommandNode { name: grep, suffix: [error] },
      CommandNode {
        name: wc,
        suffix: [-l],
        redirects: [RedirectNode(">", "count.txt")]
      }
    ]
  }
```

### 示例 3：多命令与引号

输入：`echo "hello;world"; ls '*.md' 2> /dev/null`

```
Token 流: [echo, "hello;world", ;, ls, "*.md", 2>, /dev/null]
AST:
  CommandNode { name: echo, suffix: [hello;world] },
  CommandNode {
    name: ls,
    suffix: [*.md],
    redirects: [RedirectNode("2>", "/dev/null")]
  }
```

注意 `hello;world` 中的 `;` 在双引号内，不分割命令；`*.md` 在单引号内，通配符不会展开，作为字面值 `*.md` 传给 ls。

## 相关概念

- [命令系统](03-command-system.md)
- [架构总览](02-architecture-overview.md)
- [IO 系统](05-io-system.md)
