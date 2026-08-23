---
type: Reference
title: 常量与Token定义源码（src/tokens.ts）
description: 定义命名空间、插件ID、默认信令服务器、命令ID、PageConfig键名、IWebRtcManager接口与Token
tags: [tokens, constants, plugin-id, token, interface, lumino]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tokens-ts
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/src/tokens.ts
    title: src/tokens.ts - Constants and DI tokens
---

## tokens.ts 源码分析

本文件定义所有常量、插件 ID 和依赖注入 Token。

### 命名空间与插件ID

```typescript
export const NS = '@jupyterlite/webrtc-docprovider';
export const PLUGIN_ID = `${NS}:plugin`;           // 核心插件
export const FACTORY_PLUGIN_ID = `${NS}:factory`;   // 文档提供者工厂插件
export const STATUS_PLUGIN_ID = `${NS}:status`;     // JupyterLab状态栏插件
export const RETRO_STATUS_PLUGIN_ID = `${NS}:retro-status`; // RetroLab状态栏插件
```

### RetroLab页面常量

```typescript
export const RETRO_NOTEBOOK_PAGE = 'notebooks';
export const RETRO_EDIT_PAGE = 'edit';
export const RETRO_STATUS_PAGES = [RETRO_NOTEBOOK_PAGE, RETRO_EDIT_PAGE];
```

### 默认信令服务器

```typescript
export const DEFAULT_SIGNALING_SERVERS = [
  'wss://signaling.yjs.dev',
  'wss://y-webrtc-signaling-eu.herokuapp.com',
  'wss://y-webrtc-signaling-us.herokuapp.com',
];
```

3个公共信令服务器，分别位于：yjs.dev官方、Heroku EU、Heroku US。

### 本地主机列表

```typescript
export const LOCAL_HOSTS = ['127.0.0.1', 'localhost'];
```

用于判断是否为本地开发环境，本地环境下自动生成随机 roomPrefix。

### 命令ID

```typescript
export namespace CommandIds {
  export const disable = 'webrtc-docprovider:disable';
}
```

注册到 JupyterLab 命令系统的 toggle 命令 ID。

### PageConfig 键名

```typescript
export namespace PageOptions {
  export const urls = 'fullWebRtcSignalingUrls';
  export const prefix = 'webRtcRoomPrefix';
  export const collaborative = 'collaborative';
}
```

用于通过 `PageConfig.getOption()` 从页面配置中读取服务器端注入的配置值。

### IWebRtcManager 接口与Token

```typescript
export const IWebRtcManager = new Token<IWebRtcManager>(`${NS}:IWebRtcManager`);

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

使用 Lumino 的 `Token` 机制创建依赖注入 Token，其他插件可通过 `IWebRtcManager` 注入管理器实例。

## 相关概念

- [4个JupyterLab插件架构](/concepts/06-plugin-system.md)
- [配置三级优先级系统](/concepts/09-configuration.md)
- [房间ID与信令机制](/concepts/05-room-and-signaling.md)
