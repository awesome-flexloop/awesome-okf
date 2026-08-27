---
type: Concept
title: 快速开始
description: 安装和配置 sphinx-external-toc 的最小步骤，创建第一个 _toc.yml 文件并替换原生 toctree
tags: [sphinx, sphinx-extension, toctree, getting-started, setup, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:05:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: etoc-source
    resource: /references/etoc-source.md
    title: sphinx-external-toc 源码路径映射
---

# 快速开始

本文档介绍如何安装 sphinx-external-toc 并将现有 Sphinx 项目迁移到 `_toc.yml` 导航定义方式。

## 安装

使用 pip 安装：

```bash
pip install sphinx-external-toc
```

sphinx-external-toc 会自动安装其依赖 `sphinx-multitoc-numbering`。

## 启用扩展

在 `conf.py` 中将 `sphinx_external_toc` 添加到 `extensions` 列表：

```python
# conf.py
extensions = [
    # ... 其他扩展
    'sphinx_external_toc',
]
```

## 创建 _toc.yml

在 Sphinx 源目录（`conf.py` 所在目录，或 `master_doc` 所在目录）创建 `_toc.yml` 文件：

```yaml
# _toc.yml
root: index
subtrees:
  - entries:
      - file: install
      - file: usage
      - file: api
```

这等价于在 `index.rst` 中写：

```rst
.. toctree::
   :maxdepth: 2

   install
   usage
   api
```

## 从现有项目迁移

如果你已有使用 `.. toctree::` 的项目：

1. **创建 `_toc.yml`**：根据现有 toctree 结构编写 YAML 文件
2. **移除文档中的 `.. toctree::` 指令**（可选但推荐）：扩展会在检测到原生 toctree 时发出警告
3. **添加 `.. tableofcontents::` 占位符**（可选）：在需要子文档列表的位置放置此指令。如果不放置，toctree 会自动追加到文档末尾

### 迁移示例

**原来的 index.rst：**

```rst
Welcome to My Project
=====================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   usage
```

**迁移后：**

index.rst（移除 toctree）：

```rst
Welcome to My Project
=====================

.. tableofcontents::
```

_toc.yml：

```yaml
root: index
subtrees:
  - caption: Contents:
    entries:
      - file: install
      - file: usage
```

## 配置选项

在 `conf.py` 中可以配置以下选项：

```python
# _toc.yml 文件路径（默认值为 "_toc.yml"）
external_toc_path = "_toc.yml"

# 是否自动将不在 ToC 中的文件加入排除列表（默认 False）
external_toc_exclude_missing = False
```

### external_toc_exclude_missing

设为 `True` 时，构建时会扫描源目录中所有文档文件，将未在 `_toc.yml` 中引用的文件自动加入 `exclude_patterns`，避免它们被构建。这对于确保"只有 ToC 中的文档才会被构建"很有用。

```python
external_toc_exclude_missing = True
```

## 构建文档

```bash
sphinx-build -b html docs docs/_build/html
```

构建时观察输出，确认：

1. 没有 `[etoc]` 错误信息
2. 侧边栏导航正确显示 `_toc.yml` 中定义的结构
3. 如果有警告 `toctree directive not expected with external-toc`，说明文档中还残留原生 `.. toctree::` 指令，需要移除

## 最小项目结构

```
my-project/
├── docs/
│   ├── _toc.yml          # 导航定义（必须）
│   ├── conf.py           # 已添加 sphinx_external_toc
│   ├── index.rst         # 根文档
│   ├── install.rst
│   ├── usage.rst
│   └── api.rst
└── pyproject.toml
```

## 验证安装成功

构建后检查以下事项：

1. 页面侧边栏/导航栏显示正确的文档层级
2. 上/下页导航链接与 `_toc.yml` 中顺序一致
3. 如果使用 `tableofcontents` 指令，该位置显示子文档列表
4. 访问根 URL 时正确重定向到根文档（自动创建 index.html 重定向）

## 使用 CLI 工具验证 ToC

sphinx-external-toc 提供了 CLI 工具来验证和检查 `_toc.yml`：

```bash
# 解析 ToC 文件并输出 JSON 格式的 sitemap
sphinx-etoc parse _toc.yml

# 从 ToC 文件生成项目骨架文件
sphinx-etoc to-project _toc.yml -e rst -p docs
```

注意：CLI 入口点可能是 `sphinx-etoc` 或 `sphinx-external-toc`，取决于安装方式。如果上述命令不可用，可以用：

```bash
python -m sphinx_external_toc.cli parse _toc.yml
```

## 常见问题

**Q: 构建报错 `[etoc] external_toc_path does not exist`？**

A: 确保 `_toc.yml` 文件存在于 `conf.py` 所在的源目录中。如果文件在其他位置，设置 `external_toc_path` 配置。

**Q: 文档侧边栏是空的？**

A: 检查 `_toc.yml` 中 `root` 指向的文档是否存在，文件路径是否正确（POSIX 格式，不带扩展名）。

**Q: 出现警告 `toctree directive not expected with external-toc`？**

A: 文档中存在原生 `.. toctree::` 指令，需要移除它们，因为 sphinx-external-toc 已接管导航管理。

**Q: 根页面访问 404？**

A: 如果根文档不是 `index`，sphinx-external-toc 会在 `build-finished` 时自动创建一个重定向 `index.html`。确保构建过程正常完成。

## 下一步

- [_toc.yml 语法详解](02-toc-yaml-syntax.md)——学习完整的 YAML 语法
- [扩展工作机制](03-extension-mechanism.md)——理解扩展如何替换 Sphinx 内置 toctree
- [基础 _toc.yml 示例](../examples/basic-toc.md)——多种格式的完整示例

## 相关概念

- [sphinx-external-toc 简介](00-introduction.md)
- [_toc.yml 语法详解](02-toc-yaml-syntax.md)
- [高级功能](04-advanced-features.md)
