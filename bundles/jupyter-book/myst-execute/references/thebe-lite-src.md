---
type: reference
title: "thebe-lite Pyodide 无服务器源码"
description: "thebe-lite 包提供基于 JupyterLite/Pyodide 的浏览器内 Jupyter 内核支持，无需远程服务器即可执行代码"
tags: [thebe, thebe-lite, jupyterlite, pyodide, serverless]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "thebe/packages/lite/src/index.ts"
    facts: [F-007, F-075]
  - path: "thebe/packages/lite/src/jlite.ts"
    facts: [F-071, F-072, F-073, F-074]
  - path: "thebe/packages/lite/src/types.ts"
    facts: []
---

# thebe-lite Pyodide 无服务器源码

## 源码位置

**仓库根**：`external/libs/ai/jupyter-book/thebe/`
**包目录**：`packages/lite/src/`

## 核心文件清单

| 文件 | 职责 | 关键导出 |
|------|------|---------|
| `index.ts` | 包入口/UMD 挂载 | `startJupyterLiteServer()`, `setupThebeLite()`, 自动挂载 `window.thebeLite` |
| `jlite.ts` | JupyterLite 服务器初始化 | `startJupyterLiteServer(config?)` |
| `types.ts` | 类型定义 | `ThebeLiteGlobal`, `LiteServerConfig` |
| `service-worker.js` | Service Worker（静态资源服务） | 辅助文件 |

## startJupyterLiteServer 流程

```
startJupyterLiteServer(config?)
  ├─ PageConfig.setOption('litePluginSettings', ...)  // 配置 pyodide-kernel piplite 地址
  ├─ PageConfig.setOption('enableMemoryStorage', true)
  ├─ PageConfig.setOption('settingsStorageDrivers', ['memoryStorageDriver'])
  ├─ import('@jupyterlite/server-extension')         // 基础服务器扩展
  ├─ import('@jupyterlite/pyodide-kernel-extension') // Pyodide 内核
  ├─ new JupyterLiteServer()                         // 创建内存中服务器
  ├─ jupyterLiteServer.registerPluginModules(...)    // 注册插件
  ├─ await jupyterLiteServer.start()                 // 启动服务器
  └─ return serviceManager                           // 返回与远程服务器兼容的 ServiceManager
```

## 默认配置

- Pyodide kernel 版本：`@jupyterlite/pyodide-kernel@0.4.7`
- pipliteUrls：`https://unpkg.com/@jupyterlite/pyodide-kernel@0.4.7/pypi/all.json`
- pipliteWheelUrl：对应版本的 piplite wheel
- 存储驱动：内存存储（memoryStorageDriver），不使用 IndexedDB 持久化

## UMD 挂载

thebe-lite 的 UMD bundle 加载时自动执行：

```js
if (typeof window !== 'undefined') {
  setupThebeLite(); // window.thebeLite = { startJupyterLiteServer, version }
}
```

## 版本与构建

- 构建工具：webpack（CJS bundle）
- 运行时依赖：`@jupyterlite/server`、`@jupyterlite/server-extension`、`@jupyterlite/pyodide-kernel-extension`、`@jupyterlab/coreutils`、`@jupyterlab/services`
- 与 thebe-core 的关系：thebe-core 的 `connectToJupyterLiteServer()` 方法检测 `window.thebeLite` 是否存在并调用其 API
