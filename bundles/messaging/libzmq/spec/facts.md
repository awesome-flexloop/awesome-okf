---
type: Facts
title: libzmq 源码事实采集
sources:
  - id: libzmq-source
    resource: https://github.com/zeromq/libzmq
    title: ZeroMQ core library (libzmq)
---

# libzmq 源码事实采集（R 阶段）

> 信源根目录：`external/libs/remote/libzmq/`
> 版本：4.3.6（`ZMQ_VERSION_MAJOR=4, MINOR=3, PATCH=6`）
> 事实总数：75 条

---

## 一、公共 C API（zmq.h）

### F-001：版本宏定义
**信源**：`include/zmq.h` L15-L22

定义 `ZMQ_VERSION_MAJOR=4`、`ZMQ_VERSION_MINOR=3`、`ZMQ_VERSION_PATCH=6`，并通过 `ZMQ_MAKE_VERSION(major,minor,patch)` 宏计算整数版本号 `major*10000+minor*100+patch`。

### F-002：上下文生命周期函数
**信源**：`include/zmq.h` L198-L207

声明 `void *zmq_ctx_new(void)`、`int zmq_ctx_term(void *context_)`、`int zmq_ctx_shutdown(void *context_)`、`int zmq_ctx_set(void*,int,int)`、`int zmq_ctx_get(void*,int)`，以及遗留 API `zmq_init`/`zmq_term`/`zmq_ctx_destroy`。

### F-003：上下文选项常量
**信源**：`include/zmq.h` L181-L196

定义 `ZMQ_IO_THREADS=1`、`ZMQ_MAX_SOCKETS=2`、`ZMQ_SOCKET_LIMIT=3`、`ZMQ_THREAD_PRIORITY=3`、`ZMQ_THREAD_SCHED_POLICY=4`、`ZMQ_MAX_MSGSZ=5`、`ZMQ_MSG_T_SIZE=6` 等；默认值 `ZMQ_IO_THREADS_DFLT=1`、`ZMQ_MAX_SOCKETS_DFLT=1023`。

### F-004：zmq_msg_t 为 64 字节不透明结构体
**信源**：`include/zmq.h` L218-L232

`zmq_msg_t` 是一个 64 字节的固定大小结构体（`unsigned char _[64]`），在不同平台上按指针大小对齐（MSVC x64/ARM64 对齐 8 字节，GCC 对齐 `sizeof(void*)`）。

### F-005：消息操作函数集
**信源**：`include/zmq.h` L236-L251

声明 `zmq_msg_init`、`zmq_msg_init_size`、`zmq_msg_init_data`、`zmq_msg_send`、`zmq_msg_recv`、`zmq_msg_close`、`zmq_msg_move`、`zmq_msg_copy`、`zmq_msg_data`、`zmq_msg_size`、`zmq_msg_more`、`zmq_msg_get`、`zmq_msg_set`、`zmq_msg_gets`。

### F-006：套接字类型枚举
**信源**：`include/zmq.h` L258-L269

定义稳定套接字类型：`ZMQ_PAIR=0`、`ZMQ_PUB=1`、`ZMQ_SUB=2`、`ZMQ_REQ=3`、`ZMQ_REP=4`、`ZMQ_DEALER=5`、`ZMQ_ROUTER=6`、`ZMQ_PULL=7`、`ZMQ_PUSH=8`、`ZMQ_XPUB=9`、`ZMQ_XSUB=10`、`ZMQ_STREAM=11`。Draft 类型包括 `ZMQ_SERVER=12` 至 `ZMQ_CHANNEL=20`。

### F-007：套接字选项常量
**信源**：`include/zmq.h` L276-L351

定义大量 `ZMQ_*` 选项常量，包括 `ZMQ_AFFINITY=4`、`ZMQ_ROUTING_ID=5`、`ZMQ_SUBSCRIBE=6`、`ZMQ_SNDBUF=11`、`ZMQ_RCVBUF=12`、`ZMQ_RCVMORE=13`、`ZMQ_FD=14`、`ZMQ_EVENTS=15`、`ZMQ_TYPE=16`、`ZMQ_LINGER=17`、`ZMQ_SNDHWM=23`、`ZMQ_RCVHWM=24`、`ZMQ_RCVTIMEO=27`、`ZMQ_SNDTIMEO=28`、`ZMQ_ROUTER_MANDATORY=33`、`ZMQ_MECHANISM=43`、`ZMQ_HEARTBEAT_IVL=75` 等。

### F-008：安全机制常量
**信源**：`include/zmq.h` L362-L365

定义 `ZMQ_NULL=0`、`ZMQ_PLAIN=1`、`ZMQ_CURVE=2`、`ZMQ_GSSAPI=3` 四种安全机制。

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
轮询事件标志：`ZMQ_POLLIN=1`、`ZMQ_POLLOUT=2`、`ZMQ_POLLERR=4`、`ZMQ_POLLPRI=8`。

### F-010：套接字监控事件
**信源**：`include/zmq.h` L401-L445

定义 `ZMQ_EVENT_CONNECTED=0x0001`、`ZMQ_EVENT_CONNECT_DELAYED=0x0002`、`ZMQ_EVENT_LISTENING=0x0008`、`ZMQ_EVENT_ACCEPTED=0x0020`、`ZMQ_EVENT_CLOSED=0x0080`、`ZMQ_EVENT_DISCONNECTED=0x0200`、`ZMQ_EVENT_HANDSHAKE_SUCCEEDED=0x1000`、`ZMQ_EVENT_HANDSHAKE_FAILED_PROTOCOL=0x2000`、`ZMQ_EVENT_HANDSHAKE_FAILED_AUTH=0x4000` 等。

### F-011：zmq_proxy 函数
**信源**：`include/zmq.h` L503-L507

