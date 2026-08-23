---
type: Reference
title: "base/websocket.py 与 WebSocket 基源码信源"
description: "WebSocketMixin WebSocket 基类、ZMQ 消息桥接、会话管理与跨域检查"
tags: [websocket, zmq, kernel-channels, real-time]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: websocket-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/base/websocket.py
    title: jupyter_server/base/websocket.py
  - id: zmqhandlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/base/zmqhandlers.py
    title: jupyter_server/base/zmqhandlers.py
---

# base/websocket.py WebSocket 基源码信源

## WebSocketMixin (websocket.py L17)

所有 Jupyter Server WebSocket Handler 的 Mixin 基类。

**核心功能**：
- 来源检查（Origin/Host 验证）
- 认证检查（Token/Cookie）
- WebSocket 子协议协商
- 会话管理
- CORS 策略应用

**核心方法**：
| 方法 | 说明 |
|------|------|
| `check_origin(origin)` | WebSocket 跨域来源检查 |
| `get_compression_options()` | WebSocket 压缩选项（默认关闭，避免二进制消息问题） |
| `open(*args, **kwargs)` | WebSocket 连接建立 |
| `on_message(message)` | 收到前端消息 |
| `on_close()` | 连接关闭清理 |
| `write_message(message, binary=False)` | 发送消息到前端 |

## ZMQ WebSocket 处理 (zmqhandlers.py)

ZMQChannelsHandler 相关 WebSocket 处理器：
- `AuthenticatedZMQStreamHandler`: 带认证的 ZMQ Stream Handler
- `ZMQChannelsHandler`: ZMQ 通道 WebSocket Handler，管理五个通道消息路由

**消息路由**：
- Shell/IOPub/Stdin/Control/HB 五通道独立处理
- 使用 jupyter_client.session.Session 进行消息序列化
- 支持消息签名验证
