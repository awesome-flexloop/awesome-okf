---
type: Concept
title: 命令索引生成
description: CommandsIndex和CommandsByGroupIndex两种索引、临时文件桥接机制、in_toctree配置、索引自定义
tags: [sphinx-argparse, index, CommandsIndex, CommandsByGroupIndex, temporary-files, toctree, index-groups]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:42:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:42:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# 命令索引生成

sphinx-argparse 支持自动生成两种命令索引：简单命令索引（Commands Index）和分组命令索引（Commands by Group Index）。索引通过 Sphinx 的 Domain/Index 机制实现，并使用临时文件桥接方案解决扩展索引无法直接加入 toctree 的问题。

## 简单命令索引（Commands Index）

简单索引按命令名首字母分组，列出所有文档化的命令及其链接。

### 启用索引

在 `conf.py` 中添加配置：

```python
sphinxarg_build_commands_index = True
```

启用后，HTML 构建会生成 `commands-index.html` 页面，可以通过 `:ref:`commands-index`` 引用：

```rst
参见 :ref:`commands-index` 查看所有命令列表。
```

### 加入 Toctree

默认情况下，Sphinx 扩展生成的索引页面无法直接加入 toctree（目录树）。要让索引出现在侧边栏导航中，需要启用 in_toctree 选项：

```python
sphinxarg_build_commands_index = True
sphinxarg_commands_index_in_toctree = True
```

启用后，扩展会在 Sphinx 源码目录创建一个临时 RST 文件 `commands-index.rst`，使得 Sphinx 将其视为普通文档页面，可以添加到 toctree：

```rst
.. toctree::

   commands-index
```

## 分组命令索引（Commands by Group Index）

分组索引允许你将命令按功能分组显示，例如"基础命令"、"项目管理"、"部署"等。

### 启用分组索引

在 `conf.py` 中添加：

```python
sphinxarg_build_commands_by_group_index = True
sphinxarg_commands_by_group_index_in_toctree = True
```

### 为命令分配分组

在 `.. argparse::` 指令中使用 `:index-groups:` 选项指定命令所属的分组（多个分组用逗号分隔）：

```rst
.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
   :index-groups: 基础命令

.. argparse::
   :module: mypackage.cli
   :func: build_parser
   :prog: mytool
   :path: init
   :index-groups: 基础命令, 项目管理
```

### 自定义索引标题和文件名

```python
# 自定义文件名后缀（默认 "by-group"，生成 commands-by-group.html）
sphinxarg_commands_by_group_index_file_suffix = "by-service"
# 自定义索引标题（默认 "Commands by Group"）
sphinxarg_commands_by_group_index_title = "按服务分类的命令"
```

使用自定义后缀后，引用标签也会相应变化：`:ref:`commands-by-service``。

## 临时文件桥接机制

扩展索引加入 toctree 的核心是临时文件机制，这是一个务实的工程方案：

### 创建阶段（builder-inited 事件）

`configure_ext()` 在构建初始化时检查配置，如果 `*_in_toctree` 为 True：

1. 调用 `_create_temporary_dummy_file()` 创建临时 RST 文件
2. 文件内容包含标题和说明文本（告知这是由扩展生成的临时文件）
3. 文件路径被记录在 `domain.temporary_index_files` 列表中

```python
def _create_temporary_dummy_file(app, domain, docname, title):
    dummy_file = app.srcdir / docname
    if dummy_file.exists():
        raise ExtensionError(...)  # 防止覆盖真实文件
    content = '\n'.join((
        f'{title}',
        f'{len(title) * "="}',
        '',
        'Temporary file that is replaced with an index...',
    ))
    dummy_file.write_text(content, encoding='utf-8')
    domain.temporary_index_files.append(dummy_file)
```

### 清理阶段（build-finished 事件）

构建完成后，`_delete_temporary_files()` 遍历 `temporary_index_files` 列表，删除所有临时文件：

```python
def _delete_temporary_files(app, _err):
    domain = app.env.domains[ArgParseDomain.name]
    for fpath in domain.temporary_index_files:
        fpath.unlink(missing_ok=True)
```

### 安全保护

- 如果目标位置已存在同名文件，抛出 ExtensionError，防止覆盖用户的真实文档
- 临时文件使用 `unlink(missing_ok=True)` 安全删除，文件不存在时不报错
- 仅在启用 in_toctree 时创建临时文件

## Index 类实现

### CommandsIndex

```python
class CommandsIndex(Index):
    name = 'index'
    localname = 'Commands Index'

    def generate(self, docnames=None):
        content = {}
        commands = sorted(self.domain.get_objects(), key=operator.itemgetter(0))
        for cmd, dispname, _typ, docname, anchor, priority in commands:
            inx_entry = IndexEntry(cmd, priority, docname, anchor, docname, '', dispname)
            content.setdefault(cmd[0].lower(), []).append(inx_entry)
        return sorted(content.items()), True
```

- 按命令全名的首字母（小写）分组
- 返回值格式为 `(list of (letter, entries)], collapse)`，collapse=True 表示子项可折叠

### CommandsByGroupIndex

```python
class CommandsByGroupIndex(Index):
    name = 'by-group'
    localname = 'Commands by Group'

    def generate(self, docnames=None):
        content = {}
        commands_by_group = self.domain.data['commands-by-group']
        for group in sorted(commands_by_group):
            commands = sorted(commands_by_group[group], key=operator.itemgetter(0))
            for cmd, dispname, _typ, docname, anchor, priority in commands:
                idx_entry = IndexEntry(cmd, priority, docname, anchor, docname, '', dispname)
                content.setdefault(group, []).append(idx_entry)
        return sorted(content.items()), True
```

- 按分组名分组（而非首字母）
- 命令可属于多个分组（在多个组中重复出现）

## 自定义索引外观

默认情况下，索引使用 `domainindex.html` 模板渲染。要自定义外观，可以：

1. 复制主题的 `domainindex.html` 到项目 `_templates` 目录并修改
2. 为不同索引使用不同模板（通过 `html-page-context` 事件）：

```python
def page_template(app, pagename, templatename, context, doctree):
    if pagename == "commands-by-group":
        return "customindex.html"
    return templatename

def setup(app):
    app.connect('html-page-context', page_template)
```

## 完整配置示例

```python
# conf.py
extensions = ['sphinxarg.ext']

# 启用简单命令索引
sphinxarg_build_commands_index = True
sphinxarg_commands_index_in_toctree = True

# 启用分组命令索引
sphinxarg_build_commands_by_group_index = True
sphinxarg_commands_by_group_index_in_toctree = True
sphinxarg_commands_by_group_index_file_suffix = "by-group"
sphinxarg_commands_by_group_index_title = "命令索引（按分组）"

# 显示完整子命令名
sphinxarg_full_subcommand_name = True
```

## 相关概念

- [Commands 域与交叉引用](/concepts/09-domain-crossref.md)
- [配置选项详解](/concepts/11-configuration.md)
- [基础用法完整示例](/examples/basic-usage.md)
