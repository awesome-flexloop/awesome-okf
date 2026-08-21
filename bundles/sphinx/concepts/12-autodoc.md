---
type: "concept"
title: "Autodoc 自动文档生成"
description: "sphinx.ext.autodoc从Python docstring自动提取文档、autoclass/automodule/autofunction指令、Documenter体系、autodoc_default_options配置"
tags: [extension, autodoc, docstring, python, api-doc]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: autodoc-py
    resource: sphinx/ext/autodoc/
    title: "sphinx.ext.autodoc module"
---

# Autodoc 自动文档生成

`sphinx.ext.autodoc` 是 Sphinx 最常用的内置扩展之一，它能够从 Python 模块的 docstring 中自动提取文档内容，将代码注释直接渲染为格式化的API文档，避免了文档与代码不同步的问题。

## 核心指令

Autodoc 提供了一组 auto 指令，每个对应 Python 域中的一种对象类型 [F-052]：

| 指令 | 对应py域指令 | 文档化内容 |
|------|-------------|-----------|
| `.. automodule::` | `.. py:module::` | 模块（包含其成员） |
| `.. autoclass::` | `.. py:class::` | 类（包含方法/属性） |
| `.. autoexception::` | `.. py:exception::` | 异常类 |
| `.. autofunction::` | `.. py:function::` | 函数 |
| `.. autodecorator::` | `.. py:decorator::` | 装饰器 |
| `.. automethod::` | `.. py:method::` | 方法（在autoclass内部使用） |
| `.. autoattribute::` | `.. py:attribute::` | 属性（在autoclass内部使用） |
| `.. autodata::` | `.. py:data::` | 模块级数据 |

### 基本用法

```rst
.. automodule:: mypackage.mymodule
   :members:                    # 显示所有公共成员
   :undoc-members:              # 也显示没有docstring的成员
   :show-inheritance:           # 显示继承关系
   :inherited-members:         # 显示继承的成员
   :private-members:           # 显示以下划线开头的私有成员
   :special-members: __init__  # 显示特殊成员（如__init__）
   :member-order: bysource     # 成员排序：alphabetical/bysource/groupwise
   :exclude-members: secret    # 排除特定成员
   :no-index:                  # 不为这些条目生成索引项
   :synopsis: Short description  # 模块摘要（仅用于模块列表）
   :platform: Platform info     # 平台信息
   :deprecated:                 # 标记为已弃用
```

### 自动类文档示例

```rst
.. autoclass:: mypackage.MyClass
   :members: hello, goodbye
   :special-members: __init__
   :show-inheritance:
```

这将导入 `mypackage.MyClass`，提取其docstring和 `hello`、`goodbye` 方法的docstring，以及 `__init__` 方法，生成包含类签名、描述、方法列表和继承关系的完整文档。

## Documenter 体系

Autodoc 使用 Documenter 类体系来处理不同类型的Python对象 [F-053]。每个Documenter子类负责一种对象类型：

| Documenter类 | 处理对象 | 注册名 |
|-------------|---------|--------|
| `ModuleDocumenter` | 模块 | `'module'` |
| `ClassDocumenter` | 类 | `'class'` |
| `ExceptionDocumenter` | 异常 | `'exception'` |
| `FunctionDocumenter` | 函数 | `'function'` |
| `DecoratorDocumenter` | 装饰器 | `'decorator'` |
| `MethodDocumenter` | 方法 | `'method'` |
| `AttributeDocumenter` | 属性/数据 | `'attribute'`/`'data'` |
| `PropertyDocumenter` | property | `'property'` |

Documenter通过 `app.add_documenter(objtype, documenter_class)` 注册到registry，扩展可以注册自定义Documenter来支持新的对象类型。

### Documenter 核心方法

```python
class Documenter:
    objtype = ''        # 对象类型名
    directivetype = ''  # 对应的指令类型
    priority = 0        # 优先级（决定多个Documenter匹配时的选择顺序）

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent) -> bool:
        """判断此Documenter能否文档化给定成员"""

    def import_object(self) -> bool:
        """导入目标对象，设置self.object"""

    def add_directive_header(self, sig) -> None:
        """生成指令头部（签名行）"""

    def add_content(self, more_content) -> None:
        """生成文档内容（docstring）"""

    def get_doc(self) -> list[list[str]] | None:
        """获取docstring行列表"""

    def filter_members(self, members, want_all) -> list[tuple]:
        """过滤成员列表"""
```

## autodoc 默认选项

`autodoc_default_options` 配置项为所有autodoc指令设置默认选项 [F-054]：

