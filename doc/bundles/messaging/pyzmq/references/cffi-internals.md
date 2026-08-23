---
type: reference
title: "CFFI 后端内部实现参考"
description: "pyzmq CFFI 后端的 ffi/lib 加载、Context/Socket/Frame 实现细节、_opt_type 指针分派、zero-copy 发送路径、recv copy 与 non-copy、monitor 调用、GC 回调机制、错误绑定"
tags: [pyzmq, reference, cffi, backend, internals]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/pyzmq/zmq/backend/cffi/"
    facts: [F-079, F-080, F-081, F-082, F-083, F-084, F-085, F-086, F-087, F-088]
---

# CFFI 后端内部实现参考

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `zmq/backend/cffi/__init__.py` | 包初始化 | 加载 ffi/lib，聚合子模块，版本查询 |
| `zmq/backend/cffi/context.py` | Context 实现 | `zmq_ctx_new/destroy/set/get` 的 CFFI 绑定 |
| `zmq/backend/cffi/socket.py` | Socket 实现 | setsockopt/getsockopt/send/recv/monitor 的 CFFI 绑定 |
| `zmq/backend/cffi/message.py` | Frame 实现 | zero-copy 消息、GC 回调、fast_copy |
| `zmq/backend/cffi/error.py` | 错误绑定 | strerror/zmq_errno C 函数绑定 |
| `zmq/backend/cffi/_poll.py` | Poll 实现 | zmq_poll 的 CFFI 绑定 |
| `zmq/backend/cffi/utils.py` | 工具函数 | 指针构造辅助函数 |
| `zmq/backend/cffi/devices.py` | 设备实现 | proxy 的 CFFI 绑定 |

CFFI（C Foreign Function Interface）后端是 pyzmq 的两个可插拔后端之一，在 PyPy 上为默认选择，在 CPython 上作为 Cython 后端不可用时的回退（F-077）。

## F-079：后端初始化与版本查询

**信源**：`zmq/backend/cffi/__init__.py:7-23`

```python
from ._cffi import ffi, lib as C
from . import (
    _poll, context, devices, error, message, socket, utils,
)
```

CFFI 后端通过预编译的 `_cffi` 扩展模块加载两个核心对象：

| 对象 | 类型 | 说明 |
|------|------|------|
| `ffi` | `cffi.FFI` 实例 | C 类型构造、指针操作、内存管理接口 |
| `C`（`lib`） | CFFI 库对象 | 所有 libzmq C 函数的直接绑定（`C.zmq_ctx_new`、`C.zmq_send` 等） |

`zmq_version_info()` 通过 CFFI 分配三个 int 指针并调用 C 函数：

```python
def zmq_version_info():
    major = ffi.new('int*')
    minor = ffi.new('int*')
    patch = ffi.new('int*')
    C.zmq_version(major, minor, patch)
    return (int(major[0]), int(minor[0]), int(patch[0]))
```

`ffi.new('int*')` 分配一个 C int 指针（`int*`），通过 `major[0]` 解引用取值。

## F-080：Context 实现

**信源**：`zmq/backend/cffi/context.py:13-74`

CFFI Context 直接调用 libzmq C API：

| 操作 | C 函数 | 说明 |
|------|--------|------|
| 创建 | `C.zmq_ctx_new()` | 返回 `void*` 上下文指针 |
| 设置选项 | `C.zmq_ctx_set(self._zmq_ctx, option, value)` | 设置 context 选项 |
| 获取选项 | `C.zmq_ctx_get(self._zmq_ctx, option)` | 获取 context 选项 |
| 销毁 | `C.zmq_ctx_destroy(self._zmq_ctx)` | 终止并释放上下文 |

**Shadow 模式**：通过 `ffi.cast("void *", shadow)` 将传入的整数地址转换为 C void 指针，实现对已有 libzmq context 的包装，不拥有所有权，不负责销毁。

**`underlying` 属性**：

