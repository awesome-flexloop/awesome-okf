---
type: Concept
title: argparse 指令基础
description: 三种指定 parser 的方式（module+func、ref、filename+func）、passparser 模式、获取 parser 的机制
tags: [sphinx-argparse, directive, argparse-directive, module, ref, filename, passparser]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:38:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:38:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# argparse 指令基础

## 指令概述

`.. argparse::` 是 sphinx-argparse 提供的唯一 RST 指令。它是一个块级指令（`has_content = True`），可以包含嵌套内容用于注入自定义文档。指令执行时会：

1. 根据选项找到并获取 ArgumentParser 对象
2. 调用 `parse_parser()` 将 parser 转换为结构化字典数据
3. 如果指定了 `:path:`，导航到对应的子命令
4. 将字典数据渲染为 docutils 节点树
5. 处理嵌套内容并注入到适当位置
6. 注册命令到 Sphinx 域系统（用于交叉引用和索引）

## 指定 Parser 的三种方式

sphinx-argparse 支持三种方式告诉扩展去哪里找到 ArgumentParser 对象。

### 方式一：:module: + :func:（最常用）

这是最常见的方式，分别指定模块名和函数名：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
```

执行流程：
1. 使用 `importlib.import_module('mypackage.cli')` 导入模块
2. 使用 `getattr(mod, 'build_parser')` 获取函数
3. 导入过程中使用 `sphinx.ext.autodoc.mock` 机制模拟缺失的依赖（避免文档构建时因可选依赖缺失而失败）
4. 调用函数获取 parser（或传递 parser，见下文 passparser）

如果模块导入失败或函数不存在，会产生明确的错误信息，指出具体是模块导入错误还是属性缺失。

### 方式二：:ref:（简写形式）

`:ref:` 是 `:module:` + `:func:` 的简写，用点分路径组合两者：

```rst
.. argparse::
   :ref: mypackage.cli.build_parser
   :prog: mytool
```

内部实现会将最后一个点之后的部分作为函数名，前面的部分作为模块名。这等价于：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
```

### 方式三：:filename: + :func:（外部脚本）

当要文档化的 CLI 工具不是可导入的 Python 模块，而是一个独立的脚本文件时，使用 `:filename:` 选项：

```rst
.. argparse::
   :filename: ../scripts/mytool.py
   :func: build_parser
   :prog: mytool
```

执行流程：
1. 如果路径是相对路径，相对于 Sphinx 源码目录（`conf.py` 所在目录）解析
2. 使用 `open()` 打开文件
3. 使用 `compile()` + `exec()` 在临时命名空间中执行文件代码
4. 从执行后的命名空间中获取指定的函数

这种方式不会走 import 流程，因此不需要脚本所在目录在 Python 路径上。文件不存在时会抛出 FileNotFoundError，错误信息包含解析后的绝对路径。

> **注意**：`:filename:` 方式执行脚本文件，如果脚本在模块级别有副作用（如下载文件、创建目录等），这些副作用会在文档构建时发生。建议将 parser 构建逻辑封装在函数中，脚本入口使用 `if __name__ == '__main__':` 保护。

## passparser 模式

默认情况下，`:func:` 指定的函数应该**返回**一个 ArgumentParser 实例。但有些代码风格是创建一个空 parser 传给函数，让函数向其中添加参数：

```python
def build_parser(parser):
    """向传入的 parser 添加参数。"""
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('name', help='名称')
    # 注意：这个函数不返回 parser
```

这种情况下，使用 `:passparser:` 标志：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
   :passparser:
```

启用 `:passparser:` 后，扩展会创建一个空的 `ArgumentParser()`，然后调用 `func(parser)` 将其传入，最后使用这个被填充的 parser。

## 错误处理

指令在以下情况会产生错误：

- 未提供 `:module:+:func:`、`:ref:` 或 `:filename:+:func:` 中任何一种组合：报错提示需要指定这些选项
- 模块导入失败：错误信息包含模块名和原始 ImportError 信息
- 函数不存在：错误信息提示模块没有该属性，建议检查 module/func 值
- 文件不存在（filename方式）：错误信息包含原始路径和解析后的绝对路径
- 子命令路径导航失败：抛出 NavigationException，指示当前路径位置

## prog 选项

`:prog:` 选项用于设置工具在文档中的显示名称，它会覆盖 parser 的 `prog` 属性。这在文档中显示的命令名与实际可执行文件名不同时很有用：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: my-awesome-tool
```

`:prog:` 影响：
- usage 行中的程序名
- 子命令的完整命令路径（如 `my-awesome-tool init`）
- 交叉引用中的命令标识

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [指令选项全解](/concepts/03-directive-options.md)
- [子命令与路径导航](/concepts/05-nested-subcommands.md)
- [基础用法完整示例](/examples/basic-usage.md)（包含外部脚本文件文档化方法）
