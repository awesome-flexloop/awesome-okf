---
type: example
title: "inproc 线程间零拷贝通信"
description: "使用 inproc 传输在同一进程的多个线程间传递消息，演示 msg_t 引用计数零拷贝、pipepair 直连、zmq_msg_init_data 发送端零拷贝、zmq_msg_move 所有权转移，包含完整多线程 C 代码"
tags: [libzmq, example, inproc, thread, zero-copy, msg, reference-counting]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmq-h-api.md, ../references/msg.md, ../references/ctx.md]
  facts: [F-004, F-005, F-028, F-029, F-032, F-039, F-040, F-042, F-043, F-044, F-045, F-046]
---

# inproc 线程间零拷贝通信

## 目标

使用 `inproc://` 传输在同一进程的多个线程间高效传递消息，演示 ZeroMQ 的零拷贝机制：
- `zmq_msg_init_data()` 发送端零拷贝（直接引用应用缓冲区）
- `zmq_msg_move()` 所有权零开销转移
- 大消息的 `content_t` 引用计数共享
- inproc 不经过网络栈和编解码，直接在 socket 间创建 pipepair

## 架构

```
┌─────────────────────────────────────────────┐
│              进程 (同一 context)              │
│                                              │
│  ┌──────────┐         pipepair        ┌─────┴────┐
│  │ 主线程    │◄──────────────────────►│ worker   │
│  │ PUSH     │   ypipe_t<msg_t>       │ PULL     │
│  │ (bind)   │   64字节值拷贝          │ (connect)│
│  └──────────┘   content_t引用计数     └──────────┘
│       ▲                                    │
│       │                                    ▼
│  ┌──────────┐                       ┌──────────┐
│  │ 结果收集  │◄────── pipepair ──────│ worker 2 │
│  │ PULL     │                       │ PUSH     │
│  │ (bind)   │                       │ (connect)│
│  └──────────┘                       └──────────┘
└─────────────────────────────────────────────┘
```

inproc 连接不经过 TCP/IP 栈：
- `bind("inproc://name")` 在 ctx 中注册 endpoint
- `connect("inproc://name")` 直接创建 `pipepair()`
- 消息通过 `ypipe_t<msg_t>` 传递（64 字节值拷贝）
- 大消息数据通过 `content_t` 引用计数共享，无数据拷贝

## 完整代码

### inproc 零拷贝示例（inproc_demo.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#define THREAD_RET DWORD WINAPI
#define THREAD_ARG LPVOID
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#define THREAD_RET void *
#define THREAD_ARG void *
#endif

/* 大消息大小：超过 max_vsm_size(~30字节)，会使用 content_t */
#define LARGE_MSG_SIZE (4 * 1024)
#define NBR_ITEMS 100

/* ============================================================
 * 自定义释放函数：用于 zmq_msg_init_data 的发送端零拷贝
 * ============================================================ */
typedef struct {
    void *data;
    int   size;
    int   id;
} my_buffer_t;

static void my_free_fn(void *data, void *hint)
{
    /* ZeroMQ 在发送完成后调用此函数释放缓冲区 */
    my_buffer_t *buf = (my_buffer_t *)hint;
    printf("[free] 释放缓冲区 #%d (%p, %d bytes)\n",
           buf->id, data, buf->size);
    free(buf->data);
    free(buf);
}

/* ============================================================
 * Worker 线程：接收任务，处理后发送结果
 * ============================================================ */
typedef struct {
    void *context;
    int   worker_id;
} worker_args_t;

