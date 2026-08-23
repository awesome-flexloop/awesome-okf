---
type: Concept
title: StateInline 行内解析状态
description: StateInline 管理行内解析的全部上下文，包括字符位置、文本缓冲区、分隔符链表、反引号缓存
tags:
- markdown-it-py
- state
- inline-parsing
- delimiters
- emphasis
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 04-parsing-pipeline
- 05-ruler
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# StateInline 行内解析状态

StateInline 是行内规则函数操作的上下文对象。每个 `inline` 类型 Token 的 content 被解析时，都会创建一个新的 StateInline 实例。

## 核心字段

### 位置与缓冲区

| 字段 | 类型 | 含义 |
|------|------|------|
| `src` | str | 要解析的文本（=inline Token 的 content） |
| `pos` | int | 当前解析位置（字符偏移） |
| `posMax` | int | 文本结束位置 |
| `pending` | str | 累积的普通文本缓冲区 |
| `pendingLevel` | int | pending 文本起始的嵌套级别 |
| `level` | int | 当前嵌套级别 |

### 关键数据结构

| 字段 | 类型 | 含义 |
|------|------|------|
| `tokens` | list[Token] | 输出的行内 Token 列表 |
| `delimiters` | list[Delimiter] | 分隔符链表（强调/删除线配对） |
| `backticks` | dict | 反引号位置缓存 |
| `backticksScanned` | bool | 反引号扫描是否完成 |
| `linkLevel` | int | 当前链接嵌套级别（防嵌套） |
| `md` | MarkdownIt | 解析器实例引用 |
| `env` | dict | 环境对象引用 |

## 文本缓冲区 pending

StateInline 使用 pending 缓冲区累积普通文本，避免为每个字符创建单独 text Token：

1. 处理特殊字符前，调用 `pushPending()` 刷新缓冲区为 text Token
2. 普通字符通过 `pending += ch` 追加
3. 解析结束时再次 `pushPending()` 刷新

```python
# text 规则核心逻辑
def text(state, silent):
    pos = state.pos
    while pos < state.posMax and not isTerminator(state.src[pos]):
        pos += 1
    if pos == state.pos:
        return False
    if not silent:
        state.pending += state.src[state.pos:pos]
    state.pos = pos
    return True
```

## push() 和 pushPending()

**push(type, tag, nesting)**：输出 Token（自动处理 level 增减，先flush pending）。

**pushPending()**：将 pending 缓冲区内容输出为 text Token，重置 pending。

## 分隔符链表 delimiters

分隔符链表是强调（`*em*`/`**strong**`）和删除线（`~~del~~`）解析的核心。

### Delimiter 结构

| 字段 | 类型 | 含义 |
|------|------|------|
| `marker` | int | 标记字符（`*` 或 `~` 的 ord 值） |
| `length` | int | 连续标记字符数 |
| `token` | int | 对应 Token 在 tokens 列表中的索引 |
| `end` | int | 配对结束分隔符索引（-1=未配对） |
| `open` | bool | 是否可作为开标签 |
| `close` | bool | 是否可作为闭标签 |
| `level` | int | 所在嵌套级别 |

### scanDelims(start, canSplitWord)

扫描分隔符，返回 `Scanned(can_open, can_close, length, jump)`：
- **can_open**：后面不是空白，且（前面是空白/标点 或 后面不是标点）
- **can_close**：前面不是空白，且（后面是空白/标点 或 前面不是标点）

这实现了 CommonMark "flanking rules"（分隔符的左右判定）。

### 双阶段强调解析

1. **tokenize 阶段**：遇到 `*`/`~` 时，scanDelims 判断开闭性，加入 delimiters 链表，标记字符暂时作为文本输出
2. **postProcess 阶段**（ruler2链）：遍历 delimiters 链表，按配对算法匹配开闭对，将分隔符文本替换为 em_open/em_close/strong_open/strong_close 等 Token

## 反引号缓存 backticks

行内代码需要匹配相同数量的反引号。StateInline 首次需要时扫描整个 src，在 `backticks` 字典记录每个位置的反引号信息（长度、是否开闭），后续匹配通过查缓存完成，避免回溯。

## 终止字符

行内解析在遇到终止字符时停下，尝试对应规则。默认终止字符包括 `*`, `_`, `~`, `` ` ``, `[`, `!`, `<`, `>`, `&`, `\`, `\n` 等。插件通过 `add_terminator_char(ch)` 添加新终止符。

## linkLevel——嵌套防护

遇到 link_open 时 linkLevel++，link_close 时 linkLevel--。当 linkLevel > 0 时，新的链接/图片规则不触发，防止链接嵌套。

## 下一步

- [块级规则详解](08-block-rules.md)
- [行内规则详解](09-inline-rules.md)
- [渲染器详解](10-renderer.md)
