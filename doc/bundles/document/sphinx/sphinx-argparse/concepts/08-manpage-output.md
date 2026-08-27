---
type: Concept
title: Man page 输出格式
description: ":manpage: 选项生成标准Unix手册页结构，SYNOPSIS/DESCRIPTION/OPTIONS/SUB-COMMANDS等章节，man page构建器使用方法"
tags: [sphinx-argparse, manpage, man-builder, ":manpage:", SYNOPSIS, troff]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:41:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:41:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# Man page 输出格式

sphinx-argparse 支持生成标准 Unix 手册页（man page）格式的输出，通过 `:manpage:` 选项启用。这使得自动生成的 CLI 文档可以直接用于 `man` 命令查看，也可以通过 Sphinx 的 manpage builder 输出为 troff 格式。

## 启用 Man Page 输出

在指令中添加 `:manpage:` 选项即可生成 man page 结构：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
   :manpage:
```

`:manpage:` 选项接受一个字符串值（目前该值未被特殊使用，存在即启用man page模式）。

## Man Page 章节结构

启用 `:manpage:` 后，输出的文档结构遵循标准 man page 格式，包含以下章节：

### SYNOPSIS（概要）

显示命令的基本用法，以 `literal_block`（代码块）形式展示 bare_usage：

```
mytool [-h] [--verbose] [--output OUTPUT] {init,build} ...
```

这一节对应 man page 中的 NAME 之后的 SYNOPSIS 部分。

### DESCRIPTION（描述）

显示 parser 的 description 文本。如果同时存在嵌套内容，会通过 `nested_parse_with_titles` 解析后追加到描述部分。

如果 parser 有 epilog 且未指定 `:noepilog:`，epilog 文本会追加到描述部分末尾。

使用 `:nodescription:` 可以跳过描述章节。

### OPTIONS（选项）

分为两个子节：

1. **Positional arguments**：位置参数列表，使用 `_format_positional_arguments()` 格式化
2. **各参数组**：遍历 action_groups，每组以 subtitle 显示组标题，使用 `_format_optional_arguments()` 格式化选项

选项列表中，非 suppressed 的默认值以 `=default` 格式显示在选项名后。

### SUB-COMMANDS（子命令）

如果不指定 `:nosubcommands:`，会生成 Sub-Commands 章节，使用 `_format_subcommands()` 格式化为 definition_list（定义列表），每个子命令显示 bare_usage 和帮助文本。

### DEBUG（调试）

如果设置了环境变量 `INCLUDE_DEBUG_SECTION`，会额外生成一个 Argparse + Sphinx Debugging 章节，以 JSON 格式输出完整的 parser_info 字典。这主要用于开发调试。

### 未实现章节

代码注释标记了以下 man page 标准章节但尚未实现：
- FILES
- SEE ALSO
- BUGS

NAME 章节由 docutils 的 manpage writer 自动生成，不在扩展控制范围内。

## 与默认输出的区别

| 特性 | 默认 HTML 输出 | Man page 输出 |
|------|---------------|--------------|
| 根节点 | 普通段落+section | section 带固定ID（synopsis-section等） |
| 用法显示 | literal_block（usage，含前缀） | literal_block（bare_usage，无前缀） |
| 位置参数 | 在action group中 | 独立的 Positional arguments 子节 |
| 选项格式 | option_list_item（option_group+description） | option_list_item（option带=default值） |
| 子命令 | 递归渲染完整子命令树 | definition_list（bare_usage+帮助文本） |
| 嵌套内容 | 在参数列表前 | 解析到DESCRIPTION section中 |
| ID生成 | make_id（Sphinx唯一ID） | 固定ID（synopsis-section等） |

## 配置 Sphinx Man Page 构建

要将生成的 man page 输出为 troff 格式文件（.1/.5等），需要在 `conf.py` 中配置 man_pages：

```python
# conf.py
extensions = ['sphinxarg.ext']

man_pages = [
    ('cli', 'mytool', 'My Tool Documentation', ['Author Name'], 1),
]
```

然后使用 man page builder 构建：

```bash
sphinx-build -b man docs/ docs/_build/man
```

生成的 `.1` 文件可以直接用 `man` 命令查看：

```bash
man docs/_build/man/mytool.1
```

## 相关选项

以下选项可以与 `:manpage:` 配合使用：

- `:nodescription:`：跳过 DESCRIPTION 章节
- `:noepilog:`：不在描述中包含 epilog 文本
- `:nosubcommands:`：跳过 SUB-COMMANDS 章节
- `:manpage:` 与 `:path:` 可以组合使用，为特定子命令生成 man page：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
   :path: init
   :manpage:
```

这会为 `mytool init` 子命令生成独立的 man page。

## 调试技巧

设置环境变量 `INCLUDE_DEBUG_SECTION` 可以在输出中看到完整的 parser 数据结构（JSON格式），这对于理解解析结果和排查问题很有帮助：

```bash
INCLUDE_DEBUG_SECTION=1 sphinx-build -b man docs/ docs/_build/man
```

## 相关概念

- [指令选项全解](03-directive-options.md)
- [Parser 数据提取模型](04-parser-data-model.md)
- [嵌套内容增强](06-nested-content-enhancement.md)
