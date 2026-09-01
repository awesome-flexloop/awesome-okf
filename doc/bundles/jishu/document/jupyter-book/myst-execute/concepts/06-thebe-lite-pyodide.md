---
type: concept
title: "Thebe Lite：Pyodide 无服务器执行"
description: "详解 thebe-lite 包的 JupyterLite/Pyodide 集成：在浏览器中通过 WebAssembly 运行 Python 内核，无需 Binder 或本地 Jupyter Server"
tags: [thebe, thebe-lite, jupyterlite, pyodide, webassembly, serverless]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-lite-src.md"
    facts: [F-007, F-071, F-072, F-073, F-074, F-075]
  - path: "/references/thebe-core-src.md"
    facts: [F-054]
---

# Thebe Lite：Pyodide 无服务器执行

thebe-lite 提供了完全在浏览器内运行的 Jupyter 内核能力，基于 JupyterLite 和 Pyodide（CPython 的 WebAssembly 移植）。使用 thebe-lite 不需要任何后端服务器——Python 代码直接在用户的浏览器中通过 WASM 执行。

## 架构概述

```
┌──────────────────────────────────────────────┐
│                  浏览器                       │
│                                              │
│  ┌──────────┐    ┌──────────────────────┐   │
│  │ thebe-   │───→│ JupyterLite Server   │   │
│  │ lite     │    │ (内存中 ServiceManager)│   │
│  └──────────┘    └──────────┬───────────┘   │
│       │                     │               │
│       │ window.thebeLite    │               │
│       │ .startJupyterLite   │               │
│       │                     ↓               │
│  ┌──────────┐    ┌──────────────────────┐   │
│  │ thebe-   │←───│ Pyodide Kernel       │   │
│  │ core     │    │ (WebWorker + WASM)   │   │
│  └──────────┘    └──────────────────────┘   │
│       │                                      │
│       ↓                                      │
│  ┌──────────┐                                │
│  │ React /  │                                │
│  │ 纯 JS    │                                │
│  └──────────┘                                │
└──────────────────────────────────────────────┘
     无任何网络请求到后端 Jupyter Server
```

与 Binder/直连模式的关键区别：
- 没有 WebSocket 连接到远程内核
- 内核运行在浏览器的 Web Worker 中
- Python 解释器是编译为 WASM 的 CPython（Pyodide）
- 文件系统是内存中的虚拟文件系统
- 首次加载需要下载 Pyodide 运行时（约 20MB）和内核文件

## startJupyterLiteServer 函数

`startJupyterLiteServer(config?)` 是 thebe-lite 的唯一核心 API，异步返回与远程 Jupyter Server 兼容的 `ServiceManager` 实例。

```ts
async function startJupyterLiteServer(
  config?: LiteServerConfig
): Promise<ServiceManager>
```

### 执行流程

```
startJupyterLiteServer(config?)
  │
  ├─ 1. 初始化 PageConfig
  │     ├─ litePluginSettings（pipliteUrls、pipliteWheelUrl）
  │     ├─ enableMemoryStorage: true
  │     └─ settingsStorageDrivers: ['memoryStorageDriver']
  │
  ├─ 2. 动态导入插件
  │     ├─ @jupyterlite/server-extension（基础服务器）
  │     └─ @jupyterlite/pyodide-kernel-extension（Pyodide 内核）
  │
  ├─ 3. 创建 JupyterLiteServer 实例
  │     └─ registerPluginModules(plugins)
  │
  ├─ 4. await jupyterLiteServer.start()
  │
  └─ 5. return serviceManager（与远程服务器接口兼容）
```

### 默认配置

```ts
const defaultLiteConfig = {
  litePluginSettings: {
    '@jupyterlite/pyodide-kernel-extension:kernel': {
      pipliteUrls: [
        'https://unpkg.com/@jupyterlite/pyodide-kernel@0.4.7/pypi/all.json',
      ],
      pipliteWheelUrl:
        'https://unpkg.com/@jupyterlite/pyodide-kernel@0.4.7/pypi/piplite-0.4.7-py3-none-any.whl',
    },
  },
  enableMemoryStorage: true,
  settingsStorageDrivers: ['memoryStorageDriver'],
};
```

### LiteServerConfig 类型

```ts
interface LiteServerConfig {
  litePluginSettings?: Record<string, any>;
  enableMemoryStorage?: boolean;
  settingsStorageDrivers?: string[];
}
```

通过 `config.litePluginSettings` 可以自定义 piplite 包索引 URL，指向自建的 PyPI 镜像或包含自定义 wheel 的位置。

## 全局挂载

thebe-lite 的 UMD bundle 加载时自动执行：

```js
if (typeof window !== 'undefined') {
  setupThebeLite();
}
```

将 `startJupyterLiteServer` 和 `version` 挂载到 `window.thebeLite`：

