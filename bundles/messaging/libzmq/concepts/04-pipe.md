---
type: concept
title: "管道 pipe_t 与流控"
description: "pipepair 双向管道创建、ypipe_t 单读单写无锁队列、HWM/LWM 背压流控、六种终止状态机、conflate 只保留最新消息模式、flush 唤醒机制"
tags: [libzmq, zeromq, pipe, ypipe, hwm, flow-control, lock-free]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/socket-base.md, ../references/command.md]
  facts: [F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-084, F-085, F-086]
---

# 管道 pipe_t 与流控

## 核心理解

`pipe_t` 是 libzmq 中连接应用线程 socket 与 I/O 线程 session 的双向消息通道。它是四层管线模型中的第二层，底层使用 `ypipe_t<msg_t>`——一个**单读单写无锁队列**。pipe 实现了基于高水位（HWM）/低水位（LWM）的背压流控，是 ZeroMQ 防止内存无限增长的核心机制。

每个 pipe 是单向的，但 `pipepair()` 工厂函数创建一对互联的 pipe，构成双向通道。socket 写消息到 pipe 的出站方向，I/O 线程从入站方向读取并发到网络；反之，网络消息从 I/O 线程写入入站方向，socket 读取。

## pipepair：创建双向管道

`pipepair()` 是创建管道的工厂函数（F-032）：

```cpp
void pipepair (object_t *parents_[2],
               pipe_t *pipes_[2],
               const int hwms_[2],
               const bool conflate_[2]);
```

参数说明：

| 参数 | 说明 |
|------|------|
| `parents_[2]` | 两个父对象（通常是 socket 和 session） |
| `pipes_[2]` | 输出参数，返回创建的两个 pipe 指针 |
| `hwms_[2]` | 两个方向的 HWM 值。hwms[0] 控制 pipe[0]→pipe[1]，hwms[1] 控制反向 |
| `conflate_[2]` | 两个方向是否启用 conflate 模式 |

创建后：
- `pipes[0]` 交给 parents[0]（socket），其 `_out_pipe` 指向 pipes[1] 的 `_in_pipe`
- `pipes[1]` 交给 parents[1]（session），其 `_out_pipe` 指向 pipes[0] 的 `_in_pipe`

对于 inproc 连接，HWM 为两端 HWM 之和（`sndhwm + rcvhwm`），确保两端流控协调。

## pipe_t 内部结构

`pipe_t` 持有双向的 ypipe（F-033）：

```cpp
class pipe_t : public object_t, public i_pipe_events {
    ypipe_base_t<msg_t> *_in_pipe;    // 读取方向
    ypipe_base_t<msg_t> *_out_pipe;   // 写入方向
    bool _in_active;                  // 入站方向是否活跃
    bool _out_active;                 // 出站方向是否活跃
    pipe_t *_peer;                    // 对端 pipe
    // ...
};
```

- `_in_pipe`：从对端接收消息的队列
- `_out_pipe`：向对端发送消息的队列
- `_in_active`/`_out_active`：控制方向是否活跃（HWM 触发时变为非活跃）
- `_peer`：指向对端 pipe，用于发送命令（activate_read/activate_write）

`ypipe_base_t<msg_t>` 是抽象基类，具体实现有两种：
- `ypipe_t<msg_t, N>`：标准无锁队列，支持 HWM 流控
- `ypipe_conflate_t<msg_t>`：conflate 模式，只保留最新消息

## ypipe_t：单读单写无锁队列

`ypipe_t<T, N>` 是 libzmq 的核心无锁数据结构（F-084）：

```cpp
template <typename T, int N>
class ypipe_t : public ypipe_base_t<T> {
    yqueue_t<T, N> _queue;
    T *_w;      // 第一个未 flush 项（写线程专用）
    T *_r;      // 第一个未预取项（读线程专用）
    T *_f;      // 将来要 flush 的位置（写线程专用）
    atomic_ptr_t<T> _c;  // 读写线程唯一争用点
};
```

**单读单写约束**：同一时刻只能有一个线程读、一个线程写。在 libzmq 中：
- 写端：消息产生方（socket 的应用线程 或 engine 的 I/O 线程）
- 读端：消息消费方（I/O 线程 或 应用线程）

三个指针的语义：

