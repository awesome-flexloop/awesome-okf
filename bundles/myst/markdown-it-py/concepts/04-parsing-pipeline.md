---
type: Concept
title: 解析管线架构
description: markdown-it-py 的 Core→Block→Inline 三链解析管线，包括块级解析与行内解析的两阶段协作、inlineMode 直通模式
tags:
- markdown-it-py
- parsing
- pipeline
- core
- block
- inline
difficulty: 核心
estimated_time: 25分钟
prerequisites:
- 03-token-stream
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

# 解析管线架构

markdown-it-py 的解析由三条规则链组成，按固定顺序执行：**Core 链 → Block 链 → Inline 链**。理解这三条链的协作方式，就理解了整个解析器的工作原理。

## 整体数据流

```
Markdown 文本 (src)
    ↓
[Core 链: normalize]          换行符规范化
    ↓
[Core 链: block] → ParserBlock.tokenize()
    ↓ 产出块级 tokens（含 inline 占位符）
[Core 链: inline] → ParserInline.parse() 遍历每个 inline token 填充 children
    ↓
[Core 链: linkify/replacements/smartquotes/text_join] 后处理
    ↓
Token 流 → Renderer.render() → HTML
```

### parse() 方法入口

`MarkdownIt.parse(src, env=None)` 的核心逻辑：
1. 创建 `StateCore(src, self, env)`
2. 调用 `self.core.process(state)`，依次执行 Core 链所有规则
3. 返回 `state.tokens`

### render() 方法

`MarkdownIt.render(src, env=None)` 调用 `parse()` 获取 tokens，然后调用 `self.renderer.render(tokens, options, env)` 渲染为 HTML。

## Core 链——全局编排器

Core 链只有 7 条规则，按固定顺序执行：

```python
[
    "normalize",     # 1. 换行符规范化
    "block",         # 2. 调度块级解析
    "inline",        # 3. 调度行内解析
    "linkify",       # 4. 自动链接（可选）
    "replacements",  # 5. 排版替换（可选）
    "smartquotes",   # 6. 智能引号（可选）
    "text_join",     # 7. 合并相邻 text tokens
]
```

Core 链的规则由 `ParserCore` 类管理，`process()` 方法依次调用每条规则的 `fn(state)`。

### normalize——换行符规范化

将 `\r\n`、`\r` 统一替换为 `\n`，将 NULL 字符（`\0`）替换为 `\uFFFD`（替换字符）。这是解析的第一步，确保后续规则只需要处理 `\n` 换行。

### block——块级解析调度

这是核心规则，它调度 `ParserBlock.parse(state, startLine, endLine)`。如果设置了 `state.inlineMode = True`（即通过 `parseInline()` 调用），则跳过块级解析，直接创建一个 `inline` Token 包含整个源文本。

### inline——行内解析调度

遍历 `state.tokens`，找到所有 `type="inline"` 的 Token，调用 `ParserInline.parse()` 填充其 `children` 字段。

### linkify/replacements/smartquotes——可选后处理

这三条规则是可选项，分别对应 `linkify`、`typographer` 选项。只有在选项启用时才生效。

### text_join——合并相邻文本

将相邻的 `type="text"` Token 合并为一个，减少 Token 数量，优化渲染性能。

## Block 链——块级解析

Block 链包含 11 条规则，按严格的优先级顺序排列：

```python
[
    "table",       # GFM 表格（优先级最高）
    "code",        # 缩进代码块（4空格）
    "fence",       # 围栏代码块（```）
    "blockquote",  # 引用块（>）
    "hr",          # 水平分隔线（---）
    "list",        # 列表（-/*/1.）
    "reference",   # 链接引用定义
    "html_block",  # HTML 块
    "heading",     # ATX 标题（#）
    "lheading",    # Setext 标题（===）
    "paragraph",   # 段落（兜底规则）
]
```

### 行驱动的解析算法

ParserBlock.tokenize() 采用行驱动算法：

```python
def tokenize(state, startLine, endLine):
    line = startLine
    while line < endLine:
        # 获取当前行缩进
        if state.sCount[line] < state.blkIndent:
            break  # 缩进减少，终止当前块

        state.line = line
        # 尝试每条规则（按顺序）
        for rule in rules:
            if rule.fn(state, line, endLine, False):
                break  # 某规则成功消费了行
        line = state.line  # 跳到规则消费后的下一行
