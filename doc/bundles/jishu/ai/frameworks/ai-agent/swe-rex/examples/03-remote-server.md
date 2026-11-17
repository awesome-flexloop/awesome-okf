---
type: Example
title: "示例三：手动启动远程 server 并连接（RemoteRuntime / RemoteDeployment）"
description: "不经过 DockerDeployment：手动运行 swerex-remote，用 RemoteRuntime 或 RemoteDeployment 连接；含 CLI 参数、curl 探活、token 与端口注意事项"
tags: [swe-rex, example, remote, server, cli, curl]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:49:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "F-033、F-062 ~ F-067、F-079"
---

# 示例三：手动启动远程 server 并连接（RemoteRuntime / RemoteDeployment）

有时你已经有一个容器或远程机器，只想让 SWE-ReX 连过去。这时不需要 `DockerDeployment`，手动起 server 即可。

## 第一步：在目标机器启动 server

```bash
pip install swe-rex
swerex-remote --host 0.0.0.0 --port 8000 --auth-token "$(python -c 'import uuid; print(uuid.uuid4())')"
```

或：

```bash
python -m swerex --host 0.0.0.0 --port 8000 --auth-token <token>
```

（F-079；`__main__.py` 调用 `server.main`，F-005）

参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--host` | `0.0.0.0` | 监听地址 |
| `--port` | `8000` | 监听端口 |
| `--auth-token` | 必填 | API key |
| `-v/--version` | — | 单独打印版本 |

## 第二步：确认可达

```bash
curl -s http://127.0.0.1:8000/is_alive \
  -H "X-API-Key: <token>"
```

预期：

```json
{"is_alive": true, "message": ""}
```

（`IsAliveResponse` 字段，F-040）

不带 key 会得到 403（缺 header）或 401（key 不匹配），取决于是否提供 header（F-073、F-083）。

## 第三步：连接

### 方式 A：RemoteRuntime（最小）

```python
import asyncio

from swerex.runtime.abstract import BashAction, CreateBashSessionRequest
from swerex.runtime.remote import RemoteRuntime

async def main():
    runtime = RemoteRuntime(
        host="http://127.0.0.1",
        port=8000,
        auth_token="<token>",
        timeout=10,
    )
    print(bool(await runtime.is_alive()))
    await runtime.create_session(CreateBashSessionRequest())
    print(await runtime.run_in_session(BashAction(command="echo hello", timeout=10)))
    await runtime.close()

asyncio.run(main())
```

### 方式 B：RemoteDeployment（统一接口）

```python
import asyncio

from swerex.deployment.remote import RemoteDeployment

async def main():
    deployment = RemoteDeployment(
        host="http://127.0.0.1",
        port=8000,
        auth_token="<token>",
        timeout=10,
    )
    await deployment.start()   # 只创建 RemoteRuntime，不启动新环境
    try:
        runtime = deployment.runtime
        print(bool(await runtime.is_alive()))
    finally:
        await deployment.stop()  # 调 runtime.close()

asyncio.run(main())
```

（F-033）

## 方式 C：Docker 手动起 server

```bash
docker run --rm -p 8000:8000 python:3.12 \
  /bin/sh -c "pip install swe-rex && swerex-remote --host 0.0.0.0 --port 8000 --auth-token <token>"
```

然后客户端连 `http://127.0.0.1:8000`。

> 容器内 server 必须监听 `0.0.0.0`（默认值），否则端口映射不可达。

## 端口语义

`RemoteRuntime._api_url`（F-063）：

| host | port | 最终 URL |
|---|---|---|
| `http://127.0.0.1` | `8000` | `http://127.0.0.1:8000` |
| `http://127.0.0.1` | `None` | `http://127.0.0.1`（80 端口） |
| `https://abc.modal.host` | `None` | `https://abc.modal.host` |

Daytona/Modal 的 tunnel URL 已是完整地址，所以 `port=None`；手动连接本地 server 时不要漏 port。

## 超时设置

`RemoteRuntimeConfig.timeout` 默认 `0.15` 秒（F-071）。跨网络或冷启动时建议 5–30 秒：

```python
RemoteRuntime(host=..., port=..., auth_token=..., timeout=30)
```

这个值同时是 `is_alive` 与普通请求的默认超时；单次调用可覆盖（F-063）。

## 认证注意事项

1. `--auth-token` 必须显式传，但可以传空字符串；空字符串等于关闭认证（F-079、F-073）。
2. 每个环境用独立随机 token；不要复用（Docker/Modal/Fargate/Daytona 都生成 UUID，F-021/F-025/F-030/F-031）。
3. token 不要写进日志或提交到仓库。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `is_alive` false，message 含连接错误 | 地址/端口错、server 未起 | `curl` 探活 |
| 403 | 没带 `X-API-Key` | 加 header |
| 401 | key 不匹配 | 核对 token |
| 连接成功但请求超时 | `timeout=0.15` 太短 | 调大 |
| 连到 80 端口 | `port=None` 但 host 无端口 | 显式给 port 或完整 URL |

## 相关文档

- [HTTP 协议](/concepts/03-http-protocol.md)
- [部署矩阵](/concepts/04-deployments.md)
- [失败模式与测试](/concepts/07-failure-modes-and-tests.md)
