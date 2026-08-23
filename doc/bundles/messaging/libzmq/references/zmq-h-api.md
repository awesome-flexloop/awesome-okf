---
type: reference
title: "zmq.h：公共 C API 完整索引"
description: "libzmq 公共头文件 include/zmq.h 中的版本宏、上下文函数、消息函数、套接字类型与选项、安全机制、轮询结构体、监控事件、代理函数的完整签名与常量值"
tags: [libzmq, reference, c-api, zmq-h]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/include/zmq.h"
    facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011]
---

# zmq.h：公共 C API 完整索引

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `include/zmq.h` | C 公共头文件 | libzmq 对外暴露的全部 C API、常量枚举、结构体定义 |

本文件是 libzmq 唯一的公共 API 入口，所有应用程序通过 `#include <zmq.h>` 使用库功能。

## 关键事实登记

### F-001：版本宏定义

**信源**：`include/zmq.h` L15-L22

```c
#define ZMQ_VERSION_MAJOR 4
#define ZMQ_VERSION_MINOR 3
#define ZMQ_VERSION_PATCH 6
#define ZMQ_MAKE_VERSION(major, minor, patch) \
    ((major) * 10000 + (minor) * 100 + (patch))
#define ZMQ_VERSION \
    ZMQ_MAKE_VERSION(ZMQ_VERSION_MAJOR, ZMQ_VERSION_MINOR, ZMQ_VERSION_PATCH)
```

整数版本号计算公式为 `major*10000 + minor*100 + patch`，4.3.6 对应 40306。

### F-002：上下文生命周期函数

**信源**：`include/zmq.h` L198-L207

```c
void *zmq_ctx_new (void);
int  zmq_ctx_term (void *context_);
int  zmq_ctx_shutdown (void *context_);
int  zmq_ctx_set (void *context_, int option_, int optval_);
int  zmq_ctx_get (void *context_, int option_);
```

遗留 API（已弃用）：
```c
void *zmq_init (int io_threads_);
int  zmq_term (void *context_);
int  zmq_ctx_destroy (void *context_);
```

- `zmq_ctx_new()`：创建新上下文，返回不透明指针
- `zmq_ctx_term()`：终止上下文，阻塞直到所有 socket 关闭
- `zmq_ctx_shutdown()`：立即关闭上下文中的所有 socket，不阻塞
- `zmq_ctx_set/get()`：设置/获取上下文选项

### F-003：上下文选项常量

**信源**：`include/zmq.h` L181-L196

| 常量 | 值 | 默认值 | 说明 |
|------|----|--------|------|
| `ZMQ_IO_THREADS` | 1 | `ZMQ_IO_THREADS_DFLT=1` | I/O 线程数 |
| `ZMQ_MAX_SOCKETS` | 2 | `ZMQ_MAX_SOCKETS_DFLT=1023` | 最大 socket 数 |
| `ZMQ_SOCKET_LIMIT` | 3 | — | 获取最大 socket 数上限 |
| `ZMQ_THREAD_PRIORITY` | 3 | — | 线程调度优先级 |
| `ZMQ_THREAD_SCHED_POLICY` | 4 | — | 线程调度策略 |
| `ZMQ_MAX_MSGSZ` | 5 | — | 最大消息大小 |
| `ZMQ_MSG_T_SIZE` | 6 | — | 获取 `zmq_msg_t` 大小 |

注意：`ZMQ_THREAD_PRIORITY` 与 `ZMQ_SOCKET_LIMIT` 共享值 3，但用途不同——一个用于 set，一个用于 get。

### F-004：zmq_msg_t 为 64 字节不透明结构体

**信源**：`include/zmq.h` L218-L232

```c
typedef struct zmq_msg_t {
    unsigned char _ [64];
} zmq_msg_t;
```

在不同平台上按指针大小对齐：
- MSVC x64/ARM64：8 字节对齐
- GCC：`sizeof(void*)` 对齐

应用程序不应直接访问 `_` 字段，必须通过 `zmq_msg_*` 函数操作。

### F-005：消息操作函数集

**信源**：`include/zmq.h` L236-L251