```ts
interface ThebeLiteGlobal {
  startJupyterLiteServer: (config?: LiteServerConfig) => Promise<ServiceManager>;
  version: string;
}
```

## 与 thebe-core 集成

thebe-core 的 `connectToJupyterLiteServer()` 方法依赖 `window.thebeLite`：

```ts
async connectToJupyterLiteServer(config?: LiteServerConfig): Promise<void> {
  if (!window.thebeLite) {
    throw new Error(
      'thebe-lite is not available at window.thebeLite - ' +
      'load this onto your page before loading thebe or thebe-core.'
    );
  }

  this.serviceManager = await window.thebeLite.startJupyterLiteServer(config);
  this.sessionManager = this.serviceManager.sessions;

  return this.sessionManager?.ready.then(() => {
    this.userServerUrl = '/';  // JupyterLite 无外部 URL
    this.resolveReadyFn?.(this);
  });
}
```

调用 `server.startNewSession()` 时，thebe-core 对 JupyterLite 模式有一个特殊处理：路径中的 `/` 会被替换为 `-`，因为 JupyterLite 尚未完全支持基于子目录的文件系统路径。

## 加载方式

### 方式1：UMD Script 标签

```html
<!-- 先加载 thebe-lite -->
<script src="thebe-lite.min.js"></script>
<!-- 再加载 thebe-core -->
<script src="thebe-core.min.js"></script>
<script>
  // thebe-lite 自动挂载到 window.thebeLite
  // thebe-core 自动挂载到 window.thebeCore
  const config = window.thebeCore.api.makeConfiguration({
    kernelOptions: { kernelName: 'python' },
  });
  const server = window.thebeCore.api.connectToJupyterLite(config);
</script>
```

### 方式2：React BundleLoaderProvider

```tsx
import { ThebeBundleLoaderProvider, ThebeServerProvider } from 'thebe-react';

<ThebeBundleLoaderProvider
  start
  loadThebeLite={true}
  publicPath="/static/thebe"
>
  <ThebeServerProvider
    connect={true}
    useJupyterLite={true}
  >
    <App />
  </ThebeServerProvider>
</ThebeBundleLoaderProvider>
```

`ThebeBundleLoaderProvider` 会动态创建 script 标签加载 `thebe-core.min.js` 和 `thebe-lite.min.js`，轮询检测 `window.thebeCore`（和可选的 `window.thebeLite`）是否可用。

### 方式3：ESM 导入

```ts
import { startJupyterLiteServer } from 'thebe-lite';
import { makeConfiguration, ThebeServer } from 'thebe-core';

const config = makeConfiguration({ kernelOptions: { kernelName: 'python' } });
const server = new ThebeServer(config);
await server.connectToJupyterLiteServer();
```

## 注意事项和限制

1. **内核名称固定**：Pyodide kernel 的名称是 `'python'`，不是 `'python3'`。配置 kernelOptions 时使用 `kernelName: 'python'`。

2. **首次加载延迟**：Pyodide 运行时约 20MB，首次下载需要时间。建议在页面中提供加载状态提示。

3. **包安装**：在 JupyterLite 中安装包使用 `%pip install` 或 `piplite`，包从 `pipliteUrls` 指定的索引下载（不是标准 PyPI）。纯 Python 包通常可以工作，但包含 C 扩展的包需要有对应 Pyodide wheel。

4. **内存存储**：默认使用 `memoryStorageDriver`，页面刷新后所有状态（包括文件和变量）丢失。可以配置 IndexedDB 存储驱动实现持久化。

5. **文件系统**：JupyterLite 使用内存中的 Emscripten 文件系统，不与服务器真实文件系统交互。

6. **路径处理**：thebe-core 中对 JupyterLite 模式有路径扁平化处理（`/` → `-`），这是因为 JupyterLite 对子目录路径的支持尚不完全。

7. **与 Binder 的 API 兼容性**：一旦 ServiceManager 就绪，上层 API（ThebeSession、ThebeNotebook、ThebeCodeCell）完全一致——代码无需区分运行在 Binder、本地服务器还是 JupyterLite 上。

## 服务 Worker

thebe-lite 包含一个 `service-worker.js`，用于缓存静态资源和提供文件系统访问。这是 JupyterLite 架构的一部分，用于在浏览器中模拟 Jupyter Server 的静态文件服务。

## 相关概念

- [03-thebe-core-api.md](03-thebe-core-api.md)：核心 API 和服务器连接
- [04-thebe-configuration.md](04-thebe-configuration.md)：配置选项
- [05-thebe-binder.md](05-thebe-binder.md)：Binder 连接（对比模式）
- [07-thebe-react.md](07-thebe-react.md)：React 集成
- [03-thebe-lite.md](../examples/03-thebe-lite.md)：JupyterLite 使用示例