static THREAD_RET worker_thread(THREAD_ARG arg)
{
    worker_args_t *args = (worker_args_t *)arg;
    void *context = args->context;
    int id = args->worker_id;

    /* 接收任务（PULL） */
    void *receiver = zmq_socket(context, ZMQ_PULL);
    zmq_connect(receiver, "inproc://tasks");

    /* 发送结果（PUSH） */
    void *sender = zmq_socket(context, ZMQ_PUSH);
    zmq_connect(sender, "inproc://results");

    printf("[worker %d] 已启动\n", id);

    int task_count = 0;
    while (task_count < NBR_ITEMS / 2) {
        /* 接收消息 */
        zmq_msg_t msg;
        zmq_msg_init(&msg);
        int rc = zmq_msg_recv(&msg, receiver, 0);
        if (rc == -1) {
            zmq_msg_close(&msg);
            break;
        }

        size_t size = zmq_msg_size(&msg);
        void *data = zmq_msg_data(&msg);

        printf("[worker %d] 收到消息: size=%zu, shared=%d\n",
               id, size,
               zmq_msg_get(&msg, ZMQ_SHARED));

        /* 模拟处理 */
        if (size >= 4) {
            unsigned char *bytes = (unsigned char *)data;
            bytes[0] ^= 0xFF;  /* 修改首字节 */
        }

        /* 使用 move 将消息所有权转移到发送 socket（零拷贝） */
        /* move 不修改引用计数，只是 64 字节 memcpy */
        zmq_msg_t result;
        zmq_msg_init(&result);
        zmq_msg_move(&result, &msg);  /* msg 变为空消息 */

        /* 添加 worker ID 前缀（演示多部分消息） */
        char header[64];
        int hlen = snprintf(header, sizeof(header),
                            "worker-%d:", id);

        /* 发送多部分消息：[header, data] */
        zmq_msg_t hdr_msg;
        zmq_msg_init_size(&hdr_msg, hlen);
        memcpy(zmq_msg_data(&hdr_msg), header, hlen);

        zmq_msg_send(&hdr_msg, sender, ZMQ_SNDMORE);
        zmq_msg_send(&result, sender, 0);

        zmq_msg_close(&hdr_msg);
        /* result 已被 send 消耗（move 语义），不需要 close */
        /* msg 已经被 move，close 是空操作 */
        zmq_msg_close(&msg);

        task_count++;
    }

    printf("[worker %d] 处理完成，共 %d 个任务\n", id, task_count);
    zmq_close(receiver);
    zmq_close(sender);
    free(args);
    return 0;
}

/* ============================================================
 * 主函数：创建 context、bind inproc endpoint、启动线程
 * ============================================================ */
