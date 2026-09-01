---
type: Concept
title: rst-to-myst 项目介绍与安装
description: rst-to-myst 是将 reStructuredText 转换为 MyST Markdown 的 CLI 工具和 Python 库。
tags: [introduction, installation, rst, myst, markdown, conversion]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-init
    resource: /spec/facts.md
    title: rst-to-myst 事实清单
---

## 什么是 rst-to-myst

rst-to-myst 是 [Executable Books](https://executablebooks.org/) 项目开发的工具，用于将 [reStructuredText（RST）](https://docutils.sourceforge.io/rst.html) 格式的文档转换为 [MyST（Markedly Structured Text）](https://myst-parser.readthedocs.io/) Markdown 格式。

RST 是 Python 生态和 Sphinx 文档系统的传统标记语言，而 MyST 是一种结合了 CommonMark 简洁性和 RST 表达能力的现代 Markdown 扩展。rst-to-myst 为希望从 RST 迁移到 MyST 的项目提供了自动化转换能力。

该工具既可以作为命令行工具使用，也可以作为 Python 库集成到其他程序中。当前版本为 0.4.0。

## 核心能力

- **RST→MyST 转换**：将 RST 语法元素（标题、列表、链接、脚注、指令、角色等）转换为 MyST 等价语法
- **Sphinx 支持**：可加载 Sphinx 及其扩展，识别 Sphinx 特有指令和角色
- **指令映射**：通过 YAML 配置文件自定义指令转换规则
- **批量转换**：支持批量转换文件和目录
- **调试模式**：可输出 docutils AST 和 Markdown-It tokens 供调试
- **自动扩展推断**：转换后报告所需的 MyST 扩展列表

## 安装

### 前置条件

- Python 3.9 或更高版本

### 使用 pip 安装

```bash
pip install rst-to-myst
```

### 带 Sphinx 支持安装

如果需要转换 Sphinx 特有的指令和角色，需要安装 sphinx 额外依赖：

```bash
pip install "rst-to-myst[sphinx]"
```

## 核心依赖

| 依赖包 | 版本约束 | 作用 |
|--------|---------|------|
| docutils | >=0.17,<0.22 | RST 解析器，生成 AST |
| markdown-it-py | ~=2.0 | Markdown 解析引擎 |
| mdformat | ~=0.7.16 | Markdown 格式化输出 |
| mdformat-myst | ~=0.1.5 | MyST 语法格式化 |
| mdformat-deflist | ~=0.1.2 | 定义列表格式化 |
| click | >=7.1,<9 | CLI 框架 |
| pyyaml | - | YAML 配置处理 |
| sphinx | >=5,<7 | 可选，Sphinx 指令支持 |

## CLI 快速开始

安装后可以使用 `rst2myst` 命令：

### 单文件转换（输出到stdout）

```bash
rst2myst stream document.rst
```

### 从标准输入读取

```bash
cat document.rst | rst2myst stream -
```

### 批量转换文件（生成 .md 文件）

```bash
rst2myst convert docs/*.rst
```

### 查看可用指令

```bash
rst2myst directives list
rst2myst directives show image
```

### 调试：查看 AST 和 tokens

```bash
rst2myst ast document.rst    # 查看 docutils AST
rst2myst tokens document.rst  # 查看 Markdown-It tokens
```

## Python API 快速开始

```python
from rst_to_myst import rst_to_myst

output = rst_to_myst("*Hello* **world**!")
print(output.text)       # 输出 MyST Markdown 文本
print(output.extensions) # 输出所需 MyST 扩展集合
```

## 转换流程概览

转换过程分为三个阶段：

1. **RST 解析**：使用定制的 `LosslessRSTParser` 将 RST 解析为 docutils AST
2. **Token 生成**：`MarkdownItRenderer` 遍历 AST 生成 markdown-it token 流
3. **文本渲染**：使用 mdformat 渲染引擎将 tokens 格式化为 MyST Markdown 文本

## 相关概念

- [命令行工具详细用法](01-cli-usage.md)
- [Python API 使用](02-python-api.md)
- [三阶段转换流水线架构](03-conversion-pipeline.md)
