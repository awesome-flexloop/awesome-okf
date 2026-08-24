---
type: Example
title: 嵌套内容增强完整示例
description: 综合运用@before/@after/@replace/@skip四种内容注入模式，添加说明、示例、警告、交叉引用，覆盖参数/子命令/参数组各层级
tags: [sphinx-argparse, example, content-enhancement, "@before", "@after", "@replace", "@skip", definition-list]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 嵌套内容增强完整示例

本示例展示如何利用嵌套内容增强系统，为自动生成的 CLI 文档添加丰富的补充说明、使用示例、警告和交叉引用。

## Parser 定义

假设我们有以下 CLI parser：

```python
# dbcli/cli.py
import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        prog='dbcli',
        description='数据库命令行工具'
    )
    parser.add_argument('--config', '-c', default='~/.dbcli.yaml',
                        help='配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='启用详细日志')

    subparsers = parser.add_subparsers(dest='command')

    # migrate 子命令
    migrate = subparsers.add_parser('migrate', help='执行数据库迁移')
    migrate.add_argument('--dry-run', action='store_true',
                         help='预览迁移不执行')
    migrate.add_argument('--down', action='store_true',
                         help='回滚迁移')
    migrate.add_argument('--steps', type=int, default=1,
                         help='迁移步数')

    # query 子命令
    query = subparsers.add_parser('query', help='执行SQL查询')
    query.add_argument('sql', help='SQL语句')
    query.add_argument('--format', '-f',
                       choices=['table', 'json', 'csv', 'raw'],
                       default='table',
                       help='输出格式')
    query.add_argument('--limit', type=int, default=100,
                       help='结果行数限制')

    return parser
```

## 基础增强：添加前言和说明

最简单的用法——添加普通 RST 内容作为前言：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   dbcli 是一个轻量级数据库管理工具，支持迁移、查询等常用操作。

   .. note::

      本工具需要 Python 3.10 及以上版本。

   .. warning::

      迁移操作可能导致数据丢失，建议在执行前创建备份。
```

## 使用 @after 追加说明（默认行为）

不指定 classifier 时，内容追加到自动生成的帮助文本之后：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   migrate
       迁移命令按照版本号顺序依次执行 SQL 文件。

       .. code-block:: bash

          # 执行所有待处理迁移
          dbcli migrate

          # 预览将执行的迁移
          dbcli migrate --dry-run

       --dry-run
           预览模式下会输出每个迁移步骤的 SQL，但不会实际执行。
           建议在生产环境执行迁移前先用 --dry-run 确认。

       --steps
           指定要执行的迁移步数。

           .. code-block:: bash

              # 只执行前2个迁移
              dbcli migrate --steps 2

              # 回滚最近3个迁移
              dbcli migrate --down --steps 3
```

**要点**：
- 子命令名 `migrate` 作为 definition term
- 缩进内容追加到 migrate 的帮助文本之后
- 子命令内部的选项（`--dry-run`、`--steps`）嵌套在子命令定义内
- 内容可以包含任意 RST 标记（code-block、note 等）

## 使用 @before 插入前置说明

在自动生成的帮助文本**之前**插入内容：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   --config : @before
       **重要**：首次使用前，请确保配置文件包含正确的数据库连接信息。
       参见 :doc:`configuration` 了解配置文件格式。
```

`:@before` 在需要强调注意事项（而帮助文本本身是常规说明）时特别有用。

## 使用 @replace 替换自动描述

当自动提取的帮助文本不够清晰、需要重写时使用 `@replace`：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   query
       执行 SQL 查询并返回结果。

       .. code-block:: bash

          dbcli query "SELECT * FROM users LIMIT 10"

       sql : @replace
           要执行的 SQL 查询语句。支持 SELECT、INSERT、UPDATE、DELETE。

           .. warning::

              DDL 语句（CREATE/ALTER/DROP）会直接修改数据库结构，
              请谨慎使用。

       --format -f : @replace
           查询结果输出格式：

           - ``table``：格式化表格（默认），适合终端查看
           - ``json``：JSON 格式，适合程序处理
           - ``csv``：CSV 格式，适合导入 Excel
           - ``raw``：原始输出，不做格式化

           .. code-block:: bash

              dbcli query "SELECT * FROM users" --format json
```

**要点**：
- `sql`（位置参数）可以直接作为目标名
- `--format -f`：多个选项名用**空格**分隔（不是逗号）
- `@replace` 完全替换自动生成的帮助文本，因此新描述需要完整说明参数用途

