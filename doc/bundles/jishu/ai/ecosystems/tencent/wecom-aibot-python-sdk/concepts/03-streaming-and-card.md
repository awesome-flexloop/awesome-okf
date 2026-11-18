---
type: concept
title: 流式回复与模板卡片
description: 说明流式与卡片回复的报文结构、同 req_id 串行队列、100 条上限与 5 秒回执窗口
tags: [wecom, aibot, python-sdk, streaming]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 流式回复与模板卡片

## 六种回复形态

所有被动回复最终都落到同一条发送通道，差异只在 `cmd` 与 `body.msgtype`（F-039）：

| 方法 | `cmd` | `body` 关键字段 | 典型用途 |
|---|---|---|---|
| `reply()` | `aibot_respond_msg` | 自定义 `msgtype` 与内容 | 通用兜底 |
| `reply_stream()` | `aibot_respond_msg` | `msgtype=stream` + `stream` | 分段输出、打字机效果 |
| `reply_welcome()` | `aibot_respond_welcome_msg` | 调用方传入的 `body` | 进入会话欢迎语 |
| `reply_template_card()` | `aibot_respond_msg` | `msgtype=template_card` + `template_card` | 单次卡片 |
| `reply_stream_with_card()` | `aibot_respond_msg` | `msgtype=stream_with_template_card` | 流式正文 + 卡片 |
| `update_template_card()` | `aibot_respond_update_msg` | `response_type=update_template_card` | 更新已有卡片 |

依据分别为 F-036 ~ F-038、F-043、F-044、F-045、F-046。欢迎语有一条额外时限：docstring 明确要求「收到事件回调后需在 5 秒内发送回复，超时将无法发送欢迎语」（F-043）。

## 串行队列：流式的真实实现

`send_reply(req_id, body, cmd)` 不直接写 socket，而是把帧放入「以 `req_id` 为键」的队列，由处理协程逐条发送并等待回执（F-040、F-041、F-042）：

1. 队列长度达到 100 时，对本次请求的 future 调用 `set_exception(RuntimeError(...))`，不再入队；已有帧不受影响（F-040）。
2. 处理协程取 `queue[0]`，`await send(frame)`，再 `await ack_future`；只有收到回执才 `pop(0)` 并 `set_result`（F-042）。
3. 每条回复登记一个 `5.0` 秒定时器，超时对 future 调用 `set_exception(TimeoutError(...))`（F-041）。
4. 发送异常、回执异常或超时后同样 `pop(0)`，队列继续处理下一条（F-042）。

这解释了一个被「流式」二字掩盖的事实：**每一帧都要等到回执才发下一帧**。若一次回复拆成 N 帧，端到端耗时约等于 `N × RTT` 加上模型生成时间，二者串行叠加。因此流式分片应尽量粗，例如按句或按段，而不是按 token。

| 参数 | 取值 | 位置 | 后果 |
|---|---|---|---|
| 队列上限 | 100 条/`req_id` | `aibot/ws.py:100`（F-040） | 超出时新请求直接失败 |
| 回执超时 | 5.0 秒 | `aibot/ws.py:99`（F-041） | 超时抛 `TimeoutError` |
| 并发模型 | 同一 `req_id` 串行 | F-042 | 多协程并发写同一 `req_id` 会互相排队 |

## stream 字段的组装规则

`reply_stream` 先构造 `{"id": stream_id, "finish": finish, "content": content}`，然后按条件追加两个可选字段（F-037）：

- `msg_item`：**仅当** `finish` 为真、列表非空时才写入；提前传会被静默忽略（F-037）。
- `feedback`：仅当字典为真时才写入（F-037）。

请求体为 `{"msgtype": "stream", "stream": stream}`（F-038）。同一 `stream_id` 的多次调用会依次进入同一条串行队列，从而保证顺序；`finish=True` 只表示语义结束，不会自动清理队列，队列在最后一条回执后由处理协程移除（F-042）。

## 模板卡片

卡片内容由调用方自行构造，SDK 只负责包装（F-044）。`reply_template_card` 在 `feedback` 为真时把卡片改写为 `{**template_card, "feedback": feedback}`，请求体为 `{"msgtype": "template_card", "template_card": card}`（F-044）。卡片类型枚举包含 `text_notice`、`news_notice`、`button_interaction`、`vote_interaction`、`multiple_interaction` 五种（F-035）。

`reply_stream_with_card` 的 `stream` 组装规则与 `reply_stream` 完全一致，`template_card` 为真时写入 `body["template_card"]`；`card_feedback` 为真时先合并进卡片再写入（F-045）。实践上应只在第一帧携带卡片，后续帧省略，否则会重复渲染。

`update_template_card` 的请求体是 `{"response_type": "update_template_card", "template_card": ...}`，注意它不是 `msgtype` 结构；`userids` 非空时追加同名字段（F-046）。docstring 强调必须使用对应 `template_card_event` 的 `req_id`，因此它只能在事件回调内、基于该事件帧调用，不能拿普通消息帧的 `req_id` 复用（F-046）。

## 失败模式对照

| 现象 | 直接原因 | 处理 |
|---|---|---|
| `RuntimeError` 提示队列已满 | 单 `req_id` 累计超过 100 条 | 合并分片，或等待前序回执 |
| `TimeoutError` | 5 秒内未收到回执 | 降低发送频率，检查网络与服务端限流 |
| `RuntimeError: Reply ack error: errcode=...` | 对端返回非零错误码 | 按 `errcode` 排查报文合法性 |
| `msg_item` 未出现 | `finish` 为假或列表为空 | 仅在最后一帧传入 |
| 卡片更新失败 | 使用了非事件帧的 `req_id` | 在 `template_card_event` 回调内调用 |

## 延伸阅读

- [帧协议与事件分发](/concepts/02-frame-protocol.md)：`req_id` 如何同时承担关联与判别。
- [连接生命周期](/concepts/01-connection-lifecycle.md)：断连时待回执消息如何被清空。
- [流式回复示例](/examples/02-streaming-reply.md)：可分步运行的演示骨架。