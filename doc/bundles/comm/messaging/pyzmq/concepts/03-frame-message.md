---
type: concept
title: "Frame 与消息：零拷贝、MessageTracker 与 GC 回调"
description: "pyzmq Frame 作为 bytes 子类的设计、zero-copy 与 COPY_THRESHOLD 自动降级、MessageTracker 发送跟踪机制、_FINISHED_TRACKER 单例、CFFI 后端 GC 回调与 fast_copy 引用计数、group/routing_id draft 属性"
tags: [pyzmq, zeromq, frame, message, zero-copy, message-tracker, cffi]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/cffi-internals.md, ../references/constants-enums.md, ../references/error-hierarchy.md]
  facts: [F-046, F-047, F-048, F-049, F-055, F-056, F-057, F-058, F-086, F-087]
---

# Frame 与消息：零拷贝、MessageTracker 与 GC 回调

## 核心理解

`zmq.Frame` 是 pyzmq 对 ZeroMQ 消息帧（`zmq_msg_t`）的 Python 封装。它最反直觉的设计是：**Frame 本身就是 bytes 的子类**——你可以直接把 Frame 当 bytes 用（切片、拼接、传给 `b''.join()`），但它同时持有 libzmq 的消息结构引用，支持零拷贝发送、发送完成跟踪和消息元数据访问。

零拷贝（zero-copy）是高性能消息系统的关键技术：发送大数据时避免内核态到用户态的内存复制。但零拷贝引入了生命周期管理问题——libzmq 异步发送时，Python 不能提前释放数据缓冲区。pyzmq 通过 `MessageTracker`、CFFI 后端的 GC 回调和 `COPY_THRESHOLD` 自动降级机制，优雅地解决了这个问题。

## Frame 类层次

### F-046：继承结构

```python
class Frame(
    zmq.backend.FrameBase,    # C 扩展基类（本身是 bytes 子类）
    AttributeSetter,          # 动态选项属性
):
    pass

Message = Frame  # 保留的废弃别名
```

`FrameBase` 是后端 C 扩展类型，本身继承自 `bytes`。这意味着每个 Frame 实例**就是一个不可变字节序列**，可以直接在任何需要 bytes 的地方使用：

```python
frame = socket.recv(copy=False)
assert isinstance(frame, bytes)       # True
assert isinstance(frame, zmq.Frame)   # True
data = bytes(frame)                   # 显式转换
print(frame[:10])                     # 切片
print(len(frame))                     # 长度
```

`Message` 是 `Frame` 的别名，保留用于向后兼容，新代码应使用 `Frame`。

## Frame 属性与方法

### F-047：字典式属性访问

`Frame.__getitem__` 把字典式访问映射到 `self.get(key)`：

```python
frame = socket.recv(copy=False)

# 字典式访问消息属性
user_id = frame['User-Id']     # 等价于 frame.get('User-Id')
socket_type = frame['Type']    # 等价于 frame.get(zmq.TYPE)

# 键可以是 int、str 或 bytes
frame[zmq.MORE]                # int 选项 ID
frame['User-Id']               # str 选项名
frame[b'User-Id']              # bytes 选项名
```

这为消息元数据提供了类似 HTTP header 的访问体验。

### F-048：智能 repr

Frame 的 `__repr__` 对大消息做截断显示，避免日志中输出海量数据：

```python
zmq.Frame(b"short")          # zmq.Frame(b"short")
zmq.Frame(b"x" * 100)        # zmq.Frame(b"xxxxxxxxxxxx...100B")
zmq.Frame(b"x" * 2048)       # zmq.Frame(b"xxxxxxxxxxxx...2kB")
```

大于 16 字节的消息只显示前 12 字节，附加 `...{n}{unit}` 后缀，单位自动选择 B/kB/MB/GB。模块名若为 `zmq.sugar.frame` 则显示为 `zmq`，使用户看到的是 `zmq.Frame(...)` 而非内部模块路径。

### F-049：draft 属性

`group`（RADIO-DISH 模式）和 `routing_id`（CLIENT-SERVER 模式）是 draft API 属性：

```python
frame.group = b"group1"           # RADIO 套接字发送时设置组
gid = frame.group                 # DISH 套接字接收时获取组

frame.routing_id = 12345          # SERVER 回复时设置路由 ID
rid = frame.routing_id            # CLIENT 接收时获取路由 ID
```

