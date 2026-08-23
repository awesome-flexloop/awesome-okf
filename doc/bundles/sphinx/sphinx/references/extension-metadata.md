---
type: "reference"
title: Sphinx 扩展元数据格式参考
description: Extension类和setup()函数返回的元数据格式。
tags: [sphinx, api, extension, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension-py
    resource: /references/extension-metadata.md
    title: sphinx/extension.py 源码
---
# Sphinx 扩展元数据格式参考

扩展相关类定义在`sphinx/extension.py`。

## Extension 类

```python
class Extension:
    def __init__(self, name: str, module: Any, **kwargs: Any) -> None:
        self.name = name
        self.module = module
        self.metadata: ExtensionMetadata = kwargs
        self.version = kwargs.pop('version', 'unknown version')
        self.parallel_read_safe = kwargs.pop('parallel_read_safe', None)
        self.parallel_write_safe = kwargs.pop('parallel_write_safe', True)
```

### 属性说明

| 属性 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| `name` | `str` | - | 扩展名（模块路径） |
| `module` | `Any` | - | 扩展模块对象 |
| `version` | `str` | `'unknown version'` | 扩展版本 |
| `parallel_read_safe` | `bool | None` | `None` | 是否支持并行读取。None时Sphinx会发出警告 |
| `parallel_write_safe` | `bool` | `True` | 是否支持并行写入 |

## setup() 函数返回格式

每个Sphinx扩展模块必须实现`setup(app)`函数，返回`ExtensionMetadata`字典：

```python
def setup(app: Sphinx) -> dict[str, Any]:
    # 注册组件、连接事件...
    return {
        'version': '1.0.0',                    # 必填，扩展版本
        'parallel_read_safe': True,            # 可选，默认None（会警告）
        'parallel_write_safe': True,           # 可选，默认True
    }
```

### 元数据字段

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `version` | `str` | ✅ | - | 扩展版本字符串 |
| `parallel_read_safe` | `bool` | ❌ | `None` | 并行读取安全标记 |
| `parallel_write_safe` | `bool` | ❌ | `True` | 并行写入安全标记 |

## 版本要求检查

通过`app.require_sphinx(version)`声明最低Sphinx版本要求：

```python
def setup(app):
    app.require_sphinx('5.0')  # 需要Sphinx >= 5.0
    # 或元组形式：app.require_sphinx((5, 0))
    ...
```

通过`needs_extensions`配置项声明对其他扩展的版本依赖：

```python
# conf.py
needs_extensions = {'sphinx.ext.autodoc': '4.0'}
```
