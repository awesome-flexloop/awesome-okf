---
type: Example
title: Man Page 与命令索引完整示例
description: 从man page生成到命令索引配置的完整流程，包含:manpage:输出、conf.py索引配置、分组索引使用
tags: [sphinx-argparse, example, manpage, index, commands-index, by-group, man-builder]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:47:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# Man Page 与命令索引完整示例

本示例展示如何生成 Unix man page 格式的 CLI 文档，以及如何配置自动命令索引。

## 一、生成 Man Page

### Parser 定义

```python
# gitlike/cli.py
import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        prog='gitlike',
        description='A Git-like version control system CLI tool.',
        epilog='For more information, see https://gitlike.example.com/docs'
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--repo', '-C', default='.',
                        help='Run as if gitlike was started in <path>')

    subparsers = parser.add_subparsers(dest='command')

    # init
    init_p = subparsers.add_parser('init', help='Create a new repository')
    init_p.add_argument('path', nargs='?', default='.',
                        help='Directory to initialize')
    init_p.add_argument('--bare', action='store_true',
                        help='Create a bare repository')

    # add
    add_p = subparsers.add_parser('add', help='Add file contents to the index')
    add_p.add_argument('files', nargs='+', help='Files to add')
    add_p.add_argument('--all', '-A', action='store_true',
                       help='Add all modified files')

    # commit
    commit_p = subparsers.add_parser('commit', help='Record changes to the repository')
    commit_p.add_argument('--message', '-m', required=True,
                          help='Commit message')
    commit_p.add_argument('--amend', action='store_true',
                          help='Amend the previous commit')

    # log
    log_p = subparsers.add_parser('log', help='Show commit logs')
    log_p.add_argument('--oneline', action='store_true',
                       help='One commit per line')
    log_p.add_argument('-n', type=int, default=None,
                       help='Number of commits to show')

    return parser
```

### RST 文档（Man Page 格式）

```rst
.. cli/gitlike.1.rst

#######
gitlike
#######

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :manpage:
```

**注意**：使用 `:manpage:` 选项后，输出结构遵循标准 man page 格式（SYNOPSIS/DESCRIPTION/OPTIONS/SUB-COMMANDS），而非默认的 HTML 友好格式。

### 配置 man_pages

在 `conf.py` 中配置 man page 构建：

```python
import os, sys
sys.path.insert(0, os.path.abspath('..'))

project = 'GitLike'
extensions = ['sphinxarg.ext']

man_pages = [
    ('cli/gitlike.1', 'gitlike', 'GitLike Documentation', ['Dev Team'], 1),
]

# 子命令的man page
man_pages.append(
    ('cli/gitlike-init.1', 'gitlike-init', 'GitLike Init Documentation', ['Dev Team'], 1),
)
man_pages.append(
    ('cli/gitlike-add.1', 'gitlike-add', 'GitLike Add Documentation', ['Dev Team'], 1),
)
man_pages.append(
    ('cli/gitlike-commit.1', 'gitlike-commit', 'GitLike Commit Documentation', ['Dev Team'], 1),
)
```

### 为子命令生成独立 Man Page

每个子命令可以单独生成 man page：

```rst
.. cli/gitlike-init.1.rst

###########
gitlike-init
###########

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :path: init
   :manpage:
```

### 构建 Man Page

```bash
# 生成 man page 文件
sphinx-build -b man docs/ docs/_build/man

# 查看 man page
man docs/_build/man/gitlike.1
man docs/_build/man/gitlike-init.1
```

### Man Page 输出结构

生成的 man page 包含以下章节：

```
GITLIKE(1)                    GitLike Manual                   GITLIKE(1)

SYNOPSIS
       gitlike [-h] [--verbose] [--repo REPO] {init,add,commit,log} ...

DESCRIPTION
       A Git-like version control system CLI tool.

       For more information, see https://gitlike.example.com/docs

OPTIONS
       Positional arguments:
         {init,add,commit,log}

       Named Arguments:
         -h, --help           show this help message and exit
         --verbose, -v        Enable verbose output
         --repo REPO, -C REPO
                              Run as if gitlike was started in <path> ='.'

SUB-COMMANDS
       init   Create a new repository
       add    Add file contents to the index
       commit Record changes to the repository
       log    Show commit logs

                                  1.0.0                         GITLIKE(1)
```

## 二、HTML 命令索引

### 简单命令索引

在 `conf.py` 中启用命令索引：

```python
extensions = ['sphinxarg.ext']

# 启用简单命令索引（按首字母分组）
sphinxarg_build_commands_index = True
sphinxarg_commands_index_in_toctree = True

sphinxarg_full_subcommand_name = True
```