## 使用 @skip 隐藏内容

隐藏不打算公开的开发者选项或内部参数组：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   --verbose : @skip
       此选项为开发者调试用，不在最终文档中显示。
```

也可以跳过整个参数组（如果 parser 中有自定义组）：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   Debug Options : @skip
```

子命令也可以被跳过：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   debug : @skip
```

## 选项别名的指定方式

当选项有短选项和长选项时，在 definition term 中用空格分隔列出：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   --config -c
       配置文件支持 YAML 和 JSON 格式，根据文件扩展名自动识别。

   --format -f
       参见 :ref:`output-formats` 了解各格式的详细说明。

   --dry-run
       别名 ``--dryrun``（如果在parser中添加了的话）也可使用。
```

## 跨参数组选项

如果一个选项出现在特定参数组中，需要通过嵌套在组内来定位：

```rst
.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   Named Arguments
       --verbose -v
           详细模式会输出 SQL 语句、连接信息等调试内容。
           可与 ``--config`` 指定的日志级别配置结合使用。
```

## 完整增强示例

以下是一个综合使用所有技巧的完整示例：

```rst
数据库命令行工具
================

.. argparse::
   :module: dbcli.cli
   :func: build_parser
   :prog: dbcli

   dbcli 是一个轻量级数据库管理工具，支持迁移、查询等常用操作。

   .. note::

      本工具需要 Python 3.10 及以上版本。安装方式::

         pip install dbcli

   .. warning::

      迁移操作可能导致数据丢失，建议在执行前创建备份::

         dbcli query "SELECT * INTO backup_users FROM users"

   --config -c : @before
       **重要**：首次使用前，请确保配置文件包含正确的数据库连接信息。
       参见 :doc:`configuration` 了解配置文件格式。

   migrate
       迁移命令按照 ``migrations/`` 目录中的版本号顺序依次执行 SQL 文件。
       迁移文件命名格式：``V{version}__{description}.sql``。

       .. code-block:: bash

          # 执行所有待处理迁移
          dbcli migrate

          # 预览将执行的迁移（不实际执行）
          dbcli migrate --dry-run

          # 回滚最近3个迁移
          dbcli migrate --down --steps 3

       --dry-run
           预览模式下会输出每个迁移步骤的 SQL，但不会对数据库做任何修改。
           **强烈建议**在生产环境执行迁移前先用 ``--dry-run`` 确认。

       --down
           默认情况下迁移按升序执行（up 方向）。使用 ``--down`` 执行回滚。
           回滚需要对应的 down 迁移文件（``U{version}__{description}.sql``）。

       --steps
           指定要执行的迁移步数。值必须是正整数。

   query
       执行 SQL 查询并返回结果。支持所有标准 SQL 语句。

       .. code-block:: bash

          # 查询所有用户
          dbcli query "SELECT * FROM users"

          # 以JSON格式输出
          dbcli query "SELECT * FROM users" --format json

          # 插入数据
          dbcli query "INSERT INTO users (name) VALUES ('Alice')"

       sql : @replace
           要执行的 SQL 查询语句。

           .. warning::

              未加 LIMIT 的大表查询可能返回大量数据，建议始终使用
              ``--limit`` 选项或在 SQL 中添加 LIMIT 子句。

       --format -f : @replace
           查询结果输出格式：

           - ``table``：格式化表格（默认），适合终端查看
           - ``json``：JSON 格式，适合脚本处理
           - ``csv``：CSV 格式，适合导入电子表格
           - ``raw``：原始制表符分隔输出

       --limit
           结果最大返回行数。默认 100 行，设为 0 表示不限制。
```

## 常见错误

1. **使用逗号分隔选项名**：`--format, -f` 是错误的，应使用 `--format -f`（空格分隔）
2. **Markdown 模式下使用注入**：`:markdown:` 模式不支持 definition_list 注入
3. **嵌套层级错误**：子命令的选项必须缩进嵌套在子命令定义内
4. **目标名拼写错误**：目标名必须与 argparse 中的选项名/子命令名完全匹配（含短横线）

## 相关概念

- [嵌套内容增强系统](/concepts/06-nested-content-enhancement.md)
- [Markdown 支持](/concepts/07-markdown-support.md)
- [基础用法完整示例](/examples/basic-usage.md)
