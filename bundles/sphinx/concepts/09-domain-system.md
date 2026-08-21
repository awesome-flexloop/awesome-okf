---
type: "concept"
title: "Domain 领域系统"
description: "Domain基类、内置6大领域(py/c/cpp/js/rst/std)、ObjType对象类型、directives/roles/indices注册、resolve_xref交叉引用解析、get_objects搜索索引"
tags: [core, domain, cross-reference, python-domain, std-domain]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: domain-py
    resource: sphinx/domains/__init__.py
    title: "Domain base class"
  - id: registry-py
    resource: sphinx/registry.py
    title: "SphinxComponentRegistry domain registration"
---

# Domain 领域系统

Domain（领域）是 Sphinx 实现**语义化交叉引用**的核心抽象，定义在 [sphinx/domains/__init__.py](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/domains/__init__.py)。每个 Domain 封装了一类知识域（通常是一种编程语言）的描述指令、引用角色和对象索引，使得 Sphinx 能够理解代码实体间的关系并生成智能交叉链接。

## 什么是 Domain

简单来说，Domain 是一组"描述+引用"工具包：

- **描述指令（Directives）**：用于在文档中标记/描述对象（如 `.. py:function::` 描述Python函数）
- **引用角色（Roles）**：用于在文本中引用对象（如 `:py:func:\`name\`` 引用Python函数）
- **对象类型（ObjType）**：定义可被描述和引用的实体种类（function、class、method等）
- **索引（Indices）**：生成对象索引页（如Python模块索引、全局对象索引）
- **交叉引用解析**：将引用链接到正确的描述位置

例如，Python域（py domain）让你可以这样写：

```rst
.. py:function:: greet(name: str) -> str
   向用户问好。

你可以使用 :py:func:`greet` 函数来...
```

Sphinx 会将 `:py:func:\`greet\`` 自动链接到 `.. py:function:: greet` 的位置。

## 内置 Domain

Sphinx 内置 6 个 Domain [F-035]：

| 域名 | label | 模块 | 用途 |
|------|-------|------|------|
| `std` | "Standard" | `sphinx.domains.std` | 标准标记域（通用reST指令、标签、引用、选项等） |
| `py` | "Python" | `sphinx.domains.python` | Python语言文档（模块、类、函数、方法、属性、异常等） |
| `c` | "C" | `sphinx.domains.c` | C语言文档（函数、类型、宏、变量等） |
| `cpp` | "C++" | `sphinx.domains.cpp` | C++语言文档（类、函数、命名空间、模板等） |
| `js` | "JavaScript" | `sphinx.domains.javascript` | JavaScript语言文档（模块、类、函数、方法等） |
| `rst` | "reStructuredText" | `sphinx.domains.rst` | reST标记语言文档（指令、角色等） |

默认的主域（primary_domain）是 `py`，可以通过 `primary_domain` 配置项修改。在文档中也可以使用 `.. default-domain::` 指令临时切换。

## Domain 基类

### 类属性

每个 Domain 子类需要定义以下类属性 [F-036]：

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 域名（简短唯一，如'py'、'c'） |
| `label` | `str` | 显示名称（用于消息，如'Python'、'C'） |
| `object_types` | `dict[str, ObjType]` | 对象类型映射：类型名→ObjType实例 |
| `directives` | `dict[str, type[Directive]]` | 指令映射：指令名→Directive类 |
| `roles` | `dict[str, RoleFunction\|XRefRole]` | 角色映射：角色名→角色函数/XRefRole |
| `indices` | `list[type[Index]]` | 索引类列表 |
| `dangling_warnings` | `dict[str, str]` | dangling引用的警告消息模板 |
| `enumerable_nodes` | `dict[type[Node], tuple]` | 可编号节点 |
| `initial_data` | `dict[str, Any]` | 新环境的初始数据结构 |
| `data_version` | `int` | 数据格式版本号（变更data结构时递增） |

### 核心实例方法

Domain 实例持有对 BuildEnvironment 的引用，其核心方法包括 [F-037]：

| 方法 | 说明 |
|------|------|
| `setup()` | 域初始化（注册索引页的超链接目标） |
| `add_object_type(name, objtype)` | 动态添加对象类型 |
| `role(name)` | 获取角色适配器（自动注入完整域名） |
| `directive(name)` | 获取指令适配器（自动注入完整域名） |
| `clear_doc(docname)` | 清除指定文档的数据（重新读取时调用） |
| `merge_domaindata(docnames, otherdata)` | 合并并行子进程的数据 |
| `process_doc(env, docname, document)` | 处理已读取文档（收集对象信息） |
| `check_consistency()` | 一致性检查（实验性） |
| `resolve_xref(env, fromdocname, builder, typ, target, node, contnode)` | 解析跨文档引用，返回reference节点或None |
| `resolve_any_xref(env, fromdocname, builder, target, node, contnode)` | 解析"any"类型引用（不知道具体类型），返回`[(domain:role, node), ...]`列表 |
| `get_objects()` | 返回所有对象描述元组，用于搜索索引 |