在文档中引用索引：

```rst
.. docs/index.rst

GitLike 文档
============

.. toctree::
   :maxdepth: 2

   cli/index
   commands-index   <!-- 自动生成的命令索引页面 -->

所有命令参见 :ref:`commands-index`。
```

构建后访问 `commands-index.html`，可以看到按首字母分组的所有命令列表。

### 分组命令索引

对于命令较多的工具，使用分组索引更清晰：

```python
# conf.py
sphinxarg_build_commands_by_group_index = True
sphinxarg_commands_by_group_index_in_toctree = True
sphinxarg_commands_by_group_index_title = "命令分类索引"
sphinxarg_commands_by_group_index_file_suffix = "by-group"
```

在指令中使用 `:index-groups:` 为命令分配分组：

```rst
.. cli/index.rst

GitLike CLI
===========

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :nosubcommands:
   :index-groups: 基础命令

子命令文档：

.. toctree::
   :maxdepth: 1

   init
   add
   commit
   log
```

```rst
.. cli/init.rst

gitlike init
============

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :path: init
   :index-groups: 基础命令, 仓库管理

初始化一个新的 GitLike 仓库。
```

```rst
.. cli/add.rst

gitlike add
===========

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :path: add
   :index-groups: 基础命令, 文件操作

将文件内容添加到暂存区。
```

```rst
.. cli/commit.rst

gitlike commit
==============

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :path: commit
   :index-groups: 基础命令, 历史记录

提交更改到仓库。
```

```rst
.. cli/log.rst

gitlike log
===========

.. argparse::
   :module: gitlike.cli
   :func: build_parser
   :prog: gitlike
   :path: log
   :index-groups: 历史记录, 查询命令

查看提交历史。
```

在 toctree 中加入分组索引：

```rst
.. docs/index.rst

.. toctree::
   :maxdepth: 2

   cli/index
   commands-by-group   <!-- 自动生成的分组索引 -->
```

生成的分组索引会按"基础命令"、"仓库管理"、"文件操作"、"历史记录"、"查询命令"分组显示命令。

### 使用交叉引用

在任意文档中使用 `:command:` 角色引用命令：

```rst
使用 :command:`gitlike init` 初始化仓库后，
用 :command:`gitlike add` 添加文件，
最后通过 :command:`gitlike commit -m "message"` 提交更改。

查看历史使用 :command:`gitlike log --oneline`。
```

## 三、同时支持 HTML 和 Man Page

如果需要同时生成 HTML 文档和 man page，可以创建两套 RST 文件：

```
docs/
├── conf.py
├── index.rst           # HTML 入口
├── cli/
│   ├── index.rst       # HTML 总览（非manpage格式）
│   ├── init.rst        # HTML init页面
│   └── ...
└── man/
    ├── gitlike.1.rst   # man page 格式
    ├── gitlike-init.1.rst
    └── ...
```

`conf.py` 中同时配置两个构建目标：

```python
# HTML 文档
master_doc = 'index'

# Man pages
man_pages = [
    ('man/gitlike.1', 'gitlike', 'GitLike Documentation', ['Dev Team'], 1),
    ('man/gitlike-init.1', 'gitlike-init', 'GitLike Init Documentation', ['Dev Team'], 1),
    ('man/gitlike-add.1', 'gitlike-add', 'GitLike Add Documentation', ['Dev Team'], 1),
    ('man/gitlike-commit.1', 'gitlike-commit', 'GitLike Commit Documentation', ['Dev Team'], 1),
    ('man/gitlike-log.1', 'gitlike-log', 'GitLike Log Documentation', ['Dev Team'], 1),
]

# 命令索引（仅 HTML）
sphinxarg_build_commands_index = True
sphinxarg_commands_index_in_toctree = True
sphinxarg_full_subcommand_name = True
```

构建两种格式：

```bash
# HTML 文档（含索引）
sphinx-build -b html docs/ docs/_build/html

# Man pages
sphinx-build -b man docs/ docs/_build/man
```

## 四、Makefile 便捷目标

在 `docs/Makefile` 中添加便捷目标：

```makefile
html:
	@$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html

man:
	@$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(BUILDDIR)/man
	@echo "Man pages generated in $(BUILDDIR)/man/"
	@echo "View with: man $(BUILDDIR)/man/gitlike.1"

all: html man
```

## 相关概念

- [Man page 输出格式](/concepts/08-manpage-output.md)
- [命令索引生成](/concepts/10-command-indices.md)
- [配置选项详解](/concepts/11-configuration.md)
- [Commands 域与交叉引用](/concepts/09-domain-crossref.md)
- [多页面子命令文档化](/examples/subcommand-docs.md)
