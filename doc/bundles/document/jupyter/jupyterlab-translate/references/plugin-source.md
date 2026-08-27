---
type: Reference
title: Hatch构建钩子源码映射
description: jupyterlab-translate Hatch Build Hook插件（plugin.py）的构建时编译逻辑
tags: [hatch, build-hook, plugin, wheel, compile]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-source
    resource: /references/plugin-source.md
    title: plugin.py 和 hooks.py 源码
---

# Hatch构建钩子源码映射

本文档记录 `jupyterlab_translate/plugin.py` 和 `jupyterlab_translate/hooks.py` 的构建钩子实现。

## 模块信息

- **源文件**：`jupyterlab_translate/plugin.py`, `jupyterlab_translate/hooks.py`
- **基类**：`hatchling.builders.hooks.plugin.interface.BuildHookInterface`
- **注册入口**：`hatch_register_build_hook()` 在hooks.py中

## 常量

| 常量 | 值 | 源码行 | 说明 |
|------|-----|--------|------|
| `COMPILATION_THRESHOLD` | `0` | plugin.py第17行 | PO文件编译最小翻译百分比阈值 |
| `PACKAGE_PREFIX` | `"jupyterlab_language_pack_"` | plugin.py第18行 | 语言包Python包名前缀 |
| `PLUGIN_NAME` | `"jupyter-translate"` | plugin.py第24行 | Hatch插件名称 |

## 类：JupyterLanguageBuildHook

| 方法 | 签名 | 源码行 | 触发时机 | 功能 |
|------|------|--------|---------|------|
| `_get_locale_name` | `() -> tuple[Path, str]` | 第26-41行 | 内部方法 | 发现语言包目录和locale名称 |
| `clean` | `(versions: list[str]) -> None` | 第43-55行 | hatch build -c/--clean 或 hatch clean | 删除所有.json和.mo编译产物 |
| `initialize` | `(version: str, build_data: dict[str, Any]) -> None` | 第57-98行 | 每次构建前 | wheel构建时编译PO→MO/JSON；非wheel时更新贡献者 |

## 构建行为差异

### Wheel构建（target_name == "wheel"）

1. 发现messages_folder中所有.po文件
2. 对每个PO文件检查翻译百分比（`po.percent_translated()`）
3. 如果百分比 >= COMPILATION_THRESHOLD（默认0，即全部编译），调用 `compile_po_file()`
4. compile_po_file同时生成.json和.mo文件
5. wheel中包含.json和.mo，排除.po文件

### 非Wheel构建（如sdist）

1. 如果设置了CROWDIN_API_KEY环境变量，更新CONTRIBUTORS.md
2. sdist中保留.po源文件，不包含编译产物

## hooks.py注册

```python
@hookimpl
def hatch_register_build_hook():
    return JupyterLanguageBuildHook
```

Entry point注册（pyproject.toml）：
```toml
[project.entry-points.hatch]
jupyter-translate = "jupyterlab_translate.hooks"
```

## 相关概念

- [Hatch构建钩子集成](../concepts/07-hatch-build-hook.md)
- [翻译目录管理](../concepts/05-catalog-management.md)
- [Jed JSON翻译格式](../concepts/06-json-jed-format.md)
