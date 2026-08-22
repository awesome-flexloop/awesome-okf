---
type: Concept
title: 行内规则详解
description: markdown-it-py 内置的 12 条行内主规则和 4 条后置规则的功能与匹配语法
tags:
- markdown-it-py
- inline-rules
- emphasis
- link
- backticks
- strikethrough
difficulty: 核心
estimated_time: 25分钟
prerequisites:
- 07-state-inline
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

# 行内规则详解

Inline 解析器有双 Ruler：主链（ruler）12条规则负责tokenize，后置链（ruler2）4条规则处理分隔符配对。

## 主链规则（ruler，12条）

按执行顺序：

| 序号 | 规则名 | 匹配语法 | 输出 Token |
|------|--------|---------|-----------|
| 1 | text | 普通字符序列 | text（累积到pending） |
| 2 | linkify | 纯文本URL | link_open/text/link_close |
| 3 | newline | `\n` | hardbreak / softbreak |
| 4 | escape | `\x`（反斜杠转义） | text |
| 5 | backticks | `` `code` `` | code_inline |
| 6 | strikethrough | `~~del~~` / `~del~` | （标记+delimiter） |
| 7 | emphasis | `*em*`/`**strong**` | （标记+delimiter） |
| 8 | link | `[text](url)` 或 `[text][ref]` | link_open/.../link_close |
| 9 | image | `![alt](url)` | image（自闭合） |
| 10 | autolink | `<url>` / `<email>` | link_open/text/link_close |
| 11 | html_inline | `<tag>` | html_inline |
| 12 | entity | `&amp;` | text（实体解码后） |

## 各规则详解

### 1. text（文本）

