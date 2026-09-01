---
type: "concept"
title: "Intersphinx 跨项目引用"
description: "sphinx.ext.intersphinx实现跨Sphinx项目链接、objects.inv清单格式、intersphinx_mapping配置、引用其他项目API的方法"
tags: [extension, intersphinx, cross-project, references]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: intersphinx-py
    resource: sphinx/ext/intersphinx.py
    title: "sphinx.ext.intersphinx module"
---

# Intersphinx 跨项目引用

`sphinx.ext.interspxhinx` 是 Sphinx 的内置扩展，它允许你链接到其他Sphinx项目的文档，就像引用自己项目内的对象一样。这使得跨项目API引用变得简单——你可以直接引用Python标准库、Django、NumPy等外部库的文档，而无需手动维护URL。

## 工作原理

每个启用intersphinx的Sphinx项目在构建时会生成一个 `objects.inv` 文件（Inventory，对象清单），该文件包含所有可引用对象的名称、类型和URL映射 [F-059]。Intersphinx扩展：

1. 从配置的远程项目下载 `objects.inv` 文件
2. 解析清单并缓存到本地
3. 在missing-reference事件中尝试将未解析的引用匹配到外部项目的对象
4. 生成正确的外部链接URL

## 配置

在conf.py中启用并配置：

```python
extensions = ['sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}
```

每个映射项的格式为：
```python
'alias': (target_uri, inventory_location)
```

- `target_uri`：目标文档的基础URL
- `inventory_location`：objects.inv文件路径，`None`表示使用默认位置 `{target_uri}/objects.inv`；可以指定本地路径或自定义URL

### 高级配置

```python
intersphinx_mapping = {
    # 指定本地objects.inv（离线构建时使用）
    'python': ('https://docs.python.org/3', 'python-inv.txt'),
    # 多版本映射
    'django': (
        'https://docs.djangoproject.com/en/5.0',
        'https://docs.djangoproject.com/en/5.0/_objects',
    ),
}

# 缓存控制
intersphinx_cache_limit = 5  # 缓存5天（默认），-1表示永久缓存
intersphinx_timeout = 30     # 请求超时秒数
```

## 使用外部引用

配置好intersphinx_mapping后，使用标准角色语法即可引用外部项目的对象：

```rst
使用 :py:func:`open` 打开文件。              → 链接到Python标准库open()
参考 :py:class:`~pathlib.Path`。             → 链接到pathlib.Path（~前缀只显示最后部分）
查看 :external+sphinx:doc:`usage/quickstart`。 → 显式指定引用sphinx项目的文档页
```

### 引用语法

| 语法 | 说明 |
|------|------|
| `:py:func:\`name\`` | 在默认搜索顺序中查找（先本地后外部） |
| `:external+alias:domain:role:\`target\`` | 显式指定外部项目alias |
| `:py:class:\`~package.module.Class\`` | `~`前缀使链接文本只显示最后部分 |
| `:external+python:doc:\`install/index\`` | 引用外部项目的文档页（:doc:角色） |
| `:external+python:ref:\`reference-label\`` | 引用外部项目的标签（:ref:角色） |

### 外部前缀（`external+alias:`）

Sphinx提供 `:external+alias:` 前缀来显式指定目标项目，这在名称冲突时特别有用：

```rst
:external+python:py:class:`dict`   → 强制引用Python标准库的dict
:external+sphinx:std:doc:`usage/builders` → 引用Sphinx文档页
```

## objects.inv 格式

`objects.inv` 文件有两种格式 [F-060]：

### 版本2格式（压缩二进制）

这是默认格式，使用zlib压缩：

```
# Sphinx inventory version 2
# Project: <project_name>
# Version: <version>
# The remainder of this file is compressed using zlib.
<zlib压缩数据>
```

压缩数据中每行格式为：
```
name domain:role priority uri displayname
```

字段说明：
- `name`：对象完全限定名
- `domain:role`：域和角色（如 `py:function`、`std:doc`）
- `priority`：搜索优先级（-1/0/1/2）
- `uri`：相对URL（`$` 表示与name相同）
- `displayname`：显示名称（`-` 表示与name相同）

### 版本1格式（明文）

旧格式（Sphinx < 1.0）为明文，用于调试时可将v2转为明文：

```bash
python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv
```

输出示例：
```
std:doc logging
std:label logging-config
py:class argparse.ArgumentParser
py:function open
...
```

## Intersphinx 与 missing-reference

Intersphinx通过订阅 `missing-reference` 事件工作 [F-061]：

1. Sphinx首先尝试在本地Domain中解析引用
2. 本地解析失败时，触发 `missing-reference` 事件
3. Intersphinx收到事件后，在所有配置的外部inventories中查找目标
4. 找到匹配项后，创建指向外部URL的reference节点
5. 多个项目包含相同对象名时，按intersphinx_mapping的顺序取第一个匹配

## 内置外部引用支持

Intersphinx不仅支持Python域的对象，还支持：

| 域:角色 | 说明 |
|--------|------|
| `std:doc` | 文档页面 |
| `std:label`/`std:ref` | 标签/引用 |
| `std:term` | 术语表条目 |
| `std:option` | 命令行选项 |
| `std:envvar` | 环境变量 |
| `py:mod`/`py:class`/`py:func`/... | Python对象 |
| `c:func`/`c:type`/... | C对象 |
| `cpp:class`/... | C++对象 |
| `js:func`/`js:class`/... | JavaScript对象 |

## 调试Intersphinx

### 查看Inventory内容

```bash
# 列出inventory中所有对象
python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv

# 只列出特定模式
python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv | grep "pathlib"
```

### 常见问题排查

1. **引用不工作**：运行 `python -m sphinx.ext.intersphinx <url>` 检查inventory是否可下载
2. **版本不匹配**：确保intersphinx_mapping中的URL指向正确版本
3. **本地缓存问题**：删除构建目录中的 `environment.pickle` 或使用 `sphinx-build -E` 全量重建
4. **网络问题**：下载objects.inv到本地，使用本地路径作为inventory_location
5. **名称冲突**：使用 `:external+alias:` 前缀显式指定项目

## 相关概念

- [事件系统](05-event-system.md)
- [Domain 域系统](09-domain-system.md)
- [Autodoc 自动文档生成](12-autodoc.md)
