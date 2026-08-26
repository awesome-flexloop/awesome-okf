# 概念文档

sphinx-argparse 的核心概念按学习路径排列，建议按顺序阅读。

## 入门篇

| 文档 | 内容 |
|------|------|
| [00 - 简介](00-introduction.md) | 功能概览、设计理念、工作原理、安装方法 |
| [01 - 5分钟快速上手](01-getting-started.md) | Parser代码组织、指令基本用法、Sphinx构建流程 |
| [02 - argparse 指令基础](02-directive-basics.md) | module+func/ref/filename+func三种指定方式、passparser模式 |
| [03 - 指令选项全解](03-directive-options.md) | 17个选项按四类（Parser指定/渲染控制/内容格式/索引分组）详解 |

## 核心篇

| 文档 | 内容 |
|------|------|
| [04 - Parser 数据提取模型](04-parser-data-model.md) | parse_parser()输出的嵌套字典结构、字段含义、默认值处理 |
| [05 - 子命令与路径导航](05-nested-subcommands.md) | :path:选项、parser_navigate递归导航、多页面文档化策略 |
| [06 - 嵌套内容增强系统](06-nested-content-enhancement.md) | definition_list语法、@before/@after/@replace/@skip四种注入模式 |
| [07 - Markdown 支持](07-markdown-support.md) | :markdown:/:markdownhelp:标志、CommonMark解析、支持的语法与限制 |
| [08 - Man page 输出格式](08-manpage-output.md) | :manpage:选项、SYNOPSIS/DESCRIPTION/OPTIONS/SUB-COMMANDS章节结构 |

## 高级篇

| 文档 | 内容 |
|------|------|
| [09 - Commands 域与交叉引用](09-domain-crossref.md) | ArgParseDomain自定义域、:command:角色、命令注册与resolve_xref解析 |
| [10 - 命令索引生成](10-command-indices.md) | CommandsIndex/CommandsByGroupIndex、临时文件桥接机制、in_toctree配置 |
| [11 - conf.py 配置选项详解](11-configuration.md) | 全部sphinxarg_配置项、四种典型配置方案 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-directive-basics
03-directive-options
04-parser-data-model
05-nested-subcommands
06-nested-content-enhancement
07-markdown-support
08-manpage-output
09-domain-crossref
10-command-indices
11-configuration
```