声明 `int zmq_proxy(void *frontend_, void *backend_, void *capture_)` 和 `zmq_proxy_steerable(frontend, backend, capture, control)`，用于在两个套接字之间转发消息。

---

## 二、上下文（ctx_t）

### F-012：ctx_t 继承自 thread_ctx_t
**信源**：`src/ctx.hpp` L37-L61, L66

`thread_ctx_t` 基类管理线程参数（`_thread_priority`、`_thread_sched_policy`、`_thread_affinity_cpus`、`_thread_name_prefix`），通过 `_opt_sync` 互斥锁保护。`ctx_t` 以 `ZMQ_FINAL` 标记，不可再被继承。

### F-013：ctx_t 关键成员
**信源**：`src/ctx.hpp` L150-L221

`ctx_t` 包含：`_tag`（魔数 0xabadcafe）、`_sockets`（`array_t<socket_base_t>`）、`_empty_slots`（空闲线程槽位 vector）、`_starting`（延迟启动标志）、`_terminating`（终止中标志）、`_slot_sync`（槽位互斥锁）、`_reaper`（reaper 线程指针）、`_io_threads`（IO 线程 vector）、`_slots`（mailbox 指针 vector）、`_term_mailbox`（终止线程邮箱）、`_endpoints`（inproc 端点 map）、`_pending_connections`（待连接 multimap）、`_max_sockets`、`_max_msgsz`、`_io_thread_count`、`_blocky`、`_ipv6`、`_zero_copy`。

### F-014：endpoint_t 结构体
**信源**：`src/ctx.hpp` L31-L35

```cpp
struct endpoint_t {
    socket_base_t *socket;
    options_t options;
};
```
inproc 端点注册时同时存储 socket 指针和选项副本，使对端无需同步即可访问选项。

### F-015：ctx_t 构造函数默认值
**信源**：`src/ctx.cpp` L53-L63

构造时 `_tag=0xabadcafe`、`_starting=true`、`_terminating=false`、`_reaper=NULL`、`_max_sockets=clipped_maxsocket(1023)`、`_max_msgsz=INT_MAX`、`_io_thread_count=1`、`_blocky=true`、`_ipv6=false`、`_zero_copy=true`。

### F-016：start() 延迟启动基础设施
**信源**：`src/ctx.cpp` L390-L460

`start()` 在首次创建 socket 时调用：分配 `slot_count = max_sockets + io_thread_count + 2` 个槽位；槽位 0 为 term mailbox（`term_tid=0`），槽位 1 为 reaper mailbox（`reaper_tid=1`）；创建 reaper 线程并启动；创建 `io_thread_count` 个 IO 线程并启动；剩余槽位加入 `_empty_slots`。

### F-017：create_socket 分配槽位并委托工厂方法
**信源**：`src/ctx.cpp` L462-L501

`create_socket(type_)` 加锁 `_slot_sync`，检查 `_terminating` 返回 ETERM；若 `_starting` 则调用 `start()`；从 `_empty_slots` 取一个槽位；通过 `max_socket_id.add(1)+1` 生成唯一 sid；调用 `socket_base_t::create(type_, this, slot, sid)` 创建具体 socket；将 socket mailbox 注册到 `_slots[slot]`。

### F-018：terminate 等待 reaper 完成
**信源**：`src/ctx.cpp` L133-L210

`terminate()` 先连接所有 pending inproc 连接（创建临时 PAIR socket 绑定），然后向所有 socket 发送 `stop` 命令；若 socket 列表为空则停止 reaper；随后阻塞在 `_term_mailbox.recv(&cmd, -1)` 等待 `command_t::done` 命令；最后 `delete this` 自销毁。

### F-019：choose_io_thread 按负载选择
**信源**：`src/ctx.hpp` L102-L105

声明 `io_thread_t *choose_io_thread(uint64_t affinity_)`，返回当前最空闲的 IO 线程；`affinity` 参数指定哪些 IO 线程合格（0 表示全部）。

---

## 三、对象层次（object_t / own_t）

### F-020：object_t 是线程间通信基类
**信源**：`src/object.hpp` L28-L140

`object_t` 持有 `ctx_t *_ctx` 和 `uint32_t _tid`（所属线程 ID）；提供 `process_command` 分发命令；声明大量 `send_*` 方法（`send_stop`、`send_plug`、`send_own`、`send_attach`、`send_bind`、`send_activate_read/write`、`send_pipe_term/ack`、`send_term/ack`、`send_reap` 等）和对应的虚函数 `process_*` 处理器。

### F-021：own_t 实现所有权层次和终止序列
**信源**：`src/own.hpp` L21-L117

`own_t` 继承 `object_t`，管理对象树：`_owner` 指向所有者，`_owned` 是 `std::set<own_t*>` 子对象集合；`_terminating` 标志、`_sent_seqnum`（原子计数器）、`_processed_seqnum`、`_term_acks`（待确认终止数）；提供 `launch_child`、`term_child`、`terminate`、`register_term_acks`/`unregister_term_ack`；当所有 term acks 收齐后对象自销毁。

### F-022：own_t 有两种构造方式
**信源**：`src/own.hpp` L29-L32

`own_t(ctx_t *parent_, uint32_t tid_)` 用于不在 IO 线程内的对象（如 socket_base_t）；`own_t(io_thread_t *io_thread_, const options_t &options_)` 用于生活在 IO 线程内的对象（如 session、listener、connecter），后者会将 options 复制到成员 `options`。

---

## 四、套接字基类（socket_base_t）

### F-023：socket_base_t 多继承结构
**信源**：`src/socket_base.hpp` L31-L35

```cpp
class socket_base_t : public own_t,
                     public array_item_t<>,
                     public i_poll_events,
                     public i_pipe_events
```
同时继承所有权管理、数组项、poller 事件接口和 pipe 事件接口。`routing_socket_base_t` 进一步继承 `socket_base_t`，增加按 routing_id 索引出站 pipe 的能力。

