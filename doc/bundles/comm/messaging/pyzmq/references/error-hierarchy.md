---
type: reference
title: "error.py：异常类层次与 _check_rc 决策表"
description: "pyzmq 异常类继承体系：ZMQBaseError → ZMQError/ZMQBindError/NotDone，及 ContextTerminated/Again/InterruptedSystemCall/ZMQVersionError；_check_rc 与 _check_version 的错误码分派逻辑"
tags: [pyzmq, reference, error, exception]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/pyzmq/zmq/error.py"
    facts: [F-092, F-093, F-094, F-095]
---

# error.py：异常类层次与 _check_rc 决策表

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `zmq/error.py` | Python 异常定义 | ~231行 | 所有 pyzmq 异常类、错误码检查工具、版本检查工具 |

## 异常类层次

```
Exception
└── ZMQBaseError
    ├── ZMQError
    │   ├── ContextTerminated
    │   ├── Again
    │   └── InterruptedSystemCall(InterruptedError)
    ├── ZMQBindError
    └── NotDone
ZMQVersionError(Exception)
```

### ZMQBaseError

所有 pyzmq 异常的基类，继承自 Python 内建 `Exception`。本身不添加额外逻辑，仅用于统一捕获 `except ZMQBaseError`。

### F-092：ZMQError

**信源**：`zmq/error.py:31-82`

`ZMQError` 是最常用的 ZeroMQ 异常类，封装了一个 errno 和对应的错误描述字符串。

```python
class ZMQError(ZMQBaseError):
    def __init__(self, errno=None, msg=None):
        if errno is None:
            errno = zmq_errno()
        if msg is None:
            msg = strerror(errno)
        self.errno = errno
        self.strerror = msg

    def __str__(self):
        return self.strerror
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `errno` | `int \| None` | ZeroMQ 错误码，为 None 时自动调用 `zmq_errno()` 获取 |
| `strerror` | `str` | 错误描述字符串，为 None 时自动调用 `strerror(errno)` 获取 |

构造时两个参数均可省略：省略 errno 则从 C 层 `zmq_errno()` 取当前错误码；省略 msg 则从 C 层 `zmq_strerror(errno)` 取描述。`__str__` 直接返回 strerror，使 `str(err)` 输出人类可读信息。

### F-093：三个固定错误码异常子类

**信源**：`zmq/error.py:103-156`

| 异常类 | 固定 errno | 额外继承 | 说明 |
|--------|-----------|---------|------|
| `ContextTerminated` | `zmq.ETERM` | — | Context 已终止时抛出；构造函数忽略传入的 errno/msg |
| `Again` | `zmq.EAGAIN` | — | 非阻塞操作无法立即完成时抛出；构造函数忽略传入参数 |
| `InterruptedSystemCall` | `zmq.EINTR` | `InterruptedError` | 系统调用被信号中断时抛出；同时继承 Python 内建 `InterruptedError` |

这三个子类的共同特点：

1. **固定错误码**：类定义时即绑定特定 errno，构造函数忽略用户传入的 errno/msg 参数。
2. **语义精确化**：允许调用方用 `except Again` 精确捕获 EAGAIN，而不必先捕获 ZMQError 再判断 `e.errno == zmq.EAGAIN`。
3. **InterruptedSystemCall 的双重继承**：继承 `InterruptedError` 使其也能被 `except InterruptedError` 捕获，与 Python 标准库的中断异常体系对齐。

### 其他异常类

| 异常类 | 继承 | 触发场景 |
|--------|------|---------|
| `ZMQBindError` | `ZMQBaseError` | `bind_to_random_port` 超过最大尝试次数仍无法绑定端口时抛出（F-043） |
| `NotDone` | `ZMQBaseError` | `MessageTracker.wait(timeout)` 在超时时间内消息未完成发送时抛出（F-057） |

### F-095：ZMQVersionError

**信源**：`zmq/error.py:187-231`

`ZMQVersionError` 不继承 `ZMQBaseError`，而是直接继承 `Exception`，用于表示当前运行时加载的 libzmq 版本不满足 API 要求。

```python
class ZMQVersionError(Exception):
    def __init__(self, msg, min_version_info, version_info=None):
        self.msg = msg
        self.min_version_info = min_version_info
        if version_info is None:
            version_info = zmq_version_info()
        self.version_info = version_info

    def __str__(self):
        return f"{self.msg} requires libzmq >= {self.min_version}, have {self.version}"
