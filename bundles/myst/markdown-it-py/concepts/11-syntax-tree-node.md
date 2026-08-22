---
type: Concept
title: SyntaxTreeNode 语法树
description: Python 端扩展的树状视图，将线性 Token 流转换为可遍历的树结构
tags:
- markdown-it-py
- tree
- syntax-tree
- node
- python-extension
difficulty: 高级
estimated_time: 15分钟
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

# SyntaxTreeNode 语法树

SyntaxTreeNode 是 markdown-it-py Python 端提供的树状视图，将线性 Token 流转换为嵌套的树结构。它不是解析核心的一部分（JS上游没有），但对需要树遍历的场景非常有用。

## 创建语法树

```python
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

md = MarkdownIt()
tokens = md.parse("# Hello **world**")
node = SyntaxTreeNode(tokens)
```

## 节点属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `token` | Token | 对应的源 Token（根节点为 None） |
| `children` | list[SyntaxTreeNode] | 子节点列表 |
| `parent` | SyntaxTreeNode\|None | 父节点 |
| `is_root` | bool | 是否为根节点 |
| `next_sibling` | SyntaxTreeNode\|None | 下一个兄弟节点 |
| `previous_sibling` | SyntaxTreeNode\|None | 上一个兄弟节点 |
| `source_lines` | tuple[int,int]\|None | 源码行范围 |

### 节点类型便捷属性

| 属性 | 说明 |
|------|------|
| `nesting` | 来自 token.nesting（-1/0/1） |
| `type` | 来自 token.type |
| `tag` | 来自 token.tag |
| `level` | 来自 token.level |
| `content` | 来自 token.content |
| `markup` | 来自 token.markup |
| `info` | 来自 token.info |
| `attrs` | 来自 token.attrs |
| `meta` | 来自 token.meta |
| `hidden` | 来自 token.hidden |
| `block` | 来自 token.block |

## 常用方法

### pretty(indent=2)→str

打印树结构的可读字符串：
```python
print(node.pretty())
# <root>
#   <heading level=1>
#     <inline>
#       <text>
#       <strong>
#         <text>
```

### walk()→Iterator[SyntaxTreeNode]

深度优先遍历所有节点（含自身）：
```python
for n in node.walk():
    if n.type == "text":
        print(n.content)
```

### walk_depth_first() / descendants

- `walk_depth_first(include_self=True)`：深度优先遍历
- `descendants` 属性：所有后代节点列表（不含自身）

### to_tokens()→list[Token]

将树转换回 Token 列表（含原始 token 引用）。

## 构建原理

`_set_children_from_tokens(tokens)` 方法从线性 Token 流构建树：
1. 维护一个节点栈
2. 遇到开标签（nesting=1）：创建节点，压栈
3. 遇到自闭合（nesting=0）：创建节点，添加为当前栈顶的子节点
4. 遇到闭标签（nesting=-1）：弹出栈顶
5. inline Token 的 children 递归构建子树

## 示例：提取所有标题

```python
md = MarkdownIt("gfm-like")
tokens = md.parse(md_text)
node = SyntaxTreeNode(tokens)

for n in node.walk():
    if n.type == "heading":
        # 从 inline 子节点获取标题文本
        inline = n.children[0] if n.children else None
        title = inline.children[0].content if inline and inline.children else ""
        level = int(n.tag[1])
        print(f"{'#' * level} {title}")
```

## 何时使用 Token 流，何时用 SyntaxTreeNode？

- **渲染输出**：直接遍历 Token 流，顺序输出 HTML（Renderer 就是这么做的）
- **插件中修改 Token**：直接操作 tokens 列表
- **需要树遍历**（提取标题树、分析文档结构）：使用 SyntaxTreeNode
- **需要理解 nesting/level 关系**：SyntaxTreeNode 的 parent/children 更直观