### F-024：socket_base_t 关键纯虚钩子
**信源**：`src/socket_base.hpp` L155-L182

声明纯虚函数 `xattach_pipe(pipe_t*, bool, bool)` 和 `xpipe_terminated(pipe_t*)`；虚函数 `xsetsockopt`/`xgetsockopt` 默认无特殊选项；`xhas_out`/`xsend` 默认不支持发送；`xhas_in`/`xrecv` 默认不支持接收；`xread_activated`/`xwrite_activated`/`xhiccuped` 为 pipe 事件钩子。

### F-025：socket_base_t 持有 pipe 数组和 mailbox
**信源**：`src/socket_base.hpp` L293-L297

`i_mailbox *_mailbox` 指向 socket 的邮箱；`typedef array_t<pipe_t, 3> pipes_t`，`_pipes` 存储所有附加的 pipe；3 表示 pipe 可同时存在于入站数组(1)、出站数组(2)和待释放数组(3)。

### F-026：socket_base_t::create 工厂方法
**信源**：`src/socket_base.cpp` L141-L225

静态工厂方法根据 `type_` 参数 switch 创建具体类型实例：`ZMQ_PAIR→pair_t`、`ZMQ_PUB→pub_t`、`ZMQ_SUB→sub_t`、`ZMQ_REQ→req_t`、`ZMQ_REP→rep_t`、`ZMQ_DEALER→dealer_t`、`ZMQ_ROUTER→router_t`、`ZMQ_PULL→pull_t`、`ZMQ_PUSH→push_t`、`ZMQ_XPUB→xpub_t`、`ZMQ_XSUB→xsub_t`、`ZMQ_STREAM→stream_t`，以及 Draft 类型 `server_t`/`client_t`/`radio_t`/`dish_t` 等。

### F-027：线程安全 socket 使用 mailbox_safe_t
**信源**：`src/socket_base.cpp` L253-L266

构造函数中若 `_thread_safe=true`，创建 `mailbox_safe_t(&_sync)`；否则创建普通 `mailbox_t`。线程安全 socket 的所有公共 API 调用通过 `scoped_optional_lock_t` 加锁 `_sync`。

### F-028：bind 区分 inproc 和网络协议
**信源**：`src/socket_base.cpp` L536-L568

`bind()` 解析 URI（`protocol://address`），若协议为 `inproc`，则构造 `endpoint_t{this, options}` 注册到 ctx 的 `_endpoints` map，并调用 `connect_pending` 连接已等待的连接；其他协议（tcp/ipc 等）走 listener 创建流程。

### F-029：connect_internal 为 inproc 直接创建 pipepair
**信源**：`src/socket_base.cpp` L823-L911

inproc connect 时从 ctx 查找已注册的 endpoint；若对端存在，创建 `pipepair`，HWM 为两端之和；通过 `send_bind` 命令将远端 pipe 附加到对端 socket；本地端调用 `attach_pipe`。若对端不存在，则将连接放入 `_pending_connections` 等待 bind。

### F-030：send 调用 xsend 并支持超时重试
**信源**：`src/socket_base.cpp` L1263-L1349

`send()` 先处理待处理命令，重置消息 flags，根据 `ZMQ_SNDMORE` 设置 `more` 标志；调用虚函数 `xsend(msg_)`；若返回 EAGAIN 且非 `DONTWAIT`，则循环 `process_commands(timeout)` 后重试，直到超时或成功。

### F-031：routing_socket_base_t 按 routing_id 索引出站 pipe
**信源**：`src/socket_base.hpp` L339-L386

`routing_socket_base_t` 持有 `std::map<blob_t, out_pipe_t> _out_pipes`，其中 `out_pipe_t` 包含 `pipe_t *pipe` 和 `bool active`；提供 `add_out_pipe`、`lookup_out_pipe`、`erase_out_pipe`、`has_out_pipe` 方法；ROUTER 和 STREAM 继承此类。

---

## 五、管道（pipe_t）

### F-032：pipepair 工厂函数创建双向管道
**信源**：`src/pipe.hpp` L20-L31

自由函数 `pipepair(object_t *parents_[2], pipe_t *pipes_[2], const int hwms_[2], const bool conflate_[2])` 创建一对互联的 `pipe_t` 对象，构成双向消息通道。第一个 HWM 控制从 pipe[0]→pipe[1] 的方向，第二个控制反向。

### F-033：pipe_t 持有双向 ypipe
**信源**：`src/pipe.hpp` L128-L165

`pipe_t` 内部持有 `upipe_t *_in_pipe` 和 `upipe_t *_out_pipe`（`ypipe_base_t<msg_t>`），分别用于读取和写入；`_in_active`/`_out_active` 标志控制方向是否活跃；`_peer` 指向对端 pipe。

### F-034：pipe_t 六种终止状态
**信源**：`src/pipe.hpp` L196-L214

枚举状态：`active`（正常）、`delimiter_received`（读到分隔符但未收到 term 命令）、`waiting_for_delimiter`（已收到 term 命令但仍有未读消息）、`term_ack_sent`（所有待处理消息已读，等待对端 ack）、`term_req_sent1`（用户显式调用 terminate）、`term_req_sent2`（用户 terminate 后又收到对端 term）。

### F-035：pipe_t 读写实现
**信源**：`src/pipe.cpp` L170-L234

`read(msg_)` 从 `_in_pipe` 读取消息，跳过 credential 消息，遇到 delimiter 则调用 `process_delimiter` 返回 false；每读 `_lwm` 条消息向对端发送 `activate_write` 命令。`write(msg_)` 检查 HWM 后写入 `_out_pipe`，非 more 帧递增 `_msgs_written`。

### F-036：HWM/LWM 流控机制
**信源**：`src/pipe.hpp` L171-L179, `src/pipe.cpp` L207-L220

