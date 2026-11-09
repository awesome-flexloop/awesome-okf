---
type: example
title: 模板卡片回复与文件下载解密
description: 用模板卡片承载结果并以事件帧更新同一张卡片，同时下载媒体文件按 AES-256-CBC 解密落盘
tags: [wecom, aibot, python-sdk, example, template-card, file]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 模板卡片回复与文件下载解密

> **声明：本示例未在本机实跑**，仅按源码事实重构调用序列。文中的输出、耗时、文件大小与卡片渲染均为「示意」，不构成运行结果承诺。

## 适用场景

一次回答既要给结构化摘要（标题、按钮），又要交付一个附件。做法是两条链路拼合：

1. 收到文件消息 → `download_file` 下载并解密 → 落盘（F-050）；
2. 同时用 `reply_template_card` 回一张卡片告知进度（F-044）；
3. 用户操作卡片后，企业微信回调 `template_card_event`，在**该事件帧**上用 `update_template_card` 把同一张卡片改为「已完成」（F-046、F-034）。

## 前置条件

| 条件 | 要求 | 依据 |
|---|---|---|
| 已完成最小接入 | 能收到 `message.text` 并成功回复一帧 | [01 最小回声机器人](01-minimal-echo-bot.md) |
| 依赖版本 | `cryptography>=42.0`（解密）、`aiohttp>=3.9`（下载） | F-006 |
| 卡片结构 | 由调用方按企业微信模板卡片规范自行构造，SDK 只负责包装、不定义字段 | F-044 |
| 事件注册 | 需注册 `event.template_card_event` 处理器 | F-034、F-048 |

## 分步实现

### 第一步：回复模板卡片

```python
await client.reply_template_card(frame, card)
```

`reply_template_card(frame, template_card, feedback=None)` 的请求体为 `{"msgtype": "template_card", "template_card": card}`，`cmd` 取默认 `WsCmd.RESPONSE`（值 `aibot_respond_msg`）；`feedback` 为真时卡片被改写为 `{**template_card, "feedback": feedback}`（F-044、F-030）。

卡片类型共五种：`text_notice`、`news_notice`、`button_interaction`、`vote_interaction`、`multiple_interaction`（F-035）。SDK 不校验卡片内容，只做透传包装（F-044）。

卡片回复与流式回复走同一条通道：都经 `reply()` 取帧头 `headers.req_id`，再调 `send_reply(req_id, body, cmd)`（F-039）。因此它同样受「单 `req_id` 队列上限 100 条」与「回执超时 5.0 秒」约束（F-040、F-041）。

### 第二步：在事件帧上更新同一张卡片

```python
@client.on("event.template_card_event")
async def on_card_event(frame):
    await client.update_template_card(frame, card_completed)
```

分发路径：`MessageHandler.handle_frame` 对 `cmd == WsCmd.EVENT_CALLBACK` 的帧走事件分支，取 `event.eventtype` 后 emit `event.{eventtype}`（F-047、F-048）；`EventType.TemplateCardEvent` 的取值正是 `template_card_event`（F-034）。

`update_template_card(frame, template_card, userids=None)` 的请求体为 `{"response_type": "update_template_card", "template_card": template_card}`，`userids` 非空时追加同名字段，`cmd` 取 `WsCmd.RESPONSE_UPDATE`（值 `aibot_respond_update_msg`）（F-046）。两点必须注意：

- 它是 `response_type` 结构，**不是** `msgtype` 结构（F-046）；
- docstring 明确要求「使用对应事件（`template_card_event`）的 `req_id`」，拿普通消息帧的 `req_id` 调用无法生效（F-046）。

### 第三步：流式正文与卡片同时返回（可选形态）

若正文较长、需要先流式输出、卡片只出现一次，可用 `reply_stream_with_card`：其 `stream` 字段组装规则与 `reply_stream` 完全一致，`template_card` 为真时写入 `body["template_card"]`，`msgtype` 为 `stream_with_template_card`，`card_feedback` 为真时先合并为 `{**template_card, "feedback": card_feedback}`（F-045；`stream` 组装条件见 F-037）。

```python
stream_id = generate_req_id("stream")
await client.reply_stream_with_card(
    frame, stream_id, "正在解析附件……", False, template_card=card
)
```

`examples/comparison_test.py` 的「流式卡片」分支就是两阶段调用该接口（F-058）。形参名依 F-045 所述字段（`template_card`、`card_feedback`）给出，精确签名以源码为准。

### 第四步：下载并解密文件

```python
data, filename = await client.download_file(url, aes_key)
```

`WSClient.download_file(url, aes_key=None) -> Tuple[bytes, Optional[str]]` 内部是三层（F-050）：

| 层 | 实现 | 关键行为 | 依据 |
|---|---|---|---|
| 门面 | `WSClient.download_file` | 先调 `download_file_raw(url)`；`aes_key` 为假值时记 `warn` 并**原样返回密文**；否则调 `decrypt_file` 后返回明文 | F-050 |
| 传输 | `WeComApiClient.download_file_raw` | `aiohttp.TCPConnector(ssl=_SSL_CONTEXT)` + `ClientSession(timeout=self._timeout)`，`raise_for_status()` 后 `await response.read()`；`_timeout` 为 `ClientTimeout(total=timeout / 1000)`，`timeout` 默认 10000，即总时限 10 秒 | F-051 |
| 密码 | `decrypt_file` | Base64 补齐 → `key = base64.b64decode(...)` → `iv = key[:16]` → `Cipher(algorithms.AES(key), modes.CBC(iv))`，即 AES-256-CBC | F-053 |

文件名来自响应头 `Content-Disposition`，解析顺序固定：先按 RFC 5987 的 `filename*=UTF-8''([^;\s]+)`，未命中再按 `filename="?([^";\s]+)"?`，两者都经 `unquote`，都未命中时 `filename` 保持 `None`（F-052）。