| 指针 | 所属线程 | 含义 |
|------|---------|------|
| `_w` | 写线程 | 第一个未被 flush 的写入位置 |
| `_f` | 写线程 | 下次 flush 的目标位置（`_f` 和 `_w` 之间是已写入但未 flush 的项） |
| `_r` | 读线程 | 第一个未被预取的读取位置 |
| `_c` | 原子共享 | 读端当前位置；NULL 表示读端休眠 |

### write 和 flush

写线程先 `write()` 多项到 `_w`~`_f` 之间，然后调用 `flush()` 使这些项对读线程可见（F-037, F-085）：

```
flush():
  if _c.cas(_w, _f):        // CAS 尝试
    _w = _f                  // 成功：读端存活，直接推进
    return true
  else:                      // _c == NULL（读端休眠）
    _c = _f                  // 非原子设置
    _w = _f
    return false             // 通知调用者需要唤醒读端
```

flush 返回 false 时，调用者通过 signaler 发送信号唤醒读线程。在 pipe 中，这通过 `send_activate_read(_peer)` 命令完成。

### read

读线程 `read()`：
1. 检查 `_r` 是否有预取项
2. 若有，返回该项，推进 `_r`
3. 若无，检查 `_c`（原子交换为 NULL）
4. 若 `_c` 有值，批量预取到 `_r`，返回第一项
5. 若无，返回 false（无消息可读）

## yqueue_t：批量内存块

`yqueue_t<T, N>` 是 ypipe 的底层队列（F-086），以 `chunk_t` 为单位分配内存：

```cpp
struct chunk_t {
    T values[N];              // N 个元素（消息管道 N=256，命令管道 N=16）
    chunk_t *prev;
    chunk_t *next;
};

atomic_ptr_t<chunk_t> _spare_chunk;  // 缓存最近释放的块
```

- N=256 用于消息管道（`ypipe_t<msg_t, 256>`）
- N=16 用于命令管道（`ypipe_t<command_t, 16>`）
- `_spare_chunk` 缓存最近释放的块，减少 malloc/free 频率
- 支持 POSIX `posix_memalign` 按缓存行对齐（默认 64 字节），避免伪共享

## HWM/LWM 流控机制

HWM（High Water Mark，高水位）和 LWM（Low Water Mark，低水位）是 pipe 的背压机制（F-036）。

### HWM

`_hwm` 限制出站方向未确认消息数：
- 当 `_msgs_written - _peers_msgs_read >= _hwm` 时，写端变为非活跃（`_out_active = false`）
- 写端非活跃时，socket 的 `xsend` 返回 EAGAIN（对于非阻塞发送）或阻塞处理命令等待

### LWM

`_lwm` 由 `compute_lwm(hwm)` 计算，通常为 HWM 的一半：
- 读端每读取 `_lwm` 条消息，向对端发送 `activate_write` 命令（F-035）
- 该命令携带 `msgs_read` 计数
- 写端收到后更新 `_peers_msgs_read`，重新检查 HWM 条件
- 若已低于 HWM，设置 `_out_active = true` 并通知 socket（`xwrite_activated`）

### 流控时序

```
写端 (socket)                    读端 (session/engine)
  │                                │
  │ write msg 1..1000              │
  │ (msgs_written=1000=HWM)        │
  │ _out_active = false            │
  │ xsend → EAGAIN                 │
  │                                │ read msg 1..500
  │                                │ (读取 LWM=500 条)
  │                                │ send activate_write(500)
  │ ◄── activate_write ───────────│
  │ _peers_msgs_read = 500         │
  │ 1000-500=500 < HWM=1000       │
  │ _out_active = true             │
  │ xwrite_activated → 可继续写    │
  │                                │
```

这种设计避免了每条消息都发送确认（ACK），而是批量确认（每 LWM 条），减少跨线程命令数。

## read/write 实现

### read（F-035）

```cpp
bool read (msg_t *msg_):
  if (!_in_pipe->read(msg_)):
    return false

  if 消息是 credential:
    跳过，继续读下一条

  if 消息是 delimiter:
    process_delimiter()
    return false

  _msgs_read++
  if (_msgs_read % _lwm == 0):
    send_activate_write(_peer, _msgs_read)

  return true
```

- credential 消息（ZAP 认证凭证）被自动跳过，不传递给应用层
- delimiter 触发终止处理
- 每读 LWM 条消息通知对端恢复写入

