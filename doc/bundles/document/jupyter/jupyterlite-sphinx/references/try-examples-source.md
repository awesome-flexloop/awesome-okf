---
type: Reference
title: _try_examples.py 模块源码索引
description: doctest 到 Jupyter Notebook 转换管道的源码索引，包含解析函数和正则表达式
tags: [source, try-examples, doctest, notebook-conversion]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: source-try-examples
    resource: /references/try-examples-source.md
    title: _try_examples.py source
---

## 源码文件位置

- **模块**：`jupyterlite_sphinx/_try_examples.py`
- **功能**：将 doctest 格式的 Examples 段落解析转换为 Jupyter Notebook JSON

## 公共函数

| 函数 | 行号 | 签名 | 说明 |
|------|------|------|------|
| `examples_to_notebook` | 7-124 | `(input_lines, *, warning_text=None) -> dict` | 解析 doctest 行列表，返回 notebook JSON |
| `insert_try_examples_directive` | 334-416 | `(lines, **options) -> list[str]` | 在 docstring lines 中自动插入 try_examples 指令 |

## 内部函数

| 函数 | 行号 | 说明 |
|------|------|------|
| `_append_code_cell_and_clear_lines` | 127-141 | 创建代码单元格并附加输出，清空行列表 |
| `_append_markdown_cell_and_clear_lines` | 144-152 | 创建 Markdown 单元格（经过LaTeX/literal/链接处理），清空行列表 |
| `_convert_sphinx_link` | 159-162 | 正则替换回调：将 Sphinx 链接转为 Markdown 链接 |
| `_convert_links` | 165-171 | 将 `` `text <url>`_ `` 转为 `[text](url)` |
| `_strip_ref_identifiers` | 174-183 | 将 `[R...-n]_` 替换为 `[n]` |
| `_process_latex` | 186-225 | 处理 `:math:` 和 `.. math::` LaTeX 语法 |
| `_process_literal_blocks` | 228-269 | 将 RST `::` literal block 转为 Markdown 代码围栏 |

## 编译正则表达式

| 变量名 | 行号 | 正则模式 | 用途 |
|--------|------|---------|------|
| `_ref_identifier_pattern` | 155 | `r"\[R[a-f0-9]+-(?P<ref_num>\d+)\]_"` | 匹配 Sphinx 引用标识符 |
| `_link_pattern` | 156 | `` r"`(?P<link_text>[^`<]+)<(?P<url>[^`>]+)>`_" `` | 匹配 Sphinx 风格链接 |
| `_examples_start_pattern` | 284 | `r".. (rubric\|admonition):: Examples"` | 匹配 Examples 节标题 |
| `_next_section_pattern` | 331 | 组合所有 `_next_section_headers` | 匹配下一节标题（节结束标记） |

## examples_to_notebook 解析规则

解析过程逐行处理 input_lines，维护四个状态变量：

| 状态变量 | 初始值 | 用途 |
|---------|--------|------|
| `code_lines` | `[]` | 累积当前代码块的代码行 |
| `md_lines` | `[]` | 累积当前 Markdown 文本行 |
| `output_lines` | `[]` | 累积当前代码块的输出行 |
| `inside_multiline_code_block` | `False` | 是否处于多行代码块（`...` 续行）中 |

**行类型判定规则：**

| 行特征 | 处理方式 |
|--------|---------|
| 以 `>>>` 开头 | 代码行：去除 `>>> ` 前缀加入 code_lines；如有待处理 output_lines 则先闭合上一个代码单元格；如有待处理 md_lines 则先闭合 Markdown 单元格 |
| 以 `...` 开头且 code_lines 非空 | 多行续行：去除 `... ` 前缀加入 code_lines，标记 inside_multiline_code_block=True |
| 空行且 code_lines 非空 | 代码块结束：调用 _append_code_cell_and_clear_lines |
| 非空非前缀行且 code_lines 非空 | 输出行：加入 output_lines |
| `.. plot::` 或 `.. only::` 开头 | 进入忽略模式，跳过该指令及其缩进行 |
| 其他情况 | Markdown 文本行：加入 md_lines |

**生成的 Notebook metadata：**

```python
{
  "kernelspec": {"display_name": "Python", "language": "python", "name": "python"},
  "language_info": {"name": "python"}
}
```

## insert_try_examples_directive 注入逻辑

1. 搜索 `_examples_start_pattern` 定位 Examples 节起始行
2. 跳过空行找到首个内容行
3. 检查是否存在 `.. disable_try_examples` 注释（禁用标记）
4. 检查是否已有 `.. try_examples::` 指令（避免重复注入）
5. 使用 `_next_section_pattern` 定位节结束位置
6. 在内容前插入 `.. try_examples::` 指令和选项，将原内容缩进 4 空格

**被忽略的指令（不转换为 notebook 内容）：**
- `.. plot::`
- `.. only::`

## Markdown 后处理管线

Markdown 单元格文本在写入 notebook 前依次经过四个处理函数：

1. `_process_latex`：`:math:`...`` → `$...$`；`.. math::` 缩进行 → `$$ ... $$`
2. `_process_literal_blocks`：`::` + 缩进行 → ```` ``` ```` 围栏代码块
3. `_strip_ref_identifiers`：`[R<hash>-<n>]_` → `[n]`
4. `_convert_links`：`` `text <url>`_ `` → `[text](url)`

## 相关概念

- [try_examples 指令](/concepts/08-try-examples-directive.md)
- [TryExamples 内部机制](/concepts/13-try-examples-internals.md)
- [核心模块源码](/references/main-source.md)
