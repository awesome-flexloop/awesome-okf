# sphinx-argparse

**sphinx-argparse** 是一个 Sphinx 扩展，自动从 Python `argparse.ArgumentParser` 对象生成命令行参考文档。它通过 `.. argparse::` 指令，将代码中定义的 CLI 参数、子命令、帮助文本等信息直接提取并渲染为格式良好的文档，确保文档与代码始终保持同步。

## 版本信息

- **版本**：0.6.1
- **Python 要求**：≥ 3.10
- **Sphinx 要求**：≥ 5.1.0
- **docutils 要求**：≥ 0.19
- **源码仓库**：[sphinx-doc/sphinx-argparse](https://github.com/sphinx-doc/sphinx-argparse)
- **官方文档**：[sphinx-argparse.readthedocs.io](https://sphinx-argparse.readthedocs.io/)

## 核心能力

- **自动文档生成**：直接从 argparse parser 对象提取参数、子命令、默认值、帮助文本
- **子命令支持**：递归渲染任意深度的子命令树，支持 `:path:` 导航到特定子命令
- **内容增强**：通过 definition_list 语法精确注入自定义说明、示例、警告（@before/@after/@replace/@skip）
- **Markdown 支持**：帮助文本和嵌套内容支持 Markdown 格式（需要 CommonMark 库）
- **交叉引用**：`:command:` 角色实现命令间的交叉链接
- **命令索引**：自动生成命令索引和分组命令索引
- **Man Page 输出**：支持生成标准 Unix man page 格式
- **并行构建安全**：支持 Sphinx 并行读写构建

## 文档结构

### 概念文档（Concepts）

按学习路径分为入门篇、核心篇、高级篇三个层次：

**入门篇**：
- [简介](concepts/00-introduction.md) — 功能概览、设计理念、安装方法
- [5分钟快速上手](concepts/01-getting-started.md) — Parser组织、基本用法、构建流程
- [argparse 指令基础](concepts/02-directive-basics.md) — 三种parser指定方式、passparser模式
- [指令选项全解](concepts/03-directive-options.md) — 17个选项的分类详解

**核心篇**：
- [Parser 数据提取模型](concepts/04-parser-data-model.md) — parse_parser输出结构、字段含义
- [子命令与路径导航](concepts/05-nested-subcommands.md) — :path:导航、多页面文档化策略
- [嵌套内容增强系统](concepts/06-nested-content-enhancement.md) — @before/@after/@replace/@skip注入模式
- [Markdown 支持](concepts/07-markdown-support.md) — :markdown:/:markdownhelp:、支持的语法、限制
- [Man page 输出格式](concepts/08-manpage-output.md) — :manpage:选项、SYNOPSIS/OPTIONS章节

**高级篇**：
- [Commands 域与交叉引用](concepts/09-domain-crossref.md) — :command:角色、命令注册、resolve_xref
- [命令索引生成](concepts/10-command-indices.md) — 简单索引/分组索引、临时文件桥接
- [conf.py 配置选项详解](concepts/11-configuration.md) — 所有sphinxarg_配置项说明

### 示例文档（Examples）

- [基础用法完整示例](examples/basic-usage.md) — 从零到完整CLI文档的全流程
- [多页面子命令文档化](examples/subcommand-docs.md) — 复杂CLI的多页面拆分方案
- [嵌套内容增强完整示例](examples/content-enhancement.md) — 四种注入模式的综合运用
- [Markdown 集成示例](examples/markdown-integration.md) — Markdown格式的帮助文本与嵌套内容
- [Man Page 与命令索引完整示例](examples/manpage-and-index.md) — man page生成与索引配置

### 信源登记（References）

- [sphinx-argparse 源码信源登记](references/sphinx-argparse-source.md) — 源码版本、核心模块、API结构

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
```
