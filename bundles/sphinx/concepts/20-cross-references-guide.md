---
type: "concept"
title: "交叉引用完全指南"
description: "Sphinx交叉引用机制详解——:ref:、:doc:、:numref:、:download:、:py:func:等角色用法、自定义链接文本、~和!修饰符、intersphinx跨项目引用"
tags: [cross-references, links, roles, referencing, intersphinx]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T10:40:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: official-xref
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 Cross-references 页面"
---

# 交叉引用完全指南

交叉引用是 Sphinx 最核心的能力之一。不同于普通 Markdown 的超链接，Sphinx 的交叉引用是**语义级**的——它理解引用目标的类型（章节、文档、函数、类、图片、表格等），自动生成正确的链接文本和编号，并在目标不存在时发出警告。

## 基本语法

交叉引用使用角色（role）语法：`` :角色名:`目标` ``。可以自定义链接文本：`` :角色名:`链接文本 <目标>` ``。

两种修饰符可以改变引用行为：

| 修饰符 | 位置 | 效果 |
|--------|------|------|
| `~` | 前缀 | 缩短链接文本为最后一部分（如 `~queue.Queue.get` → `get()`） |
| `!` | 前缀 | 只显示文本，不生成链接（用于抑制不存在引用的警告） |

## 引用任意位置：`:ref:`

`:ref:` 是最通用的交叉引用角色，可以引用任何带有显式标签的位置：

```rst
.. _my-installation-section:

安装指南
--------

详细的安装步骤...

请参见 :ref:`my-installation-section` 了解安装方法。
```

当 `:ref:` 的标签紧跟在章节标题前时，链接文本自动使用章节标题。对于非章节位置（如图、表），需要显式指定链接文本：

```rst
.. _my-figure:

.. figure:: /_static/arch.png

   架构图

引用图：参见 :ref:`架构图 <my-figure>`。
```

### 标签命名规范

- 标签名以 `_` 开头（`.. _标签名:`）
- 引用时省略开头的 `_`（`:ref:`标签名``）
- 标签名在**整个项目中必须唯一**
- 推荐命名：`<文档名>-<描述>`，如 `install-requirements`、`api-config-values`

### 自动章节标签

使用 `sphinx.ext.autosectionlabel` 扩展可以自动为每个章节标题生成标签，无需手动写 `.. _label:`：

```python
# conf.py
extensions = ['sphinx.ext.autosectionlabel']

# 可选：自动添加文档名前缀，避免同名标题冲突
autosectionlabel_prefix_document = True
```

启用后可以直接用标题名引用：`:ref:`安装指南``。

## 引用文档：`:doc:`

`:doc:` 直接引用另一个文档文件（不需要 `.rst`/`.md` 后缀）：

```rst
参见 :doc:`/tutorial/first-steps` 获取入门教程。
参见 :doc:`安装指南 <install>` 了解安装方法。
```

路径规则：
- 以 `/` 开头：相对于文档源目录（source directory）的绝对路径
- 不以 `/` 开头：相对于当前文档的相对路径

## 引用下载文件：`:download:`

`:download:` 角色链接到可下载的非文档文件（如代码示例、PDF、数据文件）：

```rst
下载示例代码：:download:`example.py <../examples/example.py>`。
```

被引用的文件会自动复制到输出目录的 `_downloads/<hash>/` 下。绝对路径（以 `/` 开头）相对于源目录。

如果只想在HTML输出中显示下载链接，可以用 `only` 指令包裹：

```rst
.. only:: builder_html

   下载 :download:`数据集 <data/sample.csv>`。
```

## 编号引用：`:numref:`

`:numref:` 用于引用图、表、代码块等带编号的元素，自动插入"图1.1"、"表2.3"这样的编号文本：

```rst
.. _my-table:

.. list-table:: 版本兼容性
   :header-rows: 1

   * - Python
     - Sphinx
   * - 3.12+
     - 9.x

参见 :numref:`my-table` 了解版本兼容性。
{== 输出：参见 表 1.1 了解版本兼容性。 ==}
```

### 自定义编号格式

可以自定义链接文本，使用 `%s` 或 `{number}` 作为编号占位符，`{name}` 作为标题占位符：

```rst
:numref:`表 %s <my-table>`          → 表 1.1
:numref:`图 {number} ({name}) <fig1>` → 图 2.1 (架构图)
```

全局配置默认编号格式：

```python
# conf.py
numfig_format = {
    'figure': '图 %s',
    'table': '表 %s',
    'code-block': '代码清单 %s',
    'section': '第%s节',
}
numfig = True  # 启用编号（默认False）
numfig_secnum_depth = 1  # 编号到几级章节
```

## 代码对象引用（Python域）

Python域提供了专门的角色引用代码对象：

