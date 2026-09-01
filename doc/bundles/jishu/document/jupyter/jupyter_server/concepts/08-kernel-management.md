---
type: Concept
title: "内核管理"
description: "MappingKernelManager 多内核管理、内核生命周期、空闲回收（culling）、Kernel Spec 管理与内核进程控制"
tags: [kernels, kernel-manager, lifecycle, culling, kernel-spec, zmq, ipython]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:50:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: kernels
    resource: /references/kernels-source.md
    title: services/kernels/ 内核管理源码信源
---

# 内核管理

内核（Kernel）是 Jupyter 中执行代码的独立进程。MappingKernelManager 负责管理多个内核实例的完整生命周期：启动、通信、监控、回收、关闭。

## 内核管理架构

```
ServerApp
└── MappingKernelManager / AsyncMappingKernelManager
    ├── kernel_manager_class = AsyncIOLoopKernelManager (默认)
    │   └── 每个内核一个 KernelManager 实例
    │       ├── 启动内核子进程（ipykernel 等）
    │       ├── 管理 ZMQ 连接（Shell/IOPub/Stdin/Control/HB）
    │       └── 管理 connection 文件
    ├── cull_idle_timeout / cull_interval（空闲回收）
    └── kernel_ws_class = ZMQChannelsWebsocketConnection
```

## 内核模型

内核通过 JSON 模型表示：

```json
{
  "id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv",
  "name": "python3",
  "last_activity": "2024-01-01T12:00:00Z",
  "execution_state": "idle",
  "connections": 1
}
```

| 字段 | 说明 |
|------|------|
| `id` | 内核唯一标识符（UUID） |
| `name` | KernelSpec 名称（如 `python3`） |
| `last_activity` | 最后活动时间 |
| `execution_state` | 执行状态：`starting` / `idle` / `busy` |
| `connections` | 当前 WebSocket 连接数 |

## REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/kernels` | 列出所有运行中的内核 |
| POST | `/api/kernels` | 启动新内核 |
| GET | `/api/kernels/<kernel_id>` | 获取内核信息 |
| DELETE | `/api/kernels/<kernel_id>` | 关闭内核 |
| POST | `/api/kernels/<kernel_id>/restart` | 重启内核 |
| POST | `/api/kernels/<kernel_id>/interrupt` | 中断内核 |
| WebSocket | `/api/kernels/<kernel_id>/channels` | 内核通信通道 |
| GET | `/api/kernelspecs` | 列出所有可用 kernelspecs |
| GET | `/api/kernelspecs/<name>` | 获取指定 kernelspec |

### API 示例

```bash
# 列出运行中的内核
curl http://localhost:8888/api/kernels?token=xxx

# 启动新内核
curl -X POST http://localhost:8888/api/kernels?token=xxx \
  -H "Content-Type: application/json" \
  -d '{"name": "python3", "path": "/notebooks"}'

# 获取内核信息
curl http://localhost:8888/api/kernels/<kernel_id>?token=xxx

# 重启内核
curl -X POST http://localhost:8888/api/kernels/<kernel_id>/restart?token=xxx

# 中断内核（相当于 Ctrl+C）
curl -X POST http://localhost:8888/api/kernels/<kernel_id>/interrupt?token=xxx

# 关闭内核
curl -X DELETE http://localhost:8888/api/kernels/<kernel_id>?token=xxx

# 列出可用 kernelspecs
curl http://localhost:8888/api/kernelspecs?token=xxx
```

## 内核生命周期

### 启动流程

1. **生成 kernel_id**（UUID）
2. **创建 connection 文件**：在 `jupyter_runtime_dir/` 下创建 `kernel-<id>.json`，包含五个 ZMQ 端口和签名密钥
3. **启动内核进程**：根据 kernelspec 的 `argv` 启动内核进程（如 `python -m ipykernel_launcher -f <connection_file>`）
4. **等待内核就绪**：等待 HB 通道响应或内核发布 `status: starting` → `idle`
5. **注册到内核字典**：`_kernels[kernel_id] = kernel_manager`
6. **返回内核模型**

### 运行期间

- 内核通过 ZMQ 通道与 Server 通信
- Server 通过 WebSocket 将消息转发给前端
- PeriodicCallback 更新 `last_activity` 时间戳
- cull 回调定期检查并回收空闲内核

### 关闭流程

