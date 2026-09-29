---
type: concept
title: "多平台 IM 网关"
description: "IMGatewayManager 九平台实例管理与连通性测试、NimGateway 消息方法族、QQ 媒体下载限额与清理策略、扫码登录与配对审批通道。"
tags: [lobsterai, im, gateway, nim, qq, weixin, pairing]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# 多平台 IM 网关

本地优先架构（[/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md)）的一个自然推论：Agent 既然全部状态在本机，把它暴露到 IM 平台只需一个"反向桥"。LobsterAI 的 IM 网关把同一套人机协作协议（[/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)）扩展到九个 IM 平台，全部实现驻留主进程（F-la-025~F-la-028）。

## 一、IMGatewayManager：九平台统一管理器

`IMGatewayManager extends EventEmitter`（`src/main/im/imGatewayManager.ts`），其方法面分四组（F-la-028）：

| 方法组 | 成员 | 职责 |
|---|---|---|
| 生命周期 | `initialize`、`startAllEnabled`、`stopAll` | 启动时装载、按配置启停全部平台 |
| 配置 | `setConfig`、`getStatus`、`getStatusWithOpenClawRuntime`、`isConnected` | 配置热更新与状态查询 |
| 单平台控制 | `startGateway`、`stopGateway`、`testGateway` | 按平台启停与试连 |
| 平台连通性测试 | `testTelegramOpenClawConnectivity`/`testDiscordOpenClawConnectivity`/`testFeishuOpenClawConnectivity`/`testDingTalkOpenClawConnectivity`/`testWecomOpenClawConnectivity`/`testWeixinOpenClawConnectivity`/`testNimOpenClawConnectivity`/`testPopoOpenClawConnectivity`/`testQQOpenClawConnectivity`/`testEmailConnectivity` 等 | 保存配置前验证凭证 |

另有扫码登录流程方法：`weixinQrLoginStart`/`weixinQrLoginWait`、`popoQrLoginStart`/`popoQrLoginPoll`。

教学要点：**每个平台一个 `testXxx` 方法而非统一 test 接口**，因为各平台鉴权方式差异大（token 校验 vs 扫码登录 vs 应用凭证），各自实现试连才能给出可信的错误归因。连通性测试独立成方法组，使"保存前验证"与"运行时启停"两条路径解耦。

## 二、平台参数化 IPC 通道

渲染层经 `im:*` 通道族操作网关（F-la-039，见 [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)）：

```
im:{platform}:instance:add
im:{platform}:instance:delete
im:{platform}:instance:config:set
```

`{platform}` 覆盖 telegram、discord、feishu、dingtalk、wecom、weixin、nim、qq、email 九平台。另有平台无关的配对审批通道 `im:pairing:list` / `im:pairing:approve` / `im:pairing:reject`——陌生联系人首次触达 Agent 时进入配对队列，由用户在 GUI 审批，是 IM 入口的必要安全闸。

## 三、NimGateway：NIM 平台的方法族

`NimGateway extends EventEmitter`（`src/main/im/nimGateway.ts`）是有道智云 NIM SDK（`nim-web-sdk-ng`，F-la-004）的封装，方法按职责分四族（F-la-025）：

| 方法族 | 成员 |
|---|---|
| 生命周期 | `start`、`stop`、`updateConfig`、`reconnectIfNeeded` |
| 消息发送 | `sendText`、`sendLongText`、`sendMedia`、`sendReplyWithMedia`、`sendTeamReply`、`sendQChatReply` |
| 通知 | `sendNotification`、`sendConversationNotification` |
| 媒体与解析 | `cleanupMediaFiles`、`parseV2Attachment`、`handleIncomingMessage` |

`sendLongText` 独立成方法说明 NIM 平台有单条消息长度限制需分段；`sendReplyWithMedia`/`sendTeamReply`/`sendQChatReply` 区分回复、群聊、圈组三种投递场景。配套 `nimQChatClient.ts` 导出 `QChatMessagePayload`、`QChatInboundMessage`、`QChatClientOptions` 接口与 `NimQChatClient` 类（`setNim`、`normalizeMessage`、`parseMessage`、`initListeners`、`activate`、`discoverJoinedServers`、`subscribeServer`、`sendText`、`stop`），把 QChat（圈组）能力从主网关中剥离为独立客户端（F-la-026）。

## 四、QQ 媒体下载：限额与清理策略

`qqMediaDownload.ts` 展示了一个务实的媒体落地策略（F-la-027）：

- `MAX_FILE_SIZE = 25MB`：单文件下载上限，超限即拒；
- `INBOUND_DIR = 'qq-inbound'`：`getQQMediaDir()` 返回 userData 下的媒体目录；
- `mapQQMediaType` 将 image/video/audio/voice 统一映射为 document 类型；
- `downloadQQAttachment(url, type, fileName?)` 返回 `{localPath, fileSize, mimeType}` 或 `null`；
- `cleanupOldQQMediaFiles(maxAgeDays = 7)`：默认清理 7 天前文件。

教学要点：IM 入站媒体是"不受控的用户上传"，必须同时有**尺寸上限**（防磁盘炸弹）、**独立目录**（与配置数据隔离）、**定期清理**（默认 7 天，防磁盘膨胀）三道闸。返回 `null` 而非抛异常的失败语义，让网关层可以把"下载失败"降级为"消息无附件"继续投递。

## 五、与 OpenClaw 插件的关系

package.json 的 `openclaw.plugins` 列出 10 个插件，其中 dingtalk-connector、qqbot、discord、wecom-openclaw-plugin、openclaw-weixin、moltbot-popo、openclaw-nim-channel、clawemail-email 等直接对应 IM 平台（F-la-006）——部分平台经 OpenClaw 插件接入运行时，与本地的 IM 网关并存，形成"本地网关管连接与会话、OpenClaw 插件管运行时集成"的双轨。

## 设计启示

1. 多平台网关用"管理器 + 每平台客户端"两层组织，管理器统一生命周期与状态，平台差异下沉到各自客户端；
2. 平台连通性测试独立成方法组，保存前验证与运行时启停分离；
3. 入站媒体必须配齐尺寸上限、独立目录、定期清理三件套；
4. 陌生联系人配对审批是 IM 入口的必备安全闸。

## 相关概念

- [/concepts/00-overall-architecture.md](00-overall-architecture.md)
- [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)
- [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)
