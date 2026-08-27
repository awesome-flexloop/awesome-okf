---
type: concept
title: "消息模式实现"
description: "fq_t 公平队列/lb_t 负载均衡/dist_t 发布分发算法、DEALER/ROUTER 路由策略、PUB/SUB 的 trie/mtrie 双端订阅过滤、REQ/REP 严格状态机、PUSH/PULL 流水线、模板方法模式在各模式中的应用"
tags: [libzmq, zeromq, patterns, pub-sub, router-dealer, push-pull, fq, lb, trie, mtrie]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/socket-base.md, ../references/msg.md]
  facts: [F-069, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-087, F-088, F-089, F-092, F-093, F-031]
---

# 消息模式实现

## 核心理解

libzmq 的消息模式通过**模板方法模式**实现：`socket_base_t` 定义收发骨架，子类覆写 `xsend`/`xrecv`/`xattach_pipe` 等钩子实现不同路由语义。路由逻辑由三个可复用的算法组件驱动：
- `fq_t`（公平队列）：轮询从多个入站 pipe 接收
- `lb_t`（负载均衡）：轮询向多个出站 pipe 发送
- `dist_t`（分发器）：向匹配的 pipe 广播

PUB/SUB 的订阅过滤通过前缀树（`trie_t`/`mtrie_t`）实现，在发布端和订阅端双端协作。

## 路由算法组件

### fq_t：公平队列（Fair Queuing）

`fq_t` 管理入站消息的轮询读取（F-087）：

```cpp
class fq_t {
    array_t<pipe_t, 1> _pipes;  // 活跃 pipe 在数组前部
    int _active;                // 活跃 pipe 数
    int _current;               // 下一个要读取的 pipe 索引
    bool _more;                 // 是否正在读多部分消息
};
```

行为：
- `_pipes` 是 intrusive array，活跃 pipe 在 `[0, _active)` 区间
- `_current` 轮询指向当前 pipe
- `recv()` 从 `_current` 读取；若无消息，切换到下一个活跃 pipe
- 多部分消息的所有帧从同一个 pipe 读取（`_more` 跟踪）
- pipe 终止时从数组移除，活跃 pipe 前移

公平队列确保每个连接有平等的接收机会，不会因为一个连接消息多而饿死其他连接。

### lb_t：负载均衡（Load Balancing）

`lb_t` 管理出站消息的轮询发送（F-088）：

```cpp
class lb_t {
    array_t<pipe_t, 2> _pipes;
    int _current;               // 最近发送的 pipe
    bool _more;                 // 是否正在发多部分消息
    bool _dropping;             // pipe 中途终止时丢弃剩余帧
};
```

行为：
- `send()` 轮询选择活跃 pipe 写入
- 多部分消息的所有帧发往同一个 pipe（`_more` 跟踪）
- 若发送中途 pipe 终止，`_dropping` 标志丢弃剩余帧
- pipe 恢复可写时（`write_activated`）重新加入轮询

### dist_t：发布分发（Distribution）

`dist_t` 用于 PUB/XPUB 向多个订阅者广播消息（F-089）：

```cpp
class dist_t {
    array_t<pipe_t, 2> _pipes;
    int _matching;    // 匹配的 pipe 数
    int _active;      // 活跃 pipe 数
    int _eligible;    // 合格 pipe 数
};
```

关键方法：
- `match(pipe)`：标记 pipe 为匹配（订阅了当前主题）
- `unmatch(pipe)`：取消匹配
- `send_to_matching(msg)`：仅向匹配的 pipe 发送消息
- `reverse_match()`：反转匹配状态（用于 `ZMQ_INVERT_MATCHING`）

dist_t 维护三个计数，区分：
- **匹配**：订阅了当前消息主题
- **活跃**：可写（HWM 未满）
- **合格**：通过其他条件过滤

只有同时匹配且活跃的 pipe 才会收到消息。

## PUSH/PULL：流水线模式

`push_t` 和 `pull_t` 是最简单的模式（F-075）：

```cpp
class push_t : public socket_base_t {
    lb_t _lb;  // 只有负载均衡，只发不收
};

class pull_t : public socket_base_t {
    fq_t _fq;  // 只有公平队列，只收不发
};
```

| 方法 | push_t | pull_t |
|------|--------|--------|
| `xsend` | ✅ 委托给 lb.send() | ❌ ENOTSUP |
| `xrecv` | ❌ ENOTSUP | ✅ 委托给 fq.recv() |
| `xhas_out` | lb.has_out() | false |
| `xhas_in` | false | fq.has_in() |
| `xattach_pipe` | lb.attach(pipe) | fq.attach(pipe) |
| `xwrite_activated` | lb.activated(pipe) | — |
| `xread_activated` | — | fq.activated(pipe) |

PUSH 轮询分发任务到所有下游 PULL，PULL 公平队列从所有上游 PUSH 接收。这是无状态的并行任务分发模式——没有"任务确认"机制，PULL 断开时正在处理的消息会丢失（除非用 LINGER）。

