---
type: Concept
title: "网关客户端"
description: "Enterprise Gateway 集成、远程内核代理、GatewayClient 架构、WebSocket 转发与 KernelSpec 发现"
tags: [gateway, enterprise-gateway, remote-kernel, proxy, kernel-gateway, distributed]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: gateway
    resource: /references/gateway-source.md
    title: gateway/ 网关客户端源码信源
---

# 网关客户端

Gateway 功能允许 Jupyter Server 将内核管理委托给远程网关服务（如 Jupyter Enterprise Gateway、Jupyter Kernel Gateway），实现内核的分布式执行和资源隔离。

## Gateway 架构

```
┌─────────────────┐     HTTP/WS      ┌──────────────────┐     ZMQ      ┌──────────┐
│   Browser/Client │ ◄──────────────► │  Jupyter Server  │ ◄──────────► │  Local   │
│   (Frontend)     │                  │  (This Package)  │              │  Kernel  │
└─────────────────┘                  └────────┬─────────┘              └──────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              │  Gateway Mode 启用时           │
                              ▼                               ▼
                    ┌──────────────────┐              ┌──────────────┐
                    │ GatewayClient    │    HTTP/WS   │ Enterprise   │
                    │ (Manager 子类)   │ ──────────►  │ Gateway      │
                    │  - 代理 API 请求 │              │  - K8s/YARN  │
                    │  - 代理 WS      │              │  - Docker    │
                    │  - 代理 Kernels │              │  - 远程进程  │
                    └──────────────────┘              └──────────────┘
```

启用 Gateway 后，所有内核管理操作被代理到远程网关，本地不再启动内核进程。

## 核心组件

| 类 | 文件 | 职责 |
|----|------|------|
| `GatewayClient` | `gateway/client.py` | Gateway 配置和 HTTP 客户端单例 |
| `GatewayKernelManager` | `gateway/managers.py` | MappingKernelManager 子类，代理内核操作 |
| `GatewayKernelSpecManager` | `gateway/managers.py` | KernelSpecManager 子类，代理 kernelspec 发现 |
| `GatewaySessionManager` | `gateway/managers.py` | SessionManager 子类，代理会话操作 |
| `GatewayWebSocketHandler` | `gateway/handlers.py` | WebSocket 代理到网关 WS 端点 |

## 启用 Gateway

### 配置方式

```python
# jupyter_server_config.py
c.GatewayClient.url = "http://enterprise-gateway:8888"
c.GatewayClient.ws_url = "ws://enterprise-gateway:8888"
```

### 命令行方式

```bash
jupyter server \
  --GatewayClient.url=http://enterprise-gateway:8888 \
  --GatewayClient.ws_url=ws://enterprise-gateway:8888
```

### 环境变量

```bash
export JUPYTER_GATEWAY_URL=http://enterprise-gateway:8888
export JUPYTER_GATEWAY_WS_URL=ws://enterprise-gateway:8888
jupyter server
```

## 核心配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `url` | None | Gateway HTTP URL（启用 Gateway 的必需项） |
| `ws_url` | None | Gateway WebSocket URL（默认从 url 推导） |
| `auth_token` | None | Gateway 认证 Token（`Authorization: token xxx`） |
| `validate_cert` | True | 验证 SSL 证书 |
| `connect_timeout` | 40 | HTTP 连接超时（秒） |
| `request_timeout` | 40 | HTTP 请求超时（秒） |
| `client_key` | None | 客户端 SSL 密钥路径 |
| `client_cert` | None | 客户端 SSL 证书路径 |
| `ca_certs` | None | CA 证书路径 |
| `allowed_kernelspecs` | [] | 允许使用的 kernelspec 白名单 |
| `blocked_kernelspecs` | [] | 禁止使用的 kernelspec 黑名单 |
| `default_kernel_name` | None | 覆盖默认内核名 |
| `env_whitelist` | [] | 传递给远程内核的环境变量白名单 |
| `headers` | {} | 附加 HTTP 请求头 |

## Gateway 工作机制

### 内核启动代理

```python
# GatewayKernelManager.start_kernel()
async def start_kernel(self, kernel_name=None, **kwargs):
    # 1. 构造启动请求
    url = f"{self.base_url}/api/kernels"
    body = {"name": kernel_name, "env": filtered_env}

    # 2. 发送 HTTP 请求到 Gateway
    response = await gateway_fetch(self, url, method="POST", body=json.dumps(body))

    # 3. 返回代理的内核模型
    kernel_id = response["id"]
    self._kernels[kernel_id] = GatewayKernelManager._kernel_id_to_resource(kernel_id)
    return kernel_id
```

### API 请求转发

所有内核相关的 REST API 请求被转发到 Gateway：

