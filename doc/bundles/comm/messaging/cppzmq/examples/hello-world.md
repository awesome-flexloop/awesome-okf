---
type: example
title: "Hello World 示例（REQ-REP）"
description: "使用 cppzmq 实现最小 REQ/REP 回显示例，展示 context_t/socket_t/message_t/buffer 与错误处理"
tags: [cppzmq, zeromq, example, req-rep]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md]
  facts: [F-026, F-035, F-039, F-040, F-043]
---

# Hello World 示例（REQ-REP）

演示 cppzmq 最常见用法：上下文、套接字、`message_t` 与 `buffer` 两种发送方式、`optional` 错误处理。

## 服务端（REP）

```c++
#include <zmq.hpp>
#include <string>
#include <iostream>

int main()
{
    zmq::context_t ctx;
    zmq::socket_t rep(ctx, zmq::socket_type::rep);
    rep.bind("tcp://*:5555");

    while (true) {
        zmq::message_t req;
        auto r = rep.recv(req);           // 阻塞等待请求
        if (!r) continue;                 // EAGAIN（此处未用 dontwait，一般不会发生）

        std::cout << "Received: " << req.to_string() << std::endl;

        // 方式一：用 message_t
        zmq::message_t reply("World", 5);
        rep.send(reply, zmq::send_flags::none);

        // 方式二：用 buffer（不拷贝到 message_t，直接发送内存）
        // rep.send(zmq::str_buffer("World"), zmq::send_flags::none);
    }
}
```

## 客户端（REQ）

```c++
#include <zmq.hpp>
#include <iostream>

int main()
{
    zmq::context_t ctx;
    zmq::socket_t req(ctx, zmq::socket_type::req);
    req.connect("tcp://localhost:5555");

    zmq::message_t hello("Hello", 5);
    req.send(hello, zmq::send_flags::none);

    zmq::message_t reply;
    req.recv(reply);
    std::cout << "Reply: " << reply.to_string() << std::endl;
}
```

## 非阻塞发送（EAGAIN 处理）

```c++
auto s = req.send(zmq::str_buffer("Hello"), zmq::send_flags::dontwait);
if (!s) {
    // 发送队列满，EAGAIN；稍后重试
}
```

## 设置套接字选项

```c++
req.set(zmq::sockopt::linger, 0);
req.set(zmq::sockopt::rcvtimeo, 1000);
req.set(zmq::sockopt::routing_id, "client-1");
```

## 要点

- `context_t`/`socket_t` 随作用域析构自动关闭，无需手动 `zmq_close`/`zmq_ctx_term`。
- `send`/`recv` 返回 `optional`，`!r` 表示 EAGAIN；真正错误抛 `zmq::error_t`。
- `zmq::str_buffer("...")` 生成不含 `'\0'` 的 `const_buffer`，适合字面量。
