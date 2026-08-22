---
type: Concept
title: WebRtcManager 配置管理
description: WebRtcManager是扩展的核心协调器，实现三级配置优先级链（URL参数→用户设置→随机默认值）、SHA256房间ID生成、信令服务器选择和Peer计数
tags: [manager, configuration, priority, sha256, room, signaling, peer-count, lumino-signal]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: manager-src
    resource: /references/manager-source.md
    title: src/manager.ts - WebRtcManager class
  - id: tokens-src
    resource: /references/tokens-source.md
    title: src/tokens.ts - Constants and tokens
---

## WebRtcManager 概述

`WebRtcManager` 是整个扩展的核心协调类，实现 `IWebRtcManager` 接口，负责：

1. 管理配置的三级优先级解析
2. 创建 `WebRtcProvider` 文档提供者实例
3. 追踪 peer 连接数量
4. 通过 Lumino Signal 通知状态变更

## IWebRtcManager 接口

```typescript
export interface IWebRtcManager {
  createProvider(options: IDocumentProviderFactory.IOptions): IDocumentProvider;
  trans: TranslationBundle;
  username: string;
  usercolor: string;
  roomName: string;
  disabled: boolean;
  peerCount: number;
  signalingUrls: string[];
  stateChanged: ISignal<IWebRtcManager, void>;
}
```

## 三级配置优先级链

每个用户可配置属性都遵循相同的优先级模式：**URL 参数 > 插件设置 > 随机/默认值**。

```
URL 参数（?room=xxx&username=yyy）
  │ 最高优先级：临时分享场景，最灵活
  ▼
插件设置（Settings Editor / overrides.json）
  │ 中优先级：用户个人偏好持久化
  ▼
PageConfig / 随机默认值
  最低优先级：服务器部署配置 / 随机生成
```

### username 解析链

```typescript
get username(): string {
  return (
    this._urlParams.username ||    // ?username= 参数
    this._composite.username ||    // 设置中的 username
    this._randomParams.username    // getAnonymousUserName() 随机生成
  );
}
```

### usercolor 解析链

```typescript
get usercolor(): string {
  return (
    this._urlParams.usercolor ||   // ?usercolor= 参数
    this._composite.usercolor ||   // 设置中的 usercolor
    this._randomParams.usercolor   // getRandomColor().slice(1) 随机生成
  );
}
```

注意：`getRandomColor()` 返回带 `#` 前缀的颜色（如 `#e65100`），slice(1) 去掉 `#`。

### roomName 解析链

```typescript
get roomName(): string {
  return this._urlParams.room || this._composite.room || this._randomParams.room;
}
```

默认 room 使用 `UUID.uuid4()` 生成随机 UUID，不与他人共享。

### disabled 解析链

```typescript
get disabled(): boolean {
  const collaborative = PageConfig.getOption(PageOptions.collaborative) === 'true';
  if (!collaborative) {
    return true;  // 服务器未启用协作模式，强制禁用
  }
  return !!this._composite.disabled;  // 用户设置中的 disabled 选项
}
```

`disabled` 有一个额外的前置检查：如果服务器的 `collaborative` 配置为 false，则 WebRTC 始终禁用。

## 房间ID生成（fullRoomId）

房间 ID 不直接使用用户可见的 `roomName`，而是通过 SHA256 哈希生成混淆后的标识符：

```typescript
get fullRoomId(): string {
  const { roomName } = this;
  let roomPrefix =
    PageConfig.getOption(PageOptions.prefix) || this._composite.roomPrefix || null;

  if (roomPrefix == null) {
    const { hostname, origin } = window.location;
    roomPrefix = LOCAL_HOSTS.includes(hostname.toLowerCase())
      ? UUID.uuid4()    // localhost 使用随机前缀
      : origin;         // 非 localhost 使用 origin 作为前缀
  }

  return codec.hex.fromBits(hash.sha256.hash(`${roomPrefix}-${roomName}`));
}
```

### roomPrefix 解析