`_hwm`（高水位）限制出站未确认消息数；`_lwm`（低水位）由 `compute_lwm` 计算，通常为 HWM 的一半；当 `_msgs_written - _peers_msgs_read >= _hwm` 时写端变为非活跃；读端每读 `_lwm` 条消息发 `activate_write` 通知写端恢复。

### F-037：flush 通过 activate_read 唤醒对端
**信源**：`src/pipe.cpp` L249-L257

`flush()` 调用 `_out_pipe->flush()`；若 flush 返回 false（表示读端正休眠），则通过 `send_activate_read(_peer)` 发送命令唤醒对端。

### F-038：pipe_t 使用 conflate 模式时只保留最新消息
**信源**：`src/pipe.hpp` L233, L28-L31

`_conflate` 为 true 时，底层使用 `ypipe_conflate_t` 替代 `ypipe_t`，仅保留最近到达的消息，丢弃旧消息，且忽略 HWM。适用于 DEALER/PUSH/PULL/PUB/SUB 类型。

---

## 六、消息（msg_t）

### F-039：msg_t 总大小为 64 字节
**信源**：`src/msg.hpp` L148-L156

枚举 `msg_t_size = 64`；`max_vsm_size = 64 - (sizeof(metadata_t*) + 3 + 16 + sizeof(uint32_t))`，即小消息（VSM）直接存储在 msg_t 内部，无需额外堆分配。

### F-040：msg_t 六种内部类型
**信源**：`src/msg.hpp` L168-L190

枚举 `type_t`：`type_vsm=101`（微小消息，数据内联）、`type_lmsg=102`（长消息，堆分配 content_t）、`type_delimiter=103`（分隔符，用于管道终止）、`type_cmsg=104`（常量消息，指向外部常量数据）、`type_zclmsg=105`（零拷贝长消息，v2_decoder 使用）、`type_join=106`/`type_leave=107`（RADIO-DISH 组播）。

### F-041：msg_t 使用 union 紧凑存储
**信源**：`src/msg.hpp` L223-L297

`msg_t` 内部是一个匿名 union，包含 `base`（公共字段：metadata、type、flags、routing_id、group）、`vsm`（含内联 `data[max_vsm_size]` 和 `size`）、`lmsg`/`zclmsg`（含 `content_t*` 指针）、`cmsg`（含 `void* data` 和 `size_t size`）、`delimiter`（无数据）。所有变体共享前 64 字节内存。

### F-042：content_t 引用计数结构
**信源**：`src/msg.hpp` L43-L50

```cpp
struct content_t {
    void *data;
    size_t size;
    msg_free_fn *ffn;
    void *hint;
    zmq::atomic_counter_t refcnt;
};
```
长消息数据块头部嵌入 `content_t`，通过 placement new 构造原子引用计数器。

### F-043：init_size 按大小选择 VSM 或 LMSG
**信源**：`src/msg.cpp` L62-L95

`init_size(size_)`：若 `size_ <= max_vsm_size`，设为 `type_vsm`，数据直接写入 `_u.vsm.data`；否则设为 `type_lmsg`，分配 `sizeof(content_t) + size_` 字节，`content->data` 指向 content 之后的内存，使用 placement new 初始化 `refcnt`。

### F-044：copy 实现共享引用计数
**信源**：`src/msg.cpp` L326-L362

`copy(src_)` 先关闭目标消息；若源为 lmsg/zclmsg：若已 shared 则 `refcnt.add(1)`，否则设 `shared` 标志并将 `refcnt` 设为 2；metadata 和 long group 也增加引用计数；然后按位复制整个 msg_t（64 字节）。

### F-045：close 递减引用计数并条件释放
**信源**：`src/msg.cpp` L242-L303

`close()` 对 lmsg：若未 shared 或 `refcnt.sub(1)` 返回 0（引用归零），则显式析构 refcnt，若有 `ffn` 则调用 `ffn(data, hint)`，最后 `free(content)`；zclmsg 类似但必须有 ffn；metadata 和 long group 同样按引用计数释放；最后将 type 置 0 使消息失效。

### F-046：move 是零拷贝所有权转移
**信源**：`src/msg.cpp` L305-L324

`move(src_)` 先关闭目标，然后按位复制 `*this = src_`（64 字节 memcpy），最后调用 `src_.init()` 重置源为空消息。整个过程不涉及引用计数修改。

### F-047：msg_t 命令帧标志
**信源**：`src/msg.hpp` L53-L67

标志位枚举：`more=1`（多部分消息后续帧）、`command=2`（ZMTP 命令帧）、`ping=4`、`pong=8`、`subscribe=12`、`cancel=16`、`close_cmd=20`、`credential=32`、`routing_id=64`、`shared=128`。命令类型使用 bits 2-5（掩码 `0x1c`），用等值比较而非位运算。

---

## 七、邮箱与命令传递（mailbox / command）

### F-048：command_t 包含 22 种命令类型
**信源**：`src/command.hpp` L26-L50

`command_t::type_t` 枚举：`stop`、`plug`、`own`、`attach`、`bind`、`activate_read`、`activate_write`、`hiccup`、`pipe_term`、`pipe_term_ack`、`pipe_hwm`、`term_req`、`term`、`term_ack`、`term_endpoint`、`reap`、`reaped`、`inproc_connected`、`conn_failed`、`pipe_peer_stats`、`pipe_stats_publish`、`done`。

### F-049：command_t 使用 union 携带参数
**信源**：`src/command.hpp` L52-L185

`command_t` 包含 `object_t *destination` 和 `type_t type`，以及 `args_t` union。不同命令携带不同参数：`own`/`term_req`/`reap` 携带 `own_t*`/`socket_base_t*`；`attach` 携带 `i_engine*`；`bind` 携带 `pipe_t*`；`activate_write` 携带 `uint64_t msgs_read`；`term` 携带 `int linger`；`term_endpoint` 携带 `std::string*`。