| 角色 | 引用对象 | 链接文本示例 |
|------|---------|-------------|
| `:py:mod:` | 模块 | `os.path` |
| `:py:func:` | 函数 | `print()` |
| `:py:class:` | 类 | `list` |
| `:py:meth:` | 方法 | `str.join()` |
| `:py:attr:` | 属性 | `datetime.date.year` |
| `:py:data:` | 模块数据 | `sys.version` |
| `:py:const:` | 常量 | `math.pi` |
| `:py:exc:` | 异常 | `ValueError` |
| `:py:obj:` | 任意对象 | `x.y.z` |

### ~修饰符：缩短显示文本

`~` 前缀只显示目标的最后一部分：

```rst
:py:meth:`~queue.Queue.get`   → get()
:py:class:`~datetime.date`    → date
:py:func:`~os.path.join`      → join()
```

### !修饰符：禁止链接生成

`!` 前缀不生成超链接，只显示文本（用于抑制nitpicky模式的警告）：

```rst
:py:func:`!deprecated_func`   {== 显示deprecated_func()但无链接 ==}
```

这在changelog中引用已删除的API，或引用第三方库（未配置intersphinx）时特别有用。

### 其他域

除了Python域（`py`），Sphinx还内置了其他语言域：

| 域前缀 | 语言 | 示例 |
|--------|------|------|
| `c:` | C | `:c:func:\`malloc\`` |
| `cpp:` | C++ | `:cpp:class:\`std::vector\`` |
| `js:` | JavaScript | `:js:func:\`Array.prototype.map\`` |
| `rst:` | reST | `:rst:dir:\`toctree\`` |

## 其他常用引用角色

| 角色 | 用途 | 示例 |
|------|------|------|
| `:term:` | 术语表引用 | `:term:`Sphinx`` |
| `:pep:` | Python PEP | `:pep:`8`` |
| `:rfc:` | RFC文档 | `:rfc:`2822`` |
| `:envvar:` | 环境变量 | `:envvar:`PATH`` |
| `:command:` | 命令行命令 | `:command:`sphinx-build`` |
| `:file:` | 文件路径 | `:file:`conf.py`` |
| `:kbd:` | 键盘按键 | `:kbd:`Ctrl+C`` |
| `:guilabel:` | GUI按钮 | `:guilabel:`OK``` |
| `:menuselection:` | 菜单路径 | `:menuselection:`File → Save`` |

## 交叉引用到 URL

标准 reST 链接语法可以直接用于外部URL：

```rst
`Sphinx官网 <https://www.sphinx-doc.org/>`_
```

### 缩短外部链接：extlinks 扩展

`sphinx.ext.extlinks` 扩展可以定义常用外部链接的快捷方式：

```python
# conf.py
extlinks = {
    'pypi': ('https://pypi.org/project/%s/', 'PyPI:%s'),
    'wiki': ('https://en.wikipedia.org/wiki/%s', 'Wikipedia:%s'),
    'issue': ('https://github.com/sphinx-doc/sphinx/issues/%s', 'issue #%s'),
}
```

使用：

```rst
:pypi:`sphinx`           → PyPI:sphinx（链接到PyPI）
:issue:`12345`           → issue #12345（链接到GitHub issue）
```

## 跨项目引用：Intersphinx

`sphinx.ext.intersphinx` 扩展允许链接到其他Sphinx项目的文档，如Python标准库、Django、Flask等：

```python
# conf.py
extensions = ['sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}
```

配置后可以直接引用其他项目的对象：

```rst
:py:func:`print`          {== 自动链接到Python官方文档 ==}
:py:class:`list`          {== 链接到Python list文档 ==}
```

Intersphinx 自动下载并缓存其他项目的 `objects.inv` 清单文件。如果在线环境受限，可以指向本地镜像或使用本地 inventory 文件。

## 缺失引用处理

当引用目标不存在时，Sphinx 会发出警告。处理方式：

1. **修复引用**（首选）：确认标签名/对象名是否正确
2. **使用 `!` 前缀**：如果目标确实不存在但需要保留文本
3. **添加到 nitpick_ignore**：在 conf.py 中忽略特定模式的警告：

```python
nitpick_ignore = [
    ('py:class', 'SomeExternalClass'),
    ('py:func', 'deprecated_function'),
]
nitpicky = True  # 将所有缺失引用警告转为错误（CI推荐）
```

## 交叉引用检查清单

- [ ] 所有标签名全局唯一
- [ ] 引用文档使用 `.rst`/`.md` 文件名（不带扩展名）
- [ ] 使用 `~` 修饰符在重复引用时缩短显示
- [ ] 不存在的引用使用 `!` 或 nitpick_ignore 抑制警告
- [ ] 跨文件引用优先使用 `:ref:` 而非直接标题链接（标题可能被改名）
- [ ] 启用 intersphinx 链接到标准库和依赖文档
- [ ] CI 中启用 `-W`（警告转错误）和 `nitpicky = True` 防止断链

## 相关概念

- [reStructuredText 基础语法](18-rest-primer.md)
- [Markdown/MyST 支持](19-markdown-and-myst.md)
- [Intersphinx跨项目引用](14-intersphinx.md)
- [Domain领域系统](09-domain-system.md)
- [Autodoc自动文档](12-autodoc.md)
