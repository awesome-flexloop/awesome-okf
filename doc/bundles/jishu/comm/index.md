---
okf_version: "0.2"
type: group
title: "📡 通信与网络生态"
description: "消息通信与远程控制生态——ZeroMQ 消息栈、分布式任务队列、SSH 与网络自动化、Protocol Buffers 数据序列化"
---

# 📡 通信与网络生态

本域存放通信与网络相关的知识包，覆盖 ZeroMQ 消息通信生态（libzmq/cppzmq/pyzmq/dramatiq）、Python SSH/远程控制生态与 Protocol Buffers 数据序列化生态，从底层传输协议、语言绑定、结构化数据编码到高层自动化框架，构成"消息传递 + 远程控制 + 数据序列化"的完整通信范式谱。

## 域内分组导航

| 分组 | 一句话简介 |
|------|-----------|
| [📨 消息通信生态](messaging/index.md) | ZeroMQ 消息通信与分布式任务队列——libzmq 核心库、C++/Python 绑定、dramatiq 任务队列 |
| [🌐 SSH 与远程控制](networking/index.md) | Python SSH/远程控制生态——paramiko/fabric/netmiko/asyncssh/pexpect/scrapli |
| [📦 数据序列化生态](serialization/index.md) | Protocol Buffers 序列化生态——protobuf 主仓（双内核/protoc/Editions）与 protobuf-ci（CI 动作与五层缓存） |
| [🔌 FFI 外部函数接口](ffi/index.md) | FFI 跨语言互操作机制系统教程——Python ctypes/cffi、JNI、P/Invoke、Rust extern、Go cgo 各语言实现与 RPC/IPC/序列化相邻机制对比 |
| [📜 IDL 接口描述语言](idl/index.md) | IDL 接口描述语言系统教程——CORBA/COM/Protobuf/Thrift/gRPC/GraphQL Schema 主流规范、横向对比、工具链与现代格式关系辨析 |
| [📺 Apache TVM FFI](tvm-ffi/index.md) | TVM FFI 跨语言调用层完整教程——C++ 核心 API、类型系统、反射机制、DLPack 集成与 Python 绑定 |
| [🧭 接口·API·ABI·协议](interface-api-abi/index.md) | Interface/API/ABI/Protocol 四大基础概念辨析——定义、层次关系、稳定性规则与软件边界设计概念坐标系 |

```{toctree}
:hidden:
:maxdepth: 7

messaging/index
networking/index
serialization/index
ffi/index
idl/index
tvm-ffi/index
interface-api-abi/index
```