### F-050：mailbox_t 基于 ypipe + signaler
**信源**：`src/mailbox.hpp` L18-L56, `src/mailbox.cpp` L7-L74

`mailbox_t` 内部有 `ypipe_t<command_t, 16> _cpipe`（命令管道，粒度 16）、`signaler_t _signaler`（跨线程信号）、`mutex_t _sync`（保护发送端）。`send()` 加锁写入 cpipe 并 flush，若 flush 返回 false（读端休眠）则调用 `_signaler.send()` 唤醒。`recv()` 先尝试读 cpipe，无命令则等待 signaler。

### F-051：mailbox_safe_t 使用条件变量
**信源**：`src/mailbox_safe.hpp` L20-L58

`mailbox_safe_t` 用于线程安全 socket，持有 `condition_variable_t _cond_var`、外部传入的 `mutex_t *_sync`、`std::vector<signaler_t*> _signalers`。`recv` 通过条件变量等待，`send` 通知条件变量并唤醒所有 signaler。

### F-052：signaler_t 是跨平台 eventfd/pipe 封装
**信源**：`src/signaler.hpp` L15-L58

`signaler_t` 是 `signal_fd` 的跨平台等价物，任一时刻最多有一个未读信号（重复发送信号是未定义行为）。持有读/写两个 fd（`_r`、`_w`），提供 `send()`、`wait(timeout)`、`recv()`、`recv_failable()`、`get_fd()`。

---

## 八、I/O 线程与多路复用（io_thread / poller）

### F-053：io_thread_t 继承 object_t 和 i_poll_events
**信源**：`src/io_thread.hpp` L19-L62

`io_thread_t` 持有 `mailbox_t _mailbox`、`poller_t::handle_t _mailbox_handle`、`poller_t *_poller`。构造时创建 poller，将 mailbox 的 fd 注册到 poller 并关注 POLLIN。

### F-054：io_thread 主循环处理 mailbox 命令
**信源**：`src/io_thread.cpp` L54-L69

`in_event()` 在 mailbox fd 可读时被 poller 调用：循环 `_mailbox.recv(&cmd, 0)`，对每个命令调用 `cmd.destination->process_command(cmd)`，直到返回 EAGAIN。`out_event()` 和 `timer_event()` 断言 false（IO 线程不关注这些事件）。

### F-055：poller 通过编译宏选择实现
**信源**：`src/poller.hpp` L6-L33

`poller.hpp` 根据宏 `ZMQ_IOTHREAD_POLLER_USE_KQUEUE`/`EPOLL`/`DEVPOLL`/`POLLSET`/`POLL`/`SELECT` 选择包含对应头文件（`kqueue.hpp`/`epoll.hpp`/`devpoll.hpp`/`pollset.hpp`/`poll.hpp`/`select.hpp`）。同一时间只能定义一个宏，否则编译错误。

### F-056：io_object_t 是 poller 事件适配器
**信源**：`src/io_object.hpp` L20-L53

`io_object_t` 继承 `i_poll_events`，持有 `poller_t *_poller`；提供 `add_fd`/`rm_fd`/`set_pollin`/`reset_pollin`/`set_pollout`/`reset_pollout`/`add_timer`/`cancel_timer` 方法；默认的 `in_event`/`out_event`/`timer_event` 为空实现，子类按需覆写。

### F-057：i_poll_events 接口
**信源**：`src/i_poll_events.hpp` L13-L25

定义三个纯虚函数：`in_event()`（fd 可读）、`out_event()`（fd 可写）、`timer_event(int id_)`（定时器到期）。所有需要被 poller 通知的对象（io_thread_t、io_object_t、socket_base_t 在 reaper 中）都实现此接口。

---

## 九、ZMTP 协议引擎（zmtp_engine）

### F-058：zmtp_engine_t 继承 stream_engine_base_t
**信源**：`src/zmtp_engine.hpp` L36-L106

`zmtp_engine_t` 以 `ZMQ_FINAL` 标记，继承 `stream_engine_base_t`（后者继承 `io_object_t` 和 `i_engine`）。声明 Greeting 大小常量：`signature_size=10`、`v2_greeting_size=12`、`v3_greeting_size=64`。

### F-059：ZMTP 版本枚举
**信源**：`src/zmtp_engine.hpp` L22-L27

```cpp
enum { ZMTP_1_0 = 0, ZMTP_2_0 = 1, ZMTP_3_x = 3 };
```

### F-060：Greeting 帧结构
**信源**：`src/zmtp_engine.cpp` L73-L90, L157-L198

ZMTP/3.x greeting 共 64 字节：
- 字节 0：0xFF（签名首字节）
- 字节 1-9：签名剩余 9 字节 + 第 10 字节（revision_pos=10）的最低位为 1 表示版本化协议
- 字节 10：revision（3 表示 ZMTP/3.x）
- 字节 11：minor version
- 字节 12-31：20 字节安全机制名称（如 "NULL"、"PLAIN"、"CURVE"、"GSSAPI"，以 null 填充）
- 字节 32-63：32 字节填充（as-server 标志在第 32 字节）

引擎启动时先发送 10 字节签名（0xFF + 8字节长度 + flags 0x7f），随后根据对端版本发送 greeting 剩余部分。

### F-061：握手通过函数指针状态机分发
**信源**：`src/zmtp_engine.hpp` L60-L70, `src/zmtp_engine.cpp` L200-L222

`select_handshake_fun(unversioned, revision, minor)` 返回成员函数指针：无版本→`handshake_v1_0_unversioned`；revision=0→`handshake_v1_0`；revision=1→`handshake_v2_0`；revision=3 且 minor=0→`handshake_v3_0`；revision=3 且 minor≥1→`handshake_v3_1`。

