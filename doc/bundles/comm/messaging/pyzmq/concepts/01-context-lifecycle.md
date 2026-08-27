---
type: concept
title: "Context 生命周期与资源管理"
description: "pyzmq Context 的创建、单例 instance()、shadow 影子包装、term 与 destroy 的区别、WeakSet socket 跟踪、sockopts 默认选项继承、fork 安全、上下文管理器协议与析构行为"
tags: [pyzmq, zeromq, context, lifecycle, singleton, shadow, fork]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/attrsettr-options.md, ../references/error-hierarchy.md, ../references/cffi-internals.md]
  facts: [F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021]
---

# Context 生命周期与资源管理

## 核心理解

`zmq.Context` 是 ZeroMQ 应用的容器和资源管理者。它持有 I/O 线程池、套接字集合和底层 libzmq context 指针。pyzmq 的 sugar 层在后端 C 绑定基类之上，用纯 Python 实现了完整的 Context 生命周期管理：单例模式、影子包装、fork 安全、socket 弱引用跟踪、默认选项继承，以及 v24 版本改进的析构行为。

理解 Context 的生命周期是编写可靠 ZeroMQ 应用的基础——未正确关闭的 Context 会导致进程挂起、消息丢失和资源泄漏。

## Context 类层次

**F-009**：sugar 层 `Context` 的继承结构：

```python
class Context(
    zmq.backend.Context,       # C 扩展基类（Cython 或 CFFI）
    AttributeSetter,           # 动态选项属性 mixin
    Generic[_SocketType],      # 泛型，参数化为 Socket 子类
):
    _socket_class = Socket     # 决定 ctx.socket() 创建的 Socket 类型
```

关键设计点：

- **多继承组合**：后端基类提供 C API 调用，`AttributeSetter` 提供属性访问语法糖
- **泛型参数化**：`Context[_SocketType]` 使 `ctx.socket()` 的返回类型可被类型检查器推断
- **`_socket_class` 类属性**：子类（如 `zmq.asyncio.Context`）只需覆写此属性即可替换 socket 类型，实现异步 Context 而无需重写 `socket()` 方法

## 创建 Context

### F-010：三种调用形态

`Context.__init__` 支持三种创建方式：

```python
# 形态一：指定 I/O 线程数（最常用）
ctx = zmq.Context(io_threads=1)
ctx = zmq.Context(4)  # 位置参数，4 个 I/O 线程

# 形态二：shadow 另一个 Context（共享底层 libzmq context）
ctx2 = zmq.Context(other_ctx)  # other_ctx 是已存在的 Context 实例

# 形态三：shadow 一个原始地址（整数）
ctx3 = zmq.Context(shadow=0x7f8a3c0008c0)
```

当传入的是 Context 实例时，构造函数自动取其 `underlying` 属性（底层 C 指针的整数表示）进行 shadow。shadow 的 Context 不拥有底层资源，不会在销毁时终止 libzmq context。

### 默认选项字典

**F-011**：每个 Context 维护 `self.sockopts = {}` 字典。通过 `ctx.setsockopt(opt, value)` 或属性赋值设置的 SocketOption，不会立即调用 C 层，而是存入此字典。当 `ctx.socket()` 创建新 socket 时，这些选项被批量应用到新 socket 上。

```python
ctx = zmq.Context()
ctx.linger = 0        # 存入 sockopts 字典
ctx.sndhwm = 1000     # 存入 sockopts 字典

sock1 = ctx.socket(zmq.PUB)  # 自动应用 linger=0, sndhwm=1000
sock2 = ctx.socket(zmq.SUB)  # 同样继承这些默认值
```

这是 v13 新增的"为新 socket 设默认选项"机制，避免了对每个新 socket 重复设置相同选项。

### 选项分流

**F-019、F-020**：Context 覆写了 `AttributeSetter` 的 `_set_attr_opt`/`_get_attr_opt`，区分两类选项：

| 选项类型 | 判断 | 设置行为 | 示例 |
|---------|------|---------|------|
| ContextOption | `isinstance(opt, ContextOption)` | 立即调用 C 层 `self.set/get` | `IO_THREADS`、`MAX_SOCKETS` |
| SocketOption | 其他所有 | 存入/读取 `sockopts` 字典 | `LINGER`、`SNDHWM`、`RCVHWM` |

这意味着 `ctx.io_threads = 2` 立即生效（C 层调用），而 `ctx.linger = 0` 只影响后续创建的 socket。

## 单例模式

### F-015：Context.instance()

`Context.instance()` 是类方法，返回全局单例 Context：