### write（F-035）

```cpp
bool write (msg_t *msg_):
  if (!_out_active || !_out_pipe->write(msg_)):
    return false

  if (!(msg_flags & more)):
    _msgs_written++
    if (_hwm > 0 && _msgs_written - _peers_msgs_read >= _hwm):
      _out_active = false

  return true
```

- 只有非 more 帧（消息边界）才递增 `_msgs_written`
- HWM 检查基于消息数而非字节数
- HWM=0 表示无限制

## flush：唤醒对端

`flush()` 刷新出站管道（F-037）：

```cpp
void flush ():
  if (_out_pipe->flush()):
    return  // 读端存活，无需唤醒
  send_activate_read(_peer)  // 读端休眠，发送命令唤醒
```

socket 在 `send()` 后必须调用 `pipe->flush()` 确保消息对 I/O 线程可见。如果 flush 返回 false（I/O 线程的 mailbox 读端正休眠），通过 `activate_read` 命令唤醒。

## 六种终止状态

pipe_t 定义了六种终止状态（F-034），形成复杂的终止状态机：

| 状态 | 说明 |
|------|------|
| `active` | 正常运行 |
| `delimiter_received` | 读到分隔符但未收到 term 命令 |
| `waiting_for_delimiter` | 已收到 term 命令但仍有未读消息 |
| `term_ack_sent` | 所有待处理消息已读，等待对端 ack |
| `term_req_sent1` | 用户显式调用 terminate |
| `term_req_sent2` | 用户 terminate 后又收到对端 term |

终止协议确保：
1. 管道中未读消息不会丢失（等待 delimiter）
2. 两端都确认关闭后才销毁 pipe
3. 避免一端提前销毁导致对端访问已释放内存

终止流程：
```
端 A                             端 B
  │── pipe_term ──────────────────►│ (B 收到终止请求)
  │                                │ B 读完剩余消息...
  │                                │ B 写入 delimiter
  │◄── delimiter (在队列中) ───────│
  │ A 读到 delimiter              │
  │── pipe_term_ack ──────────────►│
  │                                │ B 销毁
  │ A 销毁                         │
```

## conflate 模式

当 `_conflate = true` 时（F-038），pipe 使用 `ypipe_conflate_t` 替代 `ypipe_t`：

- 只保留**最近到达**的消息
- 新消息到达时丢弃旧消息
- **忽略 HWM**（不做流控）
- 适用于只关心最新值的场景（如市场行情、传感器读数）

conflate 模式仅支持以下 socket 类型：DEALER、PUSH、PULL、PUB、SUB（内部检查，其他类型设置会报错）。

典型用例：
```c
// 传感器更新——只需要最新读数
zmq_setsockopt(socket, ZMQ_CONFLATE, &yes, sizeof(yes));
// 即使发送方发送速度远快于接收方，队列中也只有一条最新消息
```

## pipe 在四层管线中的角色

```
应用线程                         I/O 线程
┌─────────────┐                ┌──────────────┐
│ socket_base │                │ session_base │
│   _pipes[]  │                │    _pipe     │
└──────┬──────┘                └──────┬───────┘
       │                              │
       │   pipe[0]          pipe[1]   │
       │  ┌────────┐      ┌────────┐  │
       └──┤ _out   │─────►│ _in    │◄─┘
          │ ypipe  │      │ ypipe  │
       ┌──►_in    │◄─────│ _out   │──┐
       │  └────────┘      └────────┘  │
       │                              │
   msg_t write                  msg_t read
   msg_t read                   msg_t write
       │                              │
       ▼                              ▼
   应用收发                      engine 网络收发
```

## 相关概念

- [套接字基类](/concepts/02-socket-base.md) — socket 通过 _pipes 数组管理所有 pipe
- [消息与引用计数](/concepts/03-message.md) — msg_t 在 ypipe 中值拷贝传递
- [会话与连接生命周期](/concepts/05-session.md) — session 持有 pipe 连接到 socket
- [命令传递与邮箱](/concepts/08-command-mailbox.md) — activate_read/write 命令通过 mailbox 传递
- [I/O 线程与多路复用](/concepts/07-io-thread-poller.md) — ypipe flush 失败时通过 signaler 唤醒
- [消息模式实现](/concepts/11-patterns.md) — fq/lb/dist 算法管理多个 pipe
