---
type: Reference
title: WebRtcManager源码（src/manager.ts）
description: WebRtcManager类实现，负责配置解析、URL参数处理、房间ID生成、信令服务器选择、Peer计数管理
tags: [manager, configuration, factory, room, signaling, priority-chain]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: manager-ts
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/src/manager.ts
    title: src/manager.ts - WebRtcManager class
---

## manager.ts 源码分析

`WebRtcManager` 类实现 `IWebRtcManager` 接口，是整个扩展的核心协调器。

### 类结构

```typescript
export class WebRtcManager implements IWebRtcManager {
  constructor(options: WebRtcManager.IOptions)
  createProvider = (options: IDocumentProviderFactory.IOptions): IDocumentProvider
  // ... getters
}
```

### 构造函数

接收 `IOptions`（含可选 `settings` 和必填 `trans`），初始化：
- `_settings`: 设置注册表对象（可为 null）
- `_urlParams`: 通过 `initUrlParams()` 解析 URL 查询参数
- `_randomParams`: 通过 `initRandomParams()` 生成随机默认值
- `_trans`: 翻译 bundle
- 设置变更时触发 `_stateChanged` 信号

### createProvider 方法（工厂方法）

1. 如果 `disabled` 为 true，返回 `ProviderMock`（空提供者，不实际共享）
2. 组装 `WebRtcProvider.IOptions`：包含 room（fullRoomId）、usercolor、username、signalingUrls
3. 创建 `WebRtcProvider` 实例
4. 监听 `'peers'` 事件，更新 `peerCount` = `room.webrtcConns.size + room.bcConns.size`
5. 返回 provider

### 三级优先级配置链

每个配置属性都遵循 **URL参数 → 插件设置 → 随机/默认值** 的优先级链：

| 属性 | Getter | URL参数 | Settings | 默认值 |
|------|--------|---------|----------|--------|
| `disabled` | `disabled` | - | `settings.composite.disabled` | PageConfig `collaborative` 为 false 时禁用 |
| `username` | `username` | `?username=` | `settings.composite.username` | `getAnonymousUserName()` |
| `usercolor` | `usercolor` | `?usercolor=` | `settings.composite.usercolor` | `getRandomColor().slice(1)` |
| `roomName` | `roomName` | `?room=` | `settings.composite.room` | `UUID.uuid4()` |
| `signalingUrls` | `signalingUrls` | - | PageConfig JSON → settings.composite | `DEFAULT_SIGNALING_SERVERS` |

### fullRoomId 计算

```typescript
get fullRoomId(): string {
  let roomPrefix = PageConfig.getOption(PageOptions.prefix) || this._composite.roomPrefix || null;
  if (roomPrefix == null) {
    const { hostname, origin } = window.location;
    roomPrefix = LOCAL_HOSTS.includes(hostname.toLowerCase()) ? UUID.uuid4() : origin;
  }
  return codec.hex.fromBits(hash.sha256.hash(`${roomPrefix}-${roomName}`));
}
```

- roomPrefix 来源：PageConfig `webRtcRoomPrefix` → settings.roomPrefix → （localhost 时用 UUID，否则用 origin）
- 最终 room ID = SHA256(`${roomPrefix}-${roomName}`) 的十六进制表示
- 使用 `sjcl` 库进行哈希计算

### initUrlParams

解析 `window.location.search` 中的 `room`、`username`、`usercolor` 参数。

### initRandomParams

- room: `UUID.uuid4()` 生成随机 UUID
- usercolor: `getRandomColor().slice(1)`（去掉 `#` 前缀）
- username: `getAnonymousUserName()`（来自 `@jupyterlab/docprovider`）

### 命名空间类型

```typescript
export namespace WebRtcManager {
  export interface IOptions { settings?: ISettingRegistry.ISettings | null; trans: TranslationBundle; }
  export interface IURLParams { room: string | null; username: string | null; usercolor: string | null; }
  export interface IRandomParams extends IURLParams { room: string; username: string; usercolor: string; }
}
```

## 相关概念

- [配置三级优先级系统](../concepts/09-configuration.md)
- [房间ID哈希与隐私保护](../concepts/05-room-and-signaling.md)
- [WebRtcProvider文档提供者](../concepts/04-document-provider.md)
