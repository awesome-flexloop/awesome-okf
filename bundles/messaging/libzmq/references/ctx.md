---
type: reference
title: "ctx_t：上下文基础设施完整索引"
description: "src/ctx.hpp 和 src/ctx.cpp 中 ctx_t 类的完整成员、start/terminate 时序、slot 槽位分配、inproc 端点注册、IO 线程选择、reaper 终止机制"
tags: [libzmq, reference, context, ctx]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  - path: "external/libs/remote/libzmq/src/ctx.hpp"
    facts: [F-012, F-013, F-014, F-019]
  - path: "external/libs/remote/libzmq/src/ctx.cpp"
    facts: [F-015, F-016, F-017, F-018]
---

# ctx_t：上下文基础设施完整索引

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `src/ctx.hpp` | C++ 头文件 | L37-L221 | ctx_t 类声明、成员变量、endpoint_t 结构体 |
| `src/ctx.cpp` | C++ 实现 | L53-L501+ | 构造/析构、start/terminate、create_socket、端点管理 |

ctx_t 是 libzmq 的全局容器，管理 I/O 线程池、socket 槽位、inproc 端点注册表和终止序列。

## 关键事实登记

### F-012：ctx_t 继承自 thread_ctx_t

**信源**：`src/ctx.hpp` L37-L61, L66

`thread_ctx_t` 基类管理线程参数：

| 成员 | 类型 | 说明 |
|------|------|------|
| `_thread_priority` | int | 线程优先级 |
| `_thread_sched_policy` | int | 线程调度策略 |
| `_thread_affinity_cpus` | std::set<int> | CPU 亲和性集合 |
| `_thread_name_prefix` | std::string | 线程名前缀 |
| `_opt_sync` | mutex_t | 保护上述参数的互斥锁 |

`ctx_t` 声明带 `ZMQ_FINAL` 标记，不可再被继承。

### F-013：ctx_t 关键成员

**信源**：`src/ctx.hpp` L150-L221

| 成员 | 类型 | 说明 |
|------|------|------|
| `_tag` | uint32_t | 魔数 0xabadcafe，用于调试检测野指针 |
| `_sockets` | array_t<socket_base_t> | 所有已创建的 socket 数组 |
| `_empty_slots` | std::vector<uint32_t> | 空闲线程槽位列表 |
| `_starting` | bool | 延迟启动标志（true 表示基础设施尚未启动） |
| `_terminating` | bool | 终止中标志 |
| `_slot_sync` | mutex_t | 保护槽位分配的互斥锁 |
| `_reaper` | reaper_t* | reaper 线程指针 |
| `_io_threads` | std::vector<io_thread_t*> | I/O 线程池 |
| `_slots` | std::vector<i_mailbox*> | mailbox 指针数组（按 tid 索引） |
| `_term_mailbox` | mailbox_t | 终止线程邮箱（槽位 0） |
| `_endpoints` | std::map<std::string, endpoint_t> | inproc 端点注册表 |
| `_pending_connections` | std::multimap<std::string, pipe_t*> | 待连接的 inproc 管道 |
| `_max_sockets` | int | 最大 socket 数 |
| `_max_msgsz` | int | 最大消息大小（INT_MAX 表示无限制） |
| `_io_thread_count` | int | I/O 线程数 |
| `_blocky` | bool | 是否使用阻塞式套接字操作 |
| `_ipv6` | bool | 是否启用 IPv6 |
| `_zero_copy` | bool | 是否启用零拷贝接收 |

### F-014：endpoint_t 结构体

**信源**：`src/ctx.hpp` L31-L35

```cpp
struct endpoint_t {
    socket_base_t *socket;
    options_t options;
};
```

inproc 端点注册时同时存储 socket 指针和选项副本。选项副本使对端（connect 方）无需同步即可访问 bind 方的 socket 选项（如 HWM、conflate 等），因为 `options_t` 是值类型。

### F-015：ctx_t 构造函数默认值

**信源**：`src/ctx.cpp` L53-L63