## DEALER：匿名双向轮询

`dealer_t` 组合 fq 和 lb（F-069）：

```cpp
class dealer_t : public socket_base_t {
    fq_t _fq;  // 入站公平队列
    lb_t _lb;  // 出站负载均衡
};
```

DEALER 是完全异步的：
- 接收：轮询从所有连接读取消息
- 发送：轮询向所有连接发送消息
- 消息原样传递，不添加/移除任何帧
- 支持多部分消息，但不强制格式

DEALER 适用于异步客户端、负载均衡器、代理等场景。REQ 继承自 DEALER 并增加请求-回复状态机。

## ROUTER：显式寻址

`router_t` 继承 `routing_socket_base_t`（F-070, F-031），额外维护 routing_id→pipe 映射：

```cpp
class router_t : public routing_socket_base_t {
    fq_t _fq;
    msg_t _prefetched;
    blob_t _prefetched_id;
    msg_t _prefetched_msg;
    std::set<pipe_t*> _anonymous_pipes;
    uint32_t _next_integral_routing_id;
    bool _mandatory;
    bool _probe_router;
    bool _handover;
};
```

### 接收行为

ROUTER 接收消息时，`xrecv()` 自动在消息前**前置对端的 routing_id 帧**：

```
对端发送: [message body]
ROUTER 收到: [routing_id][message body]
```

应用程序需要保存 routing_id 以便后续回复。

### 发送行为

ROUTER 发送消息时，第一帧必须是 routing_id：

```
应用发送: [routing_id][reply body]
ROUTER 查 _out_pipes 表:
  ├─ 找到 → 移除 routing_id 帧，发送 [reply body] 到目标 pipe
  └─ 未找到:
      ├─ mandatory=false（默认）→ 静默丢弃
      └─ mandatory=true → 返回 EHOSTUNREACH
```

### 预取机制

`_prefetched` 机制：fq 读取消息后，ROUTER 将 identity 帧和消息体分别缓存，应用调用 recv 时返回。这使得 routing_id 帧的处理对应用透明。

### 匿名连接

未设置 routing_id 的对端连接时，ROUTER 自动生成整数 ID（`_next_integral_routing_id`），并将 pipe 加入 `_anonymous_pipes`。`ZMQ_PROBE_ROUTER` 选项使新连接时 ROUTER 自动收到一个空帧通知。

### 路由 ID 冲突处理

`_handover` 选项控制当已知 routing_id 的对端重新连接时：
- false（默认）：新连接被拒绝
- true：新连接接管，旧连接终止

## PUB/SUB：发布订阅

PUB/SUB 是主题广播模式，过滤在两端协作完成。

### pub_t / xpub_t

`pub_t` 以 `ZMQ_FINAL` 继承 `xpub_t`（F-071, F-073）：

```cpp
class xpub_t : public socket_base_t {
    mtrie_t _subscriptions;          // 前缀→pipe集合
    mtrie_t _manual_subscriptions;   // 手动订阅
    dist_t _dist;                    // 分发器
    bool _verbose_subs;              // 转发所有订阅消息
    bool _verbose_unsubs;
    bool _manual;                    // 手动模式
};
```

`pub_t` 覆写：
- `xattach_pipe`：不自动订阅所有消息（PUB 不接收）
- `xrecv`：返回 ENOTSUP
- `xhas_in`：返回 false

XPUB 与 PUB 的区别：XPUB 可见订阅事件（订阅/取消订阅消息作为入站消息传递），PUB 不可见。

发送流程：
1. `xsend(msg)` 收到消息（第一帧是主题）
2. `_subscriptions.match(msg.data(), msg.size(), ...)` 在 mtrie 中查找匹配的 pipe
3. `dist.match(pipe)` 标记每个匹配的 pipe
4. `dist.send_to_matching(msg)` 仅向匹配的 pipe 发送

### sub_t / xsub_t

`sub_t` 以 `ZMQ_FINAL` 继承 `xsub_t`（F-072, F-074）：

```cpp
class xsub_t : public socket_base_t {
    fq_t _fq;                         // 入站公平队列
    dist_t _dist;                     // 向上游分发订阅
    trie_with_size_t _subscriptions;  // 本地订阅前缀树
};
```

`sub_t` 覆写：
- `xsetsockopt`：处理 `ZMQ_SUBSCRIBE`/`ZMQ_UNSUBSCRIBE`，将前缀加入/移出 trie
- `xsend`：返回 ENOTSUP
- `xhas_out`：返回 false

接收过滤：
1. `xrecv` 从 fq 读取消息
2. `match(msg)` 在 trie 中检查消息前缀是否匹配至少一个订阅
3. 匹配则返回给应用，不匹配则丢弃

### 双端过滤协作

