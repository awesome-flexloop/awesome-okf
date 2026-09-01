---
type: Example
title: 基本 RST 到 MyST 转换
description: 使用 CLI 和 Python API 将简单 RST 文档转换为 MyST Markdown。
tags: [example, conversion, cli, python-api, basic-usage]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:58:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-cli
    resource: /references/source-cli.md
    title: rst-to-myst CLI 命令行接口
---

## CLI 流式转换

创建一个简单的 RST 文件 `intro.rst`：

```rst
=====
标题
=====

这是一个*强调*和**加粗**的段落，还包含 `行内代码`。

- 列表项1
- 列表项2
- 列表项3

1. 有序列表1
#. 有序列表2（自动编号）

`链接文本 <https://example.com>`_

.. note::

   这是一个注意指令。
```

使用 stream 子命令转换并查看输出：

```bash
rst2myst stream intro.rst
```

输出：

````markdown
# 标题

这是一个*强调*和**加粗**的段落，还包含 `行内代码`。

- 列表项1
- 列表项2
- 列表项3

1. 有序列表1
2. 有序列表2（自动编号）

[链接文本](https://example.com)

```{note}
这是一个注意指令。
```
````

## 批量文件转换

批量转换 `docs/` 目录下所有 RST 文件为 Markdown：

```bash
# 预览（不写入文件）
rst2myst convert --dry-run docs/

# 执行转换，生成 .md 文件
rst2myst convert docs/

# 转换并删除原 .rst 文件
rst2myst convert --replace-files docs/
```

每个 `file.rst` 会在同目录生成 `file.md`。转换完成后注意查看输出的 extensions 列表，在 MyST 配置中启用所需扩展：

```
CONVERTED (extensions: ['colon_fence', 'dollarmath'])
```

## Python API 单文件转换

```python
from rst_to_myst import rst_to_myst

rst_text = """
Hello World
===========

This is *emphasized* text.

.. warning::

   Be careful!
"""

output = rst_to_myst(rst_text, use_sphinx=False)
print(output.text)
print("Required extensions:", output.extensions)
```

输出：

```markdown
# Hello World

This is *emphasized* text.

```{warning}
Be careful!
```

Required extensions: set()
```

## 调试转换问题

如果转换结果不符合预期，分阶段调试：

```bash
# 查看 docutils AST
rst2myst ast problem.rst

# 查看 markdown-it tokens
rst2myst tokens problem.rst
```

对比 AST 和 tokens 输出可以定位问题发生在解析阶段还是渲染阶段。

## 从标准输入转换

```bash
echo "**Bold text**" | rst2myst stream -
```

## 相关概念

- [命令行工具详细用法](../concepts/01-cli-usage.md)
- [Python API 使用指南](../concepts/02-python-api.md)
- [三阶段转换流水线架构](../concepts/03-conversion-pipeline.md)
