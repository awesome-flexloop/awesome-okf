---
type: Concept
title: Token 流模型
description: markdown-it-py 使用线性 Token 流而非传统 AST 表示解析结果，通过 nesting/level 表示嵌套，children 存储行内子元素
tags:
- markdown-it-py
- token
- ast
- parsing
- data-structure
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 01-getting-started
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

# Token 流模型

markdown-it-py 的解析结果不是传统的抽象语法树（AST），而是一个**线性 Token 序列**。这个设计选择是理解整个库的关键。

## Token 流 vs AST

传统 AST 使用嵌套树结构表示文档：
```
Document
├── Heading(level=1)
│   └── Text("Hello")
└── Paragraph
    ├── Text("This is ")
    └── Strong
        └── Text("bold")
```

markdown-it-py 使用线性 Token 序列，每个元素由**开标签 Token** 和**闭标签 Token** 配对表示：
```python
[
    Token(type="heading_open", tag="h1", nesting=1),
    Token(type="inline", nesting=0, children=[
        Token(type="text", content="Hello")
    ]),
    Token(type="heading_close", tag="h1", nesting=-1),
    Token(type="paragraph_open", tag="p", nesting=1),
    Token(type="inline", nesting=0, children=[
        Token(type="text", content="This is "),
        Token(type="strong_open", tag="strong", nesting=1),
        Token(type="text", content="bold"),
        Token(type="strong_close", tag="strong", nesting=-1),
    ]),
    Token(type="paragraph_close", tag="p", nesting=-1),
]
```

### 为什么不用 AST？

Token 流设计在 Markdown 渲染场景下有几个优势：
1. **渲染简单**：顺序遍历 Token 列表，遇到开标签输出 `<tag>`，遇到闭标签输出 `</tag>`，无需递归树遍历
2. **性能优秀**：解析过程是线性的，不需要树构建的额外开销
3. **易于中间处理**：在 Token 流中插入/删除/修改 Token 很直观（插件可以直接操作 tokens 列表）
4. **延迟解析**：块级解析完成后才解析行内内容，children 字段实现"先产出壳子再填充内容"

## Token 的 nesting 三值

`nesting` 字段是 Token 流的核心，它决定了 Token 的类型：

| nesting 值 | 含义 | HTML 输出示例 |
|------------|------|--------------|
| 1 | **开标签**（Opening） | `<h1>`、`<p>`、`<strong>` |
| 0 | **自闭合**（Self-closing） | `<br>`、`<hr>`、`<img>`，以及文本/代码等内容容器 |
| -1 | **闭标签**（Closing） | `</h1>`、`</p>`、`</strong>` |

### nesting 与 level 的关系

`level` 字段表示嵌套深度。开标签（nesting=1）会增加层级，闭标签（nesting=-1）会减少层级：

```
nesting=1  level=0  <p>         ← 开，进入level 1
nesting=0  level=1  text         ← 内容，不改变层级
nesting=1  level=1  <strong>    ← 开，进入level 2
nesting=0  level=2  text         ← 内容
nesting=-1 level=2  </strong>   ← 闭，回到level 1
nesting=-1 level=1  </p>        ← 闭，回到level 0
```

自闭合 Token（nesting=0）的 level 值与其所在层级一致，不会改变层级。

## 核心字段详解

### type 和 tag

- `type`：Token 类型标识符，渲染规则通过 type 查找。常见值：`paragraph_open`、`heading_open`、`inline`、`text`、`code_block`、`fence`、`hardbreak`、`image`、`link_open`、`html_block`、`softbreak`
- `tag`：HTML 标签名（开/闭标签对），或空字符串（自闭合内容类型如 text、inline）。开标签和对应的闭标签有相同的 tag

### children——行内容器

`children` 是唯一引入树结构的地方。它只出现在 `type="inline"` 的 Token 上：

```python
# 块级解析产出
paragraph_open (nesting=1, tag="p")
inline (nesting=0, children=None)  # 此时 children 还未填充
paragraph_close (nesting=-1, tag="p")

# 行内解析后，inline Token 的 children 被填充
inline (children=[
    text(nesting=0, content="This is "),
    strong_open(nesting=1, tag="strong"),
    text(nesting=0, content="bold"),
    strong_close(nesting=-1, tag="strong"),
])
```

这是一种"两阶段解析"策略：块级规则先识别出段落/标题/代码块等结构块，产出 `inline` Token 作为占位符；然后 inline 规则链处理每个 inline Token 的内容，将解析结果写入 children。

### attrs——HTML 属性

`attrs` 是一个 `dict[str, str|int|float]`，存储 HTML 属性：