### F-062：ZMTP/3.x 握手创建安全机制
**信源**：`src/zmtp_engine.cpp` L317-L380

`handshake_v3_x()` 检查 greeting_recv[12..31] 中的机制名称是否与本地 `_options.mechanism` 匹配：匹配 NULL 创建 `null_mechanism_t`；匹配 PLAIN 创建 `plain_server_t` 或 `plain_client_t`；匹配 CURVE 创建 `curve_server_t`/`curve_client_t`；匹配 GSSAPI 创建对应对象。不匹配则触发 `ZMQ_PROTOCOL_ERROR_ZMTP_MECHANISM_MISMATCH`。握手期间 `_next_msg` 指向 `next_handshake_command`，`_process_msg` 指向 `process_handshake_command`。

### F-063：心跳机制
**信源**：`src/zmtp_engine.hpp` L51-L53, L103, `src/stream_engine_base.hpp` L141-L149

`zmtp_engine_t` 声明 `produce_ping_message`、`process_heartbeat_message`、`produce_pong_message`；`stream_engine_base_t` 有三个心跳定时器：`heartbeat_ivl_timer_id=0x80`、`heartbeat_timeout_timer_id=0x81`、`heartbeat_ttl_timer_id=0x82`。

---

## 十、会话（session_base_t）

### F-064：session_base_t 多继承
**信源**：`src/session_base.hpp` L21-L22

```cpp
class session_base_t : public own_t, public io_object_t, public i_pipe_events
```
会话同时具有所有权管理、IO 对象和 pipe 事件接收能力。

### F-065：session_base_t 关键成员
**信源**：`src/session_base.hpp` L98-L139

`_active`（true 表示主动连接的会话，false 表示 listener 创建的瞬态会话）、`_pipe`（连接到 socket 的管道）、`_zap_pipe`（ZAP 认证管道）、`_engine`（协议引擎指针）、`_socket`（所属 socket）、`_io_thread`（所在 IO 线程）、`_addr`（连接地址）、`_pending`（终止时是否等待消息发送完毕）。

### F-066：session 引擎就绪后通知 socket
**信源**：`src/session_base.hpp` L39, `src/i_engine.hpp` L27-L28

`engine_ready()` 在引擎握手完成后调用；`i_engine` 接口声明 `has_handshake_stage()`，若引擎有握手阶段则必须在握手完成后调用 `session.engine_ready()`。

---

## 十一、套接字选项（options_t）

### F-067：options_t 存储所有套接字选项
**信源**：`src/options.hpp` L34-L301

`options_t` 是一个结构体，包含：`sndhwm`/`rcvhwm`（高水位）、`affinity`（IO 线程亲和性）、`routing_id[256]`、`rate`/`recovery_ivl`（多播速率）、`sndbuf`/`rcvbuf`、`tos`、`priority`、`type`（int8_t）、`linger`（atomic_value_t）、`reconnect_ivl`/`reconnect_ivl_max`、`backlog`、`maxmsgsize`、`rcvtimeo`/`sndtimeo`、`ipv6`、`immediate`、`filter`、`mechanism`、`as_server`、`conflate`、`handshake_ivl`（默认 30 秒）、`heartbeat_ttl`/`heartbeat_interval`/`heartbeat_timeout`、`in_batch_size`/`out_batch_size`、`zero_copy` 等。

### F-068：CURVE 密钥长度
**信源**：`src/options.hpp` L28-L30

原始 256 位密钥为 32 字节（`CURVE_KEYSIZE=32`），Z85 编码后为 40 字节（`CURVE_KEYSIZE_Z85=40`）。options 中存储 `curve_public_key[32]`、`curve_secret_key[32]`、`curve_server_key[32]`。

---

## 十二、各消息模式实现

### F-069：dealer_t 使用 fq + lb 算法
**信源**：`src/dealer.hpp` L19-L55

`dealer_t` 直接继承 `socket_base_t`，持有 `fq_t _fq`（入站公平队列）和 `lb_t _lb`（出站负载均衡）；覆写 `xattach_pipe`、`xsend`、`xrecv`、`xhas_in/out`、`xread_activated`、`xwrite_activated`、`xpipe_terminated`；提供 `sendpipe`/`recvpipe` 返回使用的 pipe。

### F-070：router_t 使用 fq + routing_id 路由表
**信源**：`src/router.hpp` L21-L102

`router_t` 继承 `routing_socket_base_t`，持有 `fq_t _fq`、`_prefetched`/`_prefetched_id`/`_prefetched_msg`（预取机制）、`_anonymous_pipes`（未标识 pipe 集合）、`_next_integral_routing_id`（自增整数路由 ID）、`_mandatory`（不可路由时返回 EAGAIN）、`_probe_router`、`_handover`（ID 冲突时接管）。接收时先读到 peer identity 帧再读消息体；发送时第一帧为 routing_id，用于查找目标 pipe。

### F-071：pub_t 继承 xpub_t
**信源**：`src/pub.hpp` L15-L29

`pub_t` 以 `ZMQ_FINAL` 继承 `xpub_t`，覆写 `xattach_pipe`（不订阅所有消息）、`xrecv`（返回 ENOTSUP）、`xhas_in`（返回 false）。PUB 不可接收。

### F-072：sub_t 继承 xsub_t
**信源**：`src/sub.hpp` L15-L27

`sub_t` 以 `ZMQ_FINAL` 继承 `xsub_t`，覆写 `xsetsockopt`（处理 ZMQ_SUBSCRIBE/UNSUBSCRIBE）、`xsend`（返回 ENOTSUP）、`xhas_out`（返回 false）。SUB 不可发送。

### F-073：xpub_t 使用 mtrie 管理订阅
**信源**：`src/xpub.hpp` L20-L111

