---
type: "reference"
title: "扩展 setup 函数签名与返回值"
description: "Sphinx 扩展入口 setup 函数的规范签名、返回值元数据和 Extension 类"
tags: [extension, setup, metadata]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: "extension-class", resource: "sphinx/extension.py", title: "Extension class and setup" }
---

# 扩展 setup 函数签名与返回值

源码位置：`sphinx/extension.py`

## Extension 类

```python
class Extension:
    def __init__(self, name: str, module: Any, **kwargs: Any) -> None:
        self.name = name               # 扩展模块名（如 'sphinx.ext.autodoc'）
        self.module = module           # 已导入的模块对象
        self.metadata: ExtensionMetadata = kwargs
        self.version = kwargs.pop('version', 'unknown version')
        self.parallel_read_safe = kwargs.pop('parallel_read_safe', None)
        self.parallel_write_safe = kwargs.pop('parallel_write_safe', True)
```

## setup 函数规范

每个Sphinx扩展模块必须定义一个`setup`函数，Sphinx在加载扩展时调用它：

```python
def setup(app: Sphinx) -> ExtensionMetadata:
    """扩展入口函数。

    Args:
        app: Sphinx应用实例，通过其add_*方法注册组件

    Returns:
        字典，包含扩展元数据
    """
    # 注册组件
    app.add_config_value(...)
    app.add_directive(...)
    app.add_role(...)
    app.connect('event-name', callback)
    # ...

    return {
        'version': '1.0',               # 扩展版本号
        'parallel_read_safe': True,     # 是否支持并行读取（默认None=警告）
        'parallel_write_safe': True,    # 是否支持并行写入（默认True）
    }
```

## ExtensionMetadata 类型

`ExtensionMetadata` 是 `dict[str, Any]` 的类型别名，支持的键：

| 键 | 类型 | 默认值 | 说明 |
|---|------|-------|------|
| `version` | `str` | `'unknown version'` | 扩展版本字符串 |
| `parallel_read_safe` | `bool \| None` | `None` | 是否可以在子进程中并行读取源文件。None表示未声明，会触发警告 |
| `parallel_write_safe` | `bool` | `True` | 是否可以在子进程中并行写入文档 |

## app.add_* 注册方法速查

Sphinx应用提供的组件注册API：

| 方法 | 注册内容 |
|------|---------|
| `app.add_builder(builder_cls, override=False)` | 构建器 |
| `app.add_config_value(name, default, rebuild, types, description)` | 配置项 |
| `app.add_event(name)` | 自定义事件 |
| `app.add_node(node, **kwargs)` | Docutils节点 + visitor处理函数 |
| `app.add_enumerable_node(node, figtype, title_getter, **kwargs)` | 可编号节点 |
| `app.add_directive(name, directive_cls, override=False)` | 指令 |
| `app.add_role(name, role, override=False)` | 角色 |
| `app.add_generic_role(name, nodeclass, override=False)` | 通用角色 |
| `app.add_domain(domain_cls, override=False)` | 域 |
| `app.add_directive_to_domain(domain, name, cls, override=False)` | 域内指令 |
| `app.add_role_to_domain(domain, name, role, override=False)` | 域内角色 |
| `app.add_index_to_domain(domain, index_cls)` | 域内索引 |
| `app.add_object_type(directivename, rolename, indextemplate, ...)` | 对象类型（同时注册指令+角色） |
| `app.add_crossref_type(directivename, rolename, indextemplate, ...)` | 交叉引用类型 |
| `app.add_transform(transform_cls)` | Docutils Transform |
| `app.add_post_transform(transform_cls)` | Docutils PostTransform |
| `app.add_js_file(filename, priority, loading_method, **kwargs)` | JavaScript文件 |
| `app.add_css_file(filename, priority, **kwargs)` | CSS文件 |
| `app.add_latex_package(packagename, options)` | LaTeX包 |
| `app.connect(event, callback, priority=500)` | 事件监听器（返回listener_id） |
| `app.disconnect(listener_id)` | 断开事件监听器 |
| `app.require_sphinx(version)` | 最低Sphinx版本要求 |
| `app.set_translator(name, translator_class, override=False)` | 设置Translator |
| `app.setup_extension(extname)` | 加载另一个扩展 |

## 版本检查

```python
# 在setup中检查Sphinx版本
from sphinx import __version__
from packaging.version import Version

def setup(app):
    app.require_sphinx('5.0')  # 需要Sphinx >= 5.0
    # 或使用静态方法
    # Sphinx.require_sphinx((5, 0))
    ...
    return {'version': '1.0', 'parallel_read_safe': True}
```