int main(void)
{
    void *context = zmq_ctx_new();

    /* 任务分发：PUSH bind inproc */
    void *task_sender = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(task_sender, "inproc://tasks");

    /* 结果收集：PULL bind inproc */
    void *result_receiver = zmq_socket(context, ZMQ_PULL);
    zmq_bind(result_receiver, "inproc://results");

    printf("inproc 端点已绑定:\n");
    printf("  tasks:   inproc://tasks\n");
    printf("  results: inproc://results\n");

    /* 启动 worker 线程 */
    pthread_t threads[2];
    int i;
    for (i = 0; i < 2; i++) {
        worker_args_t *args = (worker_args_t *)malloc(sizeof(*args));
        args->context = context;
        args->worker_id = i + 1;
#ifdef _WIN32
        HANDLE h = CreateThread(NULL, 0, worker_thread, args, 0, NULL);
        threads[i] = (pthread_t)h;
#else
        pthread_create(&threads[i], NULL, worker_thread, args);
#endif
    }

    /* 等待 worker 启动 */
    sleep_ms(200);

    printf("\n=== 演示 1: 小消息（VSM，内联在 msg_t 内）===\n");
    {
        zmq_msg_t msg;
        const char *text = "Hello inproc!";
        zmq_msg_init_size(&msg, strlen(text));
        memcpy(zmq_msg_data(&msg), text, strlen(text));

        size_t size = zmq_msg_size(&msg);
        printf("发送小消息: '%s' (size=%zu)\n",
               (char *)zmq_msg_data(&msg), size);
        printf("  小消息数据内联在 64 字节 msg_t 中，无堆分配\n");

        zmq_msg_send(&msg, task_sender, 0);
        zmq_msg_close(&msg);
    }

    sleep_ms(100);
    printf("\n=== 演示 2: 大消息（LMSG，content_t 引用计数）===\n");
    {
        zmq_msg_t msg;
        zmq_msg_init_size(&msg, LARGE_MSG_SIZE);
        unsigned char *data = (unsigned char *)zmq_msg_data(&msg);

        /* 填充数据 */
        memset(data, 0xAB, LARGE_MSG_SIZE);
        snprintf((char *)data, 32, "Large message payload #%d", 1);

        printf("发送大消息: size=%d\n", LARGE_MSG_SIZE);
        printf("  数据存储在堆分配的 content_t 中\n");
        printf("  inproc 传递时只有指针拷贝（引用计数共享）\n");

        /* 发送后 msg 被 move 到管道，引用计数保持 1 */
        zmq_msg_send(&msg, task_sender, 0);
        zmq_msg_close(&msg);
    }

    sleep_ms(100);
    printf("\n=== 演示 3: zmq_msg_copy 共享引用（非深拷贝）===\n");
    {
        zmq_msg_t original;
        zmq_msg_init_size(&original, LARGE_MSG_SIZE);
        unsigned char *p = (unsigned char *)zmq_msg_data(&original);
        memset(p, 0xCD, LARGE_MSG_SIZE);

        zmq_msg_t copy;
        zmq_msg_init(&copy);
        zmq_msg_copy(&copy, &original);

        printf("original 和 copy 共享同一个 content_t\n");
        printf("  original shared=%d, copy shared=%d\n",
               zmq_msg_get(&original, ZMQ_SHARED),
               zmq_msg_get(&copy, ZMQ_SHARED));

        /* 发送副本，原始消息仍然有效 */
        zmq_msg_send(&copy, task_sender, 0);
        zmq_msg_close(&copy);

        /* 原始消息仍然可以使用（引用计数从 2 降到 1）*/
        printf("  发送 copy 后 original 仍可用\n");

        /* 再发送原始消息 */
        zmq_msg_send(&original, task_sender, 0);
        zmq_msg_close(&original);
    }

    sleep_ms(100);
    printf("\n=== 演示 4: zmq_msg_init_data 发送端零拷贝 ===\n");
    {
        /* 应用程序分配缓冲区 */
        my_buffer_t *buf = (my_buffer_t *)malloc(sizeof(my_buffer_t));
        buf->data = malloc(LARGE_MSG_SIZE);
        buf->size = LARGE_MSG_SIZE;
        buf->id = 42;

        memset(buf->data, 0xEF, LARGE_MSG_SIZE);
        snprintf((char *)buf->data, 64,
                 "Zero-copy buffer #%d", buf->id);

        zmq_msg_t msg;
        /* ZeroMQ 直接引用 buf->data，不拷贝 */
        zmq_msg_init_data(&msg, buf->data, buf->size,
                          my_free_fn, buf);

        printf("发送零拷贝消息: buffer=%p, size=%d\n",
               buf->data, buf->size);
        printf("  ZeroMQ 直接引用应用缓冲区，无 memcpy\n");
        printf("  发送完成后调用 my_free_fn 释放\n");

        zmq_msg_send(&msg, task_sender, 0);
        zmq_msg_close(&msg);
    }

    /* 发送剩余任务 */
    int n;
    for (n = 5; n <= NBR_ITEMS; n++) {
        zmq_msg_t msg;
        zmq_msg_init_size(&msg, 64);
        snprintf((char *)zmq_msg_data(&msg), 64,
                 "Task #%d", n);
        zmq_msg_send(&msg, task_sender, 0);
        zmq_msg_close(&msg);
    }

    /* 收集结果 */
    printf("\n=== 收集结果 ===\n");
    int received = 0;
    while (received < NBR_ITEMS) {
        /* 读 header 帧 */
        char header[128];
        int rc = zmq_recv(result_receiver, header,
                          sizeof(header) - 1, 0);
        if (rc == -1) break;
        header[rc] = '\0';

        /* 读数据帧 */
        zmq_msg_t data_msg;
        zmq_msg_init(&data_msg);
        rc = zmq_msg_recv(&data_msg, result_receiver, 0);
        if (rc == -1) {
            zmq_msg_close(&data_msg);
            break;
        }

        printf("收到结果: %s data_size=%zu shared=%d\n",
               header,
               zmq_msg_size(&data_msg),
               zmq_msg_get(&data_msg, ZMQ_SHARED));

        zmq_msg_close(&data_msg);
        received++;
    }

    printf("\n共收到 %d 个结果\n", received);

    /* 等待线程结束 */
    for (i = 0; i < 2; i++) {
#ifdef _WIN32
        WaitForSingleObject((HANDLE)threads[i], INFINITE);
        CloseHandle((HANDLE)threads[i]);
#else
        pthread_join(threads[i], NULL);
#endif
    }

    zmq_close(task_sender);
    zmq_close(result_receiver);
    zmq_ctx_term(context);

    printf("\n=== 零拷贝总结 ===\n");
    printf("1. 小消息(<=30B): 数据内联在 msg_t(64B)，copy=memcpy\n");
    printf("2. 大消息(>30B): content_t 堆分配，引用计数共享\n");
    printf("3. zmq_msg_move: 64B memcpy + 源重置，零引用计数操作\n");
    printf("4. zmq_msg_copy: 共享引用，refcnt+1，非深拷贝\n");
    printf("5. zmq_msg_init_data: 直接引用应用缓冲区，发送端零拷贝\n");
    printf("6. inproc: pipepair 直连，无编解码、无网络栈\n");

    return 0;
}
```

## 编译与运行

```bash
# Linux/macOS（需要 pthread）
gcc -o inproc_demo inproc_demo.c -lzmq -lpthread

