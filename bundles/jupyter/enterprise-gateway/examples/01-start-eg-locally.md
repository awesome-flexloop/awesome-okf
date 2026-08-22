---
okf_version: "0.2"
type: "example"
title: "本地启动EG并执行代码"
description: "从零开始：安装EG、本地启动服务、通过REST API创建Python内核、通过WebSocket发送代码执行请求"
tags: [example, local, startup, api, websocket, quickstart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: app-entry
    resource: "/references/app-entry-source.md"
    title: "主应用入口源码"
  - id: handlers
    resource: "/references/handlers-source.md"
    title: "HTTP Handler源码"
  - id: quickstart
    resource: "/concepts/01-getting-started.md"
    title: "5分钟快速上手"
---

# 本地启动EG并执行代码

本示例演示从零开始在本地启动 Enterprise Gateway，通过 REST API 创建内核，并使用 WebSocket 发送代码执行请求。

## 前置条件

- Python 3.8+
- pip
- ipykernel 已安装（Python内核）

## 步骤1：安装

```bash
pip install enterprise-gateway ipykernel
```

安装完成后验证CLI可用：

```bash
jupyter enterprisegateway --help
```

## 步骤2：注册Python内核

确保ipykernel已注册到Jupyter：

```bash
python -m ipykernel install --user --name python3 --display-name "Python 3"
```

## 步骤3：启动EG

```bash
jupyter enterprisegateway --ip=127.0.0.1 --port=8888 --debug
```

启动成功后看到日志：
```
[I ...] Jupyter Enterprise Gateway 3.4.0 is available at http://127.0.0.1:8888
```

关键配置说明参见 [应用入口与配置体系](/concepts/03-app-and-config.md)。

## 步骤4：验证服务状态

```bash
curl http://127.0.0.1:8888/api
```

返回：
```json
{
  "version": "...",
  "gateway_version": "3.4.0.dev0"
}
```

## 步骤5：查看可用内核

```bash
curl http://127.0.0.1:8888/api/kernelspecs
```

在返回的 `kernelspecs` 中找到 `python3`。

## 步骤6：创建内核

```bash
curl -X POST http://127.0.0.1:8888/api/kernels \
  -H "Content-Type: application/json" \
  -d '{"name": "python3", "env": {"KERNEL_USERNAME": "demo-user"}}'
```

返回（示例）：
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "python3",
  "last_activity": "2024-01-01T00:00:00.000000Z",
  "connections": 0,
  "execution_state": "starting"
}
```

记下返回的 `id`，后续WebSocket通信需要使用。创建内核的内部流程参见 [内核启动流程详解](/concepts/09-kernel-launch-flow.md)。

等待几秒让内核启动完成，查询内核状态：

```bash
curl http://127.0.0.1:8888/api/kernels/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

`execution_state` 变为 `idle` 表示内核就绪。

## 步骤7：通过WebSocket执行代码

这是最关键的步骤——通过WebSocket连接到内核的ZMQ通道代理，发送代码执行请求。

### 使用Python websocket-client

```python
import websocket
import json
import uuid

kernel_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
url = f"ws://127.0.0.1:8888/api/kernels/{kernel_id}/channels"

# Jupyter Wire Protocol消息构造
session_id = uuid.uuid4().hex
msg_id = uuid.uuid4().hex

# 构造execute_request消息
execute_request = {
    "header": {
        "msg_id": msg_id,
        "username": "demo-user",
        "session": session_id,
        "msg_type": "execute_request",
        "version": "5.0"
    },
    "metadata": {},
    "content": {
        "code": "print('Hello from Enterprise Gateway!')\n1+1",
        "silent": False,
        "store_history": True,
        "user_expressions": {},
        "allow_stdin": False,
        "stop_on_error": True
    },
    "parent_header": {},
    "channel": "shell"
}

ws = websocket.create_connection(url)
ws.send(json.dumps(execute_request))

# 接收响应
while True:
    msg = json.loads(ws.recv())
    msg_type = msg.get("header", {}).get("msg_type", "")
    parent_msg_id = msg.get("parent_header", {}).get("msg_id", "")
    
    # 只处理我们的请求的响应
    if parent_msg_id == msg_id:
        if msg_type == "stream":
            print(f"[stdout] {msg['content']['text']}", end="")
        elif msg_type == "execute_result":
            print(f"[result] {msg['content']['data'].get('text/plain', '')}")
        elif msg_type == "status":
            state = msg["content"]["execution_state"]
            print(f"[status] {state}")
            if state == "idle":
                break  # 执行完成
        elif msg_type == "error":
            print(f"[error] {msg['content']['evalue']}")
            break

ws.close()
```

预期输出：
```
[status] busy
[stdout] Hello from Enterprise Gateway!
[result] 2
[status] idle
```

### 使用 wscat（命令行）

如果安装了 Node.js 和 wscat：

```bash
# 安装wscat
npm install -g wscat

# 连接WebSocket
wscat -c "ws://127.0.0.1:8888/api/kernels/<kernel_id>/channels"

# 粘贴execute_request JSON消息
```

## 步骤8：关闭内核

```bash
curl -X DELETE http://127.0.0.1:8888/api/kernels/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## 步骤9：使用Token认证（可选）

如果要启用认证，启动时设置：

```bash
export EG_AUTH_TOKEN=my-secret-token
jupyter enterprisegateway --ip=127.0.0.1 --port=8888
```

后续请求携带Token：

```bash
curl -H "Authorization: token my-secret-token" http://127.0.0.1:8888/api
```

参见 [安全认证与高可用](/concepts/11-security-and-ha.md) 了解更多安全配置。

## 常见问题

**Q: 创建内核时返回403？**
A: 检查是否设置了 `EG_AUTH_TOKEN` 但请求中未携带Token，或KERNEL_USERNAME在unauthorized_users列表中（默认禁止root）。

**Q: 内核一直处于starting状态？**
A: 检查EG日志确认启动错误。本地模式常见原因是ipykernel未安装、端口被占用。

**Q: WebSocket连接失败？**
A: 确认kernel_id正确、内核已启动（execution_state为idle）、防火墙未阻止连接。
