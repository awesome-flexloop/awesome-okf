---
type: concept
title: 概览与快速开始
description: 从定位、依赖与最小骨架三方面建立对 wecom-aibot-python-sdk 的整体认识
tags: [wecom, aibot, python-sdk, overview]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 概览与快速开始

## 一句话定位

`wecom-aibot-python-sdk` 是把企业微信智能机器人接入「WebSocket 长连接」的 Python 异步 SDK。它用 `bot_id` 与 `secret` 完成认证，在同一条连接上接收消息回调、发送被动回复、推送流式内容与模板卡片，并附带媒体下载解密能力（F-022、F-030、F-031、F-050）。它不是一个「企业微信办公 API 全家桶」：公开导出的 17 项能力集中在连接、消息、卡片、文件与加解密，没有文档、日程、通讯录等业务封装（F-012、F-013）。

## 在同一生态中的位置

同属 WecomTeam 的开源组件面向不同层次，选用时先确认自己缺的是哪一层：

| 组件 | 层次 | 与本 SDK 的关系 |
|---|---|---|
| `wecom-cli` | 命令行办公操作 | 面向人工或脚本驱动的办公动作，不承载机器人长连接 |
| `wecom-unified` | Agent 技能编排 | 把多种能力编排为技能，可把本 SDK 当作机器人通道实现 |
| 本 SDK | 机器人消息通道 | 只解决「连上企微、收发机器人与事件」 |

判断准则：需要机器人实时收消息、流式吐字、卡片交互，选本 SDK；需要批量处理文档、日程、审批，选办公侧组件。两者可以组合，但不要期待本 SDK 提供办公业务 API（F-013）。

## 组成模块

仓库共 19 个受控文件，其中 `aibot/` 9 个模块构成全部运行时逻辑（F-059）：

| 模块 | 职责 | 关键对象 |
|---|---|---|
| `aibot/ws.py` | 连接、认证、心跳、重连、串行回复队列 | `WsConnectionManager`、`DEFAULT_WS_URL` |
| `aibot/client.py` | 对外门面与事件注册 | `WSClient`（继承 `AsyncIOEventEmitter`，F-014） |
| `aibot/types.py` | 枚举、配置、类型别名 | `WsCmd`、`WSClientOptions`、`WsFrame` |
| `aibot/message_handler.py` | 入站帧校验与事件分发 | `MessageHandler` |
| `aibot/api.py` | 媒体下载与文件名解析 | `WeComApiClient` |
| `aibot/crypto_utils.py` | AES-256-CBC 解密 | `decrypt_file` |
| `aibot/utils.py` | 请求 ID 生成 | `generate_req_id` |
| `aibot/logger.py` | 默认 stderr 日志 | `DefaultLogger` |

## 运行环境与依赖

| 项目 | 取值 | 依据 |
|---|---|---|
| Python | `>=3.8`，classifiers 覆盖 3.8 ~ 3.13 | F-003 |
| 必装依赖 | `websockets>=12.0`、`aiohttp>=3.9`、`pyee>=11.0`、`cryptography>=42.0`、`certifi>=2023.0` | F-006 |
| 可选依赖 | `dev` 组仅 `python-dotenv>=1.0` | F-007 |
| 默认服务地址 | `wss://openws.work.weixin.qq.com` | F-019 |
| 打包版本 | `1.0.1`；运行期 `__version__` 为 `1.0.0` | F-002、F-008 |

注意依赖里是 `cryptography` 而非 `pycryptodome`，自行复刻解密逻辑时不要装错库（F-006、F-053）。

## 安装

```bash
# 从 PyPI 安装
pip install wecom-aibot-python-sdk

# 或从本仓 vendor 快照以可编辑模式安装
pip install -e vendor/WecomTeam/wecom-aibot-python-sdk
```

## 最小可运行骨架

凭据通过环境变量注入，变量名与 `.env.example` 一致：`WECHAT_BOT_ID`、`WECHAT_BOT_SECRET`（F-056）。

```python
import os

from aibot import WSClient, WSClientOptions, generate_req_id

client = WSClient(
    WSClientOptions(
        bot_id=os.environ["WECHAT_BOT_ID"],
        secret=os.environ["WECHAT_BOT_SECRET"],
    )
)


@client.on("connected")
def on_connected():
    print("WebSocket connected")


@client.on("authenticated")
def on_authenticated():
    print("Authenticated")


@client.on("message.text")
async def on_text(frame):
    content = frame.get("body", {}).get("text", {}).get("content", "")
    stream_id = generate_req_id("stream")
    await client.reply_stream(frame, stream_id, f"收到：{content}", True)


if __name__ == "__main__":
    client.run()
```

`run()` 内部新建事件循环，先 `connect()` 再 `run_forever()`，收到 `KeyboardInterrupt` 时调用 `disconnect()` 并关闭循环（`aibot/client.py:345-362`），因此最小骨架不需要自己管理 loop。处理器注册必须发生在连接建立之前；异步处理器由 `AsyncIOEventEmitter` 调度。

## 首次运行检查清单

1. 凭据是否成对配置，缺失时构造阶段不报错、认证阶段才失败（F-055）。
2. 出网是否允许 `wss://openws.work.weixin.qq.com`（F-019）。
3. 是否观察到 `connected` 与 `authenticated` 两个事件；只看到前者说明认证未通过，客户端会停在「已连接未认证」状态（F-024、F-047）。
4. 回复是否在回调后及时发出，欢迎语有 5 秒窗口限制（F-043）。

## 延伸阅读

- [连接生命周期](/concepts/01-connection-lifecycle.md)：认证、心跳与重连的真实时序。
- [帧协议与事件分发](/concepts/02-frame-protocol.md)：`req_id` 如何决定一帧的命运。
- [流式回复与模板卡片](/concepts/03-streaming-and-card.md)：为什么每次 `reply_stream` 都要等回执。
- [文件下载与解密](/concepts/04-file-download-decrypt.md)：媒体链路的补零与私有去填充。