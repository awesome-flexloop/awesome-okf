---
type: example
title: "PUB/SUB 主题订阅与过滤"
description: "使用 PUB/SUB 套接字实现主题广播，演示 ZMQ_SUBSCRIBE 前缀匹配、trie/mtrie 双端过滤、多部分消息中的主题帧，包含天气更新发布者和订阅者完整 C 代码"
tags: [libzmq, example, pub, sub, subscribe, filtering, trie, mtrie]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [../references/zmq-h-api.md, ../references/socket-base.md]
  facts: [F-006, F-007, F-071, F-072, F-073, F-074, F-092, F-093, F-047]
---

# PUB/SUB 主题订阅与过滤

## 目标

使用 PUB/SUB 套接字实现主题广播系统：发布者发送带主题前缀的天气更新，订阅者通过 `ZMQ_SUBSCRIBE` 订阅感兴趣的主题。通过这个例子理解：
- `ZMQ_SUBSCRIBE`/`ZMQ_UNSUBSCRIBE` 前缀匹配
- SUB 端 `trie_t` 本地过滤
- PUB 端 `mtrie_t` 智能分发
- 订阅消息如何作为 SUBSCRIBE 命令帧传播
- 多部分消息中主题帧的作用

## 架构

```
┌──────────┐                         ┌──────────┐
│          │══ "US.*" (匹配) ═══════►│ sub: US  │
│  weather │                         └──────────┘
│  pub     │── "US.CA.*" ──────────►┌──────────┐
│ (PUB)    │                         │ sub: CA  │
│          │══ "FR.*" (不匹配) ╳     └──────────┘
│          │                         ┌──────────┐
│          │── "US.NY 72F" ────────►│ sub: US  │
└──────────┘                         └──────────┘
     ▲
     │ SUBSCRIBE 命令帧
     │（从 SUB 上行到 PUB）
```

## 完整代码

### 天气发布者（wuserver.c）

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

/* 随机返回某个美国邮编 */
static const char *zipcodes[] = {
    "10001", "10002", "10003",  /* 纽约 */
    "90001", "90002", "90003",  /* 洛杉矶 */
    "94101", "94102", "94103",  /* 旧金山 */
    "60601", "60602",           /* 芝加哥 */
    "77001", "77002",           /* 休斯顿 */
};
#define N_ZIPCODES (sizeof(zipcodes) / sizeof(zipcodes[0]))