```python
ctx = zmq.Context.instance()  # 首次调用创建
ctx2 = zmq.Context.instance()  # 后续调用返回同一实例
assert ctx is ctx2
```

实现使用**双重检查锁**（double-checked locking）：

1. 无锁检查 `_instance` 是否存在且未关闭
2. 加锁后再次检查
3. 创建新实例并赋值给 `_instance`

### Fork 安全

单例在以下情况下自动重建：

- **进程 fork 后**：记录 `_instance_pid`，若 `os.getpid()` 不匹配则重建。这是因为 libzmq context 不能跨 fork 共享（子进程继承了父进程的文件描述符但状态不一致）。
- **单例已关闭**：若之前的单例已被 `destroy()`/`term()`，下次调用 `instance()` 创建新实例。

```python
ctx = zmq.Context.instance()
pid = os.fork()
if pid == 0:
    # 子进程：Context.instance() 自动返回新的 Context
    # 不会复用父进程的 context
    child_ctx = zmq.Context.instance()
```

`zmq.asyncio.Context` 覆写时重置 `_instance = None`（F-074），避免与同步 Context 共享单例——同步和异步 Context 需要不同的 `_socket_class`，不能混用。

## Shadow 机制

### F-021：跨边界共享 Context

`Context.shadow(address)` 类方法创建对已有 libzmq context 的影子包装：

```python
# 获取底层地址
addr = ctx.underlying  # int，C 指针的 size_t 表示

# 在另一处创建影子（可跨模块、跨后端）
shadow_ctx = zmq.Context.shadow(addr)
```

影子 Context 的特点：

- **不拥有资源**：析构时不调用 `zmq_ctx_destroy`
- **共享 I/O 线程**：与原 Context 使用相同的 I/O 线程池
- **可创建独立 socket**：影子 Context 可以创建自己的 socket，这些 socket 参与原 Context 的消息循环
- **跨后端兼容**：Cython 后端创建的 Context 可被 CFFI 后端 shadow（因为底层都是同一个 libzmq C 指针）

`__copy__` 和 `__deepcopy__` 均返回 shadow 副本，这意味着 `copy.copy(ctx)` 不会创建独立的 libzmq context，而是创建影子。

## Socket 跟踪

### F-012：WeakSet 弱引用集合

Context 用 `WeakSet()`（`self._sockets`）跟踪所有由其创建的 socket 弱引用：

```python
class Context:
    def __init__(self, ...):
        self._sockets = WeakSet()
```

使用弱引用而非强引用的原因：socket 可能被用户先显式关闭并释放，Context 不应持有强引用阻止其 GC。当 socket 被 GC 回收后，WeakSet 自动移除对应条目。

`ctx.socket()` 创建 socket 后通过 `_add_socket` 将其加入 WeakSet（F-018）。`destroy()` 时遍历此集合关闭所有未关闭的 socket。

## term vs destroy

pyzmq Context 有两个关闭方法，行为有重要区别：

### F-016：term()

```python
ctx.term()
```

直接调用 `super().term()`（后端 C 实现的 `zmq_ctx_term`）。行为：

- 中断所有阻塞调用
- 等待所有 socket 关闭
- 等待所有挂起消息发送完成（受各 socket 的 LINGER 选项控制）
- **不主动关闭 socket**：如果 socket 未关闭，term 会阻塞直到它们被关闭或 LINGER 超时

### F-017：destroy()

```python
ctx.destroy(linger=None)
```

sugar 层实现的优雅关闭方法：

1. 遍历 `_sockets` 弱引用集合
2. 对每个未关闭的 socket：
   - 如果传入了 `linger` 参数，设置 socket 的 LINGER 选项
   - 调用 `s.close()`
3. 最后调用 `self.term()`

**文档警告：`destroy()` 非线程安全。** 不应在多线程中并发调用。

### 选择建议

| 场景 | 推荐方法 |
|------|---------|
| 已确保所有 socket 已关闭 | `term()` |
| 需要统一关闭所有 socket | `destroy(linger=0)`（立即关闭不等待） |
| 上下文管理器退出 | 自动调用 `destroy()` |
| 析构函数 | 自动调用 `destroy()`（v24 起） |

## 析构行为

### F-013：__del__ 的演进

v24 之前，`Context.__del__` 调用 `self.term()`，这可能导致进程挂起——如果 socket 未关闭且 LINGER 为默认值（-1，无限等待），`term()` 会永远阻塞。

v24 起改为调用 `self.destroy()`，并发出 `ResourceWarning`：