```c
int  zmq_msg_init (zmq_msg_t *msg_);
int  zmq_msg_init_size (zmq_msg_t *msg_, size_t size_);
int  zmq_msg_init_data (zmq_msg_t *msg_, void *data_, size_t size_,
                        zmq_free_fn *ffn_, void *hint_);
int  zmq_msg_send (zmq_msg_t *msg_, void *s_, int flags_);
int  zmq_msg_recv (zmq_msg_t *msg_, void *s_, int flags_);
int  zmq_msg_close (zmq_msg_t *msg_);
int  zmq_msg_move (zmq_msg_t *dest_, zmq_msg_t *src_);
int  zmq_msg_copy (zmq_msg_t *dest_, zmq_msg_t *src_);
void *zmq_msg_data (zmq_msg_t *msg_);
size_t zmq_msg_size (const zmq_msg_t *msg_);
int  zmq_msg_more (const zmq_msg_t *msg_);
int  zmq_msg_get (const zmq_msg_t *msg_, int property_);
int  zmq_msg_set (zmq_msg_t *msg_, int property_, int optval_);
const char *zmq_msg_gets (const zmq_msg_t *msg_, const char *property_);
```

函数分类：
- **初始化**：`init`（空消息）、`init_size`（指定大小）、`init_data`（外部缓冲区零拷贝）
- **收发**：`send`/`recv`，支持 `ZMQ_DONTWAIT` 和 `ZMQ_SNDMORE` 标志
- **生命周期**：`close`（释放资源）、`move`（所有权转移）、`copy`（共享引用）
- **属性访问**：`data`（数据指针）、`size`（大小）、`more`（是否有后续帧）
- **元数据**：`get`/`set`/`gets`（消息属性，如 `ZMQ_SRC_FD`、`ZMQ_SHARED`）

### F-006：套接字类型枚举

**信源**：`include/zmq.h` L258-L269

**稳定类型**：

| 常量 | 值 | 模式 | 方向 |
|------|----|------|------|
| `ZMQ_PAIR` | 0 | 一对一配对 | 双向 |
| `ZMQ_PUB` | 1 | 发布 | 只发 |
| `ZMQ_SUB` | 2 | 订阅 | 只收 |
| `ZMQ_REQ` | 3 | 请求 | 双向（严格状态机） |
| `ZMQ_REP` | 4 | 回复 | 双向（严格状态机） |
| `ZMQ_DEALER` | 5 | 经销商（匿名轮询） | 双向 |
| `ZMQ_ROUTER` | 6 | 路由器（显式寻址） | 双向 |
| `ZMQ_PULL` | 7 | 拉取（公平队列接收） | 只收 |
| `ZMQ_PUSH` | 8 | 推送（负载均衡发送） | 只发 |
| `ZMQ_XPUB` | 9 | 扩展发布（可见订阅） | 双向 |
| `ZMQ_XSUB` | 10 | 扩展订阅（可编程订阅） | 双向 |
| `ZMQ_STREAM` | 11 | 原始 TCP 流 | 双向 |

**Draft 类型**（需 `ZMQ_BUILD_DRAFT_API`）：

| 常量 | 值 |
|------|----|
| `ZMQ_SERVER` | 12 |
| `ZMQ_CLIENT` | 13 |
| `ZMQ_RADIO` | 14 |
| `ZMQ_DISH` | 15 |
| `ZMQ_GATHER` | 16 |
| `ZMQ_SCATTER` | 17 |
| `ZMQ_DGRAM` | 18 |
| `ZMQ_PEER` | 19 |
| `ZMQ_CHANNEL` | 20 |

### F-007：套接字选项常量

**信源**：`include/zmq.h` L276-L351

核心选项（节选完整列表中的关键项）：

| 常量 | 值 | 类型 | 说明 |
|------|----|------|------|
| `ZMQ_AFFINITY` | 4 | uint64 | I/O 线程亲和性掩码 |
| `ZMQ_ROUTING_ID` | 5 | binary | 套接字路由标识 |
| `ZMQ_SUBSCRIBE` | 6 | binary | 订阅前缀 |
| `ZMQ_UNSUBSCRIBE` | 7 | binary | 取消订阅 |
| `ZMQ_SNDBUF` | 11 | int | 内核发送缓冲区大小 |
| `ZMQ_RCVBUF` | 12 | int | 内核接收缓冲区大小 |
| `ZMQ_RCVMORE` | 13 | int | 是否有更多帧（只读） |
| `ZMQ_FD` | 14 | fd | 边缘触发信号文件描述符 |
| `ZMQ_EVENTS` | 15 | int | 当前就绪事件（只读） |
| `ZMQ_TYPE` | 16 | int | 套接字类型（只读） |
| `ZMQ_LINGER` | 17 | int | 关闭时逗留时间（毫秒） |
| `ZMQ_SNDHWM` | 23 | int | 发送高水位 |
| `ZMQ_RCVHWM` | 24 | int | 接收高水位 |
| `ZMQ_RCVTIMEO` | 27 | int | 接收超时（毫秒） |
| `ZMQ_SNDTIMEO` | 28 | int | 发送超时（毫秒） |
| `ZMQ_ROUTER_MANDATORY` | 33 | int | ROUTER 不可路由时报错 |
| `ZMQ_MECHANISM` | 43 | int | 安全机制（只读） |
| `ZMQ_HEARTBEAT_IVL` | 75 | int | 心跳间隔（毫秒） |

