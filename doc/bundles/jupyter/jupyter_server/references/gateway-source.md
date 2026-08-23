---
type: Reference
title: "gateway/ 网关客户端源码信源"
description: "GatewayClient 远程内核代理、GatewayKernelManager、WebSocket 转发与多用户企业网关集成"
tags: [gateway, enterprise-gateway, remote-kernel, websocket-proxy, kernel-gateway]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: gateway-client-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/gateway_client.py
    title: jupyter_server/gateway/gateway_client.py
  - id: managers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/managers.py
    title: jupyter_server/gateway/managers.py
  - id: handlers-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/handlers.py
    title: jupyter_server/gateway/handlers.py
  - id: connections-py
    resource: ../../../../../../external/libs/jupyter/jupyter_server/jupyter_server/gateway/connections.py
    title: jupyter_server/gateway/connections.py
---

# gateway/ 网关客户端源码信源

## 模块结构

```
gateway/
├── __init__.py
├── connections.py     # GatewayWebSocketConnection WebSocket 转发
├── gateway_client.py  # GatewayClient 单例配置 + RetryableHTTPClient
├── handlers.py        # WebSocketChannelsHandler/GatewayResourceHandler
└── managers.py        # GatewayMappingKernelManager/GatewayKernelSpecManager 等
```

## GatewayClient (gateway_client.py L89)

网关客户端单例（SingletonConfigurable），配置与 Enterprise Gateway 或 Kernel Gateway 的连接。

**核心配置项**：
| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `url` | Unicode | None | 网关 URL（如 `http://localhost:8888`） |
| `ws_url` | Unicode | 自动派生 | WebSocket URL（wss:// 或 ws://） |
| `http_user` | Unicode | '' | HTTP Basic Auth 用户名 |
| `http_pwd` | Unicode | '' | HTTP Basic Auth 密码 |
| `auth_token` | Unicode | '' | 认证 Token |
| `validate_cert` | Bool | True | 验证 SSL 证书 |
| `conn_env_whitelist` | List | [...] | 传递到远程内核的白名单环境变量 |
| `client_key` | Unicode | '' | SSL 客户端密钥 |
| `client_cert` | Unicode | '' | SSL 客户端证书 |
| `ca_certs` | Unicode | '' | CA 证书路径 |
| `allowed_kernelspecs` | List | [] | 允许使用的 kernelspec 列表 |
| `kernel_ws_blacklist` | List | ['kernel_info_request'] | WebSocket 黑名单消息 |

**核心方法**：
- `instance()`: 获取单例
- `is_enabled()`: 网关是否启用（url 是否设置）
- `load_connection_args()`: 加载 HTTP 连接参数（SSL/认证）
- `gateway_request(method, url, **kwargs)`: 发送 HTTP 请求到网关
- `get_gateway_url(model)`: 构造网关 API URL

### RetryableHTTPClient (gateway_client.py L709)

带重试机制的 HTTP 客户端：
- 指数退避重试
- 可配置最大重试次数
- 支持异步请求

### GatewayTokenRenewerBase (gateway_client.py L49)

Token 更新器抽象基类，用于自动刷新网关认证 Token。

## GatewayMappingKernelManager (managers.py L40)

继承 AsyncMappingKernelManager，将内核管理委托给远程网关。

- `start_kernel()`: 通过网关 API 启动远程内核
- `shutdown_kernel()`: 通过网关 API 关闭远程内核
- `restart_kernel()`: 通过网关 API 重启远程内核
- `interrupt_kernel()`: 通过网关 API 中断远程内核
- `list_kernels()`: 从网关获取内核列表
- `kernel_model()`: 从网关获取内核模型

## GatewayKernelSpecManager (managers.py L215)

继承 KernelSpecManager，从远程网关获取 kernelspec：
- `get_all_specs()`: 从网关 API 获取所有 kernelspec
- `get_kernel_spec(name)`: 获取指定 kernelspec
- 支持 allowed_kernelspecs 过滤

## GatewaySessionManager (managers.py L357)

继承 SessionManager，通过网关管理会话。

## GatewayKernelClient (managers.py L696)

继承 AsyncKernelClient，通过 WebSocket 连接到远程内核。

## ChannelQueue (managers.py L596) / HBChannelQueue (managers.py L687)

消息队列，缓冲网关和前端之间的 ZMQ 通道消息。

## GatewayWebSocketConnection (connections.py L24)

继承 BaseKernelWebsocketConnection，将前端 WebSocket 消息转发到网关 WebSocket。
- 建立到网关的 WebSocket 连接
- 双向消息转发
- 处理连接断开与重连

## WebSocketChannelsHandler (handlers.py L39)

继承 WebSocketHandler + JupyterHandler，网关模式下的 WebSocket Handler：
- 复用 ZMQChannelsWebsocketConnection 的框架
- 但将消息转发到 GatewayClient 的 WebSocket 而非本地 ZMQ

## GatewayResourceHandler (handlers.py L287)

APIHandler，代理请求到网关的 REST API 端点。