```python
@property
def underlying(self):
    return int(ffi.cast('size_t', self._zmq_ctx))
```

将 C 指针转为 `size_t` 整数，供 shadow 另一 Context 或跨后端共享使用。

## F-081：Socket.set — setsockopt 的类型分派

**信源**：`zmq/backend/cffi/socket.py:213-241`

`set(option, value)` 根据 `SocketOption(option)._opt_type` 选择 C 指针类型：

```python
def set(self, option, value):
    opt_type = SocketOption(option)._opt_type
    c_value = initialize_opt_pointer(opt_type, value)
    rc = C.zmq_setsockopt(self._zmq_socket, option, c_value, ...)
    _check_rc(rc)
```

**类型分派**：

| _opt_type | 指针构造 | 值类型 | C 函数签名 |
|-----------|---------|--------|-----------|
| `int` | `ffi.new('int*', value)` | Python int | `zmq_setsockopt(sock, opt, int*, sizeof(int))` |
| `int64` | `ffi.new('int64_t*', value)` | Python int | `zmq_setsockopt(sock, opt, int64_t*, sizeof(int64_t))` |
| `bytes` | `ffi.new('char[]', value)` | bytes | `zmq_setsockopt(sock, opt, char*, len(value))` |
| `fd` | 平台相关 | int/socket | Windows 上 cast 为 SOCKET，POSIX 为 int |

**Unicode 拒绝**：CFFI 后端严格要求 bytes 类型，传入 str 会被拒绝（Cython 后端会隐式编码）。`initialize_opt_pointer` 检测到 unicode 值时抛出 TypeError，提示必须先 encode。

## F-082：Socket.get — getsockopt 的指针读取

**信源**：`zmq/backend/cffi/socket.py:243-312`

`get(option)` 根据 `_opt_type` 分配对应类型的指针，调用 `C.zmq_getsockopt`，再用 `value_from_opt_pointer` 转回 Python 值。

```python
def get(self, option):
    opt_type = SocketOption(option)._opt_type
    pointer, length = initialize_opt_pointer(opt_type)
    rc = C.zmq_getsockopt(self._zmq_socket, option, pointer, length_ptr)
    _check_rc(rc)
    return value_from_opt_pointer(opt_type, pointer, length)
```

对于 bytes 类型选项（如 IDENTITY、SUBSCRIBE），采用两步法：
1. 先用较大缓冲区调用 getsockopt 获取实际长度
2. 按实际长度分配精确缓冲区再次调用
3. 用 `ffi.buffer(pointer, length)[:]` 复制为 Python bytes

**Thread-safe socket FD 回退**：对 draft API 的 thread-safe socket，FD 选项可能需要调用 `zmq_poller_fd` 获取，CFFI 后端对此有 draft 回退逻辑。

## F-083：Socket.send — copy 与 zero-copy 双路径

**信源**：`zmq/backend/cffi/socket.py:314-365`

`send(data, flags=0, copy=False, track=False)` 根据 copy 参数和数据大小选择路径：

```
send(data, flags, copy, track)
├── copy=True 且 data 非 Frame → _send_copy
│   ├── zmq_msg_init_size(&msg, len(data))
│   ├── memcpy(zmq_msg_data(&msg), data, len(data))
│   ├── zmq_msg_send(&msg, socket, flags)
│   └── zmq_msg_close(&msg)
└── copy=False 或 data 是 Frame → _send_frame
    ├── frame.fast_copy()（共享引用计数，不复制数据）
    ├── zmq_msg_send(&frame.zmq_msg, socket, flags)
    └── 小于 copy_threshold 时自动走 copy 路径
        └── 返回 _FINISHED_TRACKER
```

**copy_threshold 自动降级**：当 zero-copy 发送的消息小于 `zmq.COPY_THRESHOLD`（64KB，F-003）时，CFFI 后端自动切换到 copy 路径，因为小消息的 zero-copy 开销（GC 回调注册、引用计数管理）超过数据复制本身的成本。此时返回 `_FINISHED_TRACKER`（一个已完成的 MessageTracker 单例，F-058）。

