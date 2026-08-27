---
type: Concept
title: 配置系统
description: FPS声明式配置系统详解，包括JSON配置格式、CLI参数覆盖、Pydantic类型校验、配置合并规则和help-all文档生成。
tags: [configuration, cli, json, pydantic, merge, entry-points]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:52:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:52:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-config-py
    resource: /references/config-source.md
    title: src/fps/_config.py and src/fps/_importer.py
  - id: fps-cli-py
    resource: /references/cli-source.md
    title: src/fps/cli/_cli.py
---

## 配置格式

FPS应用可以通过Python字典或JSON文件声明式配置。配置字典的结构：

```json
{
  "root_module_name": {
    "type": "module.path:ClassName",
    "config": {
      "param1": "value1",
      "param2": 42
    },
    "modules": {
      "sub_module_name": {
        "type": "package.module:SubClass",
        "config": {
          "sub_param": "sub_value"
        },
        "modules": {}
      }
    }
  }
}
```

### type字段的三种格式

`type` 字段支持三种模块引用方式：

| 格式 | 示例 | 说明 |
|------|------|------|
| Python路径 | `"fps.web.fastapi:FastAPIModule"` | `模块路径:类名`，通过importlib导入 |
| Entry-point名称 | `"fps_module"` | 在 `fps.modules` entry-points组中注册的名称 |
| 省略type | 子模块在父模块`add_module()`中已指定type时可省略 | 仅用于子模块覆盖配置 |

内置entry-point `"fps_module"` 指向 `fps:Module` 基类本身，可用作纯容器模块。

### 运行JSON配置

```bash
fps --config config.json
```

配置文件中可以有多个顶层模块，通过CLI参数指定哪个作为根模块运行：

```bash
fps --config config.json module_name
```

## CLI参数覆盖

使用 `--set` 参数可以覆盖配置中的任意参数，支持点分路径定位嵌套模块：

```bash
fps --config config.json --set server.port=8080 --set server.host=0.0.0.0
```

点分路径解析规则：最后一段是参数名，前面的部分逐级定位到子模块。例如：
- `greeting="Hello"` → 设置根模块config的greeting参数
- `server.port=8080` → 设置根模块的server子模块config的port参数
- `server.auth.timeout=30` → 设置server.auth子模块config的timeout参数

不使用 `--config` 时也可以直接使用 `--set`：

```bash
fps simple:Main --set greeting=Hi --set farewell=Bye
```

如果 `--set` 参数中没有 `=`，会抛出click异常：`No '=' while setting a module parameter`。

## Pydantic配置校验

推荐使用Pydantic BaseModel定义模块配置，获得自动类型校验和转换：

```python
from pydantic import BaseModel
from fps import Module

class RouterConfig(BaseModel):
    key: str = "count"
    value: int = 3

class Router(Module):
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.config = RouterConfig(**kwargs)
```

配置传入错误类型时，Pydantic会在模块实例化时抛出清晰的校验错误：

```bash
fps server:Main --set router.value=foo
# RuntimeError: Cannot instantiate module 'root_module.router': 1 validation error for Config
# value
#   Input should be a valid integer, unable to parse string as an integer [type=int_parsing, ...]
```

错误信息由 `initialize()` 捕获并包装，明确指出是哪个模块实例化失败。

## get_root_module与initialize

配置的处理分为两步：

### get_root_module

```python
from fps._config import get_root_module

root_module = get_root_module(config_dict)
```

`get_root_module()` 读取config字典第一项作为根模块：
1. 通过 `import_from_string()` 导入根模块类型
2. 以module_name和module_config实例化根模块
3. 将子模块配置存入根模块的 `_uninitialized_modules`
4. 不递归实例化子模块（由initialize完成）

### initialize

```python
from fps import initialize

actual_config = initialize(root_module)
```

`initialize()` 递归实例化整个模块树：
1. 提取模块 `__init__` 中有默认值的参数（通过 `inspect.signature`）
2. 合并config中的覆盖值
3. 实例化子模块，设置parent关系
4. 递归处理孙模块
5. 返回实际配置字典（含默认值）

## merge_config配置合并

```python
from fps._config import merge_config

merged = merge_config(base_config, override_config)
```

合并规则：
- 对root调用先做 `deepcopy`（不修改原始config）
- 两边都有的key：都是dict则递归合并，否则override覆盖base
- 仅在override中的key：直接添加
- 仅在base中的key：保持不变

## dump_config配置导出

```python
from fps._config import dump_config

config_str = dump_config(actual_config)
```

将配置字典转换为 `module.param=value` 格式的扁平文本，每行一个参数。CLI使用 `--show-config` 时调用此函数输出：

```bash
fps myapp:Main --show-config
# [info    ] Configuration root_module.param1=value1
# [info    ] Configuration root_module.sub.param2=value2
```

## get_config_description配置文档

当模块使用Pydantic BaseModel作为config时（`self.config = ConfigModel(...)`），框架可以自动生成配置文档：

```python
from fps._config import get_config_description

desc = get_config_description(root_module)
print(desc)
```

输出格式：
```
root_module.param1: 参数标题
    Default: 默认值
    Type: 类型注解
    Description: 参数描述
root_module.sub.param2: ...
```

CLI的 `--help-all` 选项调用此函数，用户可以直接查看所有可配置参数：

```bash
fps --config config.json --help-all
```

## 动态导入（import_from_string）

```python
from fps._importer import import_from_string
```

`import_from_string()` 是FPS模块加载的核心，支持：

### 非字符串值

直接返回原值（允许传入类对象本身）：

```python
import_from_string(MyModule)  # 返回 MyModule 类本身
```

### Entry-point查找（无冒号）

```python
import_from_string("fps_module")
# 在 "fps.modules" entry-points组中查找名为"fps_module"的entry-point，加载并返回
```

第三方包可以在 `pyproject.toml` 中注册自己的entry-point：

```toml
[project.entry-points."fps.modules"]
my_plugin = "my_package.plugin:MyPluginModule"
```

安装后即可在配置中使用 `"type": "my_plugin"` 引用。

### Python路径导入（含冒号）

```python
import_from_string("fps.web.fastapi:FastAPIModule")
# 等效于 from fps.web.fastapi import FastAPIModule
```

支持多级属性访问：

```python
import_from_string("my_package.sub:Class.NestedClass")
# 等效于 from my_package.sub import Class; return Class.NestedClass
```

## 相关概念

- [安装与快速开始](01-getting-started.md)
- [模块系统](02-module-system.md)
- [插件架构](08-plugin-architecture.md)
- [声明式配置应用](../examples/04-declarative-config.md)