这两个 property 要求：
- libzmq ≥ 4.2
- pyzmq 和 libzmq 均启用 draft API（`zmq.DRAFT_API == True`）

不满足条件时通过 `_draft()` 辅助函数抛出 `ZMQVersionError`。底层调用 `self.get/set('group'/'routing_id')`。

### Frame 核心属性

| 属性 | 说明 |
|------|------|
| `frame.bytes` | 消息数据的 bytes 表示（copy 模式下与自身相同） |
| `frame.buffer` | 消息数据的 memoryview（零拷贝访问） |
| `frame.more` | 是否有后续帧（bool，对应 `zmq.MORE`） |
| `frame.tracker` | 关联的 MessageTracker（如果有） |
| `frame.group` | RADIO-DISH 组（draft） |
| `frame.routing_id` | CLIENT-SERVER 路由 ID（draft） |

## 零拷贝发送与 COPY_THRESHOLD

### copy 参数

`send(data, copy=True, track=False)` 的 copy 参数控制发送路径：

```python
# copy=True（默认）：数据被复制到 libzmq 内部缓冲区
# send 返回后立即可安全修改/释放 data
socket.send(large_data)  # None 返回

# copy=False：零拷贝，data 的缓冲区直接被 libzmq 引用
# 必须通过 tracker 等待发送完成后才能释放 data
tracker = socket.send(large_data, copy=False, track=True)
tracker.wait()  # 等待 libzmq 完成发送
```

### F-003：COPY_THRESHOLD 自动降级

```python
zmq.COPY_THRESHOLD = 65536  # 64KB
```

即使请求 `copy=False`，当消息小于 64KB 时，后端**自动切换到 copy 路径**。原因：

- 零拷贝需要注册 GC 回调、管理引用计数、维护 C 结构体
- 这些固定开销在小消息场景下超过了数据复制本身的成本
- 64KB 是经验平衡点

自动降级后返回 `_FINISHED_TRACKER`（已完成的 tracker 单例），调用方无需等待。

```python
# 小消息：自动 copy，返回已完成 tracker
tracker = socket.send(b"small", copy=False, track=True)
assert tracker.done  # True，立即完成

# 大消息：真正零拷贝，需要等待
tracker = socket.send(b"x" * 100_000, copy=False, track=True)
tracker.wait()  # 等待异步发送完成
```

## MessageTracker

### F-055：构造与监控对象

`MessageTracker` 跟踪一个或多个异步发送操作的完成状态：

```python
tracker = MessageTracker(event1, event2, frame1, tracker2)
```

构造函数接受可变参数，每个参数可为：

| 参数类型 | 处理方式 |
|---------|---------|
| `threading.Event` | 加入 `self.events` 列表 |
| `MessageTracker` | 加入 `self.peers` 列表（递归跟踪） |
| `Frame` | 取其 `tracker` 属性加入 peers；未 tracked 的 Frame 抛 ValueError |

这使得可以组合多个发送操作的跟踪器：

```python
t1 = socket.send(frame1, copy=False, track=True)
t2 = socket.send(frame2, copy=False, track=True)
combined = MessageTracker(t1, t2)
combined.wait()  # 等待两个发送都完成
```

### F-056：done 属性

`done` 属性递归检查所有事件和 peer：

```python
@property
def done(self):
    return all(e.is_set() for e in self.events) and all(p.done for p in self.peers)
```

只有所有事件已 set 且所有 peer tracker 都 done，才返回 True。这是一个非阻塞的轮询检查。

### F-057：wait 方法

```python
tracker.wait(timeout=-1)
```

顺序等待每个 Event 和 peer：
- `timeout` 单位为秒
- 超时抛 `NotDone` 异常
- `timeout` 为 False 或负值时，用一周（3600×24×7 秒）作为"永久"上限，避免无限阻塞

```python
try:
    tracker.wait(timeout=5.0)
    print("发送完成")
except zmq.NotDone:
    print("5秒内未完成发送")
```

### F-058：_FINISHED_TRACKER 单例

模块级 `_FINISHED_TRACKER = MessageTracker()` 是一个无监控对象的已完成 tracker 单例。它在以下场景返回：

- 小消息自动降级为 copy 路径时
- copy=True 发送时（数据已复制，无需跟踪）

这避免了为每个小消息创建新的 tracker 对象，是一个性能优化。

