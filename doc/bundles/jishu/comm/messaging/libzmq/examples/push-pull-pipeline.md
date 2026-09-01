---
type: example
title: "PUSH/PULL 流水线模式"
description: "使用 PUSH/PULL 套接字实现任务分发流水线，演示负载均衡（lb_t）、公平队列（fq_t）、HWM 流控行为，包含任务分发器和工作者完整 C 代码"
tags: [libzmq, example, push, pull, pipeline, load-balancing]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmq-h-api.md, ../references/socket-base.md]
  facts: [F-006, F-007, F-075, F-087, F-088]
---

# PUSH/PULL 流水线模式

## 目标

使用 PUSH/PULL 套接字实现并行任务处理流水线：一个任务分发器将任务均匀分发给多个工作者，工作者处理后将结果发送给结果收集器。通过这个例子理解：
- PUSH 的 `lb_t` 负载均衡轮询分发
- PULL 的 `fq_t` 公平队列轮询接收
- HWM（高水位）流控如何防止内存溢出
- PUSH/PULL 的无状态特性

## 架构

```
┌──────────┐                    ┌──────────┐
│          │── task 1 ─────────►│ worker 1 │
│          │                    └────┬─────┘
│  task    │── task 2 ─────────►┌────┴─────┐
│ source   │                    │ worker 2 │── result ──►┌──────────┐
│ (PUSH)   │── task 3 ─────────►└────┬─────┘            │ result   │
│          │                    ┌────┴─────┐            │ sink     │
│          │── task 4 ─────────►│ worker 3 │── result ──►│ (PULL)   │
└──────────┘                    └──────────┘            └──────────┘
  连接 workers                      连接 sink
  (PUSH→PULL)                      (PUSH→PULL)
```

- **source（PUSH）**：均匀分发任务到所有已连接的 worker（lb_t 轮询）
- **worker（PULL + PUSH）**：PULL 公平接收任务，处理后 PUSH 发送结果
- **sink（PULL）**：公平收集所有 worker 的结果

## 完整代码

### 任务分发器（taskvent.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#endif

int main(void)
{
    void *context = zmq_ctx_new();

    /* 发送任务给 worker */
    void *sender = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(sender, "tcp://*:5557");

    /* 发送开始信号给 sink（使用 inproc 不行，sink 是独立进程） */
    void *sink = zmq_socket(context, ZMQ_PUSH);
    zmq_connect(sink, "tcp://localhost:5558");

    printf("已绑定任务分发端口 tcp://*:5557\n");
    printf("按 Enter 开始分发任务...\n");
    getchar();

    /* 发送开始信号 */
    zmq_send(sink, "0", 1, 0);

    srand((unsigned int)time(NULL));

    int total_msec = 0;
    int task_nbr;
    for (task_nbr = 0; task_nbr < 100; task_nbr++) {
        /* 随机工作量：1-100 毫秒 */
        int workload = (rand() % 100) + 1;
        total_msec += workload;

        char string[16];
        snprintf(string, sizeof(string), "%d", workload);
        zmq_send(sender, string, strlen(string), 0);
    }

    printf("共分发 100 个任务，预期总工作量: %d 毫秒\n", total_msec);

    /* 给 worker 时间发送完结果 */
    sleep_ms(1000);

    zmq_close(sink);
    zmq_close(sender);
    zmq_ctx_term(context);
    return 0;
}
```

### 工作者（taskwork.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#endif

int main(void)
{
    void *context = zmq_ctx_new();

    /* 接收任务 */
    void *receiver = zmq_socket(context, ZMQ_PULL);
    zmq_connect(receiver, "tcp://localhost:5557");

    /* 发送结果 */
    void *sender = zmq_socket(context, ZMQ_PUSH);
    zmq_connect(sender, "tcp://localhost:5558");

    printf("工作者已启动，等待任务...\n");

    while (1) {
        char buf[32];
        int rc = zmq_recv(receiver, buf, sizeof(buf) - 1, 0);
        if (rc == -1)
            break;  /* 上下文终止 */
        buf[rc] = '\0';

        int workload = atoi(buf);
        printf("处理任务: %d 毫秒\n", workload);

        /* 模拟工作 */
        sleep_ms(workload);

        /* 发送结果 */
        zmq_send(sender, buf, rc, 0);
    }

    zmq_close(receiver);
    zmq_close(sender);
    zmq_ctx_term(context);
    return 0;
}
```

### 结果收集器（tasksink.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#define sleep_ms(ms) usleep((ms) * 1000)
#endif

int64_t get_time_ms(void)
{
#ifdef _WIN32
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    int64_t t = ((int64_t)ft.dwHighDateTime << 32) | ft.dwLowDateTime;
    return (t - 116444736000000000LL) / 10000;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
#endif
}

