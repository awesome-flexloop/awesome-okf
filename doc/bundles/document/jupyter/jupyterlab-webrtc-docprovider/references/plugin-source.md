---
type: Reference
title: JupyterLab插件注册源码（src/plugin.ts）
description: jupyterlab-webrtc-docprovider的4个JupyterFrontEndPlugin定义，包括核心插件、工厂插件、状态栏插件和RetroLab状态栏插件
tags: [plugin, jupyterlab, registration, activation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-ts
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/src/plugin.ts
    title: src/plugin.ts - Plugin definitions
---

## plugin.ts 源码分析

本文件导出4个 `JupyterFrontEndPlugin`，构成扩展的全部注册入口。

### 核心插件（plugin）

- **ID**: `@jupyterlite/webrtc-docprovider:plugin`（`PLUGIN_ID`）
- **provides**: `IWebRtcManager`
- **autoStart**: `true`
- **optional依赖**: `ISettingRegistry`, `ITranslator`, `ICommandPalette`
- **activate 函数逻辑**:
  1. 创建 `WebRtcManager.IOptions`，加载翻译 bundle
  2. 如果有 `ISettingRegistry`，尝试加载设置（try/catch 容错）
  3. 注册命令 `webrtc-docprovider:disable`（toggle 命令，控制 `disabled` 设置项）
  4. 如果有 `ICommandPalette`，将命令添加到命令面板的 "WebRTC Sharing" 分类
  5. 实例化 `WebRtcManager` 并返回

### 工厂插件（factoryPlugin）

- **ID**: `@jupyterlite/webrtc-docprovider:factory`（`FACTORY_PLUGIN_ID`）
- **provides**: `IDocumentProviderFactory`
- **requires**: `IWebRtcManager`
- **activate**: 返回 `manager.createProvider` 方法作为工厂函数

### 状态栏插件（statusPlugin）

- **ID**: `@jupyterlite/webrtc-docprovider:status`（`STATUS_PLUGIN_ID`）
- **requires**: `IWebRtcManager`
- **optional**: `IStatusBar`
- **activate**: 创建 `WebRtcStatus.Model` 和 `WebRtcStatus` 组件，注册到状态栏右侧（`align: 'right'`）

### RetroLab状态栏插件（retroStatusPlugin）

- **ID**: `@jupyterlite/webrtc-docprovider:retro-status`（`RETRO_STATUS_PLUGIN_ID`）
- **requires**: `IWebRtcManager`
- **activate 逻辑**:
  1. 通过 `PageConfig.getOption('retroPage')` 检测是否在 RetroLab 环境
  2. 创建 `DocumentRegistry.IWidgetExtension`，在 Notebook 和 Editor 的工具栏中添加状态项
  3. 对于 Editor 页面（`RETRO_EDIT_PAGE`），在状态项前添加 spacer
  4. 返回 `DisposableDelegate` 用于清理

### 导出

```typescript
export default [plugin, statusPlugin, factoryPlugin, retroStatusPlugin];
```

以数组形式默认导出全部4个插件，供 JupyterLab 扩展系统批量注册。

## 相关概念

- [WebRtcManager配置管理](/concepts/03-webrtc-manager.md)
- [4个JupyterLab插件架构](/concepts/06-plugin-system.md)
- [状态栏UI与RetroLab适配](/concepts/07-status-bar.md)