## CFFI 后端的零拷贝 GC 机制

### F-086：GC 回调

零拷贝的核心挑战：libzmq 异步发送，发送完成前 Python 不能释放数据缓冲区。CFFI 后端通过以下机制解决：

1. **`zmq_wrap_msg_init_data`**：注册 C 回调函数 `free_python_msg`
2. **zhint 结构体**：持有 garbage collector 的 id、mutex 和 PULL socket 指针
3. **libzmq 释放时回调**：当 libzmq 完成发送并释放 `zmq_msg_t` 时，调用 `free_python_msg`
4. **PULL socket 通知**：回调通过 PULL socket 发送一个通知字节
5. **Python GC 线程**：收到通知后，知道对应的 Python buffer 可以安全释放

```
Python 发送零拷贝消息
  │
  ├─ Frame 持有 Python buffer
  ├─ zmq_wrap_msg_init_data 注册 free_python_msg 回调
  ├─ zmq_msg_send 将消息交给 libzmq
  │
  │  ... libzmq 异步发送中 ...
  │
  └─ libzmq 释放 zmq_msg_t
       └─ free_python_msg(data, zhint)
            └─ PULL socket 发送通知
                 └─ Python GC 线程收到通知
                      └─ 释放 Python buffer
```

这确保了 Python buffer 的生命周期严格长于 libzmq 的使用期，不会出现 use-after-free。

### F-087：fast_copy

`Frame.fast_copy()` 创建新 Frame 但不复制数据：

```python
frame_copy = frame.fast_copy()
```

实现方式：
1. 创建新空 Frame
2. 调用 `C.zmq_msg_copy` 增加底层 `zmq_msg` 的引用计数
3. 共享 `_data`/`_buffer`/`tracker`/`tracker_event`

这与 Python 的 `bytes` 不可变共享语义一致——两个 Frame 指向同一数据，但引用计数确保数据在最后一个 Frame 释放前不会被回收。当同一 Frame 需要多次发送时，`fast_copy` 避免了数据复制。

## copy vs zero-copy 选择指南

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 小消息（<64KB） | `copy=True`（默认） | 自动选择，零拷贝开销不划算 |
| 大消息（>64KB） | `copy=False, track=True` | 避免大内存复制 |
| 需要立即重用 buffer | `copy=True` | send 返回后 buffer 立即可重用 |
| 性能基准测试 | 两种都试 | 实际效果取决于消息大小和网络 |
| Cython 后端 | `copy=False` | Cython 的零拷贝路径更成熟 |
| CFFI 后端 | 大消息 `copy=False` | GC 回调开销在大消息时可摊薄 |

## 接收方向

接收时也有 copy/non-copy 选择：

```python
# copy=True（默认）：返回 bytes，数据已复制到 Python 堆
data = socket.recv()  # bytes

# copy=False：返回 Frame，数据留在 libzmq 缓冲区
frame = socket.recv(copy=False)  # Frame（bytes 子类）
# frame 被 GC 前，libzmq 缓冲区不释放
```

non-copy 接收在大消息场景下也有优势——避免一次从 C 到 Python 的内存复制。但需要注意 Frame 持有 C 内存，过早保留 Frame 引用会阻止 libzmq 回收缓冲区。

## 多帧消息中的 Frame

`recv_multipart(copy=False)` 返回 Frame 对象列表：

```python
frames = socket.recv_multipart(copy=False)
# frames = [Frame(topic), Frame(payload), ...]

for frame in frames:
    if frame.more:
        print("后续帧:", frame.bytes)
    else:
        print("最后一帧:", frame.bytes)
```

`frame.more` 属性对应 `zmq.RCVMORE`，指示是否还有后续帧。`send_multipart` 内部对除最后一帧外的所有帧设置 `SNDMORE` 标志。

## 相关概念

- [整体架构与双后端](00-architecture-dual-backend.md) — COPY_THRESHOLD 和 DRAFT_API 全局配置
- [Socket sugar 语法层](02-socket-sugar.md) — send/recv 的 copy/track 参数
- [CFFI 后端内部](../references/cffi-internals.md) — GC 回调和 fast_copy 的完整实现
- [错误层次结构](../references/error-hierarchy.md) — NotDone 异常
- [常量枚举参考](../references/constants-enums.md) — MessageOption 和 draft 相关常量
