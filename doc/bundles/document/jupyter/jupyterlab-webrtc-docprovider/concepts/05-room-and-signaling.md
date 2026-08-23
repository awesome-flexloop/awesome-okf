---
type: Concept
title: 房间ID与信令机制
description: WebRTC房间通过SHA256哈希保护隐私，信令服务器协助Peer发现，支持多信令服务器容错和BroadcastChannel本地发现
tags: [room, sha256, privacy, signaling-server, webrtc, broadcastchannel, peer-discovery, p2p]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: manager-src
    resource: /references/manager-source.md
    title: src/manager.ts - Room and signaling logic
  - id: tokens-src
    resource: /references/tokens-source.md
    title: src/tokens.ts - Default signaling servers
  - id: provider-src
    resource: /references/provider-source.md
    title: src/provider.ts - Provider connection options
---

## WebRTC 协作网络模型

jupyterlab-webrtc-docprovider 的 P2P 协作网络由三层构成：

```
┌─────────────────────────────────────────────────────────┐
│                   Signaling Servers                      │
│  (wss://signaling.yjs.dev, wss://...eu..., wss://...us) │
│         仅交换元数据（SDP offer/answer/ICE candidates）  │
└─────────┬───────────────────────────┬───────────────────┘
          │ WebSocket                 │ WebSocket
          ▼                           ▼
┌─────────────────┐           ┌─────────────────┐
│   Browser A     │◄─WebRTC──►│   Browser B     │
│   (Peer A)      │  DataCh   │   (Peer B)      │
│                 │           │                 │
│ ┌─────────────┐ │           │ ┌─────────────┐ │
│ │Yjs Doc +    │ │           │ │Yjs Doc +    │ │
│ │Awareness    │ │           │ │Awareness    │ │
│ └─────────────┘ │           │ └─────────────┘ │
└────────┬────────┘           └────────┬────────┘
         │                           │
         │    ┌──────────────┐       │
         └────►BroadcastChannel◄──────┘
              │(同浏览器标签页)│
              └──────────────┘
```

1. **信令层**：WebSocket 连接到信令服务器，用于 Peer 发现和连接协商（SDP/ICE 交换）
2. **数据层**：WebRTC DataChannel 建立 P2P 连接，传输实际的文档数据
3. **本地层**：BroadcastChannel 在同一浏览器的标签页间直接通信，无需信令服务器

## 房间ID机制

### 房间命名层级

```
用户可见房间名 (roomName)
  │  例：?room=demo, 或设置中的 room, 或随机 UUID
  ▼
加上前缀 (roomPrefix)
  │  PageConfig / settings / (localhost ? UUID : origin)
  ▼
SHA256 哈希 → fullRoomId
  │  64字符十六进制字符串，发送到信令服务器
  ▼
拼接文档路径 (path)
  │  fullRoomId + documentPath → 实际 Yjs room 名
  ▼
y-webrtc room
```

### SHA256 隐私保护

```typescript
return codec.hex.fromBits(hash.sha256.hash(`${roomPrefix}-${roomName}`));
```

**为什么哈希？**
- 发送到公共信令服务器的是哈希值而非明文房间名
- 即使信令服务器被监控，也无法直接得知用户正在使用什么房间名
- roomPrefix 确保不同站点/部署的相同房间名产生不同的哈希值
- 哈希是单向的，无法从 roomId 反推 roomName

### roomPrefix 的安全作用

| 场景 | roomPrefix 值 | 效果 |
|------|--------------|------|
| 生产部署 | 自定义长前缀（≥10字符） | 强隔离，防止房间冲突 |
| 常规域名 | 站点 origin（如 `https://example.com`） | 按域名自动隔离 |
| localhost | 随机 UUID | 防止本地开发者意外互相连接 |
| 服务器配置 | PageConfig `webRtcRoomPrefix` | 部署级别的统一前缀 |

## 信令服务器

