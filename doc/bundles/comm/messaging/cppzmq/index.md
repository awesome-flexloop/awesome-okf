---
type: bundle
title: "cppzmq：ZeroMQ C++ 绑定"
okf_version: "0.2"
---


# cppzmq 知识库

本知识包是 [cppzmq](https://github.com/zeromq/cppzmq)（MIT 许可证）的系统化中文源码教程，基于 cppzmq **4.11.0** header-only 源码（`external/libs/remote/cppzmq/` 目录下的 `zmq.hpp` 3010 行与 `zmq_addon.hpp` 859 行）深度阅读生成，覆盖从 RAII 资源管理到类型安全套接字选项、从 buffer 抽象到 poller 事件多路复用的完整知识体系。所有内容均溯源至 cppzmq 源码核心模块，遵循 OKF v0.2 规范，经 seven-concepts 方法论 R→I→E 三阶段流程生成。

## 核心概念篇（concepts/）

* [cppzmq 整体架构与设计目标](concepts/00-overview.md) — header-only 形态、与 libzmq 的分层、命名空间布局、C++11/14/17 兼容垫片、五大设计目标（零成本 RAII/类型安全/统一内存抽象/现代 C++ 兼容/错误显式化）。
* [context_t 上下文](concepts/01-context.md) — ctxopt 强类型选项、io_threads/max_sockets、shutdown vs close、EINTR 重试循环、移动语义、与 C API 互操作。
* [socket_t 与套接字层](concepts/02-socket.md) — socket_type 枚举、bind/connect、send/recv optional 结果、sockopt 标签机制（integral_option/array_option）、socket_ref 非拥有引用、proxy。
* [message_t 与 buffer 抽象](concepts/03-message-and-buffer.md) — 消息构造函数族、移动/禁拷贝语义、零拷贝 free_fn、const_buffer/mutable_buffer、buffer() 重载族、str_buffer/_zbuf 字面量。
* [错误处理](concepts/04-error-handling.md) — error_t 继承 std::exception、EAGAIN 与 optional 返回值分工、ZMQ_ASSERT 边界、EINTR 重试、ETERM 关停、常见错误码表。
* [poller_t 与事件多路复用](concepts/05-poller.md) — event_flags、poller_event<T> 二进制布局兼容、add/remove/modify/wait_all、active_poller_t 回调分发、poller_ref_t、选型建议。
* [multipart 高层抽象](concepts/06-multipart.md) — recv_multipart/send_multipart 迭代器接口、multipart_t 容器（类 CZMQ zmsg）、encode/decode RFC 50 单帧编码、三层抽象选型。

## 实战示例（examples/）

* [Hello World（REQ-REP）](examples/hello-world.md) — context_t + socket_t + message_t 与 buffer 两种写法、optional 错误处理、套接字选项设置。
* [多部分消息与 poller](examples/multipart-poller.md) — send_multipart/recv_multipart、multipart_t 拼装拆解、active_poller_t 回调事件循环、poller_t<T> 强类型用户数据、RFC 50 编码。

## 信源登记簿（references/）

* [zmq.hpp 文件参考](references/zmq-hpp.md) — zmq.hpp（3010 行）完整行号索引、类/函数/宏清单、关键条件编译开关、设计要点，覆盖 F-001~F-050。
* [zmq_addon.hpp 文件参考](references/zmq-addon-hpp.md) — zmq_addon.hpp（859 行）multipart_t、自由函数、active_poller_t、poller_ref_t 签名与依赖条件，覆盖 F-051~F-056。

## 信任与生命周期说明

* **status 判定依据**：全部 11 个内容文档（7 个概念 + 2 个示例 + 2 个信源登记）均 `status: stable`。内容基于对 cppzmq 4.11.0 源码（`external/libs/remote/cppzmq/` 目录）核心头文件的逐文件阅读与事实提取（56 条源码事实 F-001~F-056），经 seven-concepts 方法论 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。cppzmq 核心架构（RAII 三巨头/sockopt 标签类型/buffer 抽象/poller_t 模板参数）自 4.x 以来保持稳定，新 API 不断添加但核心设计不变；该日期作为针对未来大版本（如 5.x 引入 breaking change）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。当前全部文档 `verified.by` 为 `process:v-pending`，待 V 阶段核验。

本知识包共收录 11 个内容文档（7 个概念 + 2 个示例 + 2 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。R 阶段事实与 I 阶段洞察保留在 `spec/facts.md` 与 `spec/insights.md`。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/index
log
```