int main(int argc, char *argv[])
{
    void *context = zmq_ctx_new();
    void *publisher = zmq_socket(context, ZMQ_PUB);

    /* 设置 HWM 防止慢消费者导致内存溢出 */
    int sndhwm = 10000;
    zmq_setsockopt(publisher, ZMQ_SNDHWM, &sndhwm, sizeof(sndhwm));

    const char *bind_addr = "tcp://*:5556";
    if (argc > 1)
        bind_addr = argv[1];

    int rc = zmq_bind(publisher, bind_addr);
    if (rc != 0) {
        printf("绑定失败: %s\n", zmq_strerror(zmq_errno()));
        return 1;
    }

    printf("天气发布者已启动: %s\n", bind_addr);
    printf("按 Ctrl+C 停止\n");

    srand((unsigned int)time(NULL));

    while (1) {
        /* 随机选择邮编、温度、湿度 */
        const char *zipcode = zipcodes[rand() % N_ZIPCODES];
        int temperature = (rand() % 80) - 10;  /* -10 ~ 69 °F */
        int relhumidity = rand() % 60 + 20;    /* 20 ~ 79 % */

        /* 使用多部分消息：第一帧=主题(邮编)，第二帧=数据 */
        zmq_msg_t topic_msg;
        zmq_msg_init_size(&topic_msg, strlen(zipcode));
        memcpy(zmq_msg_data(&topic_msg), zipcode, strlen(zipcode));

        char update[64];
        int len = snprintf(update, sizeof(update),
                           "%d %d", temperature, relhumidity);

        zmq_msg_t data_msg;
        zmq_msg_init_size(&data_msg, len);
        memcpy(zmq_msg_data(&data_msg), update, len);

        /* 发送多部分消息 */
        zmq_msg_send(&topic_msg, publisher, ZMQ_SNDMORE);
        zmq_msg_send(&data_msg, publisher, 0);

        zmq_msg_close(&topic_msg);
        zmq_msg_close(&data_msg);

        /* 每秒约 100 条消息 */
        sleep_ms(10);
    }

    zmq_close(publisher);
    zmq_ctx_term(context);
    return 0;
}
```

### 天气订阅者（wuclient.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    void *context = zmq_ctx_new();
    void *subscriber = zmq_socket(context, ZMQ_SUB);

    const char *connect_addr = "tcp://localhost:5556";
    const char *filter = "";

    if (argc >= 2)
        connect_addr = argv[1];
    if (argc >= 3)
        filter = argv[2];

    int rc = zmq_connect(subscriber, connect_addr);
    if (rc != 0) {
        printf("连接失败: %s\n", zmq_strerror(zmq_errno()));
        return 1;
    }

    /* 必须在 connect 之后设置订阅过滤 */
    rc = zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE,
                        filter, strlen(filter));
    if (rc != 0) {
        printf("设置订阅失败: %s\n", zmq_strerror(zmq_errno()));
        return 1;
    }

    if (filter[0] == '\0')
        printf("订阅所有消息\n");
    else
        printf("订阅主题前缀: \"%s\"\n", filter);

    int update_nbr;
    long total_temp = 0;

    for (update_nbr = 0; update_nbr < 100; update_nbr++) {
        /* 读取主题帧 */
        char topic[32];
        rc = zmq_recv(subscriber, topic, sizeof(topic) - 1, 0);
        if (rc == -1)
            break;
        topic[rc] = '\0';

        /* 检查是否有后续帧 */
        int more = 0;
        size_t more_size = sizeof(more);
        zmq_getsockopt(subscriber, ZMQ_RCVMORE, &more, &more_size);

        /* 读取数据帧 */
        char data[64];
        if (more) {
            rc = zmq_recv(subscriber, data, sizeof(data) - 1, 0);
            if (rc == -1)
                break;
            data[rc] = '\0';
        } else {
            strcpy(data, "N/A");
        }

        int temperature = atoi(data);
        total_temp += temperature;

        printf("[%s] %s (temp=%d)\n", topic, data, temperature);
    }

    if (update_nbr > 0) {
        printf("收到 %d 条更新，平均温度: %d°F\n",
               update_nbr, (int)(total_temp / update_nbr));
    }

    zmq_close(subscriber);
    zmq_ctx_term(context);
    return 0;
}
```

### 多主题订阅示例（multi-sub.c）

```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    void *context = zmq_ctx_new();
    void *subscriber = zmq_socket(context, ZMQ_SUB);
    zmq_connect(subscriber, "tcp://localhost:5556");

    /* 订阅多个主题前缀 */
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "1000", 4);  /* 纽约邮编 */
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "9410", 4);  /* 旧金山邮编 */

    printf("订阅主题: 1000* (纽约), 9410* (旧金山)\n");

    int count = 0;
    while (count < 50) {
        char topic[32], data[64];
        int rc = zmq_recv(subscriber, topic, sizeof(topic) - 1, 0);
        if (rc == -1) break;
        topic[rc] = '\0';

        int more = 0;
        size_t optlen = sizeof(more);
        zmq_getsockopt(subscriber, ZMQ_RCVMORE, &more, &optlen);

        if (more) {
            rc = zmq_recv(subscriber, data, sizeof(data) - 1, 0);
            data[rc] = '\0';
        }

        printf("[%s] %s\n", topic, data);
        count++;
    }

    /* 取消订阅 */
    zmq_setsockopt(subscriber, ZMQ_UNSUBSCRIBE, "1000", 4);
    printf("已取消订阅 1000*\n");

    zmq_close(subscriber);
    zmq_ctx_term(context);
    return 0;
}
```

## 编译与运行

```bash
# Linux/macOS
gcc -o wuserver wuserver.c -lzmq
gcc -o wuclient wuclient.c -lzmq
gcc -o multi-sub multi-sub.c -lzmq

# 运行
./wuserver                    # 终端 1：启动发布者
./wuclient "" 5556 ""         # 终端 2：订阅所有消息
./wuclient "" 5556 "9410"     # 终端 3：只订阅旧金山（9410开头）
./multi-sub                   # 终端 4：订阅多个主题
```

**注意**：SUB 必须先 connect 再 setsockopt(ZMQ_SUBSCRIBE)。订阅是前缀匹配，不是精确匹配。订阅空字符串 `""` 接收所有消息。

## 原理解析

### 前缀匹配