# Windows (MSVC)
cl inproc_demo.c /I C:\libzmq\include C:\libzmq\lib\zmq.lib

# 运行
./inproc_demo
```

**注意**：
- inproc 要求服务端和客户端使用**同一个 context**
- bind 必须在 connect 之前，或者使用 pending connections 机制（connect 可以先于 bind）
- 不需要安装网络库，不占用端口
- 线程函数必须使用 `zmq_socket` 创建自己的 socket（socket 不可跨线程共享）

## 原理解析

### inproc 的 pipepair 直连

当 inproc 连接建立时（F-028, F-029, F-032）：

1. `bind("inproc://tasks")` 在 `ctx._endpoints` 注册 `{socket, options}`
2. `connect("inproc://tasks")` 查找 endpoint
3. 调用 `pipepair(parents, pipes, hwms, conflates)` 创建双向管道
4. 通过 `send_bind` 命令将远端 pipe 附加到对端
5. 两个 socket 直接通过 pipe 通信，**不经过**：
   - TCP/IP 协议栈
   - ZMTP 编解码（v2_encoder/decoder）
   - 网络 I/O 线程
   - 系统调用（read/write/send/recv）

### msg_t 在 inproc 中的传递

消息从发送 socket 到接收 socket 的路径：

```
发送方线程                    接收方线程
zmq_msg_send(&msg)
  │
  ├─ VSM (≤30B):
  │   64B memcpy 到 ypipe
  │   ──────────────────────► 64B memcpy 从 ypipe
  │                            （数据在 msg_t 内联）
  │
  ├─ LMSG (>30B):
  │   content_t* 拷贝到 ypipe
  │   （64B memcpy，数据指针共享）
  │   ──────────────────────► 从 ypipe 读出 msg_t
  │   refcnt 不变              （指向同一个 content_t）
  │
  └─ init_data (零拷贝):
      content_t 包装外部 buffer
      ffn 回调在最后 close 时调用