| 本地端点 | 代理到 Gateway 端点 |
|---------|-------------------|
| `GET /api/kernels` | `GET <gateway_url>/api/kernels` |
| `POST /api/kernels` | `POST <gateway_url>/api/kernels` |
| `GET /api/kernels/<id>` | `GET <gateway_url>/api/kernels/<id>` |
| `DELETE /api/kernels/<id>` | `DELETE <gateway_url>/api/kernels/<id>` |
| `POST /api/kernels/<id>/restart` | `POST <gateway_url>/api/kernels/<id>/restart` |
| `POST /api/kernels/<id>/interrupt` | `POST <gateway_url>/api/kernels/<id>/interrupt` |
| `GET /api/kernelspecs` | `GET <gateway_url>/api/kernelspecs` |

### WebSocket 代理

`GatewayWebSocketHandler` 使用 `tornado.websocket.websocket_connect` 建立到 Gateway 的 WebSocket 连接，实现双向消息转发：

```
浏览器 WS ←→ Jupyter Server WS ←→ GatewayClient WS ←→ Gateway WS ←→ 远程 Kernel
```

消息转发是透明的：客户端不需要感知内核在远程运行。

### KernelSpec 过滤

Gateway 返回的 kernelspec 列表可以通过白名单/黑名单过滤：

```python
# 只允许 Python 和 R 内核
c.GatewayClient.allowed_kernelspecs = ["python_kubernetes", "r_kubernetes"]

# 禁止本地内核
c.GatewayClient.blocked_kernelspecs = ["python3"]
```

## 环境变量传递

出于安全考虑，只有白名单中的环境变量会传递给远程内核：

```python
# 传递特定环境变量
c.GatewayClient.env_whitelist = ["PYTHONPATH", "SPARK_HOME", "LD_LIBRARY_PATH"]
```

这防止本地敏感环境变量泄露到远程执行环境。

## 认证

Gateway 支持 Token 认证和证书认证：

### Token 认证

```python
c.GatewayClient.auth_token = "my-secret-gateway-token"
# 请求自动添加 Authorization: token my-secret-gateway-token
```

### mTLS（双向 TLS）

```python
c.GatewayClient.client_cert = "/path/to/client.crt"
c.GatewayClient.client_key = "/path/to/client.key"
c.GatewayClient.ca_certs = "/path/to/ca.crt"
```

## gateway_fetch 工具函数

`gateway/handlers.py` 提供了 `gateway_fetch()` 工具函数，用于从 Handler 向 Gateway 发送 HTTP 请求：

```python
async def gateway_fetch(handler, resource, method="GET", body=None):
    """统一的 Gateway HTTP 请求函数
    - 自动添加认证头
    - 处理 SSL 配置
    - 错误转换为 HTTPError
    """
    url = f"{GatewayClient.instance().url}{resource}"
    headers = {"Authorization": f"token {GatewayClient.instance().auth_token}"}
    request = HTTPRequest(url, method=method, body=body, headers=headers, ...)
    response = await AsyncHTTPClient().fetch(request)
    return json_decode(response.body)
```

## Gateway vs 本地内核：功能差异

| 功能 | 本地内核 | Gateway 模式 |
|------|---------|-------------|
| 内核生命周期管理 | ✅ 本地进程控制 | ❌ 委托给 Gateway |
| KernelSpec 发现 | ✅ 本地扫描 | ❌ 从 Gateway 获取 |
| 终端（Terminals） | ✅ 本地 PTY | ❌ 通常不可用（取决于 Gateway） |
| 内容管理 | ✅ 本地文件系统 | ✅ 仍由本地 ContentsManager 处理 |
| WebSocket 连接 | ✅ 直连 ZMQ | ❌ 代理到 Gateway |
| 内核中断/重启 | ✅ ZMQ Control 通道 | ❌ HTTP 请求到 Gateway |
| 空闲内核回收 | ✅ 本地 culling | ❌ 由 Gateway 管理 |

## 典型部署场景

### Kubernetes 分布式内核

```
Notebook 镜像（Jupyter Server + Gateway Client）
    │
    ├── /api/contents → 本地 PVC 存储
    └── /api/kernels → Enterprise Gateway (K8s)
                        ├── Pod: python-kernel-xxx
                        ├── Pod: r-kernel-xxx
                        └── Pod: spark-kernel-xxx
```

### Hadoop/YARN 集群

```
Edge Node (Jupyter Server)
    │
    └── Gateway → Enterprise Gateway (YARN)
                  └── YARN Container: kernel (Spark on YARN)
```

### 资源隔离（Docker）

```
Jupyter Server 容器
    │
    └── Gateway → Kernel Gateway (Docker)
                  ├── Container: python-kernel
                  └── Container: r-kernel
```

## 健康检查

`GatewayClient` 定期检查 Gateway 可用性：

- 启动时连接测试：验证 Gateway URL 可达且认证成功
- Kernelspec 获取失败处理：如果 Gateway 不可用，降级为空列表或报错
- WebSocket 连接失败：自动重连（配置项控制）

## 相关概念

- [内核管理](08-kernel-management.md) — 本地内核管理对比
- [WebSocket 通信](11-websocket-communication.md) — WS 代理机制
- [配置管理](06-config-management.md) — Gateway 配置选项