`xpub_t` 持有 `mtrie_t _subscriptions`（多订阅者前缀树，映射前缀→pipe 集合）和 `mtrie_t _manual_subscriptions`；`dist_t _dist`（分发器）；`_verbose_subs`/`_verbose_unsubs` 控制是否向上游转发所有订阅/取消订阅消息；`_manual` 模式下订阅不自动添加。

### F-074：xsub_t 使用 trie/radix_tree 过滤订阅
**信源**：`src/xsub.hpp` L22-L95

`xsub_t` 持有 `fq_t _fq`（入站公平队列）、`dist_t _dist`（向所有上游连接分发订阅）、`trie_with_size_t _subscriptions`（或 `radix_tree_t`，由 `ZMQ_USE_RADIX_TREE` 宏决定）；`match(msg_)` 检查消息是否匹配至少一个订阅前缀。

### F-075：push_t / pull_t 分别使用 lb / fq
**信源**：`src/push.hpp` L17-L38, `src/pull.hpp` L17-L39

`push_t` 仅持有 `lb_t _lb`，只实现 `xsend`/`xhas_out`/`xwrite_activated`，不可接收；`pull_t` 仅持有 `fq_t _fq`，只实现 `xrecv`/`xhas_in`/`xread_activated`，不可发送。

### F-076：req_t 继承 dealer_t 并增加请求-回复状态机
**信源**：`src/req.hpp` L16-L60

`req_t` 继承 `dealer_t`，增加 `_receiving_reply`（已发送请求等待回复）、`_message_begins`（消息首帧必须为空分隔帧）、`_reply_pipe`（请求发送到的 pipe）、`_request_id_frames_enabled`、`_request_id`（递增请求 ID）、`_strict`。`req_session_t` 有三状态状态机：`bottom`→`request_id`→`body`。

---

## 十三、TCP 传输

### F-077：tcp_connecter_t 继承 stream_connecter_base_t
**信源**：`src/tcp_connecter.hpp` L12-L60

`tcp_connecter_t` 以 `ZMQ_FINAL` 标记，持有 `_connect_timer_started`；实现 `out_event`（连接完成时）、`timer_event`（连接超时）、`start_connecting`、`open`（打开 TCP socket 并发起非阻塞连接）、`connect`（获取已连接 fd）、`tune_socket`（设置 TCP 参数）。

### F-078：tcp_listener_t 继承 stream_listener_base_t
**信源**：`src/tcp_listener.hpp` L12-L41

`tcp_listener_t` 持有 `tcp_address_t _address`；`set_local_address` 解析地址并创建监听 socket；`in_event` 在新连接到达时调用 `accept()` 获取 fd，然后调用基类 `create_engine(fd)` 创建 `zmtp_engine_t`。

### F-079：stream_connecter_base_t 重连退避
**信源**：`src/stream_connecter_base.hpp` L16-L95

基类持有 `_addr`、`_s`、`_handle`、`_socket`、`_session`、`_delayed_start`、`_current_reconnect_ivl`；`get_new_reconnect_ivl()` 实现指数退避（在 `reconnect_ivl` 和 `reconnect_ivl_max` 之间）；`reconnect_timer_id=1`，`add_reconnect_timer` 设置定时器重连。

### F-080：tcp_open_socket 解析地址并设置选项
**信源**：`src/tcp.hpp` L46-L55

声明 `fd_t tcp_open_socket(const char *address_, const options_t &options_, bool local_, bool fallback_to_ipv4_, tcp_address_t *out_tcp_addr_)`，解析地址、打开 socket、根据 options 设置 IPv6、keepalive、buffer 大小等参数。

---

## 十四、编解码

### F-081：v2_encoder_t 状态机
**信源**：`src/v2_encoder.hpp` L12-L26, `src/encoder.hpp` L27-L148

`v2_encoder_t` 继承 `encoder_base_t<v2_encoder_t>`（CRTP），有两个状态：`size_ready`（写入帧头：flags 字节 + 长度字节/8字节）和 `message_ready`（写入消息体）。`_tmp_buf[10]` 暂存帧头。基类实现 `encode()` 状态机循环和零拷贝优化（当数据量≥缓冲区大小时直接返回消息内存指针）。

### F-082：v2_decoder_t 状态机
**信源**：`src/v2_decoder.hpp` L14-L40

`v2_decoder_t` 继承 `decoder_base_t<v2_decoder_t, shared_message_memory_allocator>`，状态包括：`flags_ready`（读取 flags 字节）、`one_byte_size_ready`/`eight_byte_size_ready`（读取长度）、`message_ready`（读取消息体）；支持 `_zero_copy` 模式（使用共享内存分配器）；持有 `_in_progress` 消息和 `_msg_flags`。

### F-083：i_encoder / i_decoder 接口
**信源**：`src/i_encoder.hpp` L16-L28, `src/i_decoder.hpp` L15-L31

`i_encoder` 声明 `encode(unsigned char **data_, size_t size_)` 和 `load_msg(msg_t*)`；`i_decoder` 声明 `get_buffer`、`resize_buffer`、`decode(data_, size_, processed_)`（返回 1=消息完成，0=需更多数据，-1=错误）、`msg()`。

---

## 十五、无锁队列（ypipe / yqueue）

### F-084：ypipe_t 单读单写无锁队列
**信源**：`src/ypipe.hpp` L12-L175

`ypipe_t<T,N>` 是无锁队列实现，约束：同一时刻只有一个线程读、一个线程写。内部使用 `yqueue_t<T,N> _queue`，三个指针 `_w`（第一个未 flush 项，写线程专用）、`_r`（第一个未预取项，读线程专用）、`_f`（将来要 flush 的位置，写线程专用），以及一个原子指针 `_c`（读写线程唯一争用点，NULL 表示读端休眠）。

### F-085：ypipe flush 使用 CAS
**信源**：`src/ypipe.hpp` L76-L98

