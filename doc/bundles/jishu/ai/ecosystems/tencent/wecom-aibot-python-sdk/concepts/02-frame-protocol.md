---
type: concept
title: 帧协议与事件分发
description: 拆解 WsFrame、WsCmd 与 req_id 路由规则，说明一帧从入站到事件回调的完整路径
tags: [wecom, aibot, python-sdk, protocol]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 帧协议与事件分发

## 帧的物理形状

SDK 不定义帧类，`WsFrame` 与 `WsFrameHeaders` 都只是 `Dict[str, Any]` 的类型别名（F-015）。因此所有字段访问都是字典取值，缺字段时返回 `None`，不会抛属性异常。注释声明的字段如下（F-029）：

| 字段 | 类型 | 是否必填 | 含义 |
|---|---|---|---|
| `cmd` | `str` | 否 | 命令字；下行推送类帧才有，回执类帧通常没有 |
| `headers` | `dict` | 是 | 至少包含 `req_id` |
| `headers.req_id` | `str` | 是 | 请求关联 ID，同时承担类型判别职责 |
| `body` | `Any` | 否 | 业务载荷；消息与事件帧的核心内容 |
| `errcode` | `int` | 否 | 回执错误码，`0` 表示成功 |
| `errmsg` | `str` | 否 | 错误描述 |

## 命令字典

`WsCmd` 按方向分成两组，共 8 个常量（F-030、F-031）：

| 方向 | 常量 | 字符串值 | 用途 |
|---|---|---|---|
| 开发者 → 企微 | `SUBSCRIBE` | `aibot_subscribe` | 认证订阅 |
| 开发者 → 企微 | `HEARTBEAT` | `ping` | 心跳 |
| 开发者 → 企微 | `RESPONSE` | `aibot_respond_msg` | 被动回复 |
| 开发者 → 企微 | `RESPONSE_WELCOME` | `aibot_respond_welcome_msg` | 欢迎语回复 |
| 开发者 → 企微 | `RESPONSE_UPDATE` | `aibot_respond_update_msg` | 更新模板卡片 |
| 开发者 → 企微 | `SEND_MSG` | `aibot_send_msg` | 主动发送 |
| 企微 → 开发者 | `CALLBACK` | `aibot_msg_callback` | 消息推送 |
| 企微 → 开发者 | `EVENT_CALLBACK` | `aibot_event_callback` | 事件推送 |

## req_id：关联键兼判别键

`generate_req_id(prefix)` 返回 `f"{prefix}_{毫秒时间戳}_{8位随机串}"`，随机串由 `os.urandom` 生成（F-032）。它承担两项职责：

1. **关联**：被动回复必须沿用入站帧的 `req_id`，服务端据此把回复挂到原消息上（F-039）。
2. **判别**：无 `cmd` 的下行帧靠 `req_id` 前缀区分认证响应、心跳响应与回复回执（F-024）。

这带来一个反常识约束：前缀不是自由标签。若业务自造的 `req_id` 以 `ping` 或 `aibot_subscribe` 开头，就可能被误判为心跳或认证响应，真正的回执永远等不到（F-024）。

## 下行帧的四条路由

`_handle_frame` 先看 `cmd`，再退回 `req_id`，顺序如下：

| 顺序 | 条件 | 去向 | 依据 |
|---|---|---|---|
| 1 | `cmd == aibot_msg_callback` | `on_message(frame)` | F-031、F-047 |
| 2 | `cmd == aibot_event_callback` | `on_message(frame)` | F-031、F-048 |
| 3 | 无 `cmd` 且 `req_id` 命中待回执表 | 交给回执处理，唤醒等待中的 future | F-039、F-042 |
| 4 | 无 `cmd` 且以 `aibot_subscribe` / `ping` 开头 | 认证或心跳响应分支 | F-024 |
| 5 | 其余 | 记 `warn` 后仍转发 `on_message` | `aibot/ws.py:275-278` |

第 5 条意味着「未知帧」不会静默丢弃，而是继续下探到 `MessageHandler`，由后者按 `body.msgtype` 决定是否处理。

## 事件分发：先广播，再定向

`MessageHandler.handle_frame` 有一道统一前置校验：`body` 为空或 `body["msgtype"]` 缺失时记 `warn` 并直接返回（F-047）。**这条规则同时适用于消息帧和事件帧**，所以事件推送也必须携带 `msgtype`，否则不会到达任何业务处理器。

| 帧类型 | 第一次广播 | 第二次广播 | 依据 |
|---|---|---|---|
| 消息帧 | `message` | 按 `msgtype` 分发到 `message.text` / `image` / `mixed` / `voice` / `file` | F-049 |
| 事件帧 | `event` | 取 `body.event.eventtype` 分发到 `event.<eventtype>`；为空时只记 `debug` | F-048 |

因此每个业务处理器可能被调用两次：先收到泛化的 `message`，再收到具体的 `message.text`。若同时在两处做回复，会造成重复应答。事件同理，`event` 与 `event.enter_chat` 都会触发。

## 上行帧如何组装

被动回复由 `reply()` 统一组帧：`{"cmd": cmd, "headers": {"req_id": 入站 req_id}, "body": body}`，`cmd` 缺省为 `RESPONSE`（F-039）。不同语义只改两处：`cmd` 与 `body.msgtype`。

主动发送是唯一例外：它没有入站 `req_id` 可复用，因此用 `generate_req_id("aibot_send_msg")` 新造一个，并把 `chatid` 并入请求体，组为 `{"chatid": chatid, **body}`（F-043）。

## 类型枚举

| 枚举 | 成员 | 依据 |
|---|---|---|
| `MessageType` | `text`、`image`、`mixed`、`voice`、`file` | F-033 |
| `EventType` | `enter_chat`、`template_card_event`、`feedback_event` | F-034 |
| `TemplateCardType` | `text_notice`、`news_notice`、`button_interaction`、`vote_interaction`、`multiple_interaction` | F-035 |

枚举成员与字符串一一对应，可直接用于事件名或 `msgtype` 比较；但 SDK 内部并未强制校验，拼写错误不会在发送前报错。

## 延伸阅读

- [连接生命周期](/concepts/01-connection-lifecycle.md)：认证与心跳响应如何被前缀分支消费。
- [流式回复与模板卡片](/concepts/03-streaming-and-card.md)：`req_id` 在串行队列与卡片更新中的复用。
- [文件下载与解密](/concepts/04-file-download-decrypt.md)：`message.image` / `message.file` 载荷中的 URL 与 `aeskey`。