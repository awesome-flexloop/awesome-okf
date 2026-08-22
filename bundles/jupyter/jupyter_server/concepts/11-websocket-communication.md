---
type: Concept
title: "WebSocket 通信"
description: "WebSocket 连接基类、内核频道桥接（ZMQ ↔ WS）、消息代理、终端 WS 与心跳机制"
tags: [websocket, zmq, kernel-channels, messaging, real-time, proxy]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: websocket
    resource: /references/websocket-base-source.md
    title: base/websocket.py 源码信源
---

# WebSocket 通信

WebSocket 是 Jupyter Server 实现实时双向通信的核心机制，用于内核消息推送、终端交互、实时协作等场景。Jupyter Server 提供了统一的 WebSocket 基类和内核频道桥接层。

## WebSocket 基类：JupyterWebsocketMixin

`JupyterWebsocketMixin`（在 `base/websocket.py` 中）为所有 WebSocket Handler 提供通用基础设施。

### 核心功能

| 功能 | 说明 |
|------|------|
| 认证继承 | 复用 HTTP 请求的认证信息（Cookie/Token） |
| Origin 检查 | WebSocket 握手时检查 Origin 头防跨站 |
| Session 管理 | 基于 jupyter_client.Session 的消息序列化/签名 |
| 连接追踪 | 记录活跃 WebSocket 连接数 |
| 子协议协商 | 处理 `v1.kernel.websocket.jupyter.org` 等子协议 |
| CORS 支持 | WebSocket 跨域配置 |
| 消息队列 | 连接建立前的消息缓冲 |

### WebSocketHandler 连接流程

```
客户端发起 WebSocket 握手 (Upgrade: websocket)
  │
  ├── 1. 认证检查（复用 AuthenticatedHandler 逻辑）
  ├── 2. Origin 检查（should_check_origin）
  ├── 3. 检查内核是否存在
  ├── 4. 协商子协议
  ├── 5. set_default_headers()
  └── 6. 连接建立 → open() 回调
        │
        ▼
    消息循环
        ├── on_message(msg): 客户端 → 服务端消息
        ├── on_ping/pong: 心跳检测
        └── on_close(): 连接关闭清理
```

## 内核频道桥接：KernelWebsocketHandler

`KernelWebsocketHandler`（在 `services/kernels/websocket.py`）将 WebSocket 与内核 ZMQ 通道桥接：

```
浏览器 (WebSocket)
    │  ↓ execute_request
    │  ↑ execute_reply/stream/display_data/status
    ▼
KernelWebsocketHandler
    │  ↓ ZMQ messages (multipart)
    │  ↑ ZMQ messages (multipart)
    ▼
Kernel (ZMQ channels)
    ├── Shell: 执行请求/回复
    ├── IOPub: 输出广播
    ├── Stdin: 输入请求
    └── Control: 控制命令
```

### 消息格式

WebSocket 上的消息遵循 Jupyter 消息协议，以 JSON 数组形式编码：

```json
[
  channel,        // "shell" | "iopub" | "stdin" | "control"
  header,         // 消息头（msg_id, msg_type, session, date, version, username）
  parent_header,  // 父消息头（请求-响应关联）
  metadata,       // 元数据
  content,        // 消息内容（msg_type 相关）
  buffers         // 二进制缓冲区列表（二进制数据如图片）
]
```

### 核心方法

| 方法 | 说明 |
|------|------|
| `open(pk)` | WebSocket 连接建立，连接到内核 ZMQ 通道 |
| `on_message(message)` | 收到 WS 消息 → 转发到对应 ZMQ 通道 |
| `on_close()` | 连接关闭，清理 ZMQ 订阅 |
| `_on_zmq_reply(stream, msg_list)` | ZMQ 消息到达 → 转发到 WebSocket |
| `write_message(message, binary=False)` | 发送消息到客户端 |

### ZMQ 通道订阅

连接建立后，Handler 订阅 IOPub 和 Stdin 通道：

