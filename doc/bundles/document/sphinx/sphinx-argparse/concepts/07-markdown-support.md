---
type: Concept
title: Markdown 支持
description: ":markdown: 和 :markdownhelp: 两个独立标志的用法与区别，CommonMark 解析器实现、支持的Markdown语法、限制与注意事项"
tags: [sphinx-argparse, markdown, CommonMark, markdownhelp, markdown-support, parse_markdown_block]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# Markdown 支持

sphinx-argparse 提供两种独立的 Markdown 渲染能力，分别由两个标志选项控制：`:markdown:` 控制指令体嵌套内容的解析格式，`:markdownhelp:` 控制 argparse 帮助文本和描述的解析格式。Markdown 支持基于 CommonMark-py 库实现。

## 安装依赖

Markdown 支持需要 CommonMark 库。安装带 markdown 额外依赖的 sphinx-argparse：

```bash
pip install "sphinx-argparse[markdown]"
```

或者单独安装 CommonMark：

```bash
pip install CommonMark>=0.5.6
```

代码中同时兼容 `commonmark` 和 `CommonMark` 两种包名导入方式。

## :markdown: — 嵌套内容 Markdown

默认情况下，指令体中的嵌套内容按 reStructuredText 解析。添加 `:markdown:` 标志后，嵌套内容按 Markdown 解析：

```rst
.. argparse::
   :filename: ../test/sample.py
   :func: parser
   :prog: sample
   :markdown:

   # 这是 Markdown 标题

   这是一段 **粗体** 和 *斜体* 文本。

   [这是一个链接](http://example.com)

   ## 二级标题

   ```python
   # 这是代码块
   print("hello")
   ```
```

### Markdown 标题规则

使用 `:markdown:` 时，如果嵌套内容包含标题，**第一个标题必须是一级标题**（`#` 或 `====` 下划线式）。后续标题可以使用更高级别（`##`、`###` 等）。

这是因为 `nest_sections()` 函数从 level=1 开始递归嵌套 section，需要一个一级标题作为起始点。

### 硬换行限制

由于 Sphinx 在将内容传递给扩展之前会去除行尾空白，Markdown 的硬换行（行尾两个空格加换行）目前无法正确渲染。

## :markdownhelp: — 帮助文本 Markdown

默认情况下，argparse 的 `description`、`epilog` 和各选项的 `help` 字符串按 RST 解析。添加 `:markdownhelp:` 标志后，这些文本按 Markdown 解析：

```python
# cli.py
import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        description="""
### 使用示例

访问 [项目主页](http://example.com) 了解更多。
"""
    )
    parser.add_argument(
        'cmd',
        help='执行一个 `command`（内联代码）'
    )
    return parser
```

```rst
.. argparse::
   :module: cli
   :func: build_parser
   :prog: mytool
   :markdownhelp:
```

`:markdownhelp:` 和 `:markdown:` 是独立的——你可以单独使用其中一个，也可以同时使用：

- 只使用 `:markdown:`：嵌套内容是 Markdown，help 文本是 RST
- 只使用 `:markdownhelp:`：嵌套内容是 RST，help 文本是 Markdown
- 同时使用：两者都是 Markdown

## 支持的 Markdown 语法

sphinx-argparse 实现了一个精简的 CommonMark→docutils 转换器（`sphinxarg/markdown.py`），支持以下 Markdown 元素：

