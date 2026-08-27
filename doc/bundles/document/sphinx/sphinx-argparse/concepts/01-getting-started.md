---
type: Concept
title: 5分钟快速上手
description: 创建第一个 argparse 指令，从安装到在文档中自动生成命令行参考
tags: [sphinx-argparse, getting-started, quickstart, tutorial]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:37:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:37:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 5分钟快速上手

## 准备工作

假设你有一个使用 argparse 的 Python 命令行工具。首先确保已安装 sphinx-argparse 并在 `conf.py` 中启用扩展（参见[简介](00-introduction.md)的安装部分）。

## 第一步：组织你的 parser 代码

为了让 sphinx-argparse 能够提取 parser 信息，你需要提供一个返回 `argparse.ArgumentParser` 实例的函数。推荐的组织方式是将 parser 创建逻辑封装在一个函数中：

```python
# mypackage/cli.py
import argparse

def build_parser():
    """构建并返回命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog='mytool',
        description='我的命令行工具'
    )
    parser.add_argument(
        'name',
        help='要处理的名称'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='启用详细输出'
    )
    parser.add_argument(
        '--output', '-o',
        default='output.txt',
        help='输出文件路径（默认: %(default)s）'
    )

    # 添加子命令
    subparsers = parser.add_subparsers(dest='command')

    # init 子命令
    init_parser = subparsers.add_parser('init', help='初始化新项目')
    init_parser.add_argument(
        '--template',
        choices=['basic', 'advanced'],
        default='basic',
        help='项目模板类型'
    )

    # build 子命令
    build_parser = subparsers.add_parser('build', help='构建项目')
    build_parser.add_argument(
        '--release',
        action='store_true',
        help='发布模式构建'
    )

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    # 实际的命令行逻辑...
```

关键点：
1. `build_parser()` 函数返回配置好的 ArgumentParser 对象
2. 每个参数都有 `help` 文本——这些将自动出现在生成的文档中
3. 默认值可以使用 `%(default)s` 在 help 中引用，扩展会自动格式化

## 第二步：在 RST 文档中使用 argparse 指令

在你的 Sphinx 文档目录中创建一个 RST 文件（例如 `cli.rst`），添加 `.. argparse::` 指令：

```rst
命令行参考
==========

.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
```

这三个选项是基本用法所必需的：

- `:module:`：包含 parser 构建函数的 Python 模块名
- `:func:`：返回 ArgumentParser 实例的函数名
- `:prog:`：工具在文档中显示的名称（通常就是命令行调用时使用的名字）

## 第三步：构建文档

正常运行 Sphinx 构建命令：

```bash
sphinx-build -b html docs/ docs/_build/html
```

生成的页面将自动包含：
1. 用法摘要（usage 代码块）
2. 工具描述
3. 位置参数列表（Positional Arguments）
4. 选项列表（Named Arguments 或自定义参数组）
5. 子命令部分（Sub-commands），每个子命令递归显示其参数

## 使用 :ref: 简写

如果 `:module:` 和 `:func:` 的组合写起来太长，可以使用 `:ref:` 简写：

```rst
.. argparse::
   :ref: mypackage.cli.build_parser
   :prog: mytool
```

`:ref:` 接受 `module.func` 格式的点分路径，最后一部分是函数名，前面是模块路径。

## 在文档中添加自定义内容

你可以在指令体内添加额外的 RST 内容，这些内容会出现在自动生成的参数列表之前：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   这是我的命令行工具，它可以帮助你完成很多任务。

   .. note::

      在使用 ``mytool build`` 之前，请确保已运行 ``mytool init``。
```

## 下一步

- 了解所有[指令选项](03-directive-options.md)以掌握更多控制能力
- 学习如何[单独文档化子命令](05-nested-subcommands.md)（使用 `:path:` 选项）
- 探索[嵌套内容增强](06-nested-content-enhancement.md)来精确修改自动生成的描述
- 如需 Markdown 支持，参见[Markdown 集成](07-markdown-support.md)

## 相关概念

- [sphinx-argparse 简介](00-introduction.md)
- [argparse 指令基础](02-directive-basics.md)
- [指令选项全解](03-directive-options.md)
- [基础用法完整示例](../examples/basic-usage.md)
