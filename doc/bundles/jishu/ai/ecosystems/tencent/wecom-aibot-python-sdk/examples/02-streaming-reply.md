---
type: example
title: 多阶段流式回复
description: 用同一 stream_id 分阶段推送内容，并在结束帧附带图文混排条目
tags: [wecom, aibot, python-sdk, example, streaming]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 多阶段流式回复

> **声明：本示例为基于源码阅读整理的用法演示，未在本机实跑。** 文中的输出、耗时与界面表现均为「示意」，未采集真实运行日志。

## 适用场景

回答需要分阶段产出：先给「正在检索」，再给「正在组织答案」，最后给完整结论与引用。相比一次性回复，它能显著降低用户等待焦虑，但会引入额外的网络往返。

## 前置条件

| 条件 | 要求 |
|---|---|
| 已完成最小接入 | 能收到 `message.text` 并成功回复一帧 |
| 依赖版本 | `websockets>=12.0`、`pyee>=11.0`（F-006） |
| 对延迟有预期 | 每帧都要等回执，默认超时 5 秒（F-041） |

## 分步实现

### 第一步：整个回复只生成一个 stream_id

```python
from aibot import generate_req_id

stream_id = generate_req_id("stream")
```

同一轮回复的所有中间帧与结束帧必须共用它；跨消息复用会让不同回答串在一起，因此每轮回复都应重新生成。

### 第二步：发送中间帧

```python
await client.reply_stream(frame, stream_id, "正在检索相关资料……", False)
```

`finish=False` 表示流未结束。此时即使传入 `msg_item` 也不会写入报文，因为组装条件要求 `finish` 为真（F-037）。

### 第三步：发送结束帧

```python
msg_item = [
    {
        "msgtype": "text",
        "text": {"content": "参考来源：内部知识库 / 第 3 节"},
    },
]

await client.reply_stream(
    frame,
    stream_id,
    "**结论**：……（此处为模型生成的最终答案）",
    True,
    msg_item=msg_item,
)
```

`msg_item` 的结构取自 `examples/comparison_test.py` 的第三阶段示例（F-058）；它只在 `finish=True` 且列表非空时进入 `stream` 字段（F-037）。

## 完整代码

```python
import asyncio

from aibot import WSClient, WSClientOptions, generate_req_id

client = WSClient(
    WSClientOptions(
        bot_id="your-bot-id",
        secret="your-bot-secret",
    )
)


@client.on("message.text")
async def on_text(frame):
    stream_id = generate_req_id("stream")

    try:
        await client.reply_stream(frame, stream_id, "正在检索相关资料……", False)
        await asyncio.sleep(0.5)  # 示意：替换为真实检索
        await client.reply_stream(frame, stream_id, "正在组织答案……", False)
        await asyncio.sleep(0.5)  # 示意：替换为真实生成

        await client.reply_stream(
            frame,
            stream_id,
            "**结论**：这是最终答案。",
            True,
            msg_item=[
                {
                    "msgtype": "text",
                    "text": {"content": "参考来源：内部知识库 / 第 3 节"},
                }
            ],
        )
    except Exception as exc:
        # 失败时补一帧结束，避免客户端一直停留在流式状态
        try:
            await client.reply_stream(frame, stream_id, f"生成失败：{exc}", True)
        except Exception:
            pass


if __name__ == "__main__":
    client.run()
```

## 预期结果（示意）

```text
[示意] 第 1 帧：正在检索相关资料……
[示意] 第 2 帧：正在组织答案……
[示意] 第 3 帧：**结论**：这是最终答案。 + 1 条 msg_item
```

企微侧应看到内容逐段替换或追加，最后定格在结论与引用条目。注意：三帧是**串行**发送的，每一帧都要等回执才发下一帧，因此总耗时约为「三次回执往返 + 两段本地处理时间」，而不是三帧同时到达（F-042）。

## 失败排查

| 现象 | 可能原因 | 处理 |
|---|---|---|
| `TimeoutError` | 某帧 5 秒内无回执 | 降低帧数或缩短内容；检查网络（F-041） |
| `RuntimeError` 队列已满 | 单 `stream_id` 累计超过 100 帧 | 合并内容，控制分片数（F-040） |
| 客户端一直显示「生成中」 | 最后一帧 `finish` 为假 | 确保存在且仅有一个结束帧 |
| 引用条目未显示 | `msg_item` 传在中间帧 | 仅在 `finish=True` 的帧传入 |
| 第二条回答覆盖第一条 | `stream_id` 被复用 | 每条消息重新生成 `stream_id` |
| 并发调用顺序错乱 | 多协程同时写同一 `frame` | 单处理器内顺序 `await` |

## 延伸阅读

- [流式回复与模板卡片](/concepts/03-streaming-and-card.md)：队列上限、回执窗口与 `stream` 字段的完整规则。
- [最小回声机器人](/examples/01-minimal-echo-bot.md)：先跑通单帧回复。
- [事件回调与文件](/examples/03-template-card-and-file-download.md)：把流式与卡片、文件组合使用。