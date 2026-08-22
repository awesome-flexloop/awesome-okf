---
type: Concept
title: JupyterLab扩展注册机制
description: jupyterlite-xeus如何通过JupyterLab插件系统注册内核规格、提供kernel factory、管理日志通道和empack环境元数据
tags: [extension, jupyterlab, plugin, kernel-spec, token, registration, lumino]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: extension
    resource: /references/extension-source.md
    title: 扩展注册参考
  - id: kernel-impl
    resource: /references/kernel-impl-source.md
    title: WebWorkerKernel实现
---

## JupyterLab 插件系统基础

JupyterLab 使用基于 Token 的依赖注入（DI）系统，通过 Lumino 插件机制注册功能。每个插件是一个包含 `id`、`requires`、`optional`、`provides`、`activate` 和 `autoStart` 的对象。

jupyterlite-xeus 注册了三个插件：

| 插件ID | 职责 | autoStart |
|--------|------|-----------|
| `@jupyterlite/xeus-extension:kernel` | 注册xeus内核到JupyterLite | true |
| `@jupyterlite/xeus-extension:xeus-logs` | 提供日志通道管理服务 | true |
| `@jupyterlite/xeus-extension:empack-env-meta` | 缓存和提供empack环境元数据 | true |

## kernelPlugin：内核注册插件

这是核心插件，负责将xeus内核注册到JupyterLite的内核系统。

### 依赖注入

```typescript
const kernelPlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlite/xeus-extension:kernel',
  autoStart: true,
  requires: [IServiceManager, IKernelSpecs, IBrowserContext],
  activate: (app, serviceManager, kernelSpecs, browserContext) => {
    // 插件激活逻辑
  }
};
```

| Token | 来源 | 用途 |
|-------|------|------|
| `IServiceManager` | `@jupyterlab/services` | 访问JupyterLite服务管理器（Contents API、Session等） |
| `IKernelSpecs` | `@jupyterlite/kernel` | JupyterLite内核规格注册表（注册新内核） |
| `IBrowserContext` | `@jupyterlite/browser` | 浏览器上下文ID（区分多个tab/页面） |

### 激活流程

```
activate()
  │
  ├─→ 等待 serviceManager.ready
  │
  ├─→ fetch {baseUrl}xeus/kernels.json
  │     ↓
  │   解析 kernelsData.kernels 列表
  │
  └─→ 对每个 kernelSpec:
        │
        ├─→ 构造 kernelUrl = baseUrl + 'xeus/kernels/' + spec.dir
        │
        ├─→ fetch {kernelUrl}/kernel.json
        │     ↓
        │   获取完整内核规格（argv、display_name、language、metadata等）
        │
        ├─→ 构造 resources 对象（logo图片URL映射）
        │
        └─→ kernelSpecs.register({
              name: kernelSpec.name,
              spec: kernelSpec,
              create: async (options) => {
                return new WebWorkerKernel({
                  ...options,
                  contentsManager: serviceManager.contents,
                  kernelSpec,
                  browsingContextId: await browserContext.currentId,
                });
              }
            });
```

### kernels.json 结构

