---
okf_version: "0.2"
type: "concept"
title: "加密通信机制"
description: "ResponseManager RSA+AES加密的连接信息回传通道、Response事件机制、KernelChannel枚举、launcher通信协议"
tags: [response-manager, encryption, rsa, aes, launcher, zmq, connection-info]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: response-manager
    resource: "/references/response-manager-source.md"
    title: "ResponseManager源码"
---

# 加密通信机制

远程内核启动后，kernel进程（ipykernel/IRkernel/Toree）会在远端监听5个ZMQ端口。EG需要知道这些端口才能将WebSocket消息代理到内核。ResponseManager就是解决"如何安全地将远端端口信息传回EG"这一问题的核心组件。

## 为什么需要加密回传

本地内核场景下，Jupyter通过本地文件系统共享connection file（JSON文件）。远程场景下：
- 内核运行在不同机器/容器中，无法共享文件系统
- 端口信息如果明文传输可能被窃听，导致未授权访问内核
- 需要一种安全、可靠的方式回传连接信息

ResponseManager通过 **RSA+AES混合加密** + **TCP回传通道** 解决了这个问题。

## 加密方案设计

采用经典的混合加密方案：
- **RSA**（非对称加密）：加密AES密钥。RSA加密慢但不需要预先共享密钥
- **AES**（对称加密）：加密实际的连接信息数据。AES加密快，适合加密大量数据
- 这样既避免了预共享密钥的问题，又保证了加密性能

## ResponseManager 工作原理

### 初始化 [F-092,F-095]

```
EG启动时：
1. 生成RSA 1024位密钥对（_private_key, _public_key）
2. 创建TCP socket绑定到response_port（默认8877）
3. listen(128)，settimeout(0.005s)
4. 启动PeriodicCallback（0.1秒间隔）轮询连接
```

公钥以PEM格式导出，去除头尾标记和换行符后得到纯Base64字符串 [F-093]。

### 通信流程

完整的连接信息回传流程：

```
EG (ResponseManager)                    Launcher (远程主机/容器内)
    │                                        │
    │  1. 生成RSA密钥对                       │
    │  2. 启动TCP监听(8877)                   │
    │                                        │
    │  3. 启动命令携带：                      │
    │     --response-address=eg:8877         │
    │     --public-key=<RSA公钥Base64>        │
    │     --port-range=40000..50000          │
    │     --kernel-id=<UUID>                 │
    │ ──────────────────────────────────────→ │
    │                                        │ 4. 启动kernel进程
    │                                        │ 5. kernel绑定5个ZMQ端口
    │                                        │ 6. 生成随机AES-256密钥
    │                                        │ 7. RSA公钥加密AES密钥
    │                                        │ 8. AES-CBC加密连接信息JSON
    │                                        │ 9. TCP连接 eg:8877
    │                                        │ 10. 发送加密payload
    │ ←────────────────────────────────────── │
    │ 11. 接收payload                         │
    │ 12. RSA私钥解密→AES密钥                 │
    │ 13. AES解密→连接信息JSON                │
    │ 14. 根据kernel_id触发Response事件       │
    │                                        │
    │ 15. ProcessProxy收到连接信息            │
    │ 16. 建立SSH隧道（如需）                 │
    │ 17. 连接ZMQ端口                         │
    │                                        │
```

### Payload格式 [F-099]

**v1格式（当前标准）**：
```json
{
  "version": 1,
  "key": "<Base64(RSA(AES_KEY))>",
  "conn_info": "<Base64(AES(JSON(connection_info)))>"
}
```

其中 connection_info 包含：
```json
{
  "kernel_id": "<UUID>",
  "shell_port": 40001,
  "iopub_port": 40002,
  "stdin_port": 40003,
  "hb_port": 40004,
  "control_port": 40005,
  "ip": "0.0.0.0",
  "key": "<ZMQ session key>",
  "transport": "tcp",
  "signature_scheme": "hmac-sha256"
}
```

**v0格式（遗留兼容）** [F-098]：
- 使用kernel_id前16字节作为AES密钥（MD5 hash）
- 直接Base64+AES加密，没有RSA层
- 仍被支持以兼容旧版launcher

### 连接处理循环 [F-097]

`_process_connections()` 在PeriodicCallback中持续运行：

```python
def _process_connections(self):
    try:
        while True:
            connection, addr = self._response_socket.accept()
            data = b""
            while True:
                buffer = connection.recv(1024)
                if buffer:
                    data += buffer
                else:
                    break  # 连接关闭，数据接收完毕
            connection.close()
            if data:
                connection_info = self._decode_payload(data)
                self._post_connection(connection_info)
    except socket.timeout:
        pass  # 0.005秒超时，非阻塞
```

关键点：
- 非阻塞accept（0.005秒超时），不会阻塞IOLoop
- 一次连接发送完整payload（recv直到连接关闭）
- 接收后立即关闭连接，解密并分发

### 事件分发机制 [F-100,F-101,F-102]

ResponseManager使用 `_response_registry` 字典维护kernel_id到Response事件的映射：

```python
# RemoteProcessProxy构造时注册
response_manager.register_event(kernel_id)

# confirm_remote_startup中等待
connection_info = await response_manager.get_connection_info(kernel_id)
# → 内部 await asyncio.wait_for(response.wait(), timeout=0.005)

# 收到连接信息时触发
response.response = connection_info  # setter自动调用event.set()
```

## Response 事件类 [F-103]

```python
class Response(asyncio.Event):
    def __init__(self):
        super().__init__()
        self._response = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value
        self.set()  # 设置值时自动触发事件
```

扩展了asyncio.Event，在设置response值时自动调用set()唤醒等待的协程。这种设计非常优雅——等待方只需要await response.wait()，数据到达时自动被唤醒。

## KernelChannel 枚举 [F-104]

定义了内核通信的6个通道：

| 枚举值 | 字符串 | 类型 | 说明 |
|--------|-------|------|------|
| SHELL | "shell" | ZMQ标准通道 | 代码执行请求/响应 |
| IOPUB | "iopub" | ZMQ标准通道 | 输出广播（stdout/stderr/display） |
| STDIN | "stdin" | ZMQ标准通道 | 标准输入请求 |
| HB | "hb" | ZMQ标准通道 | 心跳检测 |
| CONTROL | "control" | ZMQ标准通道 | 控制消息（shutdown/restart） |
| EG_COMM | "eg_comm" | EG扩展通道 | 向launcher发送中断通知 |

EG_COMM不是标准ZMQ通道，是EG扩展的通信通道，用于向远端launcher发送中断等控制通知。

## 连接建立后的通信

ResponseManager只负责初始连接信息的回传。连接建立后，后续通信通过ZMQ通道进行：

1. EG通过SSH隧道连接到远端5个ZMQ端口（如果是远程场景）
2. ZMQChannelsHandler建立WebSocket连接
3. 客户端消息通过WebSocket→EG→ZMQ隧道→远端kernel
4. kernel输出通过ZMQ→SSH隧道→EG→WebSocket→客户端

ResponseManager在初始握手完成后不再参与后续通信。