| Markdown 元素 | 状态 | docutils 节点 |
|---|---|---|
| 段落（paragraph） | ✅ | `nodes.paragraph` |
| 文本（text） | ✅ | `nodes.Text` |
| 软换行（softbreak） | ✅ | `nodes.Text('\n')` |
| 硬换行（hardbreak/linebreak） | ⚠️ | `nodes.Text('\n')`（受Sphinx行尾空白限制） |
| 链接（link） | ✅ | `nodes.reference`（refuri, 可选name） |
| 标题（heading） | ✅ | `nodes.title`（通过MDsection嵌套） |
| 斜体（emph） | ✅ | `nodes.emphasis` |
| 粗体（strong） | ✅ | `nodes.strong` |
| 行内代码（code） | ✅ | `nodes.literal`（支持Lexer语法高亮） |
| 代码块（code_block） | ✅ | `nodes.literal_block`（支持Lexer语法高亮） |
| HTML内联/块（html_inline/html_block） | ✅ | `nodes.raw(format='html')` |
| 引用块（block_quote） | ✅ | `nodes.block_quote` |
| 水平线（thematic_break） | ✅ | `nodes.transition` |
| 图片（image） | ✅ | `nodes.image`（uri, alt文本） |
| 无序列表（bullet list） | ✅ | `nodes.bullet_list` |
| 有序列表（ordered list） | ✅ | `nodes.enumerated_list` |
| 列表项（list item） | ✅ | `nodes.list_item` |
| 自定义section（MDsection） | ✅ | `nodes.section`（nest_sections手动构建） |

## 实现机制

Markdown 渲染分为三个步骤：

1. **CommonMark 解析**：`Parser().parse(text)` 将 Markdown 文本解析为 CommonMark AST（抽象语法树）
2. **Section 嵌套**：`nest_sections(block, level=1)` 手动将平铺的 AST 节点按标题层级嵌套为 section 结构（CommonMark 本身不处理 section 嵌套）
3. **节点转换**：`markdown(node)` 函数遍历 AST，按节点类型 `t` 分派到对应的处理函数（paragraph/text/link/heading等），递归转换为 docutils 节点

核心分发逻辑：

```python
def markdown(node):
    output = []
    cur = node.first_child
    while cur is not None:
        t = cur.t
        if t == 'paragraph':
            output.append(paragraph(cur))
        elif t == 'text':
            output.append(text(cur))
        elif t == 'link':
            output.append(reference(cur))
        # ... 其他类型
        cur = cur.nxt
    return output
```

未处理的节点类型会打印警告并调用 `cur.pretty()` 输出节点信息。

## 与 MyST-Parser 的区别

sphinx-argparse 内置的 Markdown 转换器是一个精简实现，功能远不如 MyST-Parser 等完整的 Markdown 解析器。它的设计目标是覆盖 argparse 帮助文本中常见的 Markdown 用法（粗体、斜体、链接、代码、列表），而非完整的 Markdown 规范实现。

如果你的文档主要使用 Markdown，建议：
1. 项目整体使用 MyST-Parser（`.md` 文件），但 `.. argparse::` 指令仍在 RST 文件中使用
2. 在 `.. argparse::` 指令中使用 `:markdownhelp:` 让帮助文本支持 Markdown 格式
3. 嵌套内容如果只是简单补充说明，使用默认 RST 格式可以获得更强大的内容增强能力

## 语法高亮

代码块和行内代码支持通过 docutils 的 Lexer 进行语法高亮：

```python
def literal(node):
    if node.info is not None:
        rendered = [
            node.inline(classes=_[0], text=_[1])
            for _ in Lexer(node.literal, node.info, tokennames='long')
        ]
```

这意味着 ```` ```python ```` 代码块会获得 Python 语法高亮，与 RST 的 `.. code-block:: python` 效果一致。

## Markdown 模式的限制

1. **不支持 definition_list 注入**：`:markdown:` 模式下无法使用 `@before/@after/@replace/@skip` 内容增强机制，因为 CommonMark 没有 definition_list 语法
2. **硬换行不可用**：行尾两个空格的硬换行因 Sphinx 预处理而失效
3. **alt 文本限制**：链接的 alt 文本（`[alt](url)` 中的 alt）无法在 docutils reference 节点中正确渲染
4. **不支持表格**：CommonMark-py 的基础方言不支持 GFM 表格
5. **标题级别限制**：嵌套内容第一个标题必须是一级标题

## 相关概念

- [嵌套内容增强系统](/concepts/06-nested-content-enhancement.md)
- [指令选项全解](/concepts/03-directive-options.md)
- [Markdown 集成示例](/examples/markdown-integration.md)
