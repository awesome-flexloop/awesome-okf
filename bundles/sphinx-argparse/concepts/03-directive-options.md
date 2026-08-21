---
type: Concept
title: 指令选项全解
description: argparse 指令的全部17个选项分类详解，包括基础指定、渲染控制、内容格式、索引分组四类
tags: [sphinx-argparse, directive-options, module, func, ref, filename, prog, path, nodefault, manpage, markdown, markdownhelp]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:38:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:38:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 指令选项全解

`.. argparse::` 指令支持 17 个选项，按功能可分为四类：Parser指定选项、渲染控制选项、内容格式选项、索引分组选项。

## Parser 指定选项

这组选项告诉扩展去哪里找到 ArgumentParser 对象。必须提供其中一种组合。

### :module:

- **类型**：字符串（unchanged）
- **说明**：包含 parser 构建函数的 Python 模块名
- **示例**：`:module: mypackage.cli`
- **必须与 `:func:` 配合使用**

### :func:

- **类型**：字符串（unchanged）
- **说明**：返回 ArgumentParser 实例（或接受 parser 参数，配合 `:passparser:`）的函数名
- **示例**：`:func: build_parser`
- **与 `:module:` 或 `:filename:` 配合使用**

### :ref:

- **类型**：字符串（unchanged）
- **说明**：`module.func` 格式的简写，等价于同时指定 `:module:` 和 `:func:`
- **示例**：`:ref: mypackage.cli.build_parser`

### :filename:

- **类型**：字符串（unchanged）
- **说明**：外部脚本文件路径，相对路径相对于 Sphinx 源码目录（`conf.py` 所在目录）
- **示例**：`:filename: ../scripts/mytool.py`
- **与 `:func:` 配合使用**
- **注意**：文件会被 `exec()` 执行，确保有 `if __name__ == '__main__':` 保护

### :passparser:

- **类型**：标志（flag，无值）
- **说明**：改变函数调用方式——创建一个空 ArgumentParser 传给函数，而不是调用函数获取返回值
- **使用场景**：当你的函数签名是 `def build_parser(parser):`（向传入的parser添加参数）而非 `def build_parser():`（返回parser）时使用

## 基础显示选项

### :prog:

- **类型**：字符串（unchanged）
- **说明**：覆盖 parser 的 `prog` 属性，设置工具在文档中显示的名称
- **示例**：`:prog: mytool`
- **影响范围**：usage 行、子命令完整路径名、交叉引用标识

### :path:

- **类型**：字符串（unchanged）
- **说明**：导航到指定子命令，只渲染该子命令及其子命令的文档，而非整个命令树
- **格式**：空格分隔的子命令路径
- **示例**：
  - `:path: install` — 只渲染 install 子命令
  - `:path: remote add` — 渲染嵌套子命令（如 git remote add）
- **详细说明**：参见[子命令与路径导航](/concepts/05-nested-subcommands.md)

## 渲染控制选项

### :nodefault:

- **类型**：标志（flag，无值）
- **说明**：隐藏所有选项的默认值显示
- **使用场景**：当默认值在描述文本中已说明，或默认值可能引起混淆时使用

### :nodefaultconst:

- **类型**：标志（flag，无值）
- **说明**：仅隐藏 `store_const`、`store_true`、`store_false` 类型参数的默认值
- **使用场景**：布尔标志通常不需要显示 "Default: False"，但其他选项仍需显示默认值
- **与 `:nodefault:` 的区别**：`:nodefault:` 隐藏所有默认值，`:nodefaultconst:` 只隐藏常量型动作的默认值

### :nosubcommands:

- **类型**：字符串（unchanged，实际作为标志使用）
- **说明**：不渲染子命令部分
- **使用场景**：只想展示顶层命令的参数，不需要子命令文档时使用

### :noepilog:

- **类型**：字符串（unchanged，实际作为标志使用）
- **说明**：不解析和渲染 parser 的 epilog（结尾文本）
- **使用场景**：epilog 包含无法被 RST/Markdown 正确解析的文本时使用

