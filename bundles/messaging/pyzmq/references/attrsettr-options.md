---
type: reference
title: "attrsettr：选项访问三层模型与 AttributeSetter mixin"
description: "AttributeSetter mixin 的 __setattr__/__getattr__ 常量解析机制，set/get 底层、setsockopt/getsockopt 别名、属性动态访问三层模型，Context 与 Socket 的 _set_attr_opt 分流差异，只写选项异常转换"
tags: [pyzmq, reference, attrsettr, descriptor, options]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/pyzmq/zmq/sugar/attrsettr.py"
    facts: [F-059, F-060, F-061]
  - path: "external/libs/remote/pyzmq/zmq/sugar/context.py"
    facts: [F-019, F-020]
  - path: "external/libs/remote/pyzmq/zmq/sugar/socket.py"
    facts: [F-027, F-028]
---

# attrsettr：选项访问三层模型与 AttributeSetter mixin

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `zmq/sugar/attrsettr.py` | Mixin 定义 | ~76行 | `AttributeSetter` mixin，动态选项属性访问的核心 |
| `zmq/sugar/context.py` | Context 覆写 | L381-398 | 区分 ContextOption 与 Socket 默认选项 |
| `zmq/sugar/socket.py` | Socket 别名与特判 | L375-392 | setsockopt/getockopt 别名、subscribe 属性特判 |

`AttributeSetter` 是 pyzmq sugar 层的核心 mixin，`Context`、`Socket`、`Frame` 均通过多继承组合它。它利用 Python 的属性访问协议（`__setattr__`/`__getattr__`），把 C 风格的整数常量选项包装成动态 Python 属性，提供三层等价的选项访问方式。

## 三层选项访问模型

pyzmq 为套接字和上下文选项提供了三层访问方式，三者等价但风格不同：

| 层级 | 语法 | 实现机制 | 适用场景 |
|------|------|---------|---------|
| **第一层：底层 set/get** | `socket.set(zmq.LINGER, 1000)` | 后端 C 方法直接调用 | 动态选项名、性能敏感 |
| **第二层：POSIX 别名** | `socket.setsockopt(zmq.LINGER, 1000)` | `setsockopt = SocketBase.set` 别名 | 熟悉 libzmq C API 的用户 |
| **第三层：属性访问** | `socket.linger = 1000` | `AttributeSetter.__setattr__` 动态解析 | Pythonic 代码、可读性优先 |

### 第一层：set/get 底层方法

`set(option, value)` 和 `get(option)` 由后端子类（Cython 或 CFFI）实现，是最接近 C API 的调用方式：

```python
socket.set(zmq.SUBSCRIBE, b"topic")
value = socket.get(zmq.LINGER)
```

在 `AttributeSetter` 基类中，`set`/`get` 抛 `NotImplementedError`，强制后端子类实现：

```python
class AttributeSetter:
    def set(self, option, value):
        raise NotImplementedError()

    def get(self, option):
        raise NotImplementedError()
```

### 第二层：setsockopt/getsockopt 别名

**F-027**：`Socket` 类直接把后端方法赋值为 POSIX 风格别名：

```python
class Socket(SocketBase, AttributeSetter):
    setsockopt = SocketBase.set
    getsockopt = SocketBase.get
```

这是简单的方法别名，无任何 Python 层包装。调用 `socket.setsockopt(zmq.LINGER, 1000)` 与 `socket.set(zmq.LINGER, 1000)` 完全等价。

### 第三层：属性动态访问

**F-059**：`AttributeSetter.__setattr__` 拦截属性赋值，将未知属性名映射到常量：

```python
def __setattr__(self, key, value):
    if key in self.__dict__ or key in self.__class__.__dict__:
        super().__setattr__(key, value)
        return
    for klass in type(self).__mro__:
        if key in getattr(klass, '__dict__', {}) or key in getattr(klass, '__annotations__', {}):
            super().__setattr__(key, value)
            return
    upper_key = key.upper()
    opt = getattr(constants, upper_key, None)
    if opt is not None:
        self._set_attr_opt(upper_key, opt, value)
    else:
        super().__setattr__(key, value)
```

