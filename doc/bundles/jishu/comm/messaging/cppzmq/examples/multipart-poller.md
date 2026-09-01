---
type: example
title: "多部分消息与 poller 示例"
description: "使用 send_multipart/recv_multipart、multipart_t 以及 active_poller_t 实现事件驱动的多帧消息处理"
tags: [cppzmq, zeromq, example, multipart, poller, active-poller]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: [/references/zmq-hpp.md, /references/zmq-addon-hpp.md]
  facts: [F-046, F-047, F-051, F-052, F-053, F-055, F-056]
---

# 多部分消息与 poller 示例

展示三层多部分抽象（自由函数 / `multipart_t` / `encode-decode`）与 `active_poller_t` 回调式事件循环。需包含 `zmq_addon.hpp`。

## 1. 用自由函数收发多部分

```c++
#include <zmq_addon.hpp>

// 发送
zmq::socket_t sock(ctx, zmq::socket_type::dealer);
std::vector<zmq::const_buffer> frames = {
    zmq::str_buffer("address-frame"),
    zmq::str_buffer("body")
};
auto r = zmq::send_multipart(sock, frames);
if (!r) { /* EAGAIN */ }

// 接收到 vector
std::vector<zmq::message_t> parts;
auto n = zmq::recv_multipart(sock, std::back_inserter(parts));
if (n) {
    for (auto& m : parts) { /* m.data(), m.size() */ }
}
```

## 2. 用 multipart_t 拼装/拆解

```c++
zmq::multipart_t mp;
mp.addstr("address-frame");
mp.addstr("body");
mp.addtyp<uint32_t>(42);          // 加入 4 字节定长类型

mp.send(sock);                    // 发送后自动 clear()

zmq::multipart_t received(sock);  // 构造即接收
auto addr = received.popstr();
auto body = received.popstr();
auto code = received.poptyp<uint32_t>();
```

`multipart_t` 内部是 `std::deque<message_t>`，移动语义、禁拷贝；`clone()` 可深拷贝。

## 3. active_poller_t 事件循环

```c++
#include <zmq_addon.hpp>

zmq::context_t ctx;
zmq::socket_t receiver(ctx, zmq::socket_type::pull);
receiver.bind("inproc://example");
receiver.set(zmq::sockopt::rcvtimeo, 100);

zmq::active_poller_t poller;
poller.add(receiver, zmq::event_flags::pollin,
           [&receiver](zmq::event_flags ev) {
    if (ev & zmq::event_flags::pollin) {
        std::vector<zmq::message_t> parts;
        zmq::recv_multipart(receiver, std::back_inserter(parts));
        // 处理 parts...
    }
});

while (true) {
    poller.wait(std::chrono::milliseconds{100});
    // 超时或无事件时返回 0，可做其他工作
}
```

## 4. poller_t<T> 携带自定义用户数据

```c++
struct Session { int id; };
Session s1{1}, s2{2};

zmq::poller_t<Session> poller;
poller.add(sock1, zmq::event_flags::pollin, &s1);
poller.add(sock2, zmq::event_flags::pollin, &s2);

std::vector<zmq::poller_event<Session>> events(4);
size_t n = poller.wait_all(events, std::chrono::milliseconds{-1});
for (size_t i = 0; i < n; ++i) {
    auto& ev = events[i];
    // ev.user_data->id 直接取回原类型 Session*
}
```

## 5. 单帧编码（RFC 50）

把多帧打包成单个 `message_t` 传输/存储：

```c++
zmq::multipart_t mp;
mp.addstr("A"); mp.addstr("BB"); mp.addstr("CCC");
zmq::message_t packed = mp.encode();       // 或 zmq::encode(mp)

zmq::multipart_t restored = zmq::multipart_t::decode(packed);
```

## 要点

- `send_multipart`/`recv_multipart` 零额外抽象，适合已有容器。
- `multipart_t` 提供类 CZMQ zmsg 的丰富 push/pop/peek API。
- `active_poller_t` 用 `std::function` 回调，handler 在 `wait` 内被自动调用；`poller_t<T>` 则保留手动分发但提供强类型 `user_data`。
- Draft API 需在包含头前 `#define ZMQ_BUILD_DRAFT_API` 或通过编译选项启用。