### 数据存储

Domain 的数据存储在 `env.domaindata[self.name]` 字典中 [F-038]：

```python
def __init__(self, env):
    self.env = env
    if self.name not in env.domaindata:
        new_data = copy.deepcopy(self.initial_data)
        new_data['version'] = self.data_version
        self.data = env.domaindata[self.name] = new_data
    else:
        self.data = env.domaindata[self.name]
        if self.data['version'] != self.data_version:
            raise OSError(f'data of {self.label!r} domain out of date')
```

`data_version` 机制与 BuildEnvironment 的 `ENV_VERSION` 类似——当域的数据结构变化时递增版本号，旧的pickle缓存会被废弃。

## ObjType：对象类型

`ObjType` 描述一种可被文档化和引用的对象类型 [F-039]：

```python
class ObjType:
    known_attrs = {'searchprio': 1}

    def __init__(self, lname: str, /, *roles: str, **attrs):
        self.lname = lname           # 本地化名称（如"function"、"class"）
        self.roles = roles           # 可引用此类型对象的角色名列表
        self.attrs = self.known_attrs | attrs  # 属性（searchprio控制搜索优先级）
```

searchprio 的取值：
- `0`：重要对象（在搜索结果中优先显示）
- `1`：默认优先级
- `2`：不重要对象（在全文匹配之后显示）
- `-1`：不纳入搜索索引

示例：Python域的对象类型定义

```python
object_types = {
    'function': ObjType(_('function'), 'func', 'obj'),
    'class':    ObjType(_('class'),    'class', 'obj'),
    'method':   ObjType(_('method'),   'meth', 'obj'),
    'module':   ObjType(_('module'),   'mod', 'obj'),
    'data':     ObjType(_('data'),     'data', 'obj'),
    'exception': ObjType(_('exception'), 'exc', 'obj'),
    # ...
}
```

## 指令与角色适配器

Domain 通过 `role(name)` 和 `directive(name)` 方法提供适配器模式 [F-040]：

- **角色适配器**：在原始角色函数调用前，自动将完整域名（如 `'py:func'`）作为第一个参数传入
- **指令适配器**：创建一个动态子类，在 `run()` 执行前将 `self.name` 设置为完整域名

这使得指令和角色的实现可以不关心自己属于哪个域，注册到不同域时自动获得正确的前缀。

## 交叉引用解析

`resolve_xref()` 是 Domain 的核心方法 [F-041]：

```python
def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
    """
    Args:
        env: BuildEnvironment
        fromdocname: 引用来源文档的docname
        builder: 当前Builder
        typ: 引用类型（角色名，如'func'、'class'）
        target: 引用目标字符串（如'myfunc'、'mymodule.MyClass'）
        node: pending_xref节点
        contnode: 引用的内容节点（显示文本）

    Returns:
        nodes.reference: 成功解析，返回引用节点
        None: 无法解析，交由missing-reference事件处理
        raise NoUri: 抑制missing-reference事件
    """
```

引用解析流程：
1. 解析器将 `:py:func:\`greet\`` 转为 `pending_xref` 节点，refdomain='py'、reftype='func'、reftarget='greet'
2. SphinxCrossRefResolver Transform 查找 py domain
3. 调用 `py_domain.resolve_xref(env, docname, builder, 'func', 'greet', node, contnode)`
4. Domain 在自己的 data 中查找 greet 函数的位置
5. 找到 → 创建 `reference` 节点（含正确的refuri）返回
6. 找不到 → 返回 None
7. emit('missing-reference', ...) 给扩展最后机会
8. 仍未解析 → 根据 nitpicky 配置发出警告/错误

### resolve_any_xref：any角色的解析

`:any:\`target\`` 角色不知道目标的类型和域，Sphinx会遍历所有域调用 `resolve_any_xref()`，收集所有可能的解析结果。如果有多个结果，通常取第一个（可配置为弹出歧义提示）。

## get_objects：搜索索引

`get_objects()` 返回域中所有对象的描述元组 [F-042]：

```python
def get_objects(self) -> Iterable[tuple[str, str, str, str, str, int]]:
    """Yield (name, dispname, type, docname, anchor, priority) tuples."""
```

| 字段 | 说明 |
|------|------|
| `name` | 完全限定名（如`mymodule.MyClass.my_method`） |
| `dispname` | 显示名称（搜索结果中展示的名字） |
| `type` | 对象类型（对应`object_types`的key） |
| `docname` | 对象所在文档 |
| `anchor` | 对象的锚点ID |
| `priority` | 搜索优先级（0/1/2/-1） |

这些元组被HTML/EPUB等Builder用于生成全局对象索引和搜索数据。

## 标准域（std）详解