**track 参数**：
- `track=False`（默认）：返回 None
- `track=True` 且 copy=False：返回 `MessageTracker`，可用于等待消息实际发送完成
- `copy=True`：始终返回 None（数据已复制到 libzmq 缓冲区）

## F-084：Socket.recv — copy 与 non-copy

**信源**：`zmq/backend/cffi/socket.py:367-389`

`recv(flags=0, copy=True, track=False)` 同样有两条路径：

| copy | 实现 | 返回类型 |
|------|------|---------|
| `True`（默认） | `zmq_msg_init` + `zmq_msg_recv` + `ffi.buffer` 复制 + `zmq_msg_close` | `bytes` |
| `False` | 创建 `zmq.Frame(track=track)` 并在其上 recv | `Frame` |

copy=True 路径：

```python
def _recv_copy(self, flags=0):
    msg = ffi.new('zmq_msg_t*')
    C.zmq_msg_init(msg)
    try:
        C.zmq_msg_recv(msg, self._zmq_socket, flags)
        length = C.zmq_msg_size(msg)
        buf = ffi.buffer(C.zmq_msg_data(msg), length)
        return bytes(buf)
    finally:
        C.zmq_msg_close(msg)
```

copy=False 路径直接在 Frame 对象持有的 `zmq_msg_t` 上接收，数据由 libzmq 管理，Python 端通过 Frame 访问，直到 Frame 被 GC 回收时才释放底层消息内存。

## F-085：Socket.monitor

**信源**：`zmq/backend/cffi/socket.py:409-432`

`monitor(addr, events=-1)` 调用 `C.zmq_socket_monitor`：

```python
def monitor(self, addr, events=-1):
    if events < 0:
        events = EVENT_ALL
    if addr is None:
        c_addr = ffi.NULL
    else:
        c_addr = addr.encode('utf-8')
    rc = C.zmq_socket_monitor(self._zmq_socket, c_addr, events)
    _check_rc(rc)
```

- `events < 0` 时使用 `EVENT_ALL`（所有事件）
- `addr=None` 时传 `ffi.NULL`（用于注销监控）
- 字符串地址需编码为 bytes

sugar 层的 `get_monitor_socket`（F-041）在 monitor 之上创建 PAIR socket 连接到监控端点。

## F-086：Frame zero-copy 与 GC 回调

**信源**：`zmq/backend/cffi/message.py:105-140`

zero-copy 模式的核心挑战是：libzmq 在异步发送完成后需要释放消息内存，但这块内存可能由 Python 分配。CFFI 后端通过 `zmq_wrap_msg_init_data` 注册一个 C 回调函数 `free_python_msg`，当 libzmq 释放消息时调用此回调通知 Python GC。

**zhint 结构体**：

```c
struct zhint {
    Py_ssize_t id;           // Python 对象的 gc id
    void *mutex;             // 互斥锁指针
    void *pull_socket;       // PULL socket 指针（用于 GC 通知）
};
```

zhint 持有垃圾回收器的 id、mutex 与 PULL socket 指针。当 libzmq 释放 `zmq_msg_t` 时：

1. 调用 `free_python_msg(data, hint)` 回调
2. 回调通过 PULL socket 发送一个通知字节
3. Python 端的 GC 线程收到通知，知道对应的 Python buffer 可以安全释放

这一机制确保了 Python buffer 在 libzmq 完成发送前不会被提前回收，实现了真正的 zero-copy。

## F-087：Frame.fast_copy

**信源**：`zmq/backend/cffi/message.py:203-220`

`fast_copy()` 创建一个新的空 Frame 并调用 `C.zmq_msg_copy` 增加引用计数：