填充是这套实现最不标准的部分（F-054）：

- 解密**前**先把数据零补齐到 16 字节块整数倍；
- 解密**后**手写 PKCS#7 去填充：`pad_len = decrypted[-1]`，要求 `1 <= pad_len <= 32` 且不超过数据长度，尾部逐字节比对，不一致抛 `ValueError("Invalid PKCS#7 padding: padding bytes mismatch")`；
- 上述异常在外层统一包装为 `RuntimeError("decrypt_file: Decryption failed - ...")`；
- 但输入侧的两个 `ValueError`（数据为空、`aes_key` 非非空字符串）**不包装**，需分别捕获（F-053、F-054）。

`url` 与 `aes_key` 由调用方从消息体取得：SDK 只按 `body["msgtype"]` 把帧分发到 `message.file`（F-049），不解析媒体字段。示例把取值集中在一个函数里并注明这一点，接入时以企业微信报文为准。

### 第五步：落盘

`filename` 可能为 `None`（F-052），必须兜底。`examples/comparison_test.py` 的做法是建一个 `downloads` 目录存放下载结果（F-058）。

## 完整代码

```python
import os
from pathlib import Path

from dotenv import load_dotenv

from aibot import WSClient, WSClientOptions, generate_req_id

load_dotenv()

client = WSClient(
    WSClientOptions(
        bot_id=os.getenv("WECHAT_BOT_ID"),
        secret=os.getenv("WECHAT_BOT_SECRET"),
    )
)

DOWNLOAD_DIR = Path("downloads")  # F-058 的做法
DOWNLOAD_DIR.mkdir(exist_ok=True)

# 卡片内容由调用方构造，SDK 只做包装、不定义字段（F-044）；
# card_type 的取值来自 TemplateCardType 枚举（F-035）。
CARD_TEMPLATE = {
    "card_type": "text_notice",
    "main_title": {"title": "附件处理"},
}


def make_card(status: str) -> dict:
    return {**CARD_TEMPLATE, "sub_title_text": status}


def media_of(body: dict):
    """从 file 消息帧体中取 (url, aeskey)。

    注意：SDK 只按 body["msgtype"] 分发到 message.file（F-049），
    不解析媒体字段；下方字段路径属于企业微信报文，非 SDK 事实，
    接入时请以实际报文为准。
    """
    node = body.get("file") or {}
    return node.get("url"), node.get("aeskey")


@client.on("message.file")
async def on_file(frame):
    url, aes_key = media_of(frame.get("body") or {})

    # 门面内部：download_file_raw → decrypt_file（F-050）
    data, filename = await client.download_file(url, aes_key)

    path = DOWNLOAD_DIR / (filename or f"media_{generate_req_id('file')}")
    path.write_bytes(data)  # filename 可能为 None，故上面兜底（F-052）

    # 用同一条消息帧回一张卡片（F-044）
    await client.reply_template_card(frame, make_card(f"已下载 {len(data)} 字节"))


@client.on("event.template_card_event")
async def on_card_event(frame):
    # 必须用该事件帧的 req_id，内部 cmd 为 WsCmd.RESPONSE_UPDATE（F-046）
    await client.update_template_card(frame, make_card("已完成"))


if __name__ == "__main__":
    client.run()
```

## 预期结果（示意）

```text
[示意] 收到 message.file → download_file 返回 (bytes, "report.pdf")
[示意] 写入 downloads/report.pdf
[示意] 回模板卡片：附件处理 / 已下载 20480 字节
[示意] 用户点击卡片按钮 → event.template_card_event
[示意] update_template_card：同一张卡片改为 附件处理 / 已完成
```

卡片与下载是两条独立链路：卡片回复受 5 秒回执窗口约束（F-041），下载受 10 秒总时限约束（F-051），二者不共享超时。若下载耗时接近 10 秒，应先回卡片再下载，而不是反过来。

## 失败排查

| 现象 | 可能原因 | 处理 |
|---|---|---|
| `ValueError: aes_key must be a non-empty string` | 未取到或传错 `aeskey`；此异常不被包装 | 检查消息体取值，确认与文件同源（F-053） |
| 落盘文件打不开、大小与原文不符 | `aes_key` 为假值，门面原样返回了密文 | 确认密钥非空（F-050） |
| `RuntimeError: Decryption failed - Invalid PKCS#7 padding` | 密钥错误、Base64 被截断，或末组数据损坏 | 核对 `aeskey` 完整性；本实现 `pad_len` 上限为 32（F-054） |
| `ValueError: decrypt_file: encrypted_data is empty or not provided` | 下载结果为空 | 检查 HTTP 状态与 `read()` 返回值（F-051、F-053） |
| `filename` 为 `None` | 响应头缺失或格式不符 | 用 URL 末段或时间戳兜底（F-052） |
| 下载超时 | 总时限 10 秒 | 调大 `request_timeout`（F-051、F-055） |
| 卡片更新无反应 | 用了普通消息帧的 `req_id`，或 `response_type` 被误写成 `msgtype` | 在 `template_card_event` 回调内调用（F-046） |
| `RuntimeError` 队列已满 | 单 `req_id` 累计超过 100 条 | 减少卡片/帧数量（F-040） |

## 延伸阅读

- [流式回复与模板卡片](/concepts/03-streaming-and-card.md)：六种回复形态、串行队列与 `update_template_card` 的 `req_id` 约束。
- [文件下载与解密](/concepts/04-file-download-decrypt.md)：三层链路、两套文件名正则与私有填充约定。
- [多阶段流式回复](02-streaming-reply.md)：先把流式时序跑通，再叠加卡片与附件。
