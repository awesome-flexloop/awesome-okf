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

```{toctree}
:hidden:
:maxdepth: 7

messaging/index
networking/index
serialization/index
```