```python
def __del__(self):
    if self.closed or self._shadow:
        return
    if _is_process_teardown():
        return
    try:
        self.destroy()
        warnings.warn("Unclosed context destroyed", ResourceWarning)
    except Error:
        pass
```

关键条件：

- **shadow Context 不析构**：不拥有底层资源
- **进程退出时不析构**：解释器关闭阶段不尝试清理
- **已关闭不重复析构**：检查 `closed` 标志

## 上下文管理器

### F-014：with 语句

Context 支持上下文管理器协议：

```python
with zmq.Context() as ctx:
    with ctx.socket(zmq.PUB) as pub:
        pub.bind("tcp://*:5555")
        pub.send_string("hello")
# 退出 with 块时：
# 1. socket.__exit__ 调用 socket.close()
# 2. ctx.__exit__ 调用 ctx.destroy()（先设 _warn_destroy_close=True）
```

`__exit__` 设置 `_warn_destroy_close=True` 后调用 `destroy()`，这使得在 with 块中未显式关闭的 socket 被关闭时不产生额外警告。

这是最推荐的 Context 使用方式——确保资源总是被正确释放。

## 创建 Socket

### F-018：socket() 方法

```python
def socket(self, socket_type, socket_class=None, **kwargs):
    if self.closed:
        raise ZMQError(ENOTSUP)
    if socket_class is None:
        socket_class = self._socket_class
    sock = socket_class(self, socket_type, **kwargs)
    # 应用默认选项
    for opt, value in self.sockopts.items():
        try:
            sock.set(opt, value)
        except ZMQError:
            pass  # 忽略不适用此 socket 类型的选项
    self._add_socket(sock)
    return sock
```

要点：

- Context 已关闭时抛 `ZMQError(ENOTSUP)`
- 默认使用 `self._socket_class`，可被参数覆盖
- `sockopts` 中的默认选项被逐个应用，不适用的选项（如给 PUB socket 设置 SUBSCRIBE）静默忽略
- 新 socket 通过 `_add_socket` 加入 WeakSet

## 装饰器集成

**F-096、F-097**：`zmq.decorators` 提供装饰器自动管理 Context/Socket 生命周期：

```python
@zmq.decorators.context()
def server(ctx):
    # ctx 是通过 with 语句创建的 Context
    with ctx.socket(zmq.REP) as sock:
        sock.bind("tcp://*:5555")
        ...

@zmq.decorators.socket(zmq.PUB)
def publisher(pub):
    # 自动从函数参数查找 Context 实例，找不到则用 Context.instance()
    pub.send_string("news")
```

`_SocketDecorator` 在调用时从 kwargs/args 中查找 `zmq.Context` 实例（参数名默认 `'context'`），找不到则用 `zmq.Context.instance()` 单例。

## 生命周期全景图

```
创建
  │
  ├─ Context(io_threads) → zmq_ctx_new()
  ├─ Context(other_ctx)  → shadow（不拥有）
  └─ Context.instance()  → 单例（fork 安全）
  │
  │  sockopts 字典累积默认选项
  │  WeakSet 跟踪创建的 socket
  │
使用
  │
  ├─ ctx.socket(type) → 创建 Socket + 应用默认选项
  ├─ ctx.set/get(ContextOption) → C 层立即生效
  └─ ctx.socket_option = value → 存入 sockopts
  │
关闭
  │
  ├─ with 块退出 → destroy()
  ├─ 显式 destroy(linger) → 关闭所有 socket + term()
  ├─ 显式 term() → 仅终止（不关闭 socket）
  └─ __del__ → destroy() + ResourceWarning（v24+）
```

## 最佳实践

1. **优先使用上下文管理器**：`with zmq.Context() as ctx:` 确保资源释放
2. **显式设置 LINGER**：`ctx.linger = 0` 避免关闭时无限等待
3. **不要在 fork 后复用父进程 Context**：`Context.instance()` 在子进程自动重建，但手动创建的 Context 不会
4. **shadow 用于跨边界共享**：C 扩展、多模块间传递 Context 时使用 `underlying` + `shadow`
5. **单例适合简单应用**：复杂应用应显式创建和管理 Context 生命周期

## 相关概念

- [整体架构与双后端](00-architecture-dual-backend.md) — Context 后端基类的来源
- [Socket sugar 语法层](02-socket-sugar.md) — ctx.socket() 创建的 Socket 详解
- [attrsettr 选项访问系统](../references/attrsettr-options.md) — ContextOption 与 SocketOption 分流
- [异步与 asyncio](05-async-future-asyncio.md) — asyncio.Context 如何覆写 _socket_class
- [错误层次结构](../references/error-hierarchy.md) — ContextTerminated 异常