ZMQ_SUBSCRIBE 使用**前缀匹配**，不是通配符匹配：
- 订阅 `"1000"` 匹配 `"10001"`、`"10002"`、`"10003"`（所有以 1000 开头的主题）
- 订阅 `"9410"` 匹配 `"94101"`、`"94102"`、`"94103"`
- 订阅 `""`（空字符串）匹配所有消息
- 可以多次调用 ZMQ_SUBSCRIBE 添加多个订阅前缀

匹配逻辑在 `xsub_t::match()` 中使用 `trie_t::check()` 检查消息前缀是否匹配至少一个订阅。

### trie_t：SUB 端本地过滤

SUB 套接字内部使用 `trie_t`（基数前缀树）存储所有订阅前缀（F-074, F-092）：
- 每个节点表示前缀中的一个字节
- 节点的 `_refcnt > 0` 表示该位置是一个订阅终止点
- 单子节点时用 `_one` 指针优化内存，多子节点时用 `_many` 数组
- `check(data, size)` 沿消息前导字节遍历 trie，若到达任何 refcnt > 0 的节点则匹配

即使 PUB 端已经做了过滤，SUB 端仍保留 trie 作为二次过滤（防御性检查）。这是因为旧版本 PUB 可能不支持服务端过滤。

### mtrie_t：PUB 端智能分发

PUB（实际是 XPUB）使用 `mtrie_t`（多值前缀树）将订阅前缀映射到所有订阅了该前缀的 pipe（F-073, F-093）：
- 每个终止节点关联一组 `pipe_t*`（而非布尔值）
- 发送消息时，`match()` 对所有匹配前缀的 pipe 调用回调
- 只有匹配的 pipe 会收到消息（通过 `dist_t::send_to_matching()`）

这是双端过滤协作的关键：PUB 端通过 mtrie 避免向不感兴趣的 SUB 发送消息，节省网络带宽。

### 订阅传播

当 SUB 调用 `zmq_setsockopt(ZMQ_SUBSCRIBE, prefix)` 时：
1. SUB 端 xsub_t 将 prefix 加入本地 trie
2. xsub_t 通过 `dist_t` 向上游 PUB 发送一个 SUBSCRIBE 命令帧
3. 命令帧通过 pipe 传递，其 flags 设置 `subscribe=12`（F-047）
4. PUB 端（XPUB）收到命令帧后，在 mtrie 中为该 pipe 添加前缀映射
5. 后续匹配该前缀的消息只发送给该 pipe

取消订阅同理，发送 CANCEL 命令帧（flags=`cancel=16`），PUB 从 mtrie 中移除映射。

### 多部分消息的主题帧

PUB/SUB 的订阅匹配只检查**第一帧**（主题帧）的前缀：
- 发布者使用 `ZMQ_SNDMORE` 发送多部分消息
- 第一帧是主题（如邮编），后续帧是数据
- SUB 的 trie 只匹配第一帧
- 订阅者必须接收所有帧（使用 `ZMQ_RCVMORE` 判断）

### HWM 与慢消费者

PUB/SUB 的 HWM 行为与 PUSH/PULL 不同：
- 当 SUB 处理太慢导致 pipe HWM 满时，PUB **静默丢弃**消息（不阻塞）
- 这是因为 PUB/SUB 是"尽力而为"的广播模型
- 可以通过 `ZMQ_SNDHWM` 设置较小的值加速丢弃，或使用 XPUP 的 `ZMQ_XPUB_VERBOSE` 监控订阅状态

### 连接建立时的消息丢失

SUB 在连接建立和握手完成之前发送的消息会丢失。解决方案：
1. 等待 SUB 就绪后再开始发布（使用 XPUB/XSUB + REQ/REP 同步）
2. 使用 `ZMQ_IMMEDIATE` 选项避免向未就绪连接排队
3. 在应用层实现"快照+增量"模式（先获取当前状态，再订阅更新）

## 延伸阅读

- [消息模式实现](../concepts/11-patterns.md) — trie/mtrie 前缀树和 dist 分发算法
- [编解码与帧格式](../concepts/12-encoder-decoder.md) — SUBSCRIBE/CANCEL 命令帧格式
- [管道与流控](../concepts/04-pipe.md) — HWM 流控和 conflate 模式
- [ZMTP 协议引擎](../concepts/06-zmtp-engine.md) — 命令帧在握手后传递
- [PUSH/PULL 流水线](push-pull-pipeline.md) — 另一种消息分发模式