### 默认公共服务器

```typescript
export const DEFAULT_SIGNALING_SERVERS = [
  'wss://signaling.yjs.dev',                        // yjs 官方
  'wss://y-webrtc-signaling-eu.herokuapp.com',      // 欧洲节点
  'wss://y-webrtc-signaling-us.herokuapp.com',      // 美国节点
];
```

三个公共信令服务器提供地理冗余，客户端会连接到所有列出的服务器以增加发现概率。

### 信令服务器的作用

信令服务器**不传输文档内容**，仅负责：
1. **Peer 发现**：帮助同一房间的客户端找到彼此
2. **连接协商**：转发 SDP offer/answer 和 ICE candidates
3. **在线状态**：维护房间内的 peer 列表

一旦 WebRTC DataChannel 建立成功，数据直接在 peer 间传输，不再经过信令服务器。

### 配置自定义信令服务器

在 `overrides.json` 或设置中配置：

```json
{
  "@jupyterlite/webrtc-docprovider:plugin": {
    "signalingUrls": [
      "wss://your-signaling-server.example.com"
    ]
  }
}
```

URL 必须以 `ws://` 或 `wss://` 开头（由 JSON Schema 验证）。

> **生产环境建议**：不要依赖公共信令服务器。公共服务器不保证可用性、安全性和隐私。部署自己的信令服务器（如 [y-webrtc-signaling](https://github.com/yjs/y-webrtc/blob/master/bin/server.js)）。

### 通过 PageConfig 注入（部署级别）

Jupyter Server 可以在页面配置中注入信令服务器 URL：

```python
# 在 jupyter_server_config.py 中
c.LabServerApp.app_settings = {
    'fullWebRtcSignalingUrls': ['wss://your-server.com'],
    'webRtcRoomPrefix': 'your-unique-prefix',
}
```

## Peer 发现与连接流程

```
Browser A                    Signaling Server              Browser B
    │                              │                           │
    │─── WS: Join room(hash) ─────►│                           │
    │                              │◄─── WS: Join room(hash) ──│
    │                              │                           │
    │◄─── WS: Peer found ──────────│──── WS: Peer found ──────►│
    │                              │                           │
    │─── WS: SDP Offer ───────────►│─── WS: SDP Offer ────────►│
    │                              │                           │
    │◄── WS: SDP Answer ───────────│◄── WS: SDP Answer ────────│
    │                              │                           │
    │◄═══ ICE Candidates ═════════►│◄══ ICE Candidates ═══════►│
    │     (通过信令服务器交换)        │                           │
    │                              │                           │
    │◄═════ WebRTC DataChannel 建立 P2P 连接 ═════════════════►│
    │                                                          │
    │◄═══════════ Yjs CRDT 文档同步 + Awareness ══════════════►│
    │              (直接P2P，不经过服务器)                        │
```

## 连接参数

### maxConns

```typescript
maxConns: 20 + Math.floor(Math.random() * 15)  // 20~34
```

每个客户端最多与 20-34 个其他 peer 建立直接连接。Yjs 的 WebRTC 提供者会智能选择连接对象，不需要全连接网状拓扑。

### filterBcConns

```typescript
filterBcConns: true
```

过滤 BroadcastChannel 连接，避免与 WebRTC 连接重复。

## 同浏览器协作（BroadcastChannel）

同一浏览器内打开多个 JupyterLab 标签页时：
- 通过 `BroadcastChannel` API 直接通信
- 不经过信令服务器
- 不计入 WebRTC 连接数
- 在 peerCount 中单独统计（`bcConns.size`）

## 相关概念

- [WebRtcManager配置管理](/concepts/03-webrtc-manager.md)
- [WebRtcProvider文档提供者](/concepts/04-document-provider.md)
- [配置三级优先级系统](/concepts/09-configuration.md)
- [Vendor补丁与大消息传输](/concepts/08-vendor-patches.md)
