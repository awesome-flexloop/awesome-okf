---
type: concept
title: "Thebe 核心 API"
description: "详解 thebe-core 的链式 API：从 Config 配置到 ThebeServer 连接、ThebeSession 会话、ThebeNotebook 笔记本和 ThebeCodeCell 单元格的创建与使用"
tags: [thebe, thebe-core, api, server, session, notebook, cell]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-core-src.md"
    facts: [F-005, F-006, F-051, F-052, F-053, F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-068, F-069, F-070]
---

# Thebe 核心 API

thebe-core 提供了一套链式 API 用于在浏览器中建立 Jupyter 内核连接并执行代码。核心对象按照 `Config → ThebeServer → ThebeSession → ThebeNotebook → ThebeCodeCell` 的层次组织，每个对象负责一个抽象层级。

## 对象层次结构

```
Config                  配置（Binder/Server/Kernel/MathJax 选项）
  └─ ThebeServer        服务器连接（Binder/直连/JupyterLite）
       └─ ThebeSession  内核会话（Kernel.IKernelConnection 包装）
            └─ ThebeNotebook  笔记本（单元格集合）
                 └─ ThebeCodeCell    代码单元格（执行+渲染）
                 └─ ThebeMarkdownCell Markdown 单元格
```

## Config：配置对象

`Config` 类封装了所有配置选项，通过构造函数接收 `CoreOptions`：

```ts
import { makeConfiguration } from 'thebe-core';

const config = makeConfiguration({
  mathjaxUrl: 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js',
  mathjaxConfig: 'TeX-AMS_CHTML-full,Safe',
  binderOptions: {
    repo: 'executablebooks/thebe-binder-base',
    ref: 'HEAD',
    binderUrl: 'https://mybinder.org',
    repoProvider: 'github',
  },
  kernelOptions: {
    kernelName: 'python',
    path: '/',
  },
  serverSettings: {
    baseUrl: 'http://localhost:8888',
    token: '...',
  },
});
```

Config 提供 getter 访问各子配置：`config.binder`、`config.kernels`、`config.serverSettings`、`config.savedSessions`、`config.mathjax`、`config.events`。

每个子配置都有合理的默认值（见 [04-thebe-configuration.md](04-thebe-configuration.md)）。

## ThebeServer：服务器连接

`ThebeServer` 类管理与 Jupyter 后端的连接，支持三种连接模式。

### 创建服务器

```ts
import { makeServer, connectToBinder, connectToJupyter, connectToJupyterLite } from 'thebe-core';

// 方式1：手动创建后连接
const server = makeServer(config);
await server.connectToJupyterServer();  // 或 connectToServerViaBinder() / connectToJupyterLiteServer()

// 方式2：使用便捷工厂函数
const server = connectToBinder(config);       // 自动连接 Binder
const server = connectToJupyter(config);      // 自动直连本地 Jupyter
const server = connectToJupyterLite(config);  // 自动连接 JupyterLite
```

### 服务器状态

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `server.ready` | `Promise<ThebeServer>` | 等待服务器就绪的 Promise |
| `server.isReady` | `boolean` | 服务器是否已就绪 |
| `server.isBinder` | `boolean` | 是否通过 Binder 连接 |
| `server.isDisposed` | `boolean` | 是否已销毁 |
| `server.userServerUrl` | `string` | 用户可访问的服务器 URL |
| `server.id` | `string` | 短 ID 标识符 |

### 会话管理

```ts
// 启动新会话
const session = await server.startNewSession(rendermime, {
  kernelName: 'python3',
  path: '/notebooks/demo.ipynb',
});

// 列出运行中的会话
const sessions = await server.listRunningSessions();

// 连接到已有会话
const session = await server.connectToExistingSession(model, rendermime);

// 关闭
await server.shutdownSession(id);
await server.shutdownAllSessions();
server.dispose();
```

`startNewSession()` 会从路径中提取 notebook 文件名（匹配 `/*.ipynb$/`），默认使用 `'thebe.ipynb'`。对于 JupyterLite 模式，路径中的 `/` 会被替换为 `-`。

### REST API

ThebeServer 实现了 ServerRestAPI 接口，可用于操作服务器文件系统：

```ts
// 获取内核规格
const specs = await server.getKernelSpecs();

// 内容 API
const content = await server.getContents({ path: 'notebooks/demo.ipynb', returnContent: true });
await server.uploadFile({ path: 'upload.ipynb', content: JSON.stringify(ipynb), format: 'json' });
await server.renameContents({ path: 'old.ipynb', newPath: 'new.ipynb' });
await server.createDirectory({ path: 'new-dir' });
await server.duplicateFile({ path: 'copy.ipynb', copy_from: 'original.ipynb' });
```

### 静态方法

```ts
// 检查服务器状态
import { ThebeServer } from 'thebe-core';
const response = await ThebeServer.status(serverSettings);
```

## ThebeSession：内核会话

`ThebeSession` 包装了 JupyterLab 的 Session.ISessionConnection，提供内核执行的上下文。

```ts
// 通过 server.startNewSession() 获取，不直接构造
const session: ThebeSession = await server.startNewSession(rendermime, kernelOptions);

// 属性
session.kernel;       // Kernel.IKernelConnection | null
session.isReady;      // boolean
session.id;           // string
session.path;         // string
session.name;         // string

// 操作
await session.restart();
await session.shutdown();
```

Session 是 Notebook 执行代码时必须的——ThebeNotebook 通过 `attachSession(session)` 绑定到会话后，其 cells 才能执行。

## ThebeNotebook：笔记本抽象