### F-008：安全机制常量

**信源**：`include/zmq.h` L362-L365

```c
#define ZMQ_NULL 0
#define ZMQ_PLAIN 1
#define ZMQ_CURVE 2
#define ZMQ_GSSAPI 3
```

| 机制 | 说明 |
|------|------|
| `ZMQ_NULL` | 无安全机制（默认） |
| `ZMQ_PLAIN` | 明文用户名/密码认证 |
| `ZMQ_CURVE` | CURVE 椭圆曲线加密认证 |
| `ZMQ_GSSAPI` | GSSAPI/Kerberos 认证 |

### F-009：zmq_pollitem_t 结构体

**信源**：`include/zmq.h` L487-L493

```c
typedef struct zmq_pollitem_t {
    void *socket;
    zmq_fd_t fd;
    short events;
    short revents;
} zmq_pollitem_t;
```

轮询事件标志：

| 常量 | 值 | 说明 |
|------|----|------|
| `ZMQ_POLLIN` | 1 | 可读 |
| `ZMQ_POLLOUT` | 2 | 可写 |
| `ZMQ_POLLERR` | 4 | 错误 |
| `ZMQ_POLLPRI` | 8 | 优先数据可读 |

`socket` 和 `fd` 二选一：非 NULL 时轮询 ZMQ socket，否则轮询原生 fd。`events` 是关注的事件掩码，`revents` 由 `zmq_poll()` 填充实际发生的事件。

### F-010：套接字监控事件

**信源**：`include/zmq.h` L401-L445

| 常量 | 值 | 说明 |
|------|----|------|
| `ZMQ_EVENT_CONNECTED` | 0x0001 | 连接已建立 |
| `ZMQ_EVENT_CONNECT_DELAYED` | 0x0002 | 连接尝试被延迟 |
| `ZMQ_EVENT_CONNECT_RETRIED` | 0x0004 | 连接重试中 |
| `ZMQ_EVENT_LISTENING` | 0x0008 | 正在监听 |
| `ZMQ_EVENT_BIND_FAILED` | 0x0010 | 绑定失败 |
| `ZMQ_EVENT_ACCEPTED` | 0x0020 | 接受了连接 |
| `ZMQ_EVENT_ACCEPT_FAILED` | 0x0040 | 接受连接失败 |
| `ZMQ_EVENT_CLOSED` | 0x0080 | 连接已关闭 |
| `ZMQ_EVENT_CLOSE_FAILED` | 0x0100 | 关闭失败 |
| `ZMQ_EVENT_DISCONNECTED` | 0x0200 | 连接断开 |
| `ZMQ_EVENT_MONITOR_STOPPED` | 0x0400 | 监控已停止 |
| `ZMQ_EVENT_HANDSHAKE_FAILED_NO_DETAIL` | 0x0800 | 握手失败（无详情） |
| `ZMQ_EVENT_HANDSHAKE_SUCCEEDED` | 0x1000 | 握手成功 |
| `ZMQ_EVENT_HANDSHAKE_FAILED_PROTOCOL` | 0x2000 | 握手失败（协议错误） |
| `ZMQ_EVENT_HANDSHAKE_FAILED_AUTH` | 0x4000 | 握手失败（认证失败） |

监控通过 `zmq_socket_monitor()` 注册，事件投递到 PAIR 类型的 inproc 套接字。

### F-011：zmq_proxy 函数

**信源**：`include/zmq.h` L503-L507

```c
int zmq_proxy (void *frontend_, void *backend_, void *capture_);
int zmq_proxy_steerable (void *frontend_, void *backend_,
                         void *capture_, void *control_);
```

- `zmq_proxy()`：在 frontend 和 backend 之间双向转发消息，capture 可选地镜像所有流量
- `zmq_proxy_steerable()`：额外接受 control 套接字，可通过 PAUSE/RESUME/TERMINATE 命令控制代理

代理函数在当前线程阻塞运行，直到上下文终止或收到 TERMINATE 命令。