标准域（`std`）是最基础的域，提供通用的文档标记功能：

### 指令

| 指令 | 用途 |
|------|------|
| `.. label::` | 创建可引用的标签 |
| `.. ref::` | 引用目标 |
| `.. term::` | 术语表条目 |
| `.. option::` | 命令行选项描述 |
| `.. envvar::` | 环境变量描述 |
| `.. token::` | 语法标记描述 |
| `.. seealso::` | 参见块 |
| `.. rubric::` | 无编号标题 |
| `.. centered::` | 居中文本 |
| `.. deprecated::` | 弃用标记 |
| `.. versionadded::` | 版本新增标记 |
| `.. versionchanged::` | 版本变更标记 |
| `.. index::` | 索引条目 |
| `.. glossary::` | 术语表 |
| `.. contents::` | 目录 |
| `.. sectionauthor::` | 章节作者 |
| `.. codeauthor::` | 代码作者 |

### 角色

| 角色 | 用途 |
|------|------|
| `:ref:` | 引用标签 |
| `:doc:` | 引用文档 |
| `:term:` | 引用术语 |
| `:option:` | 引用命令行选项 |
| `:envvar:` | 引用环境变量 |
| `:token:` | 引用语法标记 |
| `:keyword:` | 引用Python关键字 |
| `:numref:` | 引用编号对象（图/表/代码块） |
| `:title:` | 引用文档标题 |

## Python域（py）核心类型

Python域是最常用的域，支持的对象类型包括：

| ObjType | 描述指令 | 引用角色 | 说明 |
|---------|---------|---------|------|
| module | `.. py:module::` | `:py:mod:` | 模块 |
| class | `.. py:class::` | `:py:class:` | 类 |
| exception | `.. py:exception::` | `:py:exc:` | 异常类 |
| function | `.. py:function::` | `:py:func:` | 函数 |
| method | `.. py:method::` | `:py:meth:` | 方法 |
| attribute | `.. py:attribute::` | `:py:attr:` | 属性 |
| data | `.. py:data::` | `:py:data:` | 模块级数据/常量 |
| property | `.. py:property::` | `:py:property:` | 属性(property) |
| decorator | `.. py:decorator::` | `:py:decorator:` | 装饰器 |

Python域的 `initial_data` 包含：
- `objects`：`{(fullname, objtype): (docname, anchor)}` 对象位置索引
- `modules`：`{modname: docname}` 模块索引
- `labels`：`{label: (docname, anchor, dispname)}` 标签索引
- `note_refnames` / `anonlabels` 等：交叉引用辅助索引

## 自定义 Domain

创建自定义Domain需要继承 `Domain` 类并实现必要的方法：

```python
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.roles import XRefRole

class MyLangDomain(Domain):
    name = 'mylang'
    label = 'MyLang'

    object_types = {
        'function': ObjType('function', 'func', 'obj'),
        'class': ObjType('class', 'class', 'obj'),
    }

    directives = {
        'function': MyLangFunction,  # 继承ObjectDescription
        'class': MyLangClass,
    }

    roles = {
        'func': XRefRole(),
        'class': XRefRole(),
    }

    initial_data = {
        'objects': {},  # fullname -> (docname, anchor, objtype)
    }

    data_version = 1

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        # 在self.data['objects']中查找target
        # 返回reference节点或None
        ...

    def get_objects(self):
        for fullname, (docname, anchor, objtype) in self.data['objects'].items():
            yield (fullname, fullname, objtype, docname, anchor, 1)

def setup(app):
    app.add_domain(MyLangDomain)
    return {'version': '1.0', 'parallel_read_safe': True}
```

## 设计洞察

1. **Domain作为微内核**：每个Domain本质上是一个自包含的"文档子系统"，管理自己的指令、角色、对象索引和引用解析。Domain之间互不干扰，通过 `:any:` 角色实现跨域搜索。

2. **适配器模式**：`role()` 和 `directive()` 方法通过动态创建包装类/闭包，将域前缀透明地注入到指令/角色执行中，实现了指令/角色实现的域无关性。

3. **data_version缓存失效**：每个Domain有独立的 `data_version`，与BuildEnvironment的 `ENV_VERSION` 形成双层版本控制，精确控制缓存失效范围。

4. **resolve_any_xref的"投票"机制**：any角色的解析不是简单的"第一个匹配"，而是收集所有域的候选结果，支持歧义检测和消歧。

5. **ObjType的角色绑定**：ObjType不仅定义"是什么"，还定义"怎么引用"——通过 `roles` 参数指定哪些角色可以引用该类型对象，形成了类型系统和引用系统的连接。

## 相关概念

- [组件注册中心](06-registry.md)
- [项目管理与 Docutils 集成](08-project-and-docutils.md)
- [Autodoc 自动文档生成](12-autodoc.md)
- [扩展开发详解](15-extension-development.md)