`ThebeNotebook` 代表一个包含多个单元格的笔记本，提供批量执行能力。

### 创建 Notebook

```ts
import { setupNotebookFromBlocks, setupNotebookFromIpynb } from 'thebe-core';

// 从代码块创建
const notebook = setupNotebookFromBlocks(
  [
    { id: 'cell-1', source: 'x = 1\nprint(x)' },
    { id: 'cell-2', source: 'y = x + 1\nprint(y)' },
  ],
  config,
  rendermime,
);

// 从 ipynb JSON 创建
const notebook = setupNotebookFromIpynb(ipynbContent, config, rendermime);
```

### Notebook 操作

```ts
// 附加到会话（必须在执行前）
notebook.attachSession(session);
notebook.detachSession();

// 执行
const results = await notebook.executeAll(stopOnError = true);     // 执行所有单元格
const results = await notebook.executeCells(cellIds, stopOnError); // 执行指定单元格

// 单元格访问
notebook.cells;        // ThebeCodeCell[] / ThebeMarkdownCell[]
notebook.widgets;      // 标记了 widget 标签的单元格
notebook.cellMap;      // Map<cellId, IThebeCell>

// 清空输出
notebook.clear();
```

`executeAll()` 和 `executeCells()` 返回 `(IThebeCellExecuteReturn | null)[]`，每项包含执行后输出区域的尺寸（id, height, width）和可能的 error 信息。

## ThebeCodeCell：代码单元格

`ThebeCodeCell` 代表单个可执行代码单元格，融合了执行逻辑和输出渲染。

### 关键属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `cell.id` | `string` | 单元格唯一 ID |
| `cell.kind` | `'code' \| 'markdown'` | 单元格类型 |
| `cell.source` | `string` | 代码源文本 |
| `cell.session` | `ThebeSession` | 关联的会话 |
| `cell.isBusy` | `boolean` | 是否正在执行 |
| `cell.isAttached` | `boolean` | 是否附加到 DOM |
| `cell.executionCount` | `number \| null` | 执行计数 |
| `cell.outputs` | `IOutput[]` | 输出数组 |
| `cell.tags` | `string[]` | 单元格标签 |

### 单元格操作

```ts
// 执行
const result = await cell.execute(source?);  // 可选参数覆盖 source

// 输出管理
cell.initOutputs(initialOutputs);  // 设置初始输出（如预计算结果）
cell.render(outputs);              // 渲染输出
cell.clear();                      // 清空输出
cell.setOutputText(text);          // 设置文本输出

// DOM 挂载
cell.attachToDOM(el?);  // 将输出区域挂载到 DOM 元素
cell.detachSession();   // 断开会话

// 状态
cell.setAsBusy();
cell.setAsIdle();
cell.reset();
```

### PassiveCellRenderer：被动渲染

`PassiveCellRenderer` 提供不依赖内核的纯输出渲染能力——即使没有活动内核，也能显示预计算的输出（如构建时 myst-execute 缓存的结果）。它实现了 `IPassiveCell` 接口，是 ThebeCodeCell 渲染能力的基础。

## 事件系统

thebe-core 通过 `ThebeEvents` 提供事件订阅机制，用于跟踪连接状态变化：

```ts
const events = makeEvents();  // 或从 config.events 获取

// 监听状态变化
events.on('status', (data) => {
  console.log(data.subject, data.status, data.message);
  // subject: 'server' | 'session' | 'kernel' | 'cell'
  // status: 'launching' | 'ready' | 'error' | 'busy' | 'idle' | 'shutdown'
});

events.on('error', (data) => {
  console.error(data.message);
});
```

## 入口点与全局挂载

### ESM 模块方式

```ts
import * as thebe from 'thebe-core';
const config = thebe.makeConfiguration({ binderOptions: { repo: '...' } });
const server = thebe.connectToBinder(config);
```

### UMD script 标签方式

加载 `thebe-core.min.js` 后，`window.thebeCore` 自动可用：

```ts
// window.thebeCore 结构
window.thebeCore = {
  module: typeof thebe,       // 完整模块引用
  api: {                      // 便捷 API
    makeConfiguration,
    makeEvents,
    makeServer,
    makeRenderMimeRegistry,
    connectToBinder,
    connectToJupyter,
    connectToJupyterLite,
    setupNotebookFromBlocks,
    setupNotebookFromIpynb,
  },
  version: 'x.y.z',
};
```

入口点（`thebe/entrypoint.ts`）在浏览器环境中自动调用 `setupThebeCore()` 完成挂载。

## RenderMime 注册表

```ts
import { makeRenderMimeRegistry } from 'thebe-core';

const rendermime = makeRenderMimeRegistry({
  mathjaxUrl: '...',
  mathjaxConfig: '...',
});
```

`IRenderMimeRegistry` 来自 `@jupyterlab/rendermime`，负责将 MIME bundle（如 `text/html`、`image/png`、`application/vnd.plotly.v1+json`）渲染为 DOM 节点。创建 Session 和 Notebook 时都需要传入 rendermime 实例。

## 相关概念

- [00-execution-architecture.md](00-execution-architecture.md)：执行架构总览
- [04-thebe-configuration.md](04-thebe-configuration.md)：配置选项详解
- [05-thebe-binder.md](05-thebe-binder.md)：Binder 连接机制
- [06-thebe-lite-pyodide.md](06-thebe-lite-pyodide.md)：Pyodide 无服务器模式
- [07-thebe-react.md](07-thebe-react.md)：React 集成
- [02-thebe-interactive.md](../examples/02-thebe-interactive.md)：交互式代码示例