```python
from markdown_it import MarkdownIt

md = MarkdownIt()
tokens = md.parse('[link](https://example.com "title")')

# 找到 link_open token
for tok in tokens:
    if tok.type == "link_open":
        print(tok.attrs)
        # {'href': 'https://example.com', 'title': 'title'}
```

属性操作方法：
```python
token.attrSet("class", "highlight")   # 设置属性
token.attrGet("href")                  # 获取属性 → "https://..."
token.attrJoin("class", "active")      # 空格拼接（→ "highlight active"）
token.attrPush(("data-id", "42"))      # 添加属性
token.attrItems()                      # 获取 [(k,v), ...] 列表
```

> ⚠️ **Python 与 JS 的差异**：JS 版 markdown-it 使用 `list of [key, value]` 对存储 attrs，Python 版改用 dict。`Token.as_dict(as_upstream=True)` 可将 attrs 转回 JS 兼容格式。

### map——源码映射

块级 Token 通常有 `map` 字段，记录该 Token 在源文本中的行范围：

```python
token.map  # [start_line, end_line]  （0-indexed，左闭右开）
```

### 其他字段

| 字段 | 说明 |
|------|------|
| `content` | 自闭合 Token 的内容（text、code_block、fence、html_block 等） |
| `markup` | 触发该 Token 的 Markdown 标记符号（如 `#`、`**`、\`\`\`、`---`） |
| `info` | 附加信息字符串（围栏代码块的语言名、列表标记类型等） |
| `meta` | 插件自定义数据字典，规则和插件可用于传递信息 |
| `block` | bool，标记该 Token 是块级（True）还是行内（False） |
| `hidden` | bool，True 时 Renderer 默认跳过该 Token（用于语法辅助节点） |

## 常见 Token 类型速查

### 块级 Token

| type | nesting | tag | 说明 |
|------|---------|-----|------|
| `heading_open` / `heading_close` | 1/-1 | h1~h6 | ATX/Setext 标题 |
| `paragraph_open` / `paragraph_close` | 1/-1 | p | 段落 |
| `blockquote_open` / `blockquote_close` | 1/-1 | blockquote | 引用块 |
| `bullet_list_open` / `bullet_list_close` | 1/-1 | ul | 无序列表 |
| `ordered_list_open` / `ordered_list_close` | 1/-1 | ol | 有序列表 |
| `list_item_open` / `list_item_close` | 1/-1 | li | 列表项 |
| `hr` | 0 | hr | 水平分隔线 |
| `code_block` | 0 | pre/code | 缩进代码块 |
| `fence` | 0 | code | 围栏代码块 |
| `html_block` | 0 | - | HTML 块级内容 |
| `table_open` / `table_close` | 1/-1 | table | 表格 |
| `thead_open` / `thead_close` | 1/-1 | thead | 表头 |
| `tbody_open` / `tbody_close` | 1/-1 | tbody | 表体 |
| `tr_open` / `tr_close` | 1/-1 | tr | 表格行 |
| `th_open` / `th_close` | 1/-1 | th | 表头单元格 |
| `td_open` / `td_close` | 1/-1 | td | 数据单元格 |
| `inline` | 0 | - | 行内容器（children 包含行内 Token） |

### 行内 Token

| type | nesting | tag | 说明 |
|------|---------|-----|------|
| `text` | 0 | - | 普通文本 |
| `em_open` / `em_close` | 1/-1 | em | 斜体 |
| `strong_open` / `strong_close` | 1/-1 | strong | 粗体 |
| `s_open` / `s_close` | 1/-1 | s | 删除线 |
| `code_inline` | 0 | code | 行内代码 |
| `link_open` / `link_close` | 1/-1 | a | 链接 |
| `image` | 0 | img | 图片（自闭合） |
| `hardbreak` | 0 | br | 硬换行 |
| `softbreak` | 0 | - | 软换行（通常渲染为空格） |
| `html_inline` | 0 | - | 行内 HTML |
| `entity` | 0 | - | HTML 实体 |

## 从 Token 流到树：SyntaxTreeNode

如果需要树结构遍历，markdown-it-py 提供了 `SyntaxTreeNode` 类：

```python
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

md = MarkdownIt()
tokens = md.parse("# Hello **world**")
node = SyntaxTreeNode(tokens)
print(node.pretty())  # 打印树状结构
```

SyntaxTreeNode 是 Python 端的扩展（JS 上游没有），它将线性 Token 流转换为嵌套树，提供 `walk()`、`to_tokens()`、`descendants` 等方法。详细用法见 [SyntaxTreeNode](11-syntax-tree-node.md)。

## 下一步

- [解析管线架构](04-parsing-pipeline.md)：Token 流是如何从 Markdown 文本一步步生成的
- [Ruler 规则管理](05-ruler.md)：哪些规则生成哪些 Token
- [渲染器详解](10-renderer.md)：Token 流如何渲染为 HTML