```python
async def open(self, kernel_id):
    self.kernel_id = kernel_id
    self.session = self.kernel_manager.session
    # 订阅 IOPub（广播输出）
    self.iopub_stream = self.kernel_manager.connect_iopub()
    self.iopub_stream.on_recv(self._on_zmq_reply)
    # 订阅 Stdin（输入请求）
    self.stdin_stream = self.kernel_manager.connect_stdin()
    self.stdin_stream.on_recv(self._on_zmq_reply)
```

### 连接缓冲

内核启动过程中（`starting` 状态），WebSocket 连接会缓冲客户端发送的消息，等内核就绪后再转发，避免消息丢失。

## 终端 WebSocket：TerminalsAPIHandler

终端通过 WebSocket 传输原始终端 I/O 数据：

```
浏览器 (xterm.js)
    │  ↓ 键盘输入 (stdin)
    │  ↑ 终端输出 (stdout/stderr)
    ▼
TerminalWSHandler
    │  ↓ pty 输入
    │  ↑ pty 输出
    ▼
PTY 进程（bash/zsh/cmd.exe）
```

终端 WebSocket 消息是原始文本（非 JSON），直接对应终端输入/输出。支持二进制消息用于终端 resize 控制。

## 网关 WebSocket：GatewayWebSocketHandler

当使用 Gateway（远程内核）时，`GatewayWebSocketHandler` 直接将 WebSocket 连接代理到远程网关的 WebSocket 端点：

```
浏览器 → Server → Gateway WebSocket → 远程 Kernel
```

网关模式下，Server 不直接管理内核进程，而是作为 WebSocket 代理转发消息。

## 子协议（Subprotocols）

WebSocket 握手时通过 `Sec-WebSocket-Protocol` 头协商子协议：

| 子协议 | 用途 |
|--------|------|
| `v1.kernel.websocket.jupyter.org` | 内核频道协议 v1 |
| `base64.kernel.websocket.jupyter.org` | Base64 编码的二进制消息 |
| （无） | 终端原始数据 |

## 心跳与连接保活

- WebSocket 协议自带 ping/pong 帧用于检测连接存活
- ZMQ HB（Heartbeat）通道独立检测内核进程存活
- 客户端定期发送 ping，服务端响应 pong
- 连接超时后自动清理，防止僵尸连接

## 消息签名验证

通过 jupyter_client.Session 的签名机制，所有消息使用 HMAC 签名防止篡改：

- 密钥存储在 connection 文件的 `key` 字段
- 签名算法：HMAC-SHA256
- 签名位置：消息头的 `signature` 字段
- `Session.send()` 自动签名，`Session.deserialize()` 自动验证

## 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `KernelWebsocketConnection.kernel_ws_protocol` | '' | 强制使用的 WS 子协议 |
| `KernelWebsocketConnection.zmq_buffers_max_bytes` | 10MB | ZMQ 消息缓冲上限 |
| `KernelWebsocketConnection.kernel_timeout` | 60 | 内核启动超时（秒） |

## 自定义 WebSocket Handler

```python
from jupyter_server.base.websocket import WebSocketHandler

class MyWSHandler(WebSocketHandler):
    """自定义实时通知 WebSocket"""

    @web.authenticated
    async def open(self):
        self.log.info("WS connection opened")
        # 订阅通知事件
        self.application.event_bus.subscribe(self.on_event)

    async def on_message(self, message):
        # 处理客户端消息
        await self.write_message(f"Echo: {message}")

    def on_event(self, event):
        # 推送事件到客户端
        self.write_message(json.dumps(event))

    def on_close(self):
        self.application.event_bus.unsubscribe(self.on_event)
        self.log.info("WS connection closed")
```

## 常见问题

### WebSocket 连接失败

1. **认证问题**：确保请求携带有效的 token/cookie
2. **Origin 被拒绝**：检查 `allow_origin` 配置
3. **代理超时**：反向代理（nginx）可能需要配置更长的超时时间
4. **防火墙**：确保 WebSocket 端口可访问

### Nginx 反向代理 WebSocket 配置

```nginx
location / {
    proxy_pass http://localhost:8888;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400s;  # 长超时，适配长连接
}
```

## 相关概念

- [内核管理](08-kernel-management.md) — 内核 ZMQ 通道详解
- [网关客户端](12-gateway-client.md) — 远程内核代理
- [认证授权系统](05-auth-system.md) — WebSocket 认证机制
