---
type: Concept
title: 架构总览
description: jupyterlab-webrtc-docprovider的四插件架构：核心插件(Manager)、工厂插件(ProviderFactory)、状态栏插件(StatusBar)和RetroLab适配插件
tags: [architecture, plugin, manager, provider, factory, status, lumino, di]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-src
    resource: /references/plugin-source.md
    title: src/plugin.ts - Plugin definitions
  - id: manager-src
    resource: /references/manager-source.md
    title: src/manager.ts - WebRtcManager
  - id: provider-src
    resource: /references/provider-source.md
    title: src/provider.ts - WebRtcProvider
---

## 整体架构

jupyterlab-webrtc-docprovider 采用 JupyterLab 标准的多插件架构，由4个 `JupyterFrontEndPlugin` 组成，通过 Lumino 的依赖注入（DI）系统协作。

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    JupyterLab App                        │
│                                                          │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │  Plugin     │   │FactoryPlugin │   │ StatusPlugin │  │
│  │ (Manager)   │──▶│(ProviderFactory)│  │ (StatusBar)  │  │
│  │             │   │              │   │              │  │
│  │ IWebRtc-    │   │ IDocument-   │   │ WebRtcStatus │  │
│  │ Manager     │   │ Provider-    │   │ (VDomRender) │  │
│  │             │   │ Factory      │   │              │  │
│  └──────┬──────┘   └──────┬───────┘   └──────┬───────┘  │
│         │                 │                   │          │
│         │           ┌─────▼─────┐             │          │
│         │           │WebRtc-    │◀────────────┘          │
│         └──────────▶│Provider   │  stateChanged signal  │
│                     │(y-webrtc) │                        │
│                     └─────┬─────┘                        │
│                           │                              │
│              ┌────────────┼────────────┐                 │
│              │            │            │                  │
│         ┌────▼───┐  ┌────▼───┐  ┌─────▼────┐           │
│         │Signaling│  │WebRTC  │  │Broadcast │           │
│         │Servers  │  │DataCh  │  │Channel   │           │
│         └────────┘  └────────┘  └──────────┘           │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │         RetroStatusPlugin (RetroLab适配)           │  │
│  │   Notebook/Editor Toolbar → WebRtcStatus           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 四个插件详解

### 1. 核心插件（plugin）

- **插件ID**：`@jupyterlite/webrtc-docprovider:plugin`
- **提供服务**：`IWebRtcManager`（通过 DI 系统供其他插件注入）
- **可选依赖**：`ISettingRegistry`（用户设置）、`ITranslator`（国际化）、`ICommandPalette`（命令面板）
- **职责**：
  - 创建并配置 `WebRtcManager` 实例
  - 注册 "Toggle WebRTC Sharing" 命令（开关协作）
  - 将命令添加到命令面板

### 2. 工厂插件（factoryPlugin）

- **插件ID**：`@jupyterlite/webrtc-docprovider:factory`
- **提供服务**：`IDocumentProviderFactory`（替换 JupyterLab 默认的文档提供者工厂）
- **必须依赖**：`IWebRtcManager`
- **职责**：
  - 将 `manager.createProvider` 方法作为 `IDocumentProviderFactory` 注册
  - 当 JupyterLab 需要为文档创建协作提供者时，调用此工厂方法
  - 如果 WebRTC 被禁用，工厂返回 `ProviderMock`（空实现）

### 3. 状态栏插件（statusPlugin）

- **插件ID**：`@jupyterlite/webrtc-docprovider:status`
- **必须依赖**：`IWebRtcManager`
- **可选依赖**：`IStatusBar`
- **职责**：
  - 创建 `WebRtcStatus.Model` 和 `WebRtcStatus` VDom 组件
  - 注册到 JupyterLab 状态栏右侧位置
  - 通过 `stateChanged` 信号实时更新显示

### 4. RetroLab 适配插件（retroStatusPlugin）

- **插件ID**：`@jupyterlite/webrtc-docprovider:retro-status`
- **必须依赖**：`IWebRtcManager`
- **职责**：
  - 检测是否运行在 RetroLab 环境（通过 `PageConfig.getOption('retroPage')`）
  - 为 Notebook 和 Editor 类型的 widget 创建工具栏扩展
  - 在工具栏中添加 `WebRtcStatus` 组件

## 核心类关系

```
WebRtcManager (implements IWebRtcManager)
  ├── createProvider() → WebRtcProvider
  ├── username/usercolor/roomName (3-tier priority getters)
  ├── fullRoomId (SHA256 hash)
  ├── signalingUrls (PageConfig → Settings → Defaults)
  ├── disabled (collaborative flag → settings)
  └── stateChanged: Signal

WebRtcProvider (extends WebrtcProvider from y-webrtc, implements IDocumentProvider)
  ├── constructor: super(roomId+path, ydoc, options)
  ├── requestInitialContent(): Promise<boolean>
  ├── acquireLock()/releaseLock() (no-op for WebRTC)
  └── awareness: Awareness (CRDT awareness protocol)

WebRtcStatus (extends VDomRenderer<Model>)
  ├── render(): JSX.Element (peer count + icon + room name)
  └── Model (extends VDomModel)
      └── manager: IWebRtcManager (connects stateChanged signal)
```

## 数据流

1. 用户打开文档 → JupyterLab 调用 `IDocumentProviderFactory.createProvider(options)`
2. `factoryPlugin` 将调用转发给 `WebRtcManager.createProvider(options)`
3. `WebRtcManager` 检查 `disabled` 状态，组装配置，创建 `WebRtcProvider`
4. `WebRtcProvider` 继承 y-webrtc 的 `WebrtcProvider`：
   - 连接到信令服务器发现 peer
   - 通过 WebRTC DataChannel 建立 P2P 连接
   - 通过 BroadcastChannel 发现同浏览器的 peer
   - 使用 Yjs CRDT 同步文档内容和 Awareness 状态（光标/用户名/颜色）
5. Peer 连接变化触发 `'peers'` 事件 → 更新 `peerCount` → 状态栏自动刷新

## 关键设计决策

1. **工厂模式替换默认Provider**：通过提供 `IDocumentProviderFactory` 替换 JupyterLab 内置的 WebSocket 提供者，实现了无缝的传输层切换
2. **三级配置优先级**：URL 参数最高（临时分享）、用户设置次之（个人偏好）、PageConfig/默认值最低（部署配置）
3. **SHA256 房间ID混淆**：房间名+前缀经过 SHA256 哈希后发送到信令服务器，避免房间名泄露
4. **maxConns 随机化**：20-34 随机值减少多个客户端同时形成网状集群的概率
5. **ProviderMock 降级**：禁用时返回空提供者而非 null，保证 JupyterLab 文档系统正常运行

## 相关概念

- [项目介绍](00-introduction.md)
- [安装与快速开始](01-getting-started.md)
- [WebRtcManager配置管理](03-webrtc-manager.md)
- [WebRtcProvider文档提供者](04-document-provider.md)
- [4个JupyterLab插件详解](06-plugin-system.md)
