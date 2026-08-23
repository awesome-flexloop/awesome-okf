---
type: Reference
title: fps._module 源码信源
description: fps核心Module类与initialize函数的源码登记，对应src/fps/_module.py
tags: [core, module, lifecycle]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:50:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
---

## 源码位置

`src/fps/_module.py` — fps核心模块系统实现，约580行。

## 导出API

| API | 签名 | 行号 |
|-----|------|------|
| `Module` | `class Module` | L29 |
| `Module.__init__` | `(self, name: str, prepare_timeout: float=1, start_timeout: float=1, stop_timeout: float=1, global_start_timeout: float\|None=None)` | L53 |
| `Module.parent` | property: `Module \| None` | L91 |
| `Module.name` | property: `str` | L109 |
| `Module.path` | property: `str`（点分路径） | L117 |
| `Module.prepared` | property: `anyio.Event` | L125 |
| `Module.started` | property: `anyio.Event` | L133 |
| `Module.stopped` | property: `anyio.Event` | L141 |
| `Module.modules` | property: `dict[str, Module]` | L171 |
| `Module.exit_app()` | `() -> None` | L179 |
| `Module.add_module()` | `(module_type: type[Module]\|str, name: str, **config) -> None` | L185 |
| `Module.freed()` | `(value: Any) -> None`（async） | L210 |
| `Module.all_freed()` | `() -> None`（async） | L221 |
| `Module.drop_all()` | `() -> None` | L229 |
| `Module.drop()` | `(value: Any) -> None` | L236 |
| `Module.add_teardown_callback()` | `(callback) -> None` | L246 |
| `Module.put()` | `(value, types=None, max_borrowers=inf, teardown_callback=None) -> None` | L259 |
| `Module.get()` | `(value_type: type[T], timeout=inf) -> T`（async） | L297 |
| `Module.done()` | `() -> None` | L445 |
| `Module.prepare()` | `() -> None`（async，可覆盖） | L508 |
| `Module.start()` | `() -> None`（async，可覆盖） | L533 |
| `Module.stop()` | `() -> None`（async，可覆盖） | L564 |
| `Module.run()` | `(backend: str="asyncio") -> None` | L574 |
| `initialize()` | `(root_module: Module) -> dict[str, Any]\|None` | L594 |
| `get_kwargs_with_default()` | `(function) -> dict[str, Any]` | L661 |

## 核心数据结构

### Module实例属性

| 属性 | 类型 | 初始值 | 说明 |
|------|------|--------|------|
| `_initialized` | `bool` | `False` | 初始化标记 |
| `_prepare_timeout` | `float` | 构造参数 | prepare阶段超时秒数 |
| `_start_timeout` | `float` | 构造参数 | start阶段超时秒数 |
| `_stop_timeout` | `float` | 构造参数 | stop阶段超时秒数 |
| `_global_start_timeout` | `float\|None` | 构造参数 | prepare+start总超时 |
| `_parent` | `Module\|None` | `None` | 父模块引用 |
| `_context` | `Context` | `Context()` | 模块独立Context |
| `_prepared` | `Event` | `Event()` | prepare完成信号 |
| `_started` | `Event` | `Event()` | start完成信号 |
| `_stopped` | `Event` | `Event()` | stop完成信号 |
| `_is_stopping` | `bool` | `False` | 停止中标记 |
| `_name` | `str` | 构造参数 | 模块名称 |
| `_path` | `list[str]` | `[]` | 父路径名列表 |
| `_uninitialized_modules` | `dict[str, Any]` | `{}` | 未初始化子模块配置 |
| `_modules` | `dict[str, Module]` | `{}` | 已初始化子模块实例 |
| `_published_values` | `dict[int, SharedValue]` | `{}` | 已发布的值 |
| `_acquired_values` | `dict[int, Value]` | `{}` | 已获取的借用值 |
| `_config` | `dict[str, Any]` | `{}` | 原始配置dict |
| `config` | `Any` | `None` | 用户自定义配置对象（如Pydantic model） |
