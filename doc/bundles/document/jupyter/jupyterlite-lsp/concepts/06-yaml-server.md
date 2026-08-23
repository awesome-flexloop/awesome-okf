---
type: Concept
title: YAML/JSON 语言服务器
description: @jupyterlite/lsp-yaml 包的实现——yaml-language-server 的 Web Worker 封装、WaitQueue 消息桥接、JSONLanguageServer 类
tags: [yaml, json, language-server, web-worker, wait-queue, yaml-language-server]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yaml
    resource: /references/yaml-plugin-source.md
    title: YAML语言服务器包源码引用
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
---

## 包概述

`@jupyterlite/lsp-yaml` 是 jupyterlite-lsp 的参考语言服务器实现，它将 Red Hat 的 [yaml-language-server](https://github.com/redhat-developer/yaml-language-server) 封装为可在浏览器 Web Worker 中运行的 IJSONRPCLanguageServer。

尽管包名和 display_name 中包含 "YAML"，它同时支持 YAML 和 JSON 两种语言（yaml-language-server 本身就支持 JSON Schema 验证）。

| 属性 | 值 |
|------|-----|
| 包名 | @jupyterlite/lsp-yaml |
| 版本 | 0.1.0-alpha0 |
| 服务器 ID | `json` |
| display_name | YAML |
| 支持语言 | yaml, json |
| MIME 类型 | text/x-yaml, text/yaml, application/json |
| 核心依赖 | yaml-language-server ^1.10.0, wait-queue ^1.1.4 |

## SPEC 定义

```typescript
export const SPEC: SCHEMA.ServerSpecProperties = {
  display_name: 'YAML',
  languages: ['yaml', 'json'],
  mime_types: ['text/x-yaml', 'text/yaml', 'application/json'],
  version: 2,
};
```

这个 spec 对象会在 `/lsp/status` 响应中返回给 jupyterlab-lsp 前端，前端根据 languages 和 mime_types 决定在编辑哪些文件时激活该语言服务器。

## 插件注册

```typescript
const plugin: JupyterLiteServerPlugin<void> = {
  id: SERVER_PLUGIN_ID,
  autoStart: true,
  requires: [ILanguageServers],
  activate: (app: JupyterLiteServer, lsp: ILanguageServers) => {
    lsp.addLanguageServer('json', {
      spec: SPEC,
      createNewServer: async () => {
        const { JSONLanguageServer } = await import('./server');
        return new JSONLanguageServer();
      },
    });
  },
};
```

关键设计：
- 使用动态 `import('./server')` 延迟加载 JSONLanguageServer，减少初始包体积
- 服务器 ID 使用 `'json'`（与历史命名兼容，因为最初可能只计划支持 JSON）
- createNewServer 在每次 WebSocket 连接时被调用，创建新的服务器实例

## JSONLanguageServer 类

JSONLanguageServer 是 IJSONRPCLanguageServer 接口的具体实现，核心是将 Web Worker 的消息 API 适配为 AsyncGenerator 接口。

### 类结构

```typescript
export class JSONLanguageServer implements IJSONRPCLanguageServer {
  private _worker: Worker | null = null;
  private _readQueue: WaitQueue<any> | null = null;
}
```

两个私有字段：
- `_worker`：Web Worker 实例，运行 yaml-language-server
- `_readQueue`：WaitQueue 实例，作为 Worker 消息到 AsyncGenerator 的桥梁

### initialize 方法

```typescript
async initialize(): Promise<void> {
  const { default: WaitQueue } = await import('wait-queue');
  this._readQueue = new WaitQueue();
  this._worker = new Worker(
    new URL('yaml-language-server/lib/esm/webworker/yamlServerMain', import.meta.url)
  );
  this._worker.onmessage = this.onWorkerMessage;
}
```

初始化流程：
1. 动态导入 wait-queue（同样是延迟加载）
2. 创建 WaitQueue 实例
3. 创建 Web Worker，入口为 yaml-language-server 的 ESM webworker 入口
4. 注册 onmessage 回调

Web Worker URL 使用 `new URL('...', import.meta.url)` 构建，这是 webpack 5 原生支持的 Worker 打包方式——webpack 会自动将 yaml-language-server 的 worker 入口打包为独立的 chunk。

### write 方法（客户端→服务器）

```typescript
async write(msg: string) {
  this._worker?.postMessage(msg);
}
```

将前端发来的 LSP 消息通过 Worker.postMessage() 发送给 Worker 内的 yaml-language-server。

注意：虽然接口定义中 write 接收 `string | ArrayBuffer | Blob | ArrayBufferView`，JSONLanguageServer 的实现只标注了 `string` 类型参数。实际运行中 yaml-language-server 使用字符串消息（JSON-RPC）。

### read 方法（服务器→客户端）

```typescript
async *read(): AsyncGenerator<string> {
  let msg: any;
  while (this._worker) {
    msg = await this._readQueue?.pop();
    yield msg;
  }
}
```

AsyncGenerator 实现：
1. 当 Worker 存活时（`this._worker` 不为 null），循环等待队列消息
2. `_readQueue.pop()` 是一个异步方法，当队列为空时阻塞等待，有消息时返回队首元素
3. yield 消息给调用者（Session.read 循环），通过 MockWebSocket 发送给前端

当 `_worker` 被设为 null 时（如连接关闭），循环自然终止。

### onWorkerMessage（Worker 消息回调）

```typescript
onWorkerMessage(msg: MessageEvent) {
  this._readQueue?.unshift(msg.data);
}
```

Worker 发送消息到主线程时触发：
1. 从 MessageEvent 中提取 data 字段
2. 通过 `_readQueue.unshift()` 将消息放入队列头部
3. 如果有代码正在等待 `pop()`，会被唤醒

注意：这里使用 `unshift`（队首入队）而非 `push`（队尾入队）。WaitQueue 的实现中 unshift 添加元素到队列开头，pop 从队列开头取出——这实际上构成了 LIFO（后进先出）栈行为。但在实际使用中，因为只有一个生产者（onWorkerMessage）和一个消费者（read 循环），且消息处理是异步串行的，所以不会出现消息乱序问题。

## worker.ts：Webpack 打包入口

```typescript
import 'yaml-language-server/lib/esm/webworker/yamlServerMain';
```

这一行代码看起来多余（JSONLanguageServer 已经在 Worker 构造函数中引用了该路径），但它的作用是确保 webpack 在打包时能正确处理 yaml-language-server 的 Worker 入口。在某些构建配置中，通过 `new URL()` 创建的 Worker 可能不会被正确打包，显式 import 提供了额外的保证。

## WaitQueue 消息桥接模式

JSONLanguageServer 使用 wait-queue 库实现了一个经典的生产者-消费者模式：

```
主线程                    WaitQueue              Web Worker
──────────                ─────────              ──────────
                          ┌───────┐
onWorkerMessage ─unshift─▶│ msg1  │
                          │ msg2  │
                          │  ...  │
read() ◀──────pop─────────│ msgN  │
                          └───────┘
                                                 yaml-language-server
                                                 处理LSP请求，postMessage返回
```

这种模式将 Worker 的基于事件的 push API（onmessage 回调）转换为基于迭代器的 pull API（AsyncGenerator），与 Session.read() 中的 `for await...of` 消费模式天然契合。

## npm 依赖解析

| 依赖 | 版本 | 作用 |
|------|------|------|
| @jupyterlite/lsp | ^0.1.0a0 | 核心接口和 Token |
| @jupyterlite/server | ^0.1.0-beta.15 | JupyterLite 插件 API |
| jsonc-parser | ^3.2.0 | JSON with Comments 解析（yaml-language-server 的依赖） |
| wait-queue | ^1.1.4 | 异步等待队列 |
| yaml-language-server | ^1.10.0 | Red Hat YAML/JSON 语言服务器（提供 LSP 功能） |

## webpack 配置

lsp-yaml 的 webpack.config.js 与核心包相同，启用 source-map-loader 处理 JS source map：

```javascript
module.exports = {
  output: { clean: true },
  devtool: 'source-map',
  module: { rules: [{ test: /\.js$/, use: ['source-map-loader'] }] },
};
```

sharedPackages 配置中 @jupyterlite/lsp 设为 singleton 且不 bundled，确保与核心包共享同一个实例。

## 相关概念

- [IJSONRPCLanguageServer 接口与 Session](/concepts/04-language-server-interface.md)
- [Mock-Socket 桥接机制](/concepts/05-mock-socket-bridge.md)
- [添加自定义语言服务器示例](/examples/add-custom-language-server.md)
- [YAML包源码引用](/references/yaml-plugin-source.md)
