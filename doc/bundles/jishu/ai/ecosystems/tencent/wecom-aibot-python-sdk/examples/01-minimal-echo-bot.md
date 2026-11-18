---
type: example
title: 最小回声机器人
description: 用不到 40 行代码完成连接、认证与文本消息回声，并验证回复链路可用
tags: [wecom, aibot, python-sdk, example, echo]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 最小回声机器人

> **声明：本示例为基于源码阅读整理的用法演示，未在本机实跑。** 文中所有输出均为「示意」，不代表真实运行日志；实际日志格式、时序与错误信息以运行时为准。

## 适用场景

第一次接入 SDK，想用最小成本验证「凭据是否正确、网络是否可达、回复链路是否打通」。它只做一件事：收到文本消息后，用流式接口回一段同样的内容并立即结束。

## 前置条件

| 条件 | 要求 | 依据 |
|---|---|---|
| Python | `>=3.8` | F-003 |
| SDK | `pip install wecom-aibot-python-sdk` | F-001 |
| 凭据 | `WECHAT_BOT_ID`、`WECHAT_BOT_SECRET` 成对配置 | F-055、F-056 |
| 网络 | 可访问 `wss://openws.work.weixin.qq.com` | F-019 |
| 机器人状态 | 已在企微侧启用并允许接收消息 | 平台配置，非 SDK 断言 |

## 分步实现

### 第一步：配置凭据

把凭据放进环境变量，避免写入源码。变量名与 `.env.example` 一致（F-056）：

```bash
# PowerShell
$env:WECHAT_BOT_ID = "your-bot-id"
$env:WECHAT_BOT_SECRET = "your-bot-secret"
```

### 第二步：创建客户端并观察连接事件

```python
import os

from aibot import WSClient, WSClientOptions

client = WSClient(
    WSClientOptions(
        bot_id=os.environ["WECHAT_BOT_ID"],
        secret=os.environ["WECHAT_BOT_SECRET"],
    )
)


@client.on("connected")
def on_connected():
    print("[示意] WebSocket 已连接")


@client.on("authenticated")
def on_authenticated():
    print("[示意] 认证成功")


@client.on("disconnected")
def on_disconnected(reason):
    print(f"[示意] 连接断开: {reason}")
```

`connected` 与 `authenticated` 是两个不同阶段：前者只代表 WebSocket 握手成功，后者才代表 `aibot_subscribe` 返回 `errcode == 0`（F-020、F-024）。排障时不要只看第一个事件。

### 第三步：注册文本消息处理器

```python
from aibot import generate_req_id


@client.on("message.text")
async def on_text(frame):
    body = frame.get("body", {})
    content = body.get("text", {}).get("content", "")

    stream_id = generate_req_id("stream")
    await client.reply_stream(frame, stream_id, f"收到：{content}", True)
```

要点：

- `stream_id` 用 `generate_req_id("stream")` 生成，格式为「前缀_毫秒时间戳_8位随机串」（F-032）。
- `reply_stream` 的 `finish=True` 表示本次流式结束；只发一帧时直接置真即可（F-036、F-037）。
- `await` 会等到对端回执或 5 秒超时才返回，因此日志中回复完成与发送之间存在可感知间隔（F-041）。

### 第四步：启动

```python
if __name__ == "__main__":
    client.run()
```

`run()` 内部新建事件循环，先 `connect()` 再 `run_forever()`，收到 `KeyboardInterrupt` 时调用 `disconnect()`（`aibot/client.py:345-362`）。不需要也不应在外部再套一层 `asyncio.run()`。

## 完整代码

```python
import os

from aibot import WSClient, WSClientOptions, generate_req_id

client = WSClient(
    WSClientOptions(
        bot_id=os.environ["WECHAT_BOT_ID"],
        secret=os.environ["WECHAT_BOT_SECRET"],
    )
)


@client.on("authenticated")
def on_authenticated():
    print("[示意] 认证成功")


@client.on("message.text")
async def on_text(frame):
    content = frame.get("body", {}).get("text", {}).get("content", "")
    stream_id = generate_req_id("stream")
    await client.reply_stream(frame, stream_id, f"收到：{content}", True)


if __name__ == "__main__":
    client.run()
```

## 预期结果（示意）

```text
[示意] 认证成功
[示意] 收到消息：你好
[示意] 回复完成：stream_1730000000000_a1b2c3d4
```

企微侧应看到机器人先出现「正在输入/流式」状态，随后显示「收到：你好」。若只看到空白或一直转圈，优先检查 `finish` 是否为真、`reply_stream` 是否被 `await`（F-037）。

## 失败排查

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 启动即 `KeyError` | 环境变量未设置 | 补设 `WECHAT_BOT_ID` / `WECHAT_BOT_SECRET` |
| 只有 `connected`，无 `authenticated` | 凭据错误或机器人未启用 | 查看 `error` 事件中的 `errcode`（F-024） |
| 进程无输出 | 日志默认写 stderr | 检查终端是否分离了 stderr（F-017） |
| 回复超时 `TimeoutError` | 5 秒内未收到回执 | 检查网络与消息体合法性（F-041） |
| 收到两条回复 | 同时注册了 `message` 与 `message.text` | 只保留一个处理器（F-049） |
| `ImportError: websockets` | 依赖未安装或版本过低 | 安装 `websockets>=12.0`（F-006） |

## 延伸阅读

- [概览与快速开始](/concepts/00-overview.md)：依赖、安装与最小骨架的完整说明。
- [连接生命周期](/concepts/01-connection-lifecycle.md)：`connected` 与 `authenticated` 之间的认证细节。
- [流式回复示例](/examples/02-streaming-reply.md)：从单帧回声扩展到多阶段输出。