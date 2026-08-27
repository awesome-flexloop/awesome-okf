---
type: example
title: "ROUTER/DEALER 异步请求-回复"
description: "使用 ROUTER/DEALER 实现异步请求-回复模式，演示 identity 路由帧、多部分消息结构、ROUTER_MANDATORY 选项、异步客户端和多worker服务端，包含完整可编译 C 代码"
tags: [libzmq, example, router, dealer, async, request-reply, identity]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmq-h-api.md, ../references/socket-base.md]
  facts: [F-006, F-007, F-031, F-069, F-070]
---

# ROUTER/DEALER 异步请求-回复

## 目标

使用 ROUTER/DEALER 套接字实现异步请求-回复模式：多个 DEALER 客户端向 ROUTER 服务端发送请求，服务端将请求分发给多个工作者处理。通过这个例子理解：
- ROUTER 的 routing_id 路由机制
- DEALER 的 fq+lb 双向轮询
- 多部分消息中的 identity 帧结构
- `ZMQ_ROUTER_MANDATORY` 选项
- 异步非阻塞的请求-回复模式

## 架构

```
┌──────────┐                     ┌──────────┐
│ client 1 │── [id1]["", req] ──►│          │
│ (DEALER) │                     │  ROUTER  │── [worker_id]["", client_id, "", req] ──► worker
├──────────┤                     │ server   │
│ client 2 │── [id2]["", req] ──►│          │
│ (DEALER) │                     └────┬─────┘
└──────────┘                          │
                                      │ 多个 worker（DEALER）
                                ┌─────┴──────┐
                                ▼            ▼
                           ┌─────────┐  ┌─────────┐
                           │ worker1 │  │ worker2 │
                           │(DEALER) │  │(DEALER) │
                           └─────────┘  └─────────┘
```

### 消息帧结构

DEALER 发送时自动添加空帧：
```
DEALER 发送: ["", request_data]
ROUTER 收到: [client_routing_id, "", request_data]

ROUTER 发送给 worker: [worker_routing_id, "", client_routing_id, "", request_data]
worker 回复:       [client_routing_id, "", response_data]
ROUTER 转发给客户端: [client_routing_id, "", response_data]
```

## 完整代码

### 异步服务端（rrserver.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#endif

#define NBR_WORKERS 3

int main(void)
{
    void *context = zmq_ctx_new();

    /* ROUTER 面向客户端 */
    void *clients = zmq_socket(context, ZMQ_ROUTER);
    int mandatory = 1;
    zmq_setsockopt(clients, ZMQ_ROUTER_MANDATORY,
                   &mandatory, sizeof(mandatory));
    zmq_bind(clients, "tcp://*:5559");

    /* DEALER 面向 worker */
    void *workers = zmq_socket(context, ZMQ_DEALER);
    zmq_bind(workers, "tcp://*:5560");

    printf("异步请求-回复服务端已启动\n");
    printf("  客户端端口: 5559\n");
    printf("  Worker端口: 5560\n");
    printf("  请先启动 %d 个 worker，再启动客户端\n", NBR_WORKERS);

    /* 使用 zmq_proxy 将 ROUTER 和 DEALER 连接 */
    /* 但为了演示消息结构，我们手动转发 */
    while (1) {
        zmq_pollitem_t items[] = {
            { clients, 0, ZMQ_POLLIN, 0 },
            { workers, 0, ZMQ_POLLIN, 0 }
        };

        int rc = zmq_poll(items, 2, -1);
        if (rc == -1)
            break;

        if (items[0].revents & ZMQ_POLLIN) {
            /* 收到客户端请求，转发给 worker（DEALER 负载均衡） */
            /* 消息格式: [client_id, "", request] */
            /* 转发格式: [client_id, "", request] — DEALER 自动添加空帧 */

            /* 读取并转发所有帧 */
            int more;
            size_t more_size = sizeof(more);

            /* 读 client_id 帧 */
            char client_id[256];
            int id_len = zmq_recv(clients, client_id,
                                  sizeof(client_id), 0);
            if (id_len == -1) break;

            /* 读空帧 */
            char empty[1];
            zmq_getsockopt(clients, ZMQ_RCVMORE, &more, &more_size);
            if (more)
                zmq_recv(clients, empty, 0, 0);

            /* 读请求帧 */
            zmq_getsockopt(clients, ZMQ_RCVMORE, &more, &more_size);
            char request[256];
            int req_len = 0;
            if (more)
                req_len = zmq_recv(clients, request,
                                   sizeof(request), 0);

            printf("收到客户端请求 (id=%.*s): %.*s\n",
                   id_len, client_id, req_len, request);

            /* 发送给 worker：DEALER 会自动添加 worker_id 帧和空帧 */
            /* 我们需要发送 client_id + 空帧 + request */
            zmq_send(workers, client_id, id_len, ZMQ_SNDMORE);
            zmq_send(workers, "", 0, ZMQ_SNDMORE);
            zmq_send(workers, request, req_len, 0);
        }

        if (items[1].revents & ZMQ_POLLIN) {
            /* 收到 worker 回复，转发给客户端（ROUTER 按 routing_id 路由） */
            /* 消息格式: [client_id, "", response] */
            /* ROUTER 会使用第一帧作为路由目标 */

            /* 读取所有帧并转发 */
            char client_id[256];
            int id_len = zmq_recv(workers, client_id,
                                  sizeof(client_id), 0);
            if (id_len == -1) break;

            int more;
            size_t more_size = sizeof(more);

            /* 读空帧 */
            char empty[1];
            zmq_getsockopt(workers, ZMQ_RCVMORE, &more, &more_size);
            if (more)
                zmq_recv(workers, empty, 0, 0);

            /* 读回复帧 */
            zmq_getsockopt(workers, ZMQ_RCVMORE, &more, &more_size);
            char response[256];
            int resp_len = 0;
            if (more)
                resp_len = zmq_recv(workers, response,
                                    sizeof(response), 0);

            printf("转发回复给客户端 (id=%.*s): %.*s\n",
                   id_len, client_id, resp_len, response);

            /* 发送给客户端：ROUTER 会使用第一帧路由 */
            /* 需要发送: [client_id, "", response] */
            zmq_send(clients, client_id, id_len, ZMQ_SNDMORE);
            zmq_send(clients, "", 0, ZMQ_SNDMORE);
            zmq_send(clients, response, resp_len, 0);
        }
    }

    zmq_close(clients);
    zmq_close(workers);
    zmq_ctx_term(context);
    return 0;
}
```

### Worker（rrworker.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#endif

int main(int argc, char *argv[])
{
    void *context = zmq_ctx_new();
    void *worker = zmq_socket(context, ZMQ_DEALER);

    /* 可选：设置 worker 身份标识 */
    char worker_id[64];
    if (argc > 1) {
        snprintf(worker_id, sizeof(worker_id), "%s", argv[1]);
    } else {
        srand((unsigned int)time(NULL));
        snprintf(worker_id, sizeof(worker_id),
                 "worker-%04d", rand() % 10000);
    }
    zmq_setsockopt(worker, ZMQ_ROUTING_ID,
                   worker_id, strlen(worker_id));

    zmq_connect(worker, "tcp://localhost:5560");
    printf("Worker '%s' 已启动\n", worker_id);

    int request_nbr = 0;
    while (1) {
        /* DEALER 收到消息格式: [client_id, "", request] */
        /* 第一帧是空帧（DEALER 自动剥离），第二帧是 client_id... */
        /* 实际 DEALER 接收时去掉了前面的 worker_id 帧和空帧 */

        /* 读取 client_id 帧 */
        char client_id[256];
        int id_len = zmq_recv(worker, client_id,
                              sizeof(client_id), 0);
        if (id_len == -1) break;

        int more;
        size_t more_size = sizeof(more);

        /* 读空帧 */
        char empty[1];
        zmq_getsockopt(worker, ZMQ_RCVMORE, &more, &more_size);
        if (more)
            zmq_recv(worker, empty, 0, 0);

        /* 读请求帧 */
        zmq_getsockopt(worker, ZMQ_RCVMORE, &more, &more_size);
        char request[256];
        int req_len = 0;
        if (more)
            req_len = zmq_recv(worker, request,
                               sizeof(request), 0);

        printf("[%s] 收到请求: %.*s\n",
               worker_id, req_len, request);

        /* 模拟处理时间 */
        sleep_ms(100 + (rand() % 500));

        /* 构造回复 */
        char reply[512];
        int reply_len = snprintf(reply, sizeof(reply),
                                 "OK #%d from %s",
                                 ++request_nbr, worker_id);

        /* 回复格式: [client_id, "", reply] */
        /* DEALER 会自动添加 worker_id 和空帧到最前面 */
        zmq_send(worker, client_id, id_len, ZMQ_SNDMORE);
        zmq_send(worker, "", 0, ZMQ_SNDMORE);
        zmq_send(worker, reply, reply_len, 0);

        printf("[%s] 发送回复: %s\n", worker_id, reply);
    }

    zmq_close(worker);
    zmq_ctx_term(context);
    return 0;
}
```

### 异步客户端（rrclient.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#endif

int main(int argc, char *argv[])
{
    void *context = zmq_ctx_new();
    void *client = zmq_socket(context, ZMQ_DEALER);

    /* 设置客户端身份（可选） */
    char client_id[64];
    if (argc > 1) {
        snprintf(client_id, sizeof(client_id), "%s", argv[1]);
    } else {
        srand((unsigned int)time(NULL) ^ (intptr_t)context);
        snprintf(client_id, sizeof(client_id),
                 "client-%04d", rand() % 10000);
    }
    zmq_setsockopt(client, ZMQ_ROUTING_ID,
                   client_id, strlen(client_id));

    /* 设置接收超时，避免永久阻塞 */
    int rcvtimeo = 5000;
    zmq_setsockopt(client, ZMQ_RCVTIMEO,
                   &rcvtimeo, sizeof(rcvtimeo));

    zmq_connect(client, "tcp://localhost:5559");
    printf("客户端 '%s' 已启动\n", client_id);

    int request_nbr;
    for (request_nbr = 0; request_nbr < 10; request_nbr++) {
        /* 发送请求 */
        char request[256];
        int req_len = snprintf(request, sizeof(request),
                               "Request #%d from %s",
                               request_nbr + 1, client_id);

        /* DEALER 自动添加空帧: 实际发送 ["", request] */
        printf("发送: %s\n", request);
        zmq_send(client, request, req_len, 0);

        /* 等待回复（非严格状态机，可以异步发送多个请求） */
        char reply[512];
        int rc = zmq_recv(client, reply, sizeof(reply) - 1, 0);
        if (rc == -1) {
            printf("等待回复超时...\n");
            continue;
        }
        reply[rc] = '\0';
        printf("收到回复: %s\n", reply);

        sleep_ms(200 + (rand() % 800));
    }

    zmq_close(client);
    zmq_ctx_term(context);
    return 0;
}
```

## 编译与运行

```bash
# 编译
gcc -o rrserver rrserver.c -lzmq
gcc -o rrworker rrworker.c -lzmq
gcc -o rrclient rrclient.c -lzmq

# 运行顺序（多个终端）
# 终端 1：启动服务端
./rrserver

# 终端 2-4：启动 3 个 worker
./rrworker worker-A
./rrworker worker-B
./rrworker worker-C

# 终端 5-6：启动多个客户端
./rrclient client-1
./rrclient client-2
```

## 原理解析

### ROUTER 的 routing_id 路由

ROUTER 套接字维护 `_out_pipes` 映射表（F-031）：
```cpp
std::map<blob_t, out_pipe_t> _out_pipes;
```

- 当 DEALER 连接到 ROUTER 时，ROUTER 学习到其 routing_id
- ROUTER 接收消息时，**自动前置**对端的 routing_id 帧
- ROUTER 发送消息时，第一帧必须是 routing_id，用于查找目标 pipe
- 发送后 ROUTER 移除第一帧，剩余帧原样发送

routing_id 可以：
- 通过 `ZMQ_ROUTING_ID` 选项显式设置（最大 255 字节）
- 未设置时由引擎自动生成 UUID

### DEALER 的 fq+lb 双向轮询

DEALER 内部组合 `fq_t`（公平队列）和 `lb_t`（负载均衡）（F-069）：
- 接收：轮询从所有连接读取（fq）
- 发送：轮询向所有连接发送（lb）
- 自动添加/剥离空分隔帧
- 不强制请求-回复状态机（与 REQ 不同）

这使得 DEALER 可以完全异步：可以连续发送多个请求，回复按到达顺序返回。

### ZMQ_ROUTER_MANDATORY 选项

启用后（F-007），ROUTER 发送消息时如果 routing_id 对应的 pipe 不存在（对端已断开），返回 `EHOSTUNREACH` 错误而非静默丢弃。这对于检测死连接很重要。

```c
int mandatory = 1;
zmq_setsockopt(router, ZMQ_ROUTER_MANDATORY,
               &mandatory, sizeof(mandatory));
```

### 空分隔帧的作用

空帧（zero-length frame）在 ROUTER/DEALER 模式中作为地址帧与数据帧的分隔符：
- REQ/REP 使用空帧分隔请求/回复信封
- DEALER 自动在消息前添加空帧
- ROUTER 不修改消息结构，需要应用层处理空帧
- 多跳代理时，每经过一个 REQ/REP 层就增加一个空帧+回复地址

### 与 REQ/REP 的区别

| 特性 | REQ/REP | DEALER/ROUTER |
|------|---------|---------------|
| 状态机 | 严格（send→recv→send） | 无状态，全异步 |
| 路由 | 自动 | 手动（routing_id） |
| 多请求 | 不允许 | 允许（pipeline） |
| 复杂度 | 低 | 中 |
| 适用场景 | 简单 RPC | 异步代理、负载均衡 |

### 更简单的实现：zmq_proxy

上面的服务端手动转发消息。实际上，可以使用 `zmq_proxy()` 一行代码实现 ROUTER-DEALER 代理：

```c
void *frontend = zmq_socket(context, ZMQ_ROUTER);
void *backend  = zmq_socket(context, ZMQ_DEALER);
zmq_bind(frontend, "tcp://*:5559");
zmq_bind(backend, "tcp://*:5560");
zmq_proxy(frontend, backend, NULL);  // 阻塞
```

`zmq_proxy` 自动处理帧转发和多部分消息，但不提供自定义路由逻辑。上面的手动实现用于演示消息结构。

## 延伸阅读

- [消息模式实现](../concepts/11-patterns.md) — ROUTER routing_id 表和 DEALER fq+lb
- [套接字基类](../concepts/02-socket-base.md) — routing_socket_base_t 路由表
- [管道与流控](../concepts/04-pipe.md) — HWM 和多部分消息原子性
- [PUSH/PULL 流水线](push-pull-pipeline.md) — 更简单的无状态分发