```

### zmq_msg_move vs zmq_msg_copy

**move（F-046）**：
```
源 msg_t (64B)                目标 msg_t (64B)
┌──────────┐                 ┌──────────┐
│ content* │────────────────►│ content* │──┐
└──────────┘                 └──────────┘  │
     │                                     │
     ▼                                     ▼
源 = init() (空)                     同一个 content_t
                              refcnt 不变！
```
- 64 字节 memcpy
- 源被重置为空消息
- **不修改引用计数**
- 零开销所有权转移

**copy（F-044）**：
```
源 msg_t                     副本 msg_t
┌──────────┐                ┌──────────┐
│ content* │───共享────────►│ content* │
└──────────┘                └──────────┘
     │                            │
     └─────────► content_t ◄──────┘
               refcnt += 1
```
- 64 字节 memcpy
- 源和副本都有效
- 引用计数 +1（lmsg）
- **不是深拷贝**——修改副本数据会影响源

### content_t 引用计数生命周期

```
init_size(4096):
  malloc(content_t + 4096)
  placement new refcnt(1)
  content.ffn = NULL

  ┌─────────┬──────────────────┐
  │content_t│   4096 bytes data │
  │ refcnt=1│                   │
  └─────────┴──────────────────┘

zmq_msg_send (move 到 pipe):
  refcnt 不变（所有权转移）

worker zmq_msg_recv (从 pipe 读出):
  refcnt 不变（move 语义）

zmq_msg_move 到 result:
  refcnt 不变（所有权转移）

zmq_msg_send result (move 到另一个 pipe):
  refcnt 不变

collector zmq_msg_recv:
  refcnt 不变

zmq_msg_close:
  refcnt.sub(1) → 0
  free(content)  ← 数据在这里才释放！
```

### ZMQ_SHARED 属性

`zmq_msg_get(&msg, ZMQ_SHARED)` 返回：
- 1：消息内容可能被共享（lmsg 且 refcnt > 1，或 zclmsg）
- 0：消息内容未共享（VSM 或独占的 lmsg）

这可以用于判断是否可以安全地修改消息内容而不影响其他持有者。

### 发送端零拷贝

`zmq_msg_init_data()` 允许 ZeroMQ 直接引用应用程序缓冲区：

```c
void *my_buf = malloc(4096);
zmq_msg_init_data(&msg, my_buf, 4096, my_free_fn, hint);
zmq_msg_send(&msg, socket, 0);
/* 此时不能再访问 my_buf！ZeroMQ 拥有所有权 */
/* 发送完成后 my_free_fn 被调用 */
```

注意事项：
- 在 ffn 被调用前，应用程序不能修改或释放缓冲区
- ffn 在发送完成（对于 inproc 是接收方 close）后调用
- 如果消息被 copy，ffn 只在最后一个引用关闭时调用
- 适用于预分配的缓冲区池、内存映射文件等场景

## 性能对比

| 传递方式 | 系统调用 | 数据拷贝 | 延迟 |
|---------|---------|---------|------|
| TCP loopback | send/recv | 2次（用户→内核→用户） | ~10-20μs |
| IPC (Unix socket) | send/recv | 2次 | ~5-10μs |
| inproc (VSM) | 无 | 64B memcpy | ~0.1μs |
| inproc (LMSG move) | 无 | 64B memcpy（指针） | ~0.1μs |
| inproc (init_data) | 无 | 0 | ~0.05μs |

inproc 是最高效的线程间通信方式，特别适合高吞吐、低延迟的多线程应用。

## 延伸阅读

- [消息与引用计数](/concepts/03-message.md) — msg_t 六类型和 content_t 详细机制
- [管道与流控](/concepts/04-pipe.md) — pipepair 和 ypipe 无锁队列
- [上下文与基础设施](/concepts/01-context.md) — inproc 端点注册表
- [命令传递与邮箱](/concepts/08-command-mailbox.md) — send_bind 命令附加 pipe
- [PUSH/PULL 流水线](/examples/push-pull-pipeline.md) — 基于 TCP 的任务分发
