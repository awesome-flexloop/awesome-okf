---
type: Concept
title: 核心规则深入
description: normalize换行规范化、block调度、inline调度、linkify/replacements/smartquotes/text_join核心规则详解
tags:
- markdown-it-py
- core-rules
- normalize
- linkify
- replacements
- smartquotes
difficulty: 高级
estimated_time: 15分钟
prerequisites:
- 04-parsing-pipeline
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

# 核心规则深入

Core 链的7条规则负责全局编排。本文深入每条规则的实现细节。

## 1. normalize（换行规范化）

normalize 规则执行两项工作：

1. **换行符统一**：将 `\r\n` 和 `\r` 替换为 `\n`，确保后续规则只需处理 Unix 换行
2. **NULL 替换**：将 `\0`（NULL字符）替换为 `\uFFFD`（替换字符），防止注入攻击

```python
# normalize 核心逻辑
str = str.replace("\r\n", "\n").replace("\r", "\n")
str = str.replace("\0", "\uFFFD")
state.src = str
```

## 2. block（块级调度）

block 规则根据 `state.inlineMode` 分流：

**正常模式**（inlineMode=False）：
1. 从 startLine=0 开始
2. 调用 `md.block.parse(state, startLine, state.lineMax)`
3. ParserBlock.tokenize() 逐行执行块级规则
4. 块级规则产出块级 tokens（含 inline 占位符）

**行内直通模式**（inlineMode=True）：
1. 创建单个 `inline` Token
2. content = 整个 src
3. children 暂为 None
4. 由后续 inline 规则填充

## 3. inline（行内调度）

inline 规则遍历已有的 tokens 列表，对每个 `type="inline"` 的 Token：

1. 设置 state.src = token.content
2. 设置 state.md = md
3. 设置 state.env = env
4. state.tokens = token.children = []
5. 调用 `md.inline.parse(state)` 填充 children
6. 解析后如果 children 为空或最后一个不是 text，push 一个空 text Token

```python
# inline 规则核心逻辑
for token in state.tokens:
    if token.type != "inline":
        continue
    # 创建 StateInline，解析 token.content
    # 结果写入 token.children
```

## 4. linkify（自动链接）

仅在 `options["linkify"]` 为 True 时执行（需要安装 linkify-it-py）：

1. 遍历 tokens，对每个 inline token 的 children 处理
2. 遍历 children 中的 text tokens
3. 用 linkify-it 检测文本中的 URL
4. 将匹配的 URL 拆分为 text + link_open/text/link_close + text

## 5. replacements（排版替换）

仅在 `options["typographer"]` 为 True 时执行，处理：

- `(c) (C)` → `©`（版权符号）
- `(r) (R)` → `®`（注册商标）
- `(tm) (TM)` → `™`（商标）
- `--` → `–`（en dash，视上下文）
- `---` → `—`（em dash）
- `...` → `…`（省略号）
- `+-` → `±`（正负号）
- `(p) (P)` → `§`（段落符号）

替换只在 text tokens 上执行，不影响代码块和 HTML。

## 6. smartquotes（智能引号）

仅在 `options["typographer"]` 为 True 时执行，将直引号替换为弯引号：

- `"` → `"` / `"`（左右双引号）
- `'` → `'` / `'`（左右单引号）

替换逻辑追踪引号的开/闭状态，根据相邻字符判断是左引号还是右引号。引号字符由 `options["quotes"]` 控制，默认是中文弯引号。

## 7. text_join（文本合并）

遍历所有 tokens，将相邻的 `type="text"` tokens 合并为一个：

```python
# text_join 核心逻辑
for token in tokens:
    if token.type == "inline":
        # 递归合并 children 中的相邻text
        children = token.children
        # 合并相邻 text tokens 的 content
```

这减少了 token 数量，提高渲染效率。

## 规则链扩展点

在 Core 链中插入规则是全局修改解析行为的方式：

```python
# 在所有解析完成后添加自定义处理
def my_postprocess(state):
    for token in state.tokens:
        if token.type == "heading_open":
            token.attrSet("data-processed", "true")

md.core.ruler.push("my_postprocess", my_postprocess)
```