### :nodescription:

- **类型**：字符串（unchanged，实际作为标志使用）
- **说明**：不解析和渲染 parser 的 description（描述文本）
- **使用场景**：description 包含无法被正确解析的文本，或你想通过嵌套内容完全替换描述时使用

### :manpage:

- **类型**：字符串（unchanged）
- **说明**：生成标准 man page 格式的输出结构
- **生成章节**：SYNOPSIS、DESCRIPTION、OPTIONS、SUB-COMMANDS
- **详细说明**：参见[Man page 输出格式](/concepts/08-manpage-output.md)

### :color:

- **类型**：标志（flag，无值）
- **说明**：启用 ANSI 颜色输出（Python 3.14+ argparse 支持）
- **注意**：Python 3.14 之前的版本忽略此选项
- **默认行为**：默认禁用颜色，避免在文档中出现 ANSI 转义序列

## 内容格式选项

### :markdown:

- **类型**：标志（flag，无值）
- **说明**：指令体中的嵌套内容使用 Markdown 语法解析，而非默认的 reStructuredText
- **前置条件**：需要安装 CommonMark 依赖（`pip install sphinx-argparse[markdown]`）
- **注意**：启用此选项后，嵌套内容中不能使用 definition_list 语法进行内容增强
- **详细说明**：参见[Markdown 支持](/concepts/07-markdown-support.md)

### :markdownhelp:

- **类型**：标志（flag，无值）
- **说明**：argparse 的 program description 和 option help 字符串使用 Markdown 解析，而非默认的 RST
- **前置条件**：需要安装 CommonMark 依赖
- **与 `:markdown:` 的区别**：`:markdown:` 控制指令嵌套内容的格式，`:markdownhelp:` 控制 parser 中 help/description 字符串的格式
- **详细说明**：参见[Markdown 支持](/concepts/07-markdown-support.md)

## 索引分组选项

### :index-groups:

- **类型**：字符串（unchanged）
- **格式**：逗号分隔的分组名
- **说明**：将该命令归入指定的分组，用于 Commands by Group 索引
- **示例**：`:index-groups: 基础命令, 项目管理`
- **前置条件**：需要在 `conf.py` 中启用 `sphinxarg_build_commands_by_group_index = True`
- **详细说明**：参见[命令索引生成](/concepts/10-command-indices.md)

## 选项速查表

| 选项 | 类型 | 分类 | 必备 |
|------|------|------|------|
| `:module:` | str | Parser指定 | 三选一* |
| `:func:` | str | Parser指定 | 与module/filename配合 |
| `:ref:` | str | Parser指定 | 三选一* |
| `:filename:` | str | Parser指定 | 三选一* |
| `:prog:` | str | 显示 | 推荐 |
| `:path:` | str | 显示 | 否 |
| `:passparser:` | flag | Parser指定 | 否 |
| `:nodefault:` | flag | 渲染控制 | 否 |
| `:nodefaultconst:` | flag | 渲染控制 | 否 |
| `:nosubcommands:` | str | 渲染控制 | 否 |
| `:noepilog:` | str | 渲染控制 | 否 |
| `:nodescription:` | str | 渲染控制 | 否 |
| `:manpage:` | str | 渲染控制 | 否 |
| `:color:` | flag | 渲染控制 | 否 |
| `:markdown:` | flag | 内容格式 | 否 |
| `:markdownhelp:` | flag | 内容格式 | 否 |
| `:index-groups:` | str | 索引分组 | 否 |

\* 必须提供 `:module:+:func:`、`:ref:`、或 `:filename:+:func:` 三种组合之一。

## 相关概念

- [argparse 指令基础](/concepts/02-directive-basics.md)
- [子命令与路径导航](/concepts/05-nested-subcommands.md)
- [嵌套内容增强](/concepts/06-nested-content-enhancement.md)
- [Markdown 支持](/concepts/07-markdown-support.md)
- [Man page 输出格式](/concepts/08-manpage-output.md)
- [命令索引生成](/concepts/10-command-indices.md)
