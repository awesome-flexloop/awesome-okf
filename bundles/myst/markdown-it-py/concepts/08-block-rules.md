---
type: Concept
title: 块级规则详解
description: markdown-it-py 内置的 11 条块级规则的功能、匹配语法和执行顺序
tags:
- markdown-it-py
- block-rules
- table
- code
- fence
- list
- heading
difficulty: 核心
estimated_time: 25分钟
prerequisites:
- 06-state-block
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

# 块级规则详解

Block 链包含 11 条规则，按优先级顺序排列。解析器逐行尝试规则，第一个匹配的规则消费该行。

## 规则执行顺序

| 序号 | 规则名 | 匹配语法 | 输出 Token |
|------|--------|---------|-----------|
| 1 | table | `\| col \| col \|` | table_open/thead/tbody/tr/th/td/inline |
| 2 | code | 4空格/1Tab缩进 | code_block |
| 3 | fence | \`\`\` 或 ~~~ | fence |
| 4 | blockquote | `> ` | blockquote_open/close |
| 5 | hr | `---` / `***` / `___` | hr |
| 6 | list | `- ` / `* ` / `1. ` | bullet_list/ordered_list/list_item |
| 7 | reference | `[label]: url "title"` | （写入env.references，不输出Token） |
| 8 | html_block | HTML块标签 | html_block |
| 9 | heading | `# ` ~ `###### ` | heading_open/inline/close |
| 10 | lheading | 下一行 `===`/`---` | heading_open/inline/close |
| 11 | paragraph | （兜底） | paragraph_open/inline/close |

## 各规则详解

### 1. table（GFM 表格）

匹配 GFM 风格表格语法：
```
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

- 要求首行包含 `|`，第二行是分隔行（`|--|--|` 等）
- 分隔行中 `:` 的位置控制对齐（`:--:` 居中、`:--` 左对齐、`--:` 右对齐）
- commonmark 预设默认禁用，gfm-like/gfm-like2 启用

### 2. code（缩进代码块）

匹配4空格或1Tab缩进的代码块：
```
    def hello():
        print("hello")
```

- 缩进 ≥ 4空格（或 1Tab）视为代码
- 内部不做 Markdown 解析，content 存储原始文本
- 输出单个 `code_block` Token（nesting=0, tag="code"）

### 3. fence（围栏代码块）

匹配三个及以上反引号或波浪线的围栏：
````
```python
def hello():
    print("hello")
```
````

- 起始围栏后可跟语言标识（info字段）
- 闭合围栏字符数必须 ≥ 起始围栏
- 输出单个 `fence` Token（nesting=0, tag="code", info="python", content=代码内容）
- 支持大括号属性语法（```` {.python #id}`）

### 4. blockquote（引用块）

匹配 `>` 开头的行：
```
> This is a quote
> Multiple lines
```

- 每行可独立有 `>` 前缀
- 支持嵌套引用（`> > nested`）
- 内部递归调用 ParserBlock.parse 解析引用内容
- 输出 blockquote_open/close + 内部tokens

### 5. hr（水平分隔线）

匹配三个及以上 `-`、`*` 或 `_`：
```
---
***
___
```

- 三个及以上相同字符
- 中间可有空格（`- - -` 也可）
- 不能有其他字符
- 输出单个 `hr` Token（nesting=0, tag="hr"）

### 6. list（列表）

匹配无序列表（`- `、`* `、`+ `）和有序列表（`1. `、`2) `）：

- **无序列表标记**：`-`、`*`、`+`
- **有序列表标记**：数字+`.` 或 `)`，如 `1.`、`1)`
- **缩进**：列表项内缩进决定项边界
- **tight/loose**：项间有空行为 loose（`<p>` 包裹），无空行为 tight
- 输出 bullet_list_open/ordered_list_open + list_item_open/close + 列表项内容

### 7. reference（链接引用）

匹配链接引用定义：
```
[1]: https://example.com "Optional Title"
[label]: https://example.com
```

- **不输出 Token**，将引用信息写入 `env.references`
- 后续行内 link 规则通过 label 查找引用
- 支持多行标题和尖括号URL

### 8. html_block（HTML 块）

匹配 HTML 块级元素。有7种HTML块类型（按CommonMark规范），包括：
- `<pre>`、`<script>`、`<style>`、`<textarea>` 等特定标签（直到结束标签）
- HTML注释（`<!-- -->`）
- `<?...?>`、`<!DOCTYPE...>`、`<![CDATA[...]]>`
- 其他块级HTML标签（`<div>`、`<p>` 等），直到空行

- html=False 时此规则禁用，HTML被转义为文本
- 输出单个 `html_block` Token（nesting=0, content=原始HTML）

### 9. heading（ATX 标题）

匹配 `#` 到 `######` 开头的行：
```
# H1
## H2
### H3
```

- 1~6个 `#` 对应 h1~h6
- `#` 后需要空格
- 行尾的 `#` 序列作为闭合标记（可选）
- 输出 heading_open(tag=hN)/inline/heading_close

### 10. lheading（Setext 标题）

匹配下一行用 `===` 或 `---` 下划线的标题：
```
Title
=====

Subtitle
--------
```

- `===` 对应 h1，`---` 对应 h2
- 上一行文本作为标题内容
- 输出 heading_open/inline/heading_close

### 11. paragraph（段落——兜底规则）

所有其他规则都不匹配时，paragraph 规则将连续非空行收集为一个段落。

- 段落结束条件：空行、或遇到 alt 列表中声明的规则起始标记
- 输出 paragraph_open/inline/paragraph_close
- inline Token 的 content 是段落原文，由 inline 规则后处理

## 规则优先级为什么这样排？

- **table 最先**：表格行以 `|` 开头，如果不先于 paragraph 匹配，会被当作段落文本
- **code/fence 在 paragraph 前**：代码块和围栏有明确标记，不应被段落吸收
- **hr 在 list/heading 前**：`---` 可能被 lheading 误判为下划线标题（但lheading检测的是"上一行+下划线"模式，hr直接在当前行判断）
- **reference 在 paragraph 前**：引用定义如果被当作段落，后续链接无法解析
- **paragraph 最后**：作为兜底规则，确保所有文本都被消费

## 下一步

- [行内规则详解](09-inline-rules.md)：12+4条行内规则
- [渲染器详解](10-renderer.md)
- [核心规则深入](15-core-rules-deep-dive.md)
