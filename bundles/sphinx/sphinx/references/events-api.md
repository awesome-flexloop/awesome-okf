---
type: "reference"
title: Sphinx 事件系统 API 参考
description: EventManager类API参考，包括事件注册、监听、触发方法。
tags: [sphinx, api, events, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: events-py
    resource: /references/events-api.md
    title: sphinx/events.py 源码
---
# Sphinx 事件系统 API 参考

事件系统定义在`sphinx/events.py`，核心类是`EventManager`。

## EventListener

```python
class EventListener(NamedTuple):
    id: int
    handler: Callable[..., Any]
    priority: int
```

监听器是一个命名元组，包含唯一ID、回调函数和优先级。

## EventManager 类

### 方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `__init__` | `(self, app: Sphinx)` | 初始化，接收Sphinx实例，复制core_events |
| `add` | `(self, name: str) -> None` | 注册自定义事件名，重复注册抛ExtensionError |
| `connect` | `(self, name: str, callback: Callable, priority: int) -> int` | 连接回调到事件，返回listener_id |
| `disconnect` | `(self, listener_id: int) -> None` | 通过ID断开监听器 |
| `emit` | `(self, name: str, *args, allowed_exceptions=()) -> list[Any]` | 触发事件，返回所有回调结果列表 |
| `emit_firstresult` | `(self, name: str, *args, allowed_exceptions=()) -> Any` | 触发事件，返回第一个非None结果 |

### 行为细节

- 回调按`priority`**升序**调用（数值越小越先执行）
- 默认priority为500（通过Sphinx.connect()）
- `emit()`执行时：SphinxError直接抛出，其他异常包装为ExtensionError
- `allowed_exceptions`参数允许指定透传的异常类型
- 自定义事件必须先通过`add()`注册才能emit

## 通过Sphinx类使用事件

通常不直接操作EventManager，而是通过Sphinx应用实例：

```python
def setup(app):
    # 连接事件（默认priority=500）
    app.connect('build-finished', my_handler)
    # 指定优先级
    app.connect('config-inited', my_handler, priority=100)
    # 添加自定义事件
    app.add_event('my-custom-event')
```