**解析流程**：

1. **实例属性检查**：key 已在 `self.__dict__` 中 → 普通 setattr
2. **类/MRO 属性检查**：key 是类属性、方法或注解 → 普通 setattr（避免覆盖方法）
3. **常量查找**：将 key 大写（`linger` → `LINGER`），从 `zmq.constants` 模块查同名常量
4. **委托设置**：找到常量则调用 `self._set_attr_opt(upper_key, opt, value)`
5. **回退**：未找到常量则普通 setattr（允许动态添加实例属性）

**F-060**：`__getattr__` 同理处理属性读取：

```python
def __getattr__(self, key):
    upper_key = key.upper()
    opt = getattr(constants, upper_key, None)
    if opt is not None:
        try:
            return self._get_attr_opt(upper_key, opt)
        except ZMQError as e:
            if e.errno in (EINVAL, EFAULT):
                raise AttributeError(key)
            raise
    raise AttributeError(key)
```

**只写选项处理**：部分选项（如 SUBSCRIBE、UNSUBSCRIBE）是只写的，`getsockopt` 会返回 EINVAL 或 EFAULT。`__getattr__` 捕获这两个错误码并转为 `AttributeError`，使 `hasattr(socket, 'subscribe')` 返回 False 而非抛异常。

## F-061：_set_attr_opt / _get_attr_opt 钩子

`AttributeSetter` 提供了默认实现：

```python
def _set_attr_opt(self, name, opt, value):
    self.set(opt, value)

def _get_attr_opt(self, name, opt):
    return self.get(opt)
```

子类可覆写这两个方法以改变选项设置的行为。`Context` 即利用此机制实现了选项分流。

## Context 的选项分流

**F-019、F-020**：`Context` 维护 `self.sockopts = {}` 字典，覆写 `_set_attr_opt`/`_get_attr_opt` 以区分两类选项：

```python
def _set_attr_opt(self, name, opt, value):
    if isinstance(opt, constants.ContextOption):
        self.set(opt, value)
    else:
        self.sockopts[opt] = value

def _get_attr_opt(self, name, opt):
    if isinstance(opt, constants.ContextOption):
        return self.get(opt)
    else:
        return self.sockopts.get(opt)
```

**分流逻辑**：

| 选项类型 | 判断条件 | 设置行为 | 获取行为 |
|---------|---------|---------|---------|
| ContextOption | `isinstance(opt, ContextOption)` | 直接调 `self.set(opt, value)`（C 层） | 直接调 `self.get(opt)`（C 层） |
| SocketOption（默认选项） | 其他所有 | 存入 `self.sockopts` 字典 | 从 `self.sockopts` 字典查 |

**设计意图**：v13 新增的"默认 socket 选项"机制——在 Context 上设置的 SocketOption 不会立即生效，而是存入字典，当 `ctx.socket()` 创建新 socket 时批量应用（F-018）。这使得可以在 Context 级别统一配置所有新 socket 的默认选项。

```python
ctx = zmq.Context()
ctx.linger = 0          # 存入 sockopts，不调用 C 层
ctx.io_threads = 2      # ContextOption，直接调用 C 层 zmq_ctx_set

sock = ctx.socket(zmq.PUB)  # 创建时自动把 sockopts 中的 linger=0 应用到新 socket
```

ContextOption 包括 `IO_THREADS`、`MAX_SOCKETS`、`IPV6`、`BLOCKY` 等，这些是 context 级别的配置；而 `LINGER`、`SNDHWM`、`RCVHWM` 等是 socket 级别的选项，在 Context 上设置仅作为默认值。

## Socket 的 subscribe 特判

**F-028**：`Socket.__setattr__` 额外特判 `subscribe`/`unsubscribe` 键：