| 成员 | 默认值 | 说明 |
|------|--------|------|
| `_tag` | 0xabadcafe | 调试魔数 |
| `_starting` | true | 基础设施延迟到首个 socket 创建时启动 |
| `_terminating` | false | |
| `_reaper` | NULL | reaper 在 start() 中创建 |
| `_max_sockets` | clipped_maxsocket(1023) | 受系统限制裁剪 |
| `_max_msgsz` | INT_MAX | 无消息大小限制 |
| `_io_thread_count` | 1 | 单个 I/O 线程 |
| `_blocky` | true | |
| `_ipv6` | false | 默认 IPv4 |
| `_zero_copy` | true | 默认启用零拷贝 |

### F-016：start() 延迟启动基础设施

**信源**：`src/ctx.cpp` L390-L460

`start()` 在首次调用 `create_socket()` 时触发，执行以下步骤：

1. **计算槽位总数**：`slot_count = max_sockets + io_thread_count + 2`
   - 额外 2 个槽位用于 term mailbox 和 reaper mailbox
2. **分配槽位数组**：`_slots.resize(slot_count)`
3. **固定槽位分配**：
   - 槽位 0 = `_term_mailbox`（`term_tid = 0`）
   - 槽位 1 = reaper mailbox（`reaper_tid = 1`）
4. **创建并启动 reaper 线程**
5. **创建并启动 I/O 线程**：`io_thread_count` 个，占用槽位 2 到 2+io_thread_count-1
6. **剩余槽位加入 `_empty_slots`**：供 socket 分配使用

延迟启动设计使得仅创建上下文但不创建 socket 时不会产生任何线程。

### F-017：create_socket 分配槽位并委托工厂方法

**信源**：`src/ctx.cpp` L462-L501

```cpp
socket_base_t *create_socket (int type_);
```

执行流程：

1. 加锁 `_slot_sync`
2. 检查 `_terminating`，若 true 返回 NULL 并设置 errno=ETERM
3. 若 `_starting` 为 true，调用 `start()` 启动基础设施
4. 从 `_empty_slots` 取一个槽位（若无空闲槽位返回 EMFILE）
5. 通过 `max_socket_id.add(1) + 1` 生成唯一 sid
6. 调用静态工厂方法 `socket_base_t::create(type_, this, slot, sid)` 创建具体 socket 实例
7. 将 socket 的 mailbox 注册到 `_slots[slot]`
8. 将 socket 加入 `_sockets` 数组
9. 返回 socket 指针

`socket_base_t::create()` 根据 `type_` 参数 switch 创建对应类型实例（pair_t/pub_t/sub_t/...）。

### F-018：terminate 等待 reaper 完成

**信源**：`src/ctx.cpp` L133-L210

`terminate()` 执行流程：

1. **连接 pending inproc 连接**：遍历 `_pending_connections`，为每个等待中的连接创建临时 PAIR socket 并绑定，使对端的 connect 能完成
2. **向所有 socket 发送 `stop` 命令**：触发每个 socket 开始关闭流程
3. **若 socket 列表为空**：直接停止 reaper
4. **阻塞等待**：在 `_term_mailbox.recv(&cmd, -1)` 上阻塞，直到收到 `command_t::done` 命令
5. **清理资源**：停止 I/O 线程、释放槽位、关闭 term mailbox
6. **自销毁**：`delete this`

终止信号传播链：
```
zmq_ctx_term()
  → send stop to all sockets
    → each socket closes pipes/sessions
      → sessions send reap to reaper
        → reaper collects all sockets
          → reaper sends done to term mailbox
            → terminate() unblocks → delete this
```

### F-019：choose_io_thread 按负载选择

**信源**：`src/ctx.hpp` L102-L105

```cpp
io_thread_t *choose_io_thread (uint64_t affinity_);
```

- `affinity_` 参数指定哪些 I/O 线程合格（0 表示全部线程合格）
- 返回当前负载最低的 I/O 线程
- 每个 socket 在创建时绑定到一个 I/O 线程，该线程负责该 socket 所有连接的实际网络 I/O
