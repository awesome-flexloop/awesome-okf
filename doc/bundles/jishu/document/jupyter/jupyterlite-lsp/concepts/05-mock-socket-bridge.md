---
type: Concept
title: Mock-Socket 桥接机制
description: mock-socket 库在浏览器内创建虚拟 WebSocket 服务端、构建时 WebSocket 替换与运行时 Monkey-patch 的完整机制
tags: [mock-socket, websocket, monkey-patch, service-worker, build-patch]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: hacks
    resource: /references/hacks-source.md
    title: Monkey-patch 源码引用
  - id: build
    resource: /references/build-source.md
    title: 构建系统源码引用
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
---

## 为什么需要 Mock-Socket

传统 jupyterlab-lsp 的前端在初始化语言服务器连接时，执行类似以下代码：

```javascript
const ws = new WebSocket('ws://localhost:8888/lsp/ws/json');
```

这会发起一个真实的 WebSocket 网络连接到后端 jupyter-lsp 进程。但在 JupyterLite 环境中：

1. 没有后端 Python 进程监听 WebSocket
2. 页面通常通过 Service Worker 提供服务，HTTP 请求被拦截
3. 语言服务器运行在浏览器的 Web Worker 中，而非独立进程

因此需要拦截 WebSocket 构造函数，将连接重定向到浏览器内的虚拟服务端。

## 两阶段 Patch

Mock-Socket 桥接分为构建时和运行时两个阶段：

### 阶段一：构建时 Patch（dodo.py）

在 `jupyter lite build` 完成后，doit 的 task_hack 任务执行字符串替换：

```python
class C:
    NATIVE_WEBSOCKET = "new WebSocket"
    HACKED_WEBSOCKET = "new window.MockWebSocket"

def task_hack():
    yield dict(
        name="connection.js",
        actions=[(U.patch_one, [C.NATIVE_WEBSOCKET, C.HACKED_WEBSOCKET, B.CONNECTION_JS])],
    )
```

被 patch 的文件是 jupyterlab-lsp 构建产物中的 connection 模块：
`build/lite/extensions/@krassowski/jupyterlab-lsp/static/321.0176abf53bb1a24b854d.js`

这是一个简单的字符串查找替换，将所有 `new WebSocket(` 替换为 `new window.MockWebSocket(`。因为文件名中包含 hash（`321.0176abf5...`），hash 值在 jupyterlab-lsp 版本变更时会改变，当前版本硬编码了 hash 值。

### 阶段二：运行时 Patch（hacksPlugin）

hacksPlugin 的 `hoistMockSocket()` 函数将 mock-socket 的 WebSocket 类挂载到 window：

```typescript
import { WebSocket } from 'mock-socket';

function hoistMockSocket() {
  (window as any).MockWebSocket = WebSocket;
}
```

这样，构建时被 patch 的 `new window.MockWebSocket(...)` 在运行时就能找到 mock-socket 提供的 WebSocket 类。

## mock-socket 工作原理

mock-socket 是一个 JavaScript 库，提供浏览器内的虚拟 WebSocket 实现：

- **Server 端**：`new WebSocketServer(url)` 在浏览器内创建一个虚拟 WebSocket 服务端，监听指定 URL
- **Client 端**：`new WebSocket(url)` 创建一个虚拟客户端连接，在内存中直接路由到对应的 Server
- **无网络 I/O**：所有连接和消息传递都在浏览器内存中完成，不产生任何真实网络请求
- **API 兼容**：Client 和 Server 的 API 与标准 WebSocket API 一致（onmessage、send、close 等）

Session.initServer() 创建服务端：

```typescript
async initServer() {
  const wsServer = new WebSocketServer(this.url);
  wsServer.on('connection', async (socket) => {
    // socket 是 WebSocketClient 实例，代表一个客户端连接
    // 这里处理连接、消息收发
  });
}
```

## REST 请求桥接

除了 WebSocket，jupyterlab-lsp 还会发送 REST 请求（如 GET /lsp/status）。这些请求通过另一个 Monkey-patch 桥接：

```typescript
function hackServerConnection(app: JupyterLiteServer) {
  const realMakeSettings = ServerConnection.makeSettings;
  function makeSettings(options?) {
    const settings = realMakeSettings({
      ...(options || {}),
      fetch: app.fetch.bind(app),  // 替换 fetch 为 JupyterLite 的 Service Worker fetch
    });
    return settings;
  }
  ServerConnection.makeSettings = makeSettings;
}
```

`app.fetch` 是 JupyterLiteServer 的 fetch 处理函数，它通过 Service Worker 拦截 HTTP 请求。routesPlugin 在 app.router 上注册的 `/lsp/status` 路由由此机制处理。

## 完整的通信路径

### REST 通信路径

```
jupyterlab-lsp 前端
  → ServerConnection.makeRequest()
  → 调用 settings.fetch (app.fetch.bind(app))
  → JupyterLite Service Worker 拦截
  → 匹配 routesPlugin 注册的路由
  → lsp.status() 返回数据
  → new Response(JSON.stringify(res))
  → 前端收到响应
```

### WebSocket 通信路径

```
jupyterlab-lsp 前端（构建后代码）
  → new window.MockWebSocket(url)  [运行时：mock-socket WebSocket]
  → mock-socket 内存路由
  → WebSocketServer.on('connection') 回调
  → Session 创建 IJSONRPCLanguageServer 实例
  → 双向消息桥接（onMessage + read 循环）
  → Web Worker 中的语言服务器
```

## 关键常量与 URL 生成

```typescript
// 调试模式
export const DEBUG = window.location.href.includes('LSP_LITE_DEBUG');

// WebSocket 基础 URL
export const WS_BASE_URL = PageConfig.getBaseUrl().replace(/^http/, 'ws');
// 例如：http://localhost:8000/ → ws://localhost:8000/

// Session WebSocket URL
get url() {
  return `${WS_BASE_URL}lsp/ws/${this._id}`;
  // 例如：ws://localhost:8000/lsp/ws/json
}
```

## 注意事项与局限性

1. **硬编码 hash**：构建时 patch 目标文件名包含 hash（`321.0176abf5...`），升级 jupyterlab-lsp 版本时 hash 会变化，需要更新 dodo.py 中的路径
2. **字符串替换风险**：使用简单字符串替换 `new WebSocket`，如果其他模块也包含该字符串可能被误替换。当前版本因为 patch 的是 jupyterlab-lsp 的特定 chunk 文件，风险可控
3. **全局污染**：`window.MockWebSocket` 挂载到全局 window 对象，可能与其他代码冲突
4. **仅支持浏览器环境**：mock-socket 是浏览器专用库，整个机制不支持 Node.js 环境

## 相关概念

- [三插件体系](03-plugin-system.md)
- [IJSONRPCLanguageServer 接口与 Session](04-language-server-interface.md)
- [构建系统详解](07-build-system.md)
- [Monkey-patch 源码引用](../references/hacks-source.md)