```python
def __setattr__(self, key, value):
    if key.lower() in ('subscribe', 'unsubscribe'):
        if isinstance(value, str):
            value = value.encode('utf8')
        opt = getattr(zmq, key.upper())
        self.set(opt, value)
        return
    super().__setattr__(key, value)
```

这使得以下四种写法完全等价：

```python
socket.set(zmq.SUBSCRIBE, b"topic")
socket.setsockopt(zmq.SUBSCRIBE, b"topic")
socket.subscribe = b"topic"
socket.subscribe(b"topic")
```

注意特判是大小写不敏感的（`key.lower()`），且字符串值自动编码为 utf8。`subscribe(topic)`/`unsubscribe(topic)` 是显式方法（F-029），接受 str 或 bytes。

## Frame 的属性访问

`Frame` 也继承 `AttributeSetter`，使其支持通过属性访问消息选项：

```python
frame.more        # 等价于 frame.get(zmq.MORE)
frame['User-Id']  # 通过 __getitem__ 映射到 self.get(key)（F-047）
```

Frame 的 `group`（RADIO-DISH）和 `routing_id`（CLIENT-SERVER）是 draft 属性（F-049），要求 libzmq ≥4.2 且启用 draft API。

## 常量解析与 AUTOGENERATED 展开

属性动态查找依赖于 `constants.py` 的模块级常量展开（F-091）。当访问 `socket.linger` 时：

1. `__setattr__` 将 `linger` 大写为 `LINGER`
2. `getattr(constants, 'LINGER')` 查找模块属性
3. 由于 AUTOGENERATED 展开，`constants.LINGER` 存在，值为 `SocketOption.LINGER`（IntEnum 成员，同时是 int）
4. 委托给 `self._set_attr_opt('LINGER', SocketOption.LINGER, value)`

如果没有模块级展开，只有枚举类定义，则 `getattr(constants, 'LINGER')` 会失败（因为 `LINGER` 是 `SocketOption` 的成员而非模块属性）。AUTOGENERATED 展开是属性访问机制能工作的前提。

## 完整调用链示例

以 `socket.hwm = 1000` 为例：

```
socket.hwm = 1000
  └─ Socket.__setattr__('hwm', 1000)
       ├─ 'hwm' 不在 __dict__ / 类__dict__ / __annotations__
       ├─ upper_key = 'HWM'
       ├─ opt = constants.HWM = SocketOption.HWM (=1, _opt_type=int64)
       └─ _set_attr_opt('HWM', HWM, 1000)
            └─ AttributeSetter._set_attr_opt (默认实现)
                 └─ self.set(HWM, 1000)
                      └─ 后端 Socket.set (Cython/CFFI)
                           ├─ opt_type = SocketOption(HWM)._opt_type = int64
                           ├─ c_value = ffi.new('int64_t*', 1000)  [CFFI]
                           └─ C.zmq_setsockopt(sock, HWM, c_value, sizeof(int64_t))
```

以 `ctx.linger = 0` 为例（Context 分流）：

```
ctx.linger = 0
  └─ Context.__setattr__('linger', 0)
       ├─ upper_key = 'LINGER'
       ├─ opt = constants.LINGER = SocketOption.LINGER
       └─ _set_attr_opt('LINGER', LINGER, 0)
            └─ Context._set_attr_opt 覆写
                 ├─ isinstance(LINGER, ContextOption)? → False (是 SocketOption)
                 └─ self.sockopts[LINGER] = 0  (存入字典，不调 C)
```

## 相关概念

- [constants.py 枚举常量](constants-enums.md) — IntEnum 定义与 AUTOGENERATED 展开
- [Context 生命周期](../concepts/01-context-lifecycle.md) — sockopts 默认选项继承
- [Socket sugar 语法层](../concepts/02-socket-sugar.md) — subscribe 属性与方法
- [整体架构与双后端](../concepts/00-architecture-dual-backend.md) — set/get 的后端实现