int main(void)
{
    void *context = zmq_ctx_new();

    /* 接收结果 */
    void *receiver = zmq_socket(context, ZMQ_PULL);
    zmq_bind(receiver, "tcp://*:5558");

    printf("结果收集器已启动，等待工作者...\n");

    /* 等待开始信号 */
    char buf[32];
    zmq_recv(receiver, buf, sizeof(buf), 0);

    int64_t start_time = get_time_ms();

    /* 收集 100 个结果 */
    int task_nbr;
    for (task_nbr = 0; task_nbr < 100; task_nbr++) {
        int rc = zmq_recv(receiver, buf, sizeof(buf) - 1, 0);
        if (rc == -1)
            break;
        buf[rc] = '\0';
        if ((task_nbr / 10) * 10 == task_nbr)
            printf(":");
        else
            printf(".");
        fflush(stdout);
    }

    int64_t elapsed = get_time_ms() - start_time;
    printf("\n总共耗时: %lld 毫秒\n", (long long)elapsed);

    zmq_close(receiver);
    zmq_ctx_term(context);
    return 0;
}
```

## 编译与运行

```bash
# Linux/macOS
gcc -o taskvent taskvent.c -lzmq
gcc -o taskwork taskwork.c -lzmq
gcc -o tasksink tasksink.c -lzmq

# Windows (MSVC)
cl taskvent.c /I C:\libzmq\include C:\libzmq\lib\zmq.lib
cl taskwork.c /I C:\libzmq\include C:\libzmq\lib\zmq.lib
cl tasksink.c /I C:\libzmq\include C:\libzmq\lib\zmq.lib
```

需要先安装 libzmq 开发包：
- Ubuntu/Debian: `sudo apt-get install libzmq3-dev`
- macOS: `brew install zeromq`
- Windows: 从 [zeromq.org](https://zeromq.org/download/) 下载

运行顺序（三个终端）：
```bash
# 终端 1：启动结果收集器
./tasksink

# 终端 2：启动多个工作者（启动 2-4 个）
./taskwork &
./taskwork &
./taskwork &

# 终端 3：启动任务分发器，按 Enter 开始
./taskvent
```

## 原理解析

### PUSH 的 lb_t 负载均衡

PUSH 套接字内部持有 `lb_t`（负载均衡器），它以轮询方式向所有已连接的 PULL 套接字分发消息：
1. 新连接的 pipe 被加入轮询数组
2. `xsend()` 时，lb_t 选择 `_current` 指向的 pipe 写入
3. 写入后 `_current` 移到下一个活跃 pipe
4. 若某个 pipe 的 HWM 满了（不可写），跳过该 pipe
5. 多部分消息的所有帧发往同一个 pipe（`_more` 标志保证）

这意味着任务会均匀分配，即使工作者处理速度不同——快的工作者处理完后立即获取下一个任务。

### PULL 的 fq_t 公平队列

PULL 套接字内部持有 `fq_t`（公平队列），它以轮询方式从所有已连接的 PUSH 套接字读取消息：
1. 所有 pipe 加入公平队列数组
2. `xrecv()` 时，fq_t 从 `_current` 指向的 pipe 读取
3. 若当前 pipe 无消息，切换到下一个活跃 pipe
4. 多部分消息的所有帧从同一个 pipe 读取

### HWM 流控

PUSH/PULL 的 HWM 默认均为 1000。当 PUSH 的发送速度远超 PULL 的处理速度时：
- PUSH 端的 pipe HWM 满后，`xsend()` 返回 EAGAIN
- 阻塞发送（无 ZMQ_DONTWAIT）会等待 pipe 恢复可写
- PULL 端读取消息后，通过 `activate_write` 命令通知 PUSH 端
- 这形成了自然的背压机制

可以通过 `ZMQ_SNDHWM`/`ZMQ_RCVHWM` 调整：
```c
int hwm = 100;
zmq_setsockopt(sender, ZMQ_SNDHWM, &hwm, sizeof(hwm));
```

### 无状态特性

PUSH/PULL 是无状态的流水线模式：
- 没有"任务确认"机制
- worker 断开时，正在处理的任务会丢失（因为没有 ACK）
- PUSH 不跟踪哪个 worker 处理了哪个任务
- 如果需要可靠交付，应使用 REQ/REP 或 ROUTER/DEALER 并在应用层实现确认

### 连接顺序

PUSH/PULL 是对称的——bind/connect 的顺序不影响最终拓扑。可以先启动 worker（connect），后启动 source（bind），连接建立后消息自动流动。ZeroMQ 自动处理连接和重连。

## 延伸阅读

- [消息模式实现](../concepts/11-patterns.md) — fq_t/lb_t 算法详解
- [管道与流控](../concepts/04-pipe.md) — HWM/LWM 背压机制
- [套接字基类](../concepts/02-socket-base.md) — send/recv 骨架和 x-钩子
- [ROUTER/DEALER 异步请求-回复](router-dealer-async.md) — 需要可靠请求-回复时使用