| 优先级 | 来源 | 适用场景 |
|--------|------|----------|
| 1 | PageConfig `webRtcRoomPrefix` | 服务器端部署配置 |
| 2 | Settings `roomPrefix` | 用户自定义前缀（≥10字符） |
| 3 | `window.location.origin` | 默认：使用站点域名 |
| 3特殊 | `UUID.uuid4()` | localhost/127.0.0.1 时随机生成 |

> **为什么 localhost 使用随机前缀？** 如果多个开发者在 localhost 上使用相同的房间名（如 `demo`），origin 相同（都是 `http://localhost:8888`），会导致意外连接到彼此的房间。随机前缀防止了本地开发时的房间冲突。

### SHA256 哈希

使用 `sjcl`（Stanford JavaScript Crypto Library）计算 SHA256 哈希：

```typescript
import { hash, codec } from 'sjcl';
const roomId = codec.hex.fromBits(hash.sha256.hash(`${roomPrefix}-${roomName}`));
```

哈希结果是64字符的十六进制字符串，作为实际的 y-webrtc 房间标识。

## 信令服务器选择

```typescript
get signalingUrls(): string[] {
  // 1. 优先尝试 PageConfig（服务器端注入）
  try {
    urls = JSON.parse(PageConfig.getOption(PageOptions.urls));
    if (urls && urls.length) return urls;
  } catch { /* 忽略解析错误 */ }

  // 2. 其次尝试用户设置
  urls = this._composite.signalingUrls || null;
  if (urls && urls.length) return urls;

  // 3. 最后使用默认公共服务器
  console.warn('Using default public WebRTC signaling servers: not recommended for production.');
  return DEFAULT_SIGNALING_SERVERS;
}
```

默认公共信令服务器：
- `wss://signaling.yjs.dev`（yjs 官方）
- `wss://y-webrtc-signaling-eu.herokuapp.com`（EU）
- `wss://y-webrtc-signaling-us.herokuapp.com`（US）

> **生产环境警告**：使用公共信令服务器时，控制台会输出警告。生产部署应配置私有信令服务器。

## createProvider 工厂方法

```typescript
createProvider = (options: IDocumentProviderFactory.IOptions): IDocumentProvider => {
  if (this.disabled) {
    return new ProviderMock();  // 禁用时返回空提供者
  }

  const rtcOptions: WebRtcProvider.IOptions = {
    ...options,
    room: this.fullRoomId,
    usercolor: this.usercolor,
    username: this.username,
    signalingUrls: this.signalingUrls,
  };

  const provider = new WebRtcProvider(rtcOptions);

  // 监听 peer 变化
  provider.on('peers', (...args: any[]) => {
    const { room } = provider;
    if (!room) return;
    this.peerCount = room.webrtcConns.size + room.bcConns.size;
  });

  return provider;
};
```

peerCount 计算：`webrtcConns.size`（WebRTC P2P 连接数）+ `bcConns.size`（BroadcastChannel 连接数）。

## 状态信号

```typescript
private _stateChanged: Signal<IWebRtcManager, void> = new Signal(this);
```

使用 Lumino 的 `Signal` 机制通知状态变更：
- 设置变更时触发
- peerCount 变化时触发
- 状态栏组件通过连接此信号实现自动刷新

## 初始化流程

```
new WebRtcManager(options)
  ├── _settings = options.settings || null
  ├── _settings?.changed.connect(() => _stateChanged.emit())
  ├── _urlParams = initUrlParams()
  │     └── 解析 ?room=, ?username=, ?usercolor=
  ├── _randomParams = initRandomParams()
  │     ├── room: UUID.uuid4()
  │     ├── usercolor: getRandomColor().slice(1)
  │     └── username: getAnonymousUserName()
  └── _trans = options.trans
```

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [WebRtcProvider文档提供者](/concepts/04-document-provider.md)
- [配置三级优先级系统](/concepts/09-configuration.md)
- [房间ID哈希与信令机制](/concepts/05-room-and-signaling.md)
