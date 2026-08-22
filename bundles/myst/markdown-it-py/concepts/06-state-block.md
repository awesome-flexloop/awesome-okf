---
type: Concept
title: StateBlock 块级解析状态
description: StateBlock 管理块级解析的全部上下文，包括预计算的行偏移数组、解析状态变量和 Token 输出方法
tags:
- markdown-it-py
- state
- block-parsing
- line-offsets
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 04-parsing-pipeline
- 05-ruler
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# StateBlock 块级解析状态

StateBlock 是块级规则函数操作的上下文对象。它存储当前解析位置、已输出的 Token 列表、以及预计算的行级元数据，块级规则通过读取和修改 StateBlock 来完成解析。

## 预计算的行偏移数组

StateBlock 初始化时，一次性遍历整个源文本，为每一行预计算以下数组：

| 数组名 | 类型 | 含义 |
|--------|------|------|
| `bMarks[i]` | int | 第 i 行的起始字符偏移 |
| `eMarks[i]` | int | 第 i 行的结束字符偏移（不包含换行符） |
| `tShift[i]` | int | 第 i 行首个非空白字符的偏移（相对于bMarks[i]） |
| `sCount[i]` | int | 第 i 行有效缩进列数（Tab 展开后的空格数） |
| `bsCount[i]]` | int | 第 i 行原始空白字符偏移（tShift 之前的字符位置） |

这意味着块级规则可以通过数组下标 O(1) 访问任意行的信息，不需要反复调用字符串 split 或 search。

### 示例

对文本 `"# Hello\n\nWorld"`：
```
行0: "# Hello"  → bMarks[0]=0, eMarks[0]=7, tShift[0]=0, sCount[0]=0
行1: ""         → bMarks[1]=8, eMarks[1]=8, tShift[1]=0, sCount[0]=0
行2: "World"    → bMarks[2]=9, eMarks[2]=14, tShift[2]=0, sCount[0]=0
```

### 访问行内容

```python
def my_rule(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool:
    # 获取行的起始和结束偏移
    start = state.bMarks[startLine] + state.tShift[startLine]
    end = state.eMarks[startLine]
    # 获取行内容（去除前导空白）
    line_text = state.src[start:end]
```

## 解析状态变量

| 变量 | 类型 | 含义 |
|------|------|------|
| `line` | int | 当前解析行号（规则修改此值来"消费"多行） |
| `blkIndent` | int | 当前块缩进要求（用于嵌套列表/引用） |
| `tight` | bool | 列表是否为 tight 模式（项间无空行） |
| `parentType` | str | 父块类型（"paragraph"/"list"等） |
| `level` | int | 当前 Token 嵌套级别 |
| `result` | str | （少见）规则间传递字符串结果 |

### line 变量——消费行的机制

块级规则通过修改 `state.line` 来告诉解析器消费了多少行：

```python
def fence_rule(state, startLine, endLine, silent):
    # ...检测到围栏代码块从 startLine 开始...
    nextLine = startLine + 1
    # ...逐行查找闭合围栏...
    state.line = nextLine + 1  # 标记消费到了 nextLine+1
    # ...输出 Token...
    return True
```

tokenize() 循环使用 `state.line` 更新当前行位置，继续解析。

## Token 输出方法

### push(type, tag, nesting)——创建并追加 Token

```python
def push(self, type, tag, nesting):
    token = Token(type, tag, nesting)
    token.block = True
    token.level = self.level
    if nesting < 0:
        self.level -= 1
    token.level = self.level
    if nesting > 0:
        self.level += 1
    self.tokens.append(token)
    return token
```

关键行为：
- 自动设置 `token.block = True`
- 根据 nesting 自动管理 `token.level`
- 开标签（nesting=1）先设置 level 再递增，闭标签（nesting=-1）先递减 level
- 闭标签和其对应的开标签在同一 level

### push 示例

输出一个段落：
```python
# <p>Hello</p>
state.push("paragraph_open", "p", 1)
# ...输出 inline token（由 inline 规则后处理填充 children）...
state.push("paragraph_close", "p", -1)
```

## 行级工具方法

StateBlock 提供了多个行操作辅助方法：

### getLines(begin, end, indent, keepLastLF)

获取多行文本，用于代码块、引用等需要保留原始内容的场景：

```python
content = state.getLines(startLine, endLine, blkIndent, True)
```

- `begin`/`end`：行范围
- `indent`：要去除的缩进级别
- `keepLastLF`：是否保留末尾换行

### skipEmptyLines(from)

跳过空行，返回下一个非空行的行号：

```python
next_line = state.skipEmptyLines(startLine)
```

### skipSpaces(pos)

从指定位置跳过空白字符，返回非空白位置。

### skipChars(pos, code)

从指定位置跳过指定字符（如 `>` 用于引用块检测）。

### isEmpty(line)

判断指定行是否为空行（仅含空白）。

## 行内解析调度

StateBlock 提供了两种行内解析调度方式（通常由 inline 核心规则调用）：

### pushToken(type, tag, nesting, content, map_lines)

创建 Token 并设置 map 字段：
```python
token = state.push("inline", "", 0)
token.content = state.src[start:end]
token.map = [startLine, nextLine]
```

## 典型块级规则的状态操作模式

```python
def my_block_rule(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool:
    # 1. 检查起始标记（如果silent=True，只检查不输出）
    start = state.bMarks[startLine] + state.tShift[startLine]
    if state.src[start:start+3] != "!!!":
        return False
    
    if silent:
        return True  # 确认匹配，不输出
    
    # 2. 扫描内容，确定结束行
    nextLine = startLine + 1
    while nextLine < endLine:
        if is_terminator(state, nextLine):
            break
        nextLine += 1
    
    # 3. 输出开标签
    token = state.push("my_block_open", "div", 1)
    token.markup = "!!!"
    token.map = [startLine, nextLine]
    token.attrSet("class", "my-block")
    
    # 4. 输出 inline 占位符（行内内容将由 inline 核心规则解析）
    token = state.push("inline", "", 0)
    token.content = state.getLines(startLine+1, nextLine, state.blkIndent, False)
    token.map = [startLine+1, nextLine]
    
    # 5. 输出闭标签
    state.push("my_block_close", "div", -1)
    
    # 6. 更新行位置
    state.line = nextLine
    return True
```

## 与 StateCore 和 StateInline 的关系

```
StateCore
├── src: str          # 源文本
├── md: MarkdownIt    # 解析器实例
├── env: dict         # 环境对象
├── tokens: list      # 全局 Token 列表（StateBlock/StateInline 共享）
└── inlineMode: bool  # 是否为行内直通模式

StateBlock (由 Core 链的 block 规则创建)
├── src: str          # 引用 StateCore.src
├── md: MarkdownIt    # 引用
├── env: dict         # 引用
├── tokens: list      # 引用 StateCore.tokens
├── bMarks/eMarks/tShift/sCount/bsCount: list[int]  # 行偏移数组
├── line/blkIndent/tight/parentType/level           # 解析状态
└── ...行级工具方法

StateInline (由 Core 链的 inline 规则创建，每个 inline Token 各一个)
├── src: str          # 引用 inline Token 的 content
├── md/env/tokens     # 引用
├── pos/posMax        # 当前位置和结束位置
├── pending: str      # 文本缓冲区
├── delimiters: list  # 分隔符链表
└── ...字符级工具方法
```

## 下一步

- [StateInline 行内解析状态](07-state-inline.md)：行内解析的状态管理
- [块级规则详解](08-block-rules.md)：11 条块级规则的功能
- [行内规则详解](09-inline-rules.md)：12+4 条行内规则的功能
