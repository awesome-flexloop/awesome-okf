---
type: concept
title: "整体架构与双后端机制"
description: "pyzmq 的双层架构：后端 C 绑定（Cython/CFFI）与 sugar 纯 Python 语法层的职责分离，运行时后端选择逻辑、public_api 契约、包导入顺序、COPY_THRESHOLD 与 DRAFT_API 全局配置"
tags: [pyzmq, zeromq, architecture, backend, cython, cffi, sugar]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/cffi-internals.md, ../references/constants-enums.md]
  facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-077, F-078, F-079]
---

# 整体架构与双后端机制

## 核心理解

pyzmq 是 ZeroMQ（零消息队列，高性能异步消息库）的 Python 绑定。它的核心架构遵循**"薄绑定 + 厚语法层"**的双层设计：后端层提供与 libzmq C ABI 一一对应的薄绑定，sugar 层用纯 Python 类在其上叠加符合 Python 习惯的语法糖。更关键的是，后端本身是可插拔的——同一份 pyzmq 安装可以在 Cython 后端（高性能 C 扩展）和 CFFI 后端（可移植纯 Python+CFFI）之间运行时切换，用户代码完全不感知。

这种架构使 pyzmq 能在 CPython 上追求极致性能，在 PyPy 上自动切换到兼容的 CFFI 后端，同时保持用户 API 100% 一致。

## 双层架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    用户代码 (import zmq)                      │
│  zmq.Context() / socket.send_string() / socket.subscribe    │
├─────────────────────────────────────────────────────────────┤
│                    sugar 层（纯 Python）                      │
│  zmq/sugar/context.py  — Context 类（生命周期、单例、shadow）  │
│  zmq/sugar/socket.py   — Socket 类（序列化、multipart、poll） │
│  zmq/sugar/frame.py    — Frame 类（消息帧、属性访问）          │
│  zmq/sugar/poll.py     — Poller 类（多路复用）                │
│  zmq/sugar/tracker.py  — MessageTracker（发送跟踪）           │
│  zmq/sugar/attrsettr.py — AttributeSetter mixin（动态属性）   │
│  作用：上下文管理器、序列化、属性访问、监控、装饰器            │
├─────────────────────────────────────────────────────────────┤
│                    backend 层（C 绑定）                       │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │  Cython 后端（默认）  │    │  CFFI 后端（回退）   │         │
│  │  zmq/backend/cython/│    │  zmq/backend/cffi/  │         │
│  │  .pyx/.pxd C 扩展   │    │  ffi + lib CFFI 绑定 │         │
│  │  高性能，CPython 优化 │    │  可移植，PyPy 友好   │         │
│  └─────────┬───────────┘    └──────────┬──────────┘         │
│            └──────────┬────────────────┘                    │
│              public_api 契约（15个符号）                      │
├─────────────────────────────────────────────────────────────┤
│                    libzmq（C 库）                             │
│  zmq_ctx_new / zmq_socket / zmq_send / zmq_recv / ...       │
└─────────────────────────────────────────────────────────────┘
```

### sugar 层的职责

sugar 层（`zmq/sugar/`）是用户日常接触的 API 表面。它完全用纯 Python 实现，通过多继承组合后端基类：

- `Context` 继承 `zmq.backend.Context`（C 扩展基类）与 `AttributeSetter` mixin（F-009）
- `Socket` 继承 `zmq.backend.Socket` 与 `AttributeSetter`（F-022）
- `Frame` 继承 `zmq.backend.Frame`（C 扩展，本身是 bytes 子类）与 `AttributeSetter`（F-046）

sugar 类不直接持有 C 指针，而是通过 `super()` 调用后端方法。它在后端薄绑定之上叠加了：

- **上下文管理器协议**：`with zmq.Context() as ctx:`、`with ctx.socket(...) as sock:`
- **序列化便捷方法**：`send_string`/`recv_string`、`send_json`/`recv_json`、`send_pyobj`/`recv_pyobj`
- **多帧消息**：`send_multipart`/`recv_multipart`
- **属性访问**：`socket.linger = 1000` 而非 `socket.setsockopt(zmq.LINGER, 1000)`
- **监控**：`get_monitor_socket` 封装 PAIR 连接
- **装饰器**：`@zmq.decorators.context()`、`@zmq.decorators.socket(zmq.PUB)`

### backend 层的职责

后端层只做一件事：把 libzmq 的 C ABI 暴露为 Python 可调用对象。它不包含任何业务逻辑或语法糖。Cython 后端用 `.pyx` 文件以 C 扩展形式实现，CFFI 后端通过 CFFI 库在运行时绑定 C 函数。两者实现相同的 public API 契约。

## 后端可插拔机制

### F-077：运行时选择逻辑

**信源**：`zmq/backend/__init__.py:11-31`

后端选择在 `import zmq.backend` 时自动执行：

```
import zmq.backend
  │
  ├─ 检查环境变量 PYZMQ_BACKEND
  │   ├─ "cython" → 强制选择 Cython
  │   ├─ "cffi"   → 强制选择 CFFI
  │   └─ 未设置    → 按平台默认顺序尝试
  │
  ├─ CPython：先尝试 Cython，失败回退 CFFI
  ├─ PyPy：先尝试 CFFI，失败回退 Cython
  │
  └─ 第一个后端 import 成功 → 选定
     第一个失败 → 尝试第二个
     第二个也失败 → 抛出原始 ImportError