构建时由 [write_empack_config()](../references/python-addon-source.md#write_empack_config) 生成：

```json
{
  "kernels": [
    {
      "name": "xpython",
      "dir": "xpython",
      "display_name": "Python (XPython)",
      "language": "python"
    }
  ]
}
```

- `name`：内核标识名（对应kernel.json中的name）
- `dir`：内核文件在 `xeus/kernels/` 下的子目录
- `display_name`：JupyterLab Launcher中显示的名称
- `language`：编程语言标识

### kernel.json 结构

复制自xeus内核包或构建时生成：

```json
{
  "argv": ["xeus/kernels/xpython/xpython.js"],
  "display_name": "Python (XPython)",
  "language": "python",
  "interrupt_mode": "message",
  "metadata": {
    "shared": {
      "libxeus.so": "xeus/xpython/libxeus.so"
    },
    "kernel_type": "xeus"
  },
  "name": "xpython",
  "resources": {
    "kernel-64x64.png": "xeus/kernels/xpython/kernel-64x64.png",
    "logo-64x64.png": "xeus/kernels/xpython/logo-64x64.png",
    "logo-svg.svg": "xeus/kernels/xpython/logo-svg.svg"
  }
}
```

关键字段：
- `argv[0]`：内核JS入口文件路径（相对于baseUrl）
- `metadata.shared`：预链接共享库的URL映射
- `metadata.kernel_type`：标识为xeus内核类型
- `resources`：内核图标资源URL

### create 工厂函数

用户选择xeus内核时，JupyterLite调用 `create(options)` 创建内核实例：

```typescript
create: async (options) => new WebWorkerKernel({
  id: options.id,
  name: options.name,
  location: options.location,
  sendMessage: options.sendMessage,
  contentsManager: serviceManager.contents,
  mountDrive: true,
  kernelSpec,
  browsingContextId: await browserContext.currentId,
  empackEnvMetaLink: kernelSpec.resources?.empackEnvMetaLink,
})
```

`options` 来自 JupyterLite 的内核创建请求，包含 `id`、`name`、`location`、`sendMessage` 等。

## XeusLogManager：日志服务

```typescript
const logPlugin: JupyterFrontEndPlugin<IXeusLogManager> = {
  id: '@jupyterlite/xeus-extension:xeus-logs',
  autoStart: true,
  optional: [ILogger],
  provides: IXeusLogManager,
  activate: (app, logger) => new XeusLogManager(logger)
};
```

### 功能

Worker端通过 BroadcastChannel 发送日志，XeusLogManager 负责接收并路由：

```typescript
class XeusLogManager implements IXeusLogManager {
  registerLogChannel(channel: string, kernelId?: string): BroadcastChannel {
    const channelName = kernelId
      ? `xeus-log-${channel}-${kernelId}`
      : `xeus-log-${channel}`;
    const bc = new BroadcastChannel(channelName);
    bc.onmessage = (event) => {
      const { level, message } = event.data;
      if (this._logger) {
        switch(level) {
          case 'info': this._logger.log(message); break;
          case 'warning': this._logger.warn(message); break;
          case 'critical': this._logger.error(message); break;
        }
      } else {
        // fallback to console
        console[level === 'critical' ? 'error' : level](message);
      }
    };
    return bc;
  }
}
```

### 日志级别映射

| Worker端级别 | BroadcastChannel level | JupyterLab ILogger | Console fallback |
|-------------|----------------------|-------------------|-----------------|
| `logger.log()` | info | logger.log() | console.log() |
| `logger.warn()` | warning | logger.warn() | console.warn() |
| `logger.error()` | critical | logger.error() | console.error() |

### Worker端日志使用

[XeusWorkerLoggerBase](../references/kernel-base-source.md#xeusworkerloggerbase-类) 在Worker端创建对应名称的BroadcastChannel发送日志：

```typescript
// Worker端
const logger = new XeusWorkerLogger('kernel');
logger.log('Kernel initialized');  // → BroadcastChannel 'xeus-log-kernel'
logger.warn('Slow FS operation');  // → warning level
logger.error('WASM load failed');  // → critical level + stderr
```

## EmpackEnvMetaManager：环境元数据服务

```typescript
const empackMetaPlugin: JupyterFrontEndPlugin<IEmpackEnvMetaManager> = {
  id: '@jupyterlite/xeus-extension:empack-env-meta',
  autoStart: true,
  requires: [IKernelSpecs, IBrowserContext],
  provides: IEmpackEnvMetaManager,
  activate: (app, kernelSpecs, browserContext) => new EmpackEnvMetaManager(kernelSpecs, browserContext)
};
```

### 作用

缓存 empack_env_meta.json 内容，避免重复fetch：

```typescript
class EmpackEnvMetaManager implements IEmpackEnvMetaManager {
  async getEnvMetadata(kernelSpec: ISpecModel): Promise<unknown | undefined> {
    const key = kernelSpec.dir + kernelSpec.name;
    if (this._cache.has(key)) return this._cache.get(key);

    const kernelUrl = PageConfig.getBaseUrl() + 'xeus/kernels/' + kernelSpec.dir;
    try {
      const response = await fetch(kernelUrl + '/empack_env_meta.json');
      if (!response.ok) return undefined;
      const meta = await response.json();
      this._cache.set(key, meta);
      return meta;
    } catch {
      return undefined;
    }
  }
}
```

> 注意：当前 `WebWorkerKernel.initRemote()` 直接传递 `empackEnvMetaLink`（如果kernelSpec.resources中有），Worker端直接fetch。EmpackEnvMetaManager为其他需要环境元数据的组件提供缓存服务。

## Token定义

```typescript
// 日志服务Token
export const IXeusLogManager = new Token<IXeusLogManager>(
  '@jupyterlite/xeus:IXeusLogManager',
  'A service to manage xeus logs channels.'
);

// 环境元数据服务Token
export const IEmpackEnvMetaManager = new Token<IEmpackEnvMetaManager>(
  '@jupyterlite/xeus:IEmpackEnvMetaManager',
  'A service to provide empack environment metadata.'
);
```

Token 是JupyterLab DI系统的核心——其他插件通过Token声明依赖，运行时注入对应实现。

## IBrowserContext 的作用

`IBrowserContext`（来自 `@jupyterlite/browser`）是JupyterLite v0.6+引入的服务，提供：

```typescript
interface IBrowserContext {
  currentId: Promise<string>;  // 当前浏览上下文（tab/iframe）的唯一ID
}
```

**为什么需要**：
- SharedBufferContentsAPI和DriveFS需要区分不同的浏览上下文
- 一个用户可能打开多个JupyterLite tab，每个tab有独立的Service Worker上下文
- `browsingContextId` 用于正确路由Contents API请求到正确的上下文

在kernelPlugin中：
```typescript
create: async (options) => new WebWorkerKernel({
  ...,
  browsingContextId: await browserContext.currentId,
})
```

## 插件导出

三个插件通过数组导出：

```typescript
const plugins: JupyterFrontEndPlugin<any>[] = [
  kernelPlugin,
  logPlugin,
  empackMetaPlugin,
];
export default plugins;
```

JupyterLab自动发现并激活 `autoStart: true` 的插件。

## 扩展开发：注册自定义xeus内核

如果你开发了一个新的xeus内核（如xeus-rust），不需要修改TypeScript代码——只需在构建时正确放置文件：

1. 将内核WASM二进制放到 `{output_dir}/xeus/kernels/{kernel_name}/` 目录
2. 创建正确的 `kernel.json`（argv指向内核JS文件，metadata.kernel_type="xeus"）
3. 在 `{output_dir}/xeus/kernels.json` 的kernels数组中添加条目
4. 确保empack打包的conda环境包含对应的内核包

`kernelPlugin` 会自动读取 `kernels.json` 并注册所有列出的内核。

## 相关API

- [kernelPlugin激活流程](../references/extension-source.md#kernelplugin内核注册)
- [WebWorkerKernel构造函数](../references/kernel-impl-source.md#webworkerkernel-类)
- [XeusLogManager](../references/extension-source.md#xeuslogmanager日志管理)
- [EmpackEnvMetaManager](../references/extension-source.md#empackenvmetamanager环境元数据管理)
- [JupyterLab扩展参考](https://jupyterlab.readthedocs.io/en/stable/extension/)

## 相关概念

- [内核生命周期](04-kernel-lifecycle.md)
- [构建系统详解](05-build-system.md)
- [自定义内核集成](09-custom-kernel.md)
