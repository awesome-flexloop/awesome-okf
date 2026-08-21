---
type: Concept
title: 嵌套内容增强系统
description: 利用指令体内嵌内容和definition_list语法，通过@before/@after/@replace/@skip四种classifier精确注入自定义文档
tags: [sphinx-argparse, nested-content, definition-list, @before, @after, @replace, @skip, content-injection]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 嵌套内容增强系统

sphinx-argparse 不仅能自动生成文档，还允许你通过指令体中的嵌套内容精确增强、修改或替换自动生成的描述。这种机制基于 RST 的 definition_list（定义列表）语法，提供了四种内容注入模式。

## 基础嵌套内容

指令体内不在 definition_list 中的普通 RST 内容，会被插入到 usage 代码块之后、参数列表之前：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   这是我的命令行工具。

   .. note::

      使用前请确保配置文件存在。

   .. warning::

      此命令会修改文件系统。
```

这些内容可以包含任何有效的 RST 标记：段落、注释、指令（note/warning等）、代码块等。

## Definition List 注入语法

使用 RST definition_list 语法可以精确控制特定参数、选项、子命令或参数组的文档内容。语法格式：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   前置普通内容...

   目标名称
       注入的内容，可以包含任意RST标记

   另一个目标 : @before
       使用classifier控制注入位置
```

目标名称可以是：
- **位置参数名**：如 `foo`、`path`
- **选项名**：选项之间用空格分隔（不是逗号），如 `--upgrade -u`、`--output -o`
- **子命令名**：如 `install`、`build`
- **参数组标题**：如 `Group 1`、`Required Arguments`、`Options`

> **重要**：多个选项名之间用**空格**分隔（如 `--upgrade -u`），这与通常RST选项列表中使用逗号不同。

## 四种 Classifier 注入模式

通过在目标名后添加 `: @classifier` 可以控制内容注入方式。支持四种 classifier：

### @after（默认）

内容追加到自动生成的帮助文本之后。这是默认行为，不指定 classifier 时即为此模式：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   install
       这里的内容会追加到 install 子命令的帮助文本之后。
```

### @before

内容插入到自动生成的帮助文本之前：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   --output : @before
       **重要**：输出目录必须有写入权限。
```

### @replace

完全替换自动生成的帮助文本：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   install : @replace
       init 子命令已弃用，请使用 ``mytool setup`` 代替。
```

这在需要重写自动提取的描述（如描述不够清晰或需要添加跨文档引用）时很有用。

### @skip

完全跳过该参数组或子命令的渲染：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   Advanced Arguments : @skip
       这个参数组不会出现在文档中。
```

`:@skip` 主要用于隐藏开发者选项或不打算公开的内部参数组。

## 嵌套增强

子命令内部的选项可以嵌套定义，层级与命令树对应：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   install
       install 子命令的额外说明。

       --upgrade -u
           install --upgrade 选项的额外说明。

       --force
           install --force 选项的额外说明。
```

嵌套层级没有限制，与子命令嵌套深度对应。这是通过 `map_nested_definitions()` 递归处理 subcontent 实现的。

## 跨参数组选项匹配

当一个选项出现在多个参数组中时（通常不会，但可能因自定义分组导致），直接使用选项名会匹配所有实例。要精确匹配特定参数组中的选项，可以通过嵌套在参数组定义内来定位：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   Named Arguments
       --verbose
           为Named Arguments组中的--verbose添加说明
```

## 实用示例

### 添加使用示例和注意事项

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   build
       构建项目的发布版本。

       .. code-block:: bash

          mytool build --release --output dist/

       --release
           启用发布模式构建。启用后会进行代码压缩和优化，构建时间更长。
```

### 隐藏开发者选项

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   Debug Options : @skip

   --debug : @skip
```

### 替换不够清晰的自动描述

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   --mode : @replace
       指定运行模式。可选值：

       - ``development``：开发模式，启用热重载和详细日志
       - ``production``：生产模式，优化性能
       - ``testing``：测试模式，使用内存数据库
```

### 添加交叉引用

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool

   init
       初始化新项目。参见 :doc:`project-setup` 了解项目结构详情。
```

## Markdown 模式的限制

当使用 `:markdown:` 标志时，嵌套内容按 Markdown 解析。由于 CommonMark 不支持 definition_list 语法，此时无法使用上述注入机制，只能添加普通前置内容。这是因为 `map_nested_definitions()` 依赖 docutils 的 definition_list 节点类型来识别目标-内容对。

如果需要内容增强，建议使用 RST 格式（默认）。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [指令选项全解](/concepts/03-directive-options.md)
- [Markdown 支持](/concepts/07-markdown-support.md)
- [内容增强完整示例](/examples/content-enhancement.md)