```

用户可通过环境变量强制指定：

```bash
# 强制使用 CFFI 后端（调试、PyPy 兼容）
export PYZMQ_BACKEND=cffi

# 强制使用 Cython 后端
export PYZMQ_BACKEND=cython
```

### F-078：public_api 契约

**信源**：`zmq/backend/select.py:9-41`

`select_backend(name)` 用 `importlib.import_module` 加载后端模块，从模块中提取固定的 `public_api` 名字集合注入 `zmq.backend` 命名空间：

| 符号 | 类型 | 说明 |
|------|------|------|
| `Context` | class | 后端 Context 基类 |
| `Socket` | class | 后端 Socket 基类 |
| `Frame` | class | 后端 Frame 基类 |
| `Message` | alias | Frame 的别名 |
| `proxy` | function | `zmq_proxy` C 函数绑定 |
| `proxy_steerable` | function | `zmq_proxy_steerable` 绑定 |
| `zmq_poll` | function | `zmq_poll` C 函数绑定 |
| `strerror` | function | 错误码→字符串 |
| `zmq_errno` | function | 获取当前错误码 |
| `has` | function | 能力检测（capability） |
| `curve_keypair` | function | 生成 CURVE 密钥对 |
| `curve_public` | function | 私钥→公钥推导 |
| `zmq_version_info` | function | libzmq 版本元组 |
| `IPC_PATH_MAX_LEN` | constant | IPC 路径最大长度 |
| `PYZMQ_DRAFT_API` | bool | 是否启用 draft API |
| `monitored_queue` | function（私有） | 监控队列内部函数 |

这 15 个左右的符号是后端必须实现的完整契约。sugar 层只 `from zmq.backend import Context as ContextBase`，完全不感知具体后端。新增后端（如未来的纯 ctypes 或 Rust 扩展）只需实现这些符号即可无缝替换。

### F-079：CFFI 后端加载

CFFI 后端通过预编译的 `_cffi` 模块加载：

```python
from ._cffi import ffi, lib as C
```

`ffi` 是 `cffi.FFI` 实例（类型构造与指针操作），`C` 是 libzmq 共享库的绑定对象，所有 C 函数通过 `C.zmq_*` 访问。详见 [CFFI 后端内部参考](../references/cffi-internals.md)。

## 包导入顺序

### F-002：顶层导入顺序

**信源**：`zmq/__init__.py:51-58`

```python
from zmq import backend
from zmq.backend import *
from zmq import constants
from zmq.constants import *
from zmq import sugar
from zmq.sugar import *
```

导入顺序有严格的依赖关系：

1. **backend 先加载**：后端必须最先初始化，因为 sugar 层的类继承自后端基类
2. **constants 其次**：常量在 sugar 层属性访问时需要
3. **sugar 最后聚合**：sugar 类定义完成后，通过 `from zmq.sugar import *` 聚合到顶层 `zmq` 命名空间

### F-007：sugar 包聚合

sugar 包的 `__init__.py` 从后端导入 `proxy`，并聚合 context/frame/poll/socket/tracker/version 子模块的 `__all__`，同时把 `error` 模块的名字也通过 `from zmq.error import *` 导出。

### F-005：__all__ 拼接

顶层 `__all__` 由四部分拼接：
- `get_includes`、`COPY_THRESHOLD`、`DRAFT_API`
- `constants.__all__`
- `sugar.__all__`
- `backend.__all__`

## 全局配置常量

### F-003：COPY_THRESHOLD

```python
zmq.COPY_THRESHOLD = 65536  # 64KB
```

这是 zero-copy（零拷贝）与 copy（拷贝）模式的默认分界阈值。当发送的消息小于此值时，即使请求 zero-copy（`copy=False`），后端也会自动切换到 copy 路径。原因是小消息的 zero-copy 开销（GC 回调注册、引用计数管理、C 函数调用次数）超过了数据复制本身的成本。

### F-004：DRAFT_API

```python
zmq.DRAFT_API = backend.has('draft') and backend.PYZMQ_DRAFT_API
```

布尔值，表示当前运行时是否支持 ZeroMQ draft API（如 RADIO-DISH、CLIENT-SERVER、thread-safe socket 等实验性模式）。要求两个条件同时满足：

1. 运行时加载的 libzmq 编译时启用了 draft 支持（`backend.has('draft')`）
2. pyzmq 构建时也启用了 draft（`backend.PYZMQ_DRAFT_API`）

这是一个"双重门控"——构建时和运行时都必须启用，避免一端支持另一端不支持导致 ABI 不匹配。

### F-006：get_includes

`get_includes()` 返回用于 Cython 链接 pyzmq 的 include 目录列表，包含：
- pyzmq 包的父目录
- `utils/` 子目录
- 可选的 `include/` 目录（如果存在）

第三方 Cython 扩展可以通过 `zmq.get_includes()` 获取编译时需要的头文件路径。

## Windows DLL 路径处理

### F-001：_libs_on_path

在 Windows 上，`zmq/__init__.py` 通过 `_libs_on_path()` 上下文管理器临时把 `pyzmq.libs/` 目录加入 `PATH` 环境变量。这是为了解决 conda-forge Python ≥3.8 的 DLL 解析变更——Python 3.8+ 不再默认从 PATH 搜索 DLL，而 conda 打包的 pyzmq 把 libzmq DLL 放在 `pyzmq.libs/` 目录。

非 Windows 平台此上下文管理器直接 yield，不做任何操作。

## F-008：废弃的 device 函数

`zmq.sugar.device(device_type, frontend, backend)` 是已废弃的 `zmq.proxy` 别名，内部直接调用 `proxy(frontend, backend)`，忽略 `device_type` 参数。新代码应使用 `zmq.proxy(frontend, backend)`。

## 关键设计洞察

### 洞察一：薄绑定 + 厚语法层

pyzmq 把 ABI 稳定性和性能敏感面压缩到最小的后端层（约 15 个符号的薄绑定），把可用性、API 演进、类型提示全部放在纯 Python 的 sugar 层。这意味着：

- 后端可以整体替换（Cython ↔ CFFI）而用户代码不感知
- sugar 层的 bug 修复和新功能不需要重新编译 C 扩展
- Python 开发者可以直接阅读 sugar 层源码理解 API 行为

### 洞察二：面向接口编程

`public_api` 列表既是契约也是测试边界。两个后端只要实现相同的 15 个符号即可互换，这是"面向接口编程 + 运行时发现"的经典实践。

### 洞察三：元数据驱动选项系统

`SocketOption` 枚举成员携带 `_opt_type` 元数据（int/int64/bytes/fd），后端据此选择 C 指针类型。常量集中定义在 `constants.py`，sugar 层的 `AttributeSetter` 动态解析属性名到常量，后端按元数据封送参数——三者协作构成元数据驱动的选项系统。详见 [attrsettr 选项访问](../references/attrsettr-options.md)。

## 相关概念

- [Context 生命周期](/concepts/01-context-lifecycle.md) — sugar.Context 如何在后端基类上叠加生命周期管理
- [Socket sugar 语法层](/concepts/02-socket-sugar.md) — sugar.Socket 的 send/recv/序列化/监控
- [Frame 与消息](/concepts/03-frame-message.md) — Frame 的 zero-copy 与 COPY_THRESHOLD 实践
- [异步与 asyncio](/concepts/05-async-future-asyncio.md) — 异步后端如何通过子类覆写实现
- [CFFI 后端内部](/references/cffi-internals.md) — CFFI 后端的完整实现细节
- [常量枚举参考](/references/constants-enums.md) — public_api 中常量的完整定义