较新版本中过滤优先在 PUB 端（XPUB）完成：
- SUB 端维护 `trie_t`（单值前缀树）存储本地订阅
- SUB 发送 SUBSCRIBE 命令帧到 PUB（通过 dist 向上游转发）
- PUB 端维护 `mtrie_t`（多值前缀树）映射前缀→订阅了该前缀的所有 pipe
- PUB 发送消息时只向 mtrie 中匹配的 pipe 发送
- SUB 端仍保留 trie 作为二次过滤（防御性）

### trie_t：单值前缀树

`trie_t` 是基数前缀树（F-092）：

```cpp
class trie_t {
    unsigned int _refcnt;
    unsigned char _min;
    unsigned short _count;
    unsigned short _live_nodes;
    union {
        class trie_t *_one;
        class trie_t **_many;
    } _next;
};
```

- 每个节点表示前缀中的一个字节
- `_refcnt` > 0 表示该节点是一个订阅前缀的终止点
- 单子节点时用 `_one` 指针优化，多子节点时用 `_many` 数组
- 提供 `add(prefix, size)`、`rm(prefix, size)`、`check(data, size)`（前缀匹配）、`apply(callback)`
- 可通过 `ZMQ_USE_RADIX_TREE` 宏改用 `radix_tree_t`（自适应基数树，更省内存）

### mtrie_t：多值前缀树

`mtrie_t` 是 `generic_mtrie_t<pipe_t>` 的 typedef（F-093）：
- 每个终止节点关联一组 `pipe_t*`（而非布尔值）
- `add(prefix, pipe)`：为 pipe 添加订阅前缀
- `rm(prefix, pipe)`：移除 pipe 的订阅前缀
- `match(data, size, callback)`：对所有匹配前缀的 pipe 调用回调
- 用于 XPUB 将订阅前缀映射到所有订阅了该前缀的 pipe

## REQ/REP：请求-回复状态机

### req_t

`req_t` 继承 `dealer_t` 并增加严格状态机（F-076）：

```cpp
class req_t : public dealer_t {
    bool _receiving_reply;              // 已发送请求，等待回复
    bool _message_begins;               // 消息首帧必须为空分隔帧
    pipe_t *_reply_pipe;                // 请求发送到的 pipe
    bool _request_id_frames_enabled;
    uint32_t _request_id;               // 递增请求 ID
    bool _strict;
};
```

REQ 强制：
1. 发送的消息前自动插入空分隔帧：`["", request body]`
2. 发送请求后必须先接收回复，才能发送下一个请求
3. 回复必须从发送请求的同一个 pipe 接收（`_reply_pipe`）
4. 接收时自动移除空分隔帧

### rep_t

`rep_t` 类似 DEALER 但有服务端状态机：
1. 必须先接收请求才能发送回复
2. 回复自动路由到请求来源的 pipe
3. 接收的消息前有 routing_id 帧和空分隔帧

REQ/REP 的简单状态机在简单 RPC 场景下方便，但在需要异步/多请求时应使用 DEALER/ROUTER。

## 模式与算法组合表

| 模式 | 入站算法 | 出站算法 | 订阅存储 | 特殊行为 |
|------|---------|---------|---------|---------|
| PUSH | — | lb_t | — | 只发 |
| PULL | fq_t | — | — | 只收 |
| DEALER | fq_t | lb_t | — | 匿名轮询 |
| ROUTER | fq_t | routing_id 表 | — | 显式寻址，前置 identity |
| REQ | fq_t | lb_t | — | 请求-回复状态机 |
| REP | fq_t | lb_t | — | 服务端状态机 |
| PUB | — | dist_t | mtrie（对端订阅） | 只发，主题过滤 |
| XPUB | fq_t | dist_t | mtrie | 可见订阅事件 |
| SUB | trie 过滤 | — | trie（本地订阅） | 只收，前缀匹配 |
| XSUB | fq_t | dist_t | trie | 可编程订阅 |
| PAIR | 单 pipe | 单 pipe | — | 独占双向 |

## 自定义消息模式

实现自定义模式需要：
1. 继承 `socket_base_t`
2. 实现纯虚函数 `xattach_pipe` 和 `xpipe_terminated`
3. 按需覆写 `xsend`/`xrecv`/`xhas_in`/`xhas_out`
4. 组合 `fq_t`/`lb_t`/`dist_t` 或实现自定义路由
5. 在 `socket_base_t::create()` 工厂的 switch 中注册新类型

可复用的算法组件（fq/lb/dist）使得实现新模式不需要从零编写 pipe 管理逻辑。

## 相关概念

- [套接字基类](02-socket-base.md) — 模板方法模式和 x-钩子体系
- [管道与流控](04-pipe.md) — fq/lb/dist 管理的 pipe 对象
- [消息与引用计数](03-message.md) — 消息在模式间的传递
- [编解码与帧格式](12-encoder-decoder.md) — SUBSCRIBE/CANCEL 命令帧
- [套接字选项体系](09-options.md) — CONFLATE/MANDATORY 等模式选项
- [实战示例](../examples/push-pull-pipeline.md) — PUSH/PULL 流水线代码