```python
def fast_copy(self):
    new_frame = Frame.__new__(Frame)
    C.zmq_msg_init(ffi.addressof(new_frame._zmq_msg))
    C.zmq_msg_copy(ffi.addressof(new_frame._zmq_msg),
                   ffi.addressof(self._zmq_msg))
    new_frame._data = self._data
    new_frame._buffer = self._buffer
    new_frame.tracker = self.tracker
    new_frame.tracker_event = self.tracker_event
    return new_frame
```

`zmq_msg_copy` 是浅拷贝——它增加底层 zmq_msg 的引用计数而不复制数据。新旧 Frame 共享同一数据缓冲区，同时共享 `_data`/`_buffer`/`tracker`/`tracker_event`，确保 GC 回调和发送跟踪正确传播。

这与 `bytes` 的不可变共享语义类似，但发生在 C 层。

## F-088：错误绑定

**信源**：`zmq/backend/cffi/error.py:10-14`

```python
def strerror(errno):
    return ffi.string(C.zmq_strerror(errno)).decode()

zmq_errno = C.zmq_errno
```

| 函数 | 实现 | 返回 |
|------|------|------|
| `strerror(errno)` | `ffi.string(C.zmq_strerror(errno)).decode()` | Python str |
| `zmq_errno()` | 直接调用 C `zmq_errno()` | int |

`ffi.string()` 将 C 字符串（`const char*`）转为 Python bytes，再 `.decode()` 为 str。这两个函数被 sugar 层的 `ZMQError.__init__`（F-092）使用。

## 指针辅助函数

CFFI 后端在 `utils.py` 中提供了指针构造与值提取的辅助函数：

### initialize_opt_pointer

根据 `_opt_type` 创建对应的 C 指针并初始化为 Python 值：

| opt_type | C 类型 | 构造方式 |
|-----------|--------|---------|
| int | `int*` | `ffi.new('int*', value)` |
| int64 | `int64_t*` | `ffi.new('int64_t*', value)` |
| bytes | `char[]` | `ffi.new('char[]', value)` |
| fd | 平台相关 | Windows `SOCKET`，POSIX `int` |

### value_from_opt_pointer

从 C 指针提取 Python 值：

| opt_type | 提取方式 |
|-----------|---------|
| int/int64/fd | `int(pointer[0])` |
| bytes | `ffi.buffer(pointer, length)[:]` |

## public_api 契约

CFFI 后端必须实现的 public_api 符号列表（F-078）：

| 符号 | 类型 | 说明 |
|------|------|------|
| `Context` | class | CFFI Context 实现 |
| `Socket` | class | CFFI Socket 实现 |
| `Frame` | class | CFFI Frame 实现 |
| `Message` | alias | Frame 的别名 |
| `proxy` | function | `zmq_proxy` 绑定 |
| `proxy_steerable` | function | `zmq_proxy_steerable` 绑定 |
| `zmq_poll` | function | `zmq_poll` 绑定 |
| `strerror` | function | 错误描述 |
| `zmq_errno` | function | 获取当前错误码 |
| `has` | function | 能力检测 |
| `curve_keypair` | function | 生成 CURVE 密钥对 |
| `curve_public` | function | 从私钥推导公钥 |
| `zmq_version_info` | function | 版本元组 |
| `IPC_PATH_MAX_LEN` | constant | IPC 路径最大长度 |
| `PYZMQ_DRAFT_API` | bool | 是否启用 draft API |
| `monitored_queue` | function（私有） | 监控队列 |

sugar 层只通过 `zmq.backend` 命名空间访问这些符号，不感知具体后端实现。

## 相关概念

- [整体架构与双后端](../concepts/00-architecture-dual-backend.md) — Cython/CFFI 后端选择机制
- [attrsettr 选项访问系统](attrsettr-options.md) — `_opt_type` 如何驱动属性访问
- [错误层次结构](error-hierarchy.md) — CFFI 层的错误检查
- [Frame 与消息](../concepts/03-frame-message.md) — zero-copy 与 MessageTracker