```python
# conf.py
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '',
    'inherited-members': False,
    'show-inheritance': True,
    'member-order': 'bysource',
    'exclude-members': '__weakref__',
    'ignore-module-all': False,
    'imported-members': False,
    'autoclass_content': 'class',  # 'class'/'init'/'both'
}
```

`autoclass_content` 控制类文档的内容来源：
- `'class'`：只使用类docstring（默认）
- `'init'`：只使用 `__init__` 的docstring
- `'both'`：类和 `__init__` docstring合并

## Docstring 风格支持

Autodoc 原生支持 Google风格和NumPy风格的docstring（通过 `sphinx.ext.napoleon` 扩展）：

```python
# Google风格
def greet(name: str, greeting: str = "Hello") -> str:
    """向用户问好。

    Args:
        name: 用户姓名
        greeting: 问候语，默认为"Hello"

    Returns:
        完整的问候字符串

    Raises:
        ValueError: 如果name为空
    """
    if not name:
        raise ValueError("name cannot be empty")
    return f"{greeting}, {name}!"
```

启用napoleon扩展：
```python
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
```

## Autodoc 工作原理

Autodoc 在构建时实际**导入**Python模块来获取docstring，因此：

1. **路径设置**：需要在conf.py中通过 `sys.path.insert(0, os.path.abspath('../src'))` 将包目录加入Python路径
2. **代码执行**：模块顶层代码会被执行（类似`import`），有副作用的代码需要用 `if __name__ == '__main__'` 保护
3. **mock导入**：对于无法安装的依赖（如C扩展），使用 `autodoc_mock_imports` 配置模拟导入

### 关键事件

| 事件 | 回调签名 | 用途 |
|------|---------|------|
| `autodoc-process-docstring` | `(app, what, name, obj, options, lines)` | 处理docstring行（可以修改） |
| `autodoc-before-process-signature` | `(app, obj, bound_method)` | 签名处理前 |
| `autodoc-process-signature` | `(app, what, name, obj, options, signature, return_annotation)` | 处理签名 |
| `autodoc-skip-member` | `(app, what, name, obj, skip, options) → bool` | 决定是否跳过某个成员 |

### autodoc-process-docstring 示例

```python
def process_docstring(app, what, name, obj, options, lines):
    """将docstring中的特定标记替换为格式化内容"""
    for i, line in enumerate(lines):
        if ':my-tag:' in line:
            lines[i] = line.replace(':my-tag:', '**My Tag:**')

app.connect('autodoc-process-docstring', process_docstring)
```

## autosummary：自动生成API摘要

`sphinx.ext.autosummary` 扩展提供 `.. autosummary::` 指令，可以自动生成函数/类/方法的摘要表格，并可选生成存根（stub）页面：

```rst
.. autosummary::
   :toctree: generated

   mypackage.MyClass
   mypackage.my_function
```

配置 `autosummary_generate = True` 后，Sphinx会自动为每个条目生成独立的 `.rst` 存根页面。

## sphinx-apidoc：自动生成API骨架

`sphinx-apidoc` 命令行工具可以自动扫描Python包并生成完整的 `.rst` 文件骨架：

```bash
sphinx-apidoc -o docs/source/api src/mypackage --separate --module-first
```

| 参数 | 说明 |
|------|------|
| `-o` | 输出目录 |
| `--separate` | 每个模块单独页面 |
| `--module-first` | 模块文档在子模块之前 |
| `-f` | 覆盖已有文件 |
| `-e` | 为每个模块生成独立页面 |
| `--tocfile` | TOC文件名 |

## 注意事项与最佳实践

1. **导入错误处理**：确保所有依赖在文档构建环境中可用，或使用 `autodoc_mock_imports`
2. **性能**：大型项目中autodoc导入所有模块可能很慢，考虑使用 `--jobs N` 并行构建
3. **类型提示**：Sphinx 7+ 原生支持PEP 484类型提示，不需要 `sphinx-autodoc-typehints` 扩展的部分功能
4. **docstring编码**：确保Python源文件使用UTF-8编码（默认即可）
5. **相对导入**：autodoc需要正确的包结构，避免在脚本目录直接运行
6. **类型注解**：autodoc会自动从类型注解中提取参数和返回值类型

## 相关概念

- [Domain 领域系统](09-domain-system.md)
- [扩展开发详解](15-extension-development.md)
- [Intersphinx 跨项目引用](14-intersphinx.md)
- [使用Autodoc生成API文档](../examples/03-autodoc-api.md)