```

关键点：
1. **首次匹配原则**：对每一行，按规则顺序依次尝试，第一个返回 `True` 的规则"消费"该行
2. **行跳转**：规则通过修改 `state.line` 指示消费了多少行
3. **缩进敏感**：缩进减少会终止列表/引用等嵌套块
4. **tight/loose 列表**：列表项之间是否有空行决定 tight 属性

### 规则的 alt 列表

每条块级规则可以声明 `alt` 列表（包含可以终止当前规则的其他规则名）。例如 paragraph 规则的 alt 包含 `["paragraph", "reference", "blockquote", "list"]`，这意味着在解析段落时，如果遇到这些规则的起始标记，段落结束。

## Inline 链——行内解析

Inline 链有两条 Ruler：`ruler`（主链）和 `ruler2`（后置链）。

### 主链（12条规则）

```python
[
    "text",          # 纯文本
    "linkify",       # 自动链接
    "newline",       # 换行
    "escape",        # 反斜杠转义
    "backticks",     # 行内代码
    "strikethrough", # 删除线（含postProcess）
    "emphasis",      # 强调（含postProcess）
    "link",          # 链接
    "image",         # 图片
    "autolink",      # 自动链接 <url>
    "html_inline",   # 行内HTML
    "entity",        # HTML实体
]
```

### 后置链（4条规则）

```python
[
    "balance_pairs",     # 成对标记平衡
    "strikethrough",     # 删除线后处理
    "emphasis",          # 强调后处理
    "fragments_join",    # 合并剩余分隔符
]
```

### 字符驱动的行内解析

ParserInline.tokenize() 使用字符驱动算法，从 `state.pos` 位置开始，尝试每个终止字符和规则：

1. 扫描普通文本，累积到 `pending` 缓冲区
2. 遇到特殊字符（`_*~![]<>&` 反引号换行等终止字符）时，依次尝试各规则
3. 规则成功匹配时，先 `pushPending()` 刷新缓冲区，再输出对应 Token
4. 规则移动 `state.pos` 到匹配结束位置
5. 到达 `state.posMax` 时结束

### 双 Ruler 设计的原因

强调（`*em*`/`**strong**`）和删除线（`~~del~~`）的解析需要先扫描标记分隔符（`*`/`~`），再根据开闭配对规则决定实际的标记类型。因此 tokenize 阶段只产生"文本"和"分隔符"，ruler2 的 postProcess 阶段根据 delimiters 链表配对产生实际的 em/strong/s_open/s_close Token。

### 分隔符链表（Delimiter）

StateInline 维护 `delimiters` 链表，每个 Delimiter 记录：
- `marker`：分隔符字符（`*` 或 `~`）
- `length`：连续标记长度
- `token`：指向起始/结束位置的 Token 索引
- `open`/`close`：是否可以作为开/闭标签
- `level`：嵌套层级

emphasis 和 strikethrough 的 postProcess 遍历此链表，匹配开-闭对，将中间的文本 Token 包裹在 em_open/em_close 等 Token 中。

## 两阶段解析：块级先于行内

解析管线的一个关键设计是**两阶段解析**：

1. **第一阶段（Block 链）**：识别所有块级结构（段落、标题、列表等），为每个含文本的块创建一个 `inline` Token，`content` 字段存原文，`children` 为 None
2. **第二阶段（Inline 链）**：遍历所有 inline Token，解析其 content 为行内 Token 树，填入 children

这种设计的好处：
- 块级结构的判定不受行内元素影响（简化逻辑）
- 链接引用定义在块级阶段统一收集，行内解析时可查询
- 行内解析可以针对不同块类型做不同处理

## inlineMode——行内直通模式

通过 `parseInline()`/`renderInline()` 调用时，设置 `state.inlineMode = True`：
- Core 链的 block 规则跳过块级解析，直接创建一个 inline Token
- Inline 链正常解析这个 Token 的 content
- 适用于只解析行内容器内的内容（如已有块级结构，只需要解析某段文本）

## 数据流图示

```
                    ┌─────────────────────────────────┐
                    │         src (Markdown 文本)       │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │ Core Rule 1: normalize          │
                    │ \r\n → \n, \0 → \uFFFD          │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │ Core Rule 2: block              │
                    │ ┌───────────────────────────┐   │
                    │ │ ParserBlock.tokenize()    │   │
                    │ │ 逐行尝试 11 条块级规则      │   │
                    │ │ → 产出块级 tokens          │   │
                    │ │ （含 inline 占位符）       │   │
                    │ └───────────────────────────┘   │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │ Core Rule 3: inline             │
                    │ ┌───────────────────────────┐   │
                    │ │ ParserInline.parse()      │   │
                    │ │ 遍历 inline tokens         │   │
                    │ │ → 填充 children 字段       │   │
                    │ └───────────────────────────┘   │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │ Core: linkify/replacements/     │
                    │ smartquotes/text_join（可选）    │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼────────────────────┐
                    │        Token 流（最终结果）       │
                    └─────────────────────────────────┘
```

## 下一步

- [Ruler 规则管理](05-ruler.md)：规则链的内部机制
- [StateBlock 块级解析状态](06-state-block.md)：块级解析的状态管理
- [StateInline 行内解析状态](07-state-inline.md)：行内解析的状态管理
