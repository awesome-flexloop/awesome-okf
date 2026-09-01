---
type: Example
title: 基础用法完整示例
description: 从项目初始化到生成完整CLI文档的完整流程示例，包含parser定义、RST文档、conf.py配置
tags: [sphinx-argparse, example, basic-usage, getting-started, complete-example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:44:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:44:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 基础用法完整示例

本示例展示一个完整的 sphinx-argparse 使用流程：从定义 CLI parser 到生成 Sphinx 文档。

## 项目结构

```
myproject/
├── mypackage/
│   ├── __init__.py
│   └── cli.py          # CLI parser 定义
└── docs/
    ├── conf.py         # Sphinx 配置
    ├── index.rst       # 文档首页
    └── cli.rst         # CLI 文档页面
```

## 步骤 1：定义 Parser

在 `mypackage/cli.py` 中定义 CLI parser：

```python
"""CLI interface for mypackage."""
import argparse

def build_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog='mytool',
        description='一个示例命令行工具',
        epilog='使用 --help 查看各子命令的详细帮助'
    )
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='%(prog)s 1.0.0'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细输出'
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='配置文件路径，默认: %(default)s'
    )

    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    # init 子命令
    init_parser = subparsers.add_parser('init', help='初始化新项目')
    init_parser.add_argument(
        'path',
        help='项目目录路径'
    )
    init_parser.add_argument(
        '--template', '-t',
        choices=['basic', 'advanced', 'minimal'],
        default='basic',
        help='项目模板，可选: basic/advanced/minimal，默认: %(default)s'
    )

    # build 子命令
    build_parser = subparsers.add_parser('build', help='构建项目')
    build_parser.add_argument(
        '--output', '-o',
        type=str,
        default='dist',
        help='输出目录，默认: %(default)s'
    )
    build_parser.add_argument(
        '--release',
        action='store_true',
        help='启用发布模式构建'
    )

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    # ... 实现逻辑
```

**关键要点**：
- parser 定义在一个函数中（`build_parser()`），这样 `:func:` 选项可以调用它
- 函数必须接受0个参数（不使用 `:func:()` 传参方式）或通过 `passparser` 传入已有 parser
- `help` 文本中使用 `%(default)s` 等占位符，sphinx-argparse 会自动替换
- `prog` 参数明确设置程序名

## 步骤 2：配置 Sphinx

在 `docs/conf.py` 中启用扩展：

```python
import os
import sys
sys.path.insert(0, os.path.abspath('..'))  # 将项目根目录加入 Python 路径

project = 'My Tool'
extensions = [
    'sphinxarg.ext',  # 启用 sphinx-argparse
]
```

## 步骤 3：编写 RST 文档

最简单的用法——单页文档化整个 CLI：

```rst
.. docs/cli.rst

命令行参考
==========

.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
```

这会自动生成：
1. usage 代码块
2. description 文本
3. Named Arguments（--verbose、--config、--version）
4. Sub-commands（init、build）
5. 各子命令的参数和子子命令（递归）

## 步骤 4：构建文档

```bash
cd docs/
sphinx-build -b html . _build/html
```

打开 `_build/html/cli.html` 查看生成的文档。

## 更多控制

### 添加前言内容

在指令体内添加普通 RST 内容，会出现在 usage 和参数列表之间：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   本工具用于管理项目生命周期。以下是完整的命令参考。

   .. note::

      所有路径支持相对路径和绝对路径。
```

### 使用 ref 指定 Parser

如果 `build_parser()` 是 `__init__.py` 中的顶级函数：

```rst
.. argparse::
   :ref: mypackage.cli.build_parser
   :prog: mytool
```

### 文档化脚本文件

对于不打包为模块的独立脚本：

```rst
.. argparse::
   :filename: ../scripts/mytool.py
   :func: build_parser
   :prog: mytool
```

### 只显示特定选项组

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
   :path: build
```

这只显示 `build` 子命令的文档。

## 预期输出效果

生成的 HTML 页面包含：

1. **标题**：`mytool`（prog 值）
2. **Usage 代码块**：
   ```
   usage: mytool [-h] [--version] [--verbose] [--config CONFIG] {init,build} ...
   ```
3. **描述**："一个示例命令行工具"
4. **Named Arguments 表格**：
   - `-h, --help`：show help message
   - `--version, -V`：show version
   - `--verbose, -v`：启用详细输出
   - `--config CONFIG, -c CONFIG`：配置文件路径，默认: 'config.yaml'
5. **Sub-commands 章节**：
   - `init`：初始化新项目，含 `path` 位置参数和 `--template` 选项
   - `build`：构建项目，含 `--output` 和 `--release` 选项
6. **Epilog**："使用 --help 查看各子命令的详细帮助"

## 相关概念

- [5分钟快速上手](../concepts/01-getting-started.md)
- [argparse 指令基础](../concepts/02-directive-basics.md)
- [指令选项全解](../concepts/03-directive-options.md)
