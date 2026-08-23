---
type: "example"
title: "使用Autodoc生成API文档"
description: "实战——配置autodoc/napoleon扩展、automodule/autoclass指令、docstring风格(Google/NumPy)、autodoc事件钩子定制输出"
tags: [example, autodoc, api-doc, docstring, napoleon]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: autodoc-concept
    resource: /concepts/12-autodoc.md
    title: "Autodoc自动文档生成概念"
---

# 使用Autodoc生成API文档

本示例演示如何使用 `sphinx.ext.autodoc` 和 `sphinx.ext.napoleon` 从Python代码的docstring自动生成API文档。

## 前置知识

- 完成 [5分钟快速上手](../concepts/01-getting-started.md)
- 了解Python docstring基本格式
- 阅读 [Autodoc 自动文档生成](../concepts/12-autodoc.md)

## 项目结构

我们使用以下项目结构：

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core.py          # 要文档化的代码
│       └── utils.py
├── docs/
│   ├── conf.py
│   ├── index.rst
│   ├── api/                 # API文档
│   │   └── index.rst
│   └── _static/
└── pyproject.toml
```

## 步骤1：安装依赖

```bash
pip install sphinx sphinx-autodoc-typehints
```

## 步骤2：编写有docstring的代码

```python
# src/mypackage/core.py
from typing import Optional


class Calculator:
    """一个简单的计算器类。

    支持基本的算术运算，并保存计算历史。

    Attributes:
        history: 计算历史记录列表
        precision: 浮点数精度位数

    Example:
        >>> calc = Calculator(precision=2)
        >>> calc.add(1.5, 2.3)
        3.8
        >>> calc.multiply(2, 3)
        6
    """

    def __init__(self, precision: int = 4):
        """初始化计算器。

        Args:
            precision: 浮点数显示精度，默认4位小数
        """
        self.precision = precision
        self.history: list[tuple[str, float]] = []

    def add(self, a: float, b: float) -> float:
        """加法运算。

        Args:
            a: 第一个操作数
            b: 第二个操作数

        Returns:
            两数之和，保留指定精度

        Example:
            >>> c = Calculator()
            >>> c.add(1, 2)
            3.0
        """
        result = round(a + b, self.precision)
        self.history.append(('add', result))
        return result

    def divide(self, a: float, b: float) -> float:
        """除法运算。

        Args:
            a: 被除数
            b: 除数（不能为零）

        Returns:
            a / b 的结果

        Raises:
            ZeroDivisionError: 当b为0时抛出
            ValueError: 当a或b不是数字时抛出
        """
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        result = round(a / b, self.precision)
        self.history.append(('divide', result))
        return result


def greet(name: str, greeting: str = "Hello") -> str:
    """生成问候语。

    Args:
        name: 要问候的人名
        greeting: 问候语前缀，默认为"Hello"

    Returns:
        完整的问候字符串

    Example:
        >>> greet("World")
        'Hello, World!'
        >>> greet("Alice", "Hi")
        'Hi, Alice!'
    """
    return f"{greeting}, {name}!"
```

## 步骤3：配置conf.py

```python
# docs/conf.py
import os
import sys
from pathlib import Path

# 将src目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

project = 'MyPackage'
copyright = '2026, Your Name'
author = 'Your Name'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',        # 核心autodoc扩展
    'sphinx.ext.napoleon',       # Google/NumPy风格docstring支持
    'sphinx.ext.viewcode',       # 链接到源代码
    'sphinx.ext.autosummary',    # 自动生成API摘要
    'sphinx_autodoc_typehints',  # 类型提示支持（第三方包）
    'sphinx.ext.doctest',        # 测试docstring中的示例代码
]

# Autodoc配置
autodoc_default_options = {
    'members': True,             # 显示所有成员
    'member-order': 'bysource',  # 按源码顺序排列
    'undoc-members': False,      # 不显示没有docstring的成员
    'show-inheritance': True,    # 显示继承关系
    'special-members': '__init__',  # 显示__init__方法
    'exclude-members': '__weakref__',  # 排除的成员
}

# autodoc类型
autodoc_typehints = 'description'  # 在描述中显示类型注解
autodoc_class_signature = 'separated'
autodoc_type_aliases = {}

# Napoleon配置（Google风格docstring）
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# Autosummary配置
autosummary_generate = True
autosummary_generate_overwrite = True