累积连续非终止字符到 pending 缓冲区。遇到任何终止字符（`*`, `_`, `~`, `` ` ``, `[`, `!`, `<`, `>`, `&`, `\`, `\n` 等）时停止。

### 2. linkify（自动链接）

当 `linkify` 选项启用且安装了 linkify-it-py 时，识别纯文本中的 URL（如 `https://example.com`）并自动转为链接。

### 3. newline（换行）

处理行内的 `\n` 字符：
- 前一行末尾有2+空格 → `hardbreak`（`<br>`）
- 后一行是空行 → `hardbreak`
- 否则 → `softbreak`（渲染为空格或 `<br>` 取决于 `breaks` 选项）

### 4. escape（反斜杠转义）

匹配 `\` + 标点符号，输出转义后的字符（如 `\*` → 字面 `*` 而非强调标记）。CommonMark 支持转义的标点包括：`` \`*_{}[]()#+-.!|~``

### 5. backticks（行内代码）

匹配反引号包裹的代码：
```
`code`
``code with ` backtick``
```

- 反引号数量可以是 1 个或多个（如 ``` ``code`` ```）
- 开闭反引号数量必须相同
- 内部不做 Markdown 解析
- 输出单个 `code_inline` Token（nesting=0, tag="code", content=代码文本）
- 使用 backticks 缓存快速匹配

### 6. strikethrough（删除线）

匹配 `~~text~~`（gfm-like）或 `~text~`（strikethrough_single_tilde 选项）。

此规则在 tokenize 阶段不直接产出 s_open/s_close，而是：
1. 识别 `~` 序列
2. 通过 scanDelims 判断开闭性
3. 将标记文本作为普通文本暂存
4. 添加 Delimiter 到 delimiters 链表
5. ruler2 的 strikethrough postProcess 完成配对后产出 s_open/s_close

### 7. emphasis（强调）

匹配 `*em*`（斜体）、`**strong**`（粗体）、`_em_`（斜体）、`__strong__`（粗体）：

与 strikethrough 类似，采用双阶段处理：
1. tokenize 阶段识别 `*`/`_` 序列，scanDelims 判断开闭
2. 标记文本暂存，添加 Delimiter
3. ruler2 的 emphasis postProcess 按 CommonMark 规则配对
   - 单标记 → em_open/em_close（`<em>`）
   - 双标记 → strong_open/strong_close（`<strong>`）
   - 三标记 → strong+em 嵌套
   - `_` 的开闭判断还考虑前后是否空白/标点（单词内不触发）

### 8. link（链接）

支持三种链接形式：
- **内联链接**：`[text](url "title")`
- **引用链接**：`[text][label]` → 查找 env.references
- **隐式引用**：`[label][]` 或 `[label]`

解析流程：
1. 匹配 `[`，解析链接文本（可包含强调等行内元素）
2. 匹配 `]` 后的链接目标
3. 内联：解析 `(url "title")`
4. 引用：解析 `[label]` 并查 references
5. 输出 link_open（含href/title属性）→ 链接文本tokens → link_close
- linkLevel++/-- 防止嵌套链接

### 9. image（图片）

匹配 `![alt](url "title")` 或 `![alt][ref]`：

- 与 link 类似但以 `!` 开头
- 输出单个 `image` Token（nesting=0, tag="img"），attrs 含 src/alt/title
- alt 文本存储在 children 中

### 10. autolink（尖括号链接）

匹配 `<scheme://url>` 或 `<email@example.com>`：
- URL 必须有 scheme（http://、https://、mailto: 等）
- 邮箱自动添加 `mailto:` 前缀
- 输出 link_open/text/link_close

### 11. html_inline（行内HTML）

匹配行内 HTML 标签：
- 开标签：`<tag attr="val">`
- 闭标签：`</tag>`
- HTML注释：`<!-- comment -->`
- 处理指令：`<?...?>`
- CDATA：`<![CDATA[...]]>`

- html=False 时被转义为文本
- 输出单个 `html_inline` Token（nesting=0, content=原始HTML）

### 12. entity（HTML实体）

匹配 `&name;`（如 `&amp;`、`&lt;`、`&nbsp;`）或 `&#123;`/`&#xAB;`（数字实体）：
- 解码为对应 Unicode 字符
- 输出 text Token（content=解码后字符）
- 无效实体原样输出

## 后置链规则（ruler2，4条）

| 序号 | 规则名 | 职责 |
|------|--------|------|
| 1 | balance_pairs | 平衡链接/图片等成对标记的层级 |
| 2 | strikethrough | 处理 `~` 分隔符配对，产出 s_open/s_close |
| 3 | emphasis | 处理 `*`/`_` 分隔符配对，产出 em_open/em_close/strong_open/strong_close |
| 4 | fragments_join | 合并未配对分隔符标记回文本 |

### emphasis postProcess 配对算法

这是行内解析最复杂的部分，遵循 CommonMark 强调配对规则：

1. 遍历 delimiters 链表
2. 找到 open 的 delimiter，向后查找第一个可以 close 的同类型 delimiter
3. 匹配规则：
   - 相同 marker（`*` 配 `*`，`_` 配 `_`）
   - 中间 sum(lengths) 不是3的倍数或...（CommonMark "multiple of 3"规则）
   - `_` 还需满足两侧字符的空白/标点条件
4. 匹配成功则在对应位置插入 open/close Token
5. 标记 delimiters 之间的区域已处理

### fragments_join

未配对的分隔符标记被保留为普通文本，此规则确保这些文本片段正确合并。

## 终止字符与规则优先级

规则在 tokenize() 循环中按顺序尝试。在尝试规则之前，text 规则先累积连续非终止字符。如果某个位置的字符不是终止字符，text 规则会消费它，后续规则不会在该位置触发。

插件添加新行内语法时，需要：
1. 调用 `add_terminator_char()` 添加新的起始字符（如果默认终止字符不包含）
2. 用 `before()`/`after()` 在合适位置插入规则
3. 规则函数检查当前位置是否匹配，匹配则flush pending并输出Token

## 下一步

- [渲染器详解](10-renderer.md)
- [插件系统](12-plugin-system.md)
- [URL 与链接处理](13-url-and-link-processing.md)
