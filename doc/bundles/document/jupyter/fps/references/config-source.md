---
type: Reference
title: fps._config 与 fps._importer 源码信源
description: fps配置系统（get_root_module/merge_config）和动态导入系统的源码登记，对应src/fps/_config.py和src/fps/_importer.py
tags: [core, config, import, entry-points]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:50:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-config-py
    resource: /references/config-source.md
    title: src/fps/_config.py and src/fps/_importer.py
---

## 源码位置

- `src/fps/_config.py` — 配置系统，约85行
- `src/fps/_importer.py` — 动态字符串导入，约45行

## _config.py 导出API

| API | 签名 | 行号 |
|-----|------|------|
| `get_root_module()` | `(config: dict[str, Any]) -> Module` | L10 |
| `merge_config()` | `(config: dict, override: dict, root: bool=True) -> dict` | L34 |
| `dump_config()` | `(config: dict) -> str` | L50 |
| `get_config_description()` | `(root_module: Module) -> str` | L67 |

## _importer.py 导出API

| API | 签名 | 行号 |
|-----|------|------|
| `ImportFromStringError` | `class ImportFromStringError(Exception)` | L9 |
| `import_from_string()` | `(import_str: Any) -> Any` | L13 |

## 核心机制

### get_root_module 配置格式

config字典结构：
```python
{
    "module_name": {
        "type": "module.path:ClassName"  # 或 entry-point 名称
        "config": {  # 传给 __init__ 的 kwargs
            "param1": value1,
        },
        "modules": {  # 子模块
            "sub_name": {
                "type": "...",
                "config": {...},
                "modules": {...}
            }
        }
    }
}
```

- `get_root_module`只取config字典的第一项作为根模块
- 子模块的type/config/modules被存入`_uninitialized_modules`，由`initialize()`递归实例化

### import_from_string 三种导入模式

1. **非字符串**：直接返回原值（允许传入类对象本身）
2. **无冒号字符串**（如`"fps_module"`）：在`"fps.modules"` entry-points组中按名称查找
3. **含冒号字符串**（如`"fps.web.fastapi:FastAPIModule"`）：分割为模块路径和属性路径
   - 先`importlib.import_module(module_str)`导入模块
   - 再按`.`分割逐级`getattr`获取嵌套属性

### merge_config 合并规则

- root=True时先对config做deepcopy（不修改原dict）
- 两个dict中都存在的key：如果两边都是dict则递归合并，否则override覆盖config
- 仅在override中存在的key：直接添加到config
