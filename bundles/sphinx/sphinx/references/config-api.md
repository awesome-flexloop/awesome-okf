---
type: "reference"
title: Sphinx 配置系统 API 参考
description: Config类、_Opt类、ENUM类和ConfigValue的API参考。
tags: [sphinx, api, config, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config-py
    resource: /references/config-api.md
    title: sphinx/config.py 源码
---
# Sphinx 配置系统 API 参考

配置系统定义在`sphinx/config.py`，配置文件名固定为`conf.py`（`CONFIG_FILENAME`）。

## 常量

| 常量 | 值 | 说明 |
|------|------|------|
| `CONFIG_FILENAME` | `'conf.py'` | 配置文件名 |
| `UNSERIALIZABLE_TYPES` | `(type, ModuleType, FunctionType)` | 不可序列化的类型 |

## ENUM 类

```python
class ENUM:
    def __init__(self, *candidates: str | bool | None) -> None: ...
    def match(self, value: str | bool | None | Sequence) -> bool: ...
```

用于配置值的枚举验证。示例：

```python
app.add_config_value('latex_show_urls', 'no', None, ENUM('no', 'footnote', 'inline'))
```

## _Opt 类

```python
class _Opt:
    __slots__ = 'default', 'rebuild', 'valid_types', 'description'
    default: Any
    rebuild: _ConfigRebuild
    valid_types: frozenset[type] | ENUM
    description: str
```

配置选项的内部表示，immutable设计。

## ConfigValue

```python
class ConfigValue(NamedTuple):
    name: str
    value: Any
    rebuild: _ConfigRebuild
```

## _ConfigRebuild 类型

字符串字面量类型，控制配置变更触发的重建级别：

| 值 | 触发重建级别 |
|------|------|
| `''` | 无需特殊重建 |
| `'env'` | 需要重建整个环境（重新解析所有文档） |
| `'html'` | 需要重建HTML文档 |
| `'epub'` | 需要重建epub |
| `'gettext'` | 需要重建gettext消息目录 |
| `'applehelp'` | 需要重建applehelp |
| `'devhelp'` | 需要重建devhelp |

## Config 类关键方法

| 方法 | 说明 |
|------|------|
| `Config.read(confdir, overrides, tags) -> Config` | 类方法，从conf.py读取配置 |
| `Config(configs, overrides) -> Config` | 构造函数 |
| `add(name, default, rebuild, types, description)` | 注册新配置值 |
| `_report_override_warnings()` | 报告overrides中无效配置的警告 |

## 通过Sphinx注册配置

```python
def setup(app):
    app.add_config_value(
        name='myext_setting',
        default='default_value',
        rebuild='env',  # 变更时重建环境
        types=[str],    # 类型验证
        description='My extension setting'
    )
```

## 动态默认值

`default`参数可以是callable，接收config对象为参数，实现依赖其他配置的动态默认值：

```python
def _default_my_setting(config):
    return config.project + '_suffix'

app.add_config_value('my_setting', _default_my_setting, 'html')
```