`flush()` 尝试 `_c.cas(_w, _f)`：若成功表示读端存活，移动 `_w=_f` 返回 true；若失败（`_c` 为 NULL），非原子地设置 `_c=_f`、`_w=_f`，返回 false 通知调用者需要唤醒读端。

### F-086：yqueue_t 批量分配内存块
**信源**：`src/yqueue.hpp` L15-L185

`yqueue_t<T,N>` 以 `chunk_t`（含 `T values[N]`、`prev`、`next` 指针）为单位分配内存，N 为粒度（消息管道 256，命令管道 16）；使用 `atomic_ptr_t<chunk_t> _spare_chunk` 缓存最近释放的块以减少 malloc/free；支持 POSIX `posix_memalign` 按缓存行对齐（默认 64 字节）。

---

## 十六、分发与公平队列算法

### F-087：fq_t 公平队列入站
**信源**：`src/fq.hpp` L18-L49

`fq_t` 管理 `array_t<pipe_t,1> _pipes`，`_active` 个活跃 pipe 在数组前部；`_current` 指向下一个要读取的 pipe（轮询）；`_more` 跟踪多部分消息；`recv` 从当前 pipe 读取，遇到 pipe 无消息时切换到下一个活跃 pipe。

### F-088：lb_t 负载均衡出站
**信源**：`src/lb.hpp` L16-L55

`lb_t` 管理 `array_t<pipe_t,2> _pipes`，`_current` 指向最近发送的 pipe；`send` 轮询选择活跃 pipe 写入；`_more` 跟踪多部分消息（同一多部分消息的所有帧发往同一 pipe）；`_dropping` 处理 pipe 中途终止时丢弃剩余帧。

### F-089：dist_t 发布-订阅分发
**信源**：`src/dist.hpp` L18-L88

`dist_t` 管理 `array_t<pipe_t,2> _pipes`，维护三个计数：`_matching`（匹配的 pipe 数）、`_active`（活跃 pipe 数）、`_eligible`（合格 pipe 数）；`match(pipe)` 标记 pipe 为匹配；`send_to_matching(msg)` 仅向匹配的 pipe 发送消息；`reverse_match()` 反转匹配状态（用于 `ZMQ_INVERT_MATCHING`）。

---

## 十七、stream_engine_base_t

### F-090：stream_engine_base_t 是流协议引擎基类
**信源**：`src/stream_engine_base.hpp` L28-L191

继承 `io_object_t` 和 `i_engine`；持有 `_s`（底层 fd）、`_handle`（poller 句柄）、`_decoder`/`_encoder`、`_mechanism`（安全机制）、`_session`/`_socket`、`_handshaking`（握手中标志）、`_next_msg`/`_process_msg`（函数指针状态机）、`_inpos`/`_insize`/`_outpos`/`_outsize`（编解码缓冲区指针）、`_input_stopped`/`_output_stopped`、握手定时器和心跳定时器。

### F-091：i_engine 接口
**信源**：`src/i_engine.hpp` L15-L52

```cpp
struct i_engine {
    enum error_reason_t { protocol_error, connection_error, timeout_error };
    virtual bool has_handshake_stage() = 0;
    virtual void plug(io_thread_t*, session_base_t*) = 0;
    virtual void terminate() = 0;
    virtual bool restart_input() = 0;
    virtual void restart_output() = 0;
    virtual void zap_msg_available() = 0;
    virtual const endpoint_uri_pair_t &get_endpoint() const = 0;
};
```

---

## 十八、trie / mtrie 订阅前缀树

### F-092：trie_t 是基数前缀树
**信源**：`src/trie.hpp` L14-L56

`trie_t` 节点包含 `_refcnt`（引用计数）、`_min`（最小子节点字符）、`_count`（子节点数）、`_live_nodes`（非终止节点数）、`_next` union（单子节点时为 `trie_t*`，多子节点时为 `trie_t**`）；提供 `add`、`rm`、`check`（前缀匹配）、`apply`（遍历所有订阅前缀）。

### F-093：mtrie_t 是多值前缀树
**信源**：`src/mtrie.hpp` L16-L23, `src/generic_mtrie.hpp`

`mtrie_t` 是 `generic_mtrie_t<pipe_t>` 的 typedef，前缀树的每个终止节点关联一组 `pipe_t*`（而非布尔值），用于 XPUB 将订阅前缀映射到所有订阅了该前缀的 pipe。支持 `add(prefix, pipe)`、`rm(prefix, pipe)`、`match(data, size, callback)` 对所有匹配前缀的 pipe 调用回调。

---

## 事实统计

| 分类 | 事实编号范围 | 数量 |
|------|-------------|------|
| 公共 C API | F-001 ~ F-011 | 11 |
| 上下文 | F-012 ~ F-019 | 8 |
| 对象层次 | F-020 ~ F-022 | 3 |
| 套接字基类 | F-023 ~ F-031 | 9 |
| 管道 | F-032 ~ F-038 | 7 |
| 消息 | F-039 ~ F-047 | 9 |
| 邮箱与命令 | F-048 ~ F-052 | 5 |
| I/O 线程与 poller | F-053 ~ F-057 | 5 |
| ZMTP 引擎 | F-058 ~ F-063 | 6 |
| 会话 | F-064 ~ F-066 | 3 |
| 套接字选项 | F-067 ~ F-068 | 2 |
| 消息模式实现 | F-069 ~ F-076 | 8 |
| TCP 传输 | F-077 ~ F-080 | 4 |
| 编解码 | F-081 ~ F-083 | 3 |
| 无锁队列 | F-084 ~ F-086 | 3 |
| 分发算法 | F-087 ~ F-089 | 3 |
| 引擎基类与接口 | F-090 ~ F-091 | 2 |
| 订阅前缀树 | F-092 ~ F-093 | 2 |
| **合计** | | **93** |