1. 向内核发送 shutdown 请求（通过 Control 通道）
2. 等待内核进程终止（有超时保护）
3. 如果超时，强制终止（kill）
4. 清理 connection 文件
5. 从内核字典中移除

## 空闲内核回收（Culling）

防止长时间空闲内核消耗资源：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `cull_idle_timeout` | 0（禁用） | 空闲超时秒数，超过则回收 |
| `cull_interval` | 300（5分钟） | 检查间隔秒数 |
| `cull_connected` | False | 是否回收仍有 WebSocket 连接的空闲内核 |
| `cull_busy` | False | 是否回收忙碌的内核（通常保持 False） |

推荐配置（1小时空闲回收）：

```python
c.MappingKernelManager.cull_idle_timeout = 3600
c.MappingKernelManager.cull_interval = 300
c.MappingKernelManager.cull_connected = True
```

## KernelSpec 管理

KernelSpec 描述一种可用的内核类型（如 Python 3、R、Julia）：

### KernelSpec 格式

```json
{
  "argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "Python 3",
  "language": "python",
  "metadata": {"debugger": true}
}
```

存放位置：
- 用户级：`~/.local/share/jupyter/kernels/<name>/kernel.json`
- 系统级：`/usr/share/jupyter/kernels/<name>/kernel.json`
- 环境级：`$CONDA_PREFIX/share/jupyter/kernels/<name>/kernel.json`

`KernelSpecManager` 自动发现所有已安装的 kernelspecs。

### kernelspecs API 响应

```json
{
  "default": "python3",
  "kernelspecs": {
    "python3": {
      "name": "python3",
      "spec": {
        "argv": ["python3", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Python 3",
        "language": "python",
        "metadata": {}
      },
      "resources": {
        "logo-64x64": "/kernelspecs/python3/logo-64x64.png"
      }
    }
  }
}
```

## 内核通信通道

每个内核有五个 ZMQ 通道，通过 `ZMQChannelsWebsocketConnection` 桥接到 WebSocket：

| 通道 | 类型 | 用途 |
|------|------|------|
| Shell | ROUTER/DEALER | 代码执行请求/回复（请求-响应） |
| IOPub | PUB/SUB | 广播输出（stdout/stderr/display_data/status） |
| Stdin | ROUTER/DEALER | 标准输入请求（`input()` 函数） |
| Control | ROUTER/DEALER | 控制命令（shutdown/interrupt/restart） |
| HB | REQ/REP | 心跳检测内核存活 |

消息格式遵循 Jupyter 协议，使用 `jupyter_client.session.Session` 序列化和签名。

## 传输加密

v2.x 新增传输加密功能：

| `transport_encryption` 值 | 说明 |
|--------------------------|------|
| `disabled`（默认） | 不使用加密，ZMQ 明文通信 |
| `auto` | 如果 kernelspec 声明支持则自动启用 CurveZMQ |
| `required` | 强制启用加密，不支持则启动失败 |

## 核心配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `default_kernel_name` | 'python3' | 默认内核名称 |
| `kernel_manager_class` | AsyncIOLoopKernelManager | 单个内核管理器类 |
| `root_dir` | cwd | 内核工作根目录 |
| `kernel_argv` | [] | 内核启动额外参数 |
| `cull_idle_timeout` | 0 | 空闲回收超时 |
| `cull_interval` | 300 | 回收检查间隔 |
| `cull_connected` | False | 回收有连接的内核 |
| `cull_busy` | False | 回收忙碌内核 |
| `transport_encryption` | 'disabled' | ZMQ 传输加密 |

## 自定义内核管理

可替换 kernel_manager_class 实现自定义内核调度：

```python
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager

class KubernetesKernelManager(AsyncMappingKernelManager):
    """在 Kubernetes Pod 中启动内核"""

    async def start_kernel(self, kernel_name=None, **kwargs):
        # 在 K8s 中创建 Pod
        pod = await self.k8s_api.create_pod(kernel_name)
        kernel_id = pod.metadata.name
        # 返回 connection 信息
        return await super().start_kernel(kernel_id=kernel_id, **kwargs)

c.ServerApp.kernel_manager_class = KubernetesKernelManager
```

## 相关概念

- [WebSocket 通信](11-websocket-communication.md) — 内核与前端的实时消息通道
- [会话管理](09-sessions-service.md) — Session 如何关联 Kernel 与文件
- [网关客户端](12-gateway-client.md) — 远程内核代理模式