# HTML主题
html_theme = 'furo'
```

## 步骤4：编写API文档

```rst
.. docs/api/index.rst

API 参考
========

.. automodule:: mypackage
   :no-index:

Calculator类
------------

.. autoclass:: mypackage.core.Calculator
   :members: add, divide
   :special-members: __init__

函数
----

.. autofunction:: mypackage.core.greet
```

在 `docs/index.rst` 中引用API文档：

```rst
欢迎使用 MyPackage
==================

.. toctree::
   :maxdepth: 2
   :caption: 目录

   api/index

快速开始
========

.. code-block:: python

   from mypackage.core import Calculator, greet

   calc = Calculator()
   print(greet("World"))
   print(calc.add(1, 2))
```

## 步骤5：使用sphinx-apidoc自动生成骨架

对于大型包，可以使用 `sphinx-apidoc` 自动生成所有模块的 `.rst` 文件：

```bash
sphinx-apidoc -o docs/api src/mypackage \
    --separate \
    --module-first \
    --force \
    --no-toc
```

参数说明：
- `-o docs/api`：输出目录
- `src/mypackage`：Python包路径
- `--separate`：每个模块单独页面
- `--module-first`：模块文档在子模块之前
- `--force`：覆盖已有文件

## 步骤6：使用autodoc事件定制输出

使用事件钩子可以修改autodoc的输出行为：

```python
# docs/conf.py（添加到末尾）

def skip_member(app, what, name, obj, skip, options):
    """跳过内部方法"""
    if name.startswith('_internal_'):
        return True
    return None  # 返回None表示使用默认判断

def process_docstring(app, what, name, obj, options, lines):
    """处理docstring：添加版本标记"""
    if what == 'class' and hasattr(obj, '_added_in_version'):
        lines.append(f'.. versionadded:: {obj._added_in_version}')

def process_signature(app, what, name, obj, options, signature, return_annotation):
    """处理函数签名：隐藏复杂类型"""
    if signature and 'ContextManager' in signature:
        # 简化签名显示
        return signature.replace('ContextManager[Iterator[T]]', 'ContextManager'), return_annotation
    return None

def setup(app):
    app.connect('autodoc-skip-member', skip_member)
    app.connect('autodoc-process-docstring', process_docstring)
    app.connect('autodoc-process-signature', process_signature)
```

## 步骤7：构建并验证

```bash
# 构建文档
sphinx-build -b html docs docs/_build/html

# 运行docstring中的代码示例测试
sphinx-build -b doctest docs docs/_build/doctest
```

## autodoc指令选项速查

| 选项 | 作用 |
|------|------|
| `:members:` | 显示所有公共成员 |
| `:members: f1, f2` | 只显示指定成员 |
| `:undoc-members:` | 显示没有docstring的成员 |
| `:private-members:` | 显示私有成员（_开头） |
| `:special-members:` | 显示特殊成员（__开头） |
| `:inherited-members:` | 显示继承的成员 |
| `:show-inheritance:` | 显示基类列表 |
| `:member-order: bysource` | 按源码顺序排列 |
| `:member-order: alphabetical` | 按字母顺序排列 |
| `:member-order: groupwise` | 按类型分组排列 |
| `:exclude-members: a, b` | 排除指定成员 |
| `:no-index:` | 不生成索引项 |
| `:synopsis: 描述` | 模块简介 |
| `:platform: 平台` | 平台信息 |
| `:deprecated:` | 标记为已弃用 |

## 常见问题解决

### ImportError

如果autodoc无法导入你的模块：
1. 确保 `sys.path.insert` 指向正确的目录
2. 检查包是否可pip安装（`pip install -e .`）
3. 使用 `autodoc_mock_imports` 模拟无法安装的依赖：

```python
autodoc_mock_imports = ['torch', 'tensorflow', 'numpy']
```

### 类型注解显示不美观

安装 `sphinx-autodoc-typehints` 包：
```bash
pip install sphinx-autodoc-typehints
```
并添加到extensions列表。

### 中文docstring

确保Python源文件使用UTF-8编码（默认即可），在conf.py中设置：
```python
language = 'zh_CN'
```

## 相关资源

- [Autodoc 自动文档生成](../concepts/12-autodoc.md)
- [编写第一个Sphinx扩展](01-first-extension.md)
- [Intersphinx 跨项目引用](../concepts/14-intersphinx.md)
