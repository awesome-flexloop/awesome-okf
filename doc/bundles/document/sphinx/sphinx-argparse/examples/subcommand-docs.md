---
type: Example
title: 多页面子命令文档化
description: 为复杂CLI工具拆分为多页面文档的完整方案，包含主页面、子命令页面、交叉引用和toctree组织
tags: [sphinx-argparse, example, subcommands, multi-page, toctree, ":path:", ":nosubcommands:"]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:44:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:44:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 多页面子命令文档化

当 CLI 工具包含多个子命令（甚至嵌套子命令）时，单页文档会变得非常长。本示例展示如何将文档拆分为多个页面，保持结构清晰。

## 项目场景

假设我们有一个类似 git 的工具 `devtool`，包含以下命令结构：

```
devtool
├── init           # 初始化项目
├── build          # 构建项目
│   └── --release  # 发布模式
├── deploy         # 部署（含嵌套子命令）
│   ├── dev        # 部署到开发环境
│   ├── staging    # 部署到预发布环境
│   └── prod       # 部署到生产环境
└── remote         # 远程管理（含嵌套子命令）
    ├── add        # 添加远程
    └── remove     # 移除远程
```

## 文档结构规划

```
docs/
├── conf.py
├── index.rst
└── cli/
    ├── index.rst        # CLI 总览（只显示顶层）
    ├── init.rst         # devtool init
    ├── build.rst        # devtool build
    ├── deploy.rst       # devtool deploy（含子命令总览）
    ├── deploy-dev.rst   # devtool deploy dev
    ├── deploy-staging.rst
    ├── deploy-prod.rst
    ├── remote.rst       # devtool remote
    ├── remote-add.rst
    └── remote-remove.rst
```

## conf.py 配置

```python
import os, sys
sys.path.insert(0, os.path.abspath('..'))

project = 'DevTool'
extensions = ['sphinxarg.ext']

# 显示完整子命令名
sphinxarg_full_subcommand_name = True
```

## 主页面（CLI 总览）

```rst
.. cli/index.rst

命令行参考
==========

``devtool`` 是项目管理命令行工具。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :nosubcommands:

   使用 ``devtool <command> --help`` 查看各命令的详细帮助。

子命令
------

.. toctree::
   :maxdepth: 1

   init
   build
   deploy/index
   remote/index
```

**关键**：使用 `:nosubcommands:` 不渲染子命令详情，只显示顶层参数和子命令列表概览。

## 简单子命令页面

### init.rst

```rst
.. cli/init.rst

devtool init
============

初始化新的开发项目，创建基础目录结构和配置文件。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: init

示例
----

在当前目录初始化项目::

   devtool init .

在指定目录初始化并使用 advanced 模板::

   devtool init ./myproject --template advanced
```

### build.rst

```rst
.. cli/build.rst

devtool build
=============

构建项目产物。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: build

示例
----

开发模式构建（默认）::

   devtool build

发布模式构建::

   devtool build --release -o dist/
```

## 含嵌套子命令的页面

### deploy/index.rst（子命令组总览）

```rst
.. cli/deploy/index.rst

devtool deploy
==============

部署项目到指定环境。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: deploy
   :nosubcommands:

   根据目标环境选择对应的子命令：

   - :doc:`dev` — 部署到开发环境
   - :doc:`staging` — 部署到预发布环境
   - :doc:`prod` — 部署到生产环境

.. toctree::
   :hidden:

   dev
   staging
   prod
```

### deploy-dev.rst（深层子命令）

```rst
.. cli/deploy-dev.rst

devtool deploy dev
==================

部署到开发环境。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: deploy dev

   开发环境部署会跳过代码压缩，启用热重载。
```

### deploy-staging.rst

```rst
.. cli/deploy-staging.rst

devtool deploy staging
======================

部署到预发布环境。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: deploy staging
```

### deploy-prod.rst

```rst
.. cli/deploy-prod.rst

devtool deploy prod
===================

部署到生产环境。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: deploy prod
```

### remote/index.rst

```rst
.. cli/remote/index.rst

devtool remote
==============

管理远程仓库配置。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: remote
   :nosubcommands:

.. toctree::
   :hidden:

   add
   remove
```

### remote-add.rst

```rst
.. cli/remote-add.rst

devtool remote add
==================

添加远程仓库。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: remote add
```

### remote-remove.rst

```rst
.. cli/remote-remove.rst

devtool remote remove
=====================

移除远程仓库。

.. argparse::
   :module: devtool.cli
   :func: build_parser
   :prog: devtool
   :path: remote remove
```

## 顶层 index.rst

```rst
.. index.rst

DevTool 文档
============

.. toctree::
   :maxdepth: 2

   cli/index
```

## 文档间交叉引用

在任意页面中，可以使用 `:command:` 角色引用其他命令：

```rst
使用 :command:`devtool init` 初始化项目后，运行 :command:`devtool build`
构建产物，最后通过 :command:`devtool deploy prod` 部署到生产环境。

参见 :doc:`cli/init` 了解初始化的详细参数。
```

## 最佳实践总结

1. **`:nosubcommands:` 在总览页使用**：避免子命令详情重复出现在总览和子页面
2. **`:path:` 指定子命令路径**：路径用空格分隔（如 `deploy dev`），与命令行语法一致
3. **独立子目录组织嵌套命令**：`deploy/` 和 `remote/` 使用子目录，内部有自己的 index.rst
4. **每个子命令页面补充示例**：自动生成的参数列表之外，添加常用使用示例
5. **`:hidden:` toctree**：嵌套子命令的 toctree 使用 `:hidden:`，避免侧边栏层级过深
6. **启用 `sphinxarg_full_subcommand_name`**：多页面模式下，页面标题显示完整命令名更清晰

## 相关概念

- [子命令与路径导航](../concepts/05-nested-subcommands.md)
- [Commands 域与交叉引用](../concepts/09-domain-crossref.md)
- [配置选项详解](../concepts/11-configuration.md)
- [内容增强完整示例](content-enhancement.md)