```

| 属性 | 说明 |
|------|------|
| `msg` | 功能描述信息 |
| `min_version_info` | 所需最低 libzmq 版本元组，如 `(4, 2, 0)` |
| `version_info` | 当前 libzmq 版本元组，默认从 `zmq_version_info()` 获取 |

模块级函数 `_check_version(min_version_info, msg)` 在版本不足时抛出此异常：

```python
def _check_version(min_version_info, msg="Feature"):
    if zmq_version_info() < min_version_info:
        raise ZMQVersionError(msg, min_version_info)
```

典型使用场景：`Frame.group`/`routing_id` draft 属性要求 libzmq ≥4.2（F-049）；`Socket.get_monitor_socket` 要求 libzmq ≥4（F-041）。

## F-094：_check_rc 错误码分派

**信源**：`zmq/error.py:159-180`

`_check_rc(rc, errno=None, error_without_errno=True)` 是 pyzmq 后端层统一的返回码检查工具。C 函数返回 -1 表示出错，`_check_rc` 根据 errno 分派到对应的精确异常类。

**决策表**：

| rc 值 | errno | 抛出异常 | 说明 |
|-------|-------|---------|------|
| ≥ 0 | — | （正常返回，不抛异常） | C 函数调用成功 |
| -1 | EINTR | `InterruptedSystemCall` | 系统调用被信号中断 |
| -1 | EAGAIN | `Again` | 非阻塞操作未就绪 |
| -1 | ETERM | `ContextTerminated` | Context 已终止 |
| -1 | 其他 | `ZMQError(errno)` | 通用 ZeroMQ 错误 |

```python
def _check_rc(rc, errno=None, error_without_errno=True):
    if rc == -1:
        if errno is None:
            errno = zmq_errno()
        if errno in (EINTR,):
            raise InterruptedSystemCall(errno)
        elif errno in (EAGAIN,):
            raise Again(errno)
        elif errno in (ETERM,):
            raise ContextTerminated(errno)
        else:
            raise ZMQError(errno)
```

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rc` | `int` | — | C API 返回码，-1 表示错误 |
| `errno` | `int \| None` | `None` | 错误码；None 时自动调用 `zmq_errno()` |
| `error_without_errno` | `bool` | `True` | True 且 errno 为 0 时仍抛 ZMQError |

**设计要点**：

1. **精确异常优先**：先检查 EINTR/EAGAIN/ETERM 三个常见错误码，抛出具名异常子类，使调用方可以精确捕获。
2. **回退到通用异常**：其他错误码统一抛 `ZMQError(errno)`，保留 errno 供调用方判断。
3. **Cython 与 CFFI 共用**：两个后端的 C 调用都通过 `_check_rc` 检查返回码，保证异常类型一致性。

## CFFI 后端的错误绑定

**F-088**：CFFI 后端的错误模块直接绑定 C 函数：

```python
strerror = lambda errno: ffi.string(C.zmq_strerror(errno)).decode()
zmq_errno = C.zmq_errno
```

- `strerror(errno)`：调用 C 的 `zmq_strerror`，将返回的 C 字符串通过 `ffi.string` 转为 bytes 再 decode 为 Python str。
- `zmq_errno`：直接是 C 函数 `zmq_errno` 的绑定对象，调用后返回当前线程的 ZeroMQ 错误码。

## 异常处理最佳实践

### 精确捕获 EAGAIN

```python
try:
    msg = socket.recv(flags=zmq.NOBLOCK)
except zmq.Again:
    pass  # 暂无消息可用
```

### 捕获 Context 终止

```python
try:
    socket.send(data)
except zmq.ContextTerminated:
    break  # Context 已关闭，退出循环
```

### 捕获所有 pyzmq 异常

```python
try:
    ...
except zmq.ZMQBaseError as e:
    print(f"ZeroMQ error {e.errno}: {e.strerror}")
```

### 版本检查

```python
try:
    frame.group = b"group1"
except zmq.ZMQVersionError as e:
    print(f"需要升级 libzmq: {e}")
```

## 相关概念

- [constants.py 枚举常量](constants-enums.md) — Errno 枚举值定义
- [CFFI 后端内部](cffi-internals.md) — CFFI 层如何调用 _check_rc
- [Frame 与消息](../concepts/03-frame-message.md) — draft 属性的版本检查
- [Socket sugar 语法层](../concepts/02-socket-sugar.md) — bind_to_random_port 抛 ZMQBindError
