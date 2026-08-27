---
type: concept
title: "Binder 与 Jupyter 服务器连接"
description: "详解 thebe 的 BinderHub 连接流程：EventSource/SSE 事件监听、Binder 构建阶段、saved sessions 持久化、直连 Jupyter Server 和 REST API"
tags: [thebe, binder, binderhub, sse, eventsource, jupyter-server, websocket]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-core-src.md"
    facts: [F-053, F-055, F-056, F-058, F-059, F-065]
---

# Binder 与 Jupyter 服务器连接

ThebeServer 支持三种后端连接模式：通过 BinderHub 远程构建、直连已运行的 Jupyter Server、以及 JupyterLite 浏览器内内核。本文档重点介绍 Binder 连接和直连模式，JupyterLite 模式详见 [06-thebe-lite-pyodide.md](06-thebe-lite-pyodide.md)。

## Binder 连接流程

`connectToServerViaBinder()` 方法通过 Server-Sent Events（SSE）与 BinderHub 通信，等待远程环境构建完成。

### 流程详解

```
浏览器                              BinderHub (mybinder.org)
  │                                      │
  │  1. 构建 Binder URL                   │
  │     /build/{provider}/{repo}/{ref}    │
  │                                      │
  │  2. 检查 saved session ──→ localStorage
  │     │ 命中且存活 → 直接连接（跳到步骤6）
  │     │ 未命中/失效 → 继续构建
  │                                      │
  │  3. new EventSource(buildUrl) ──────→ 开始构建
  │                                      │
  │  4. 等待 SSE 事件 ◄───────────────── 流式推送构建日志
  │     ├─ phase: "waiting"    排队中
  │     ├─ phase: "building"   构建镜像中
  │     ├─ phase: "pushing"    推送镜像中
  │     ├─ phase: "launching"  启动服务器中
  │     ├─ phase: "ready"      ✅ 服务器就绪
  │     └─ phase: "failed"     ❌ 构建失败
  │                                      │
  │  5. phase=ready:                     │
  │     接收 {url, token}                 │
  │                                      │
  │  6. 创建 KernelManager               │
  │     创建 SessionManager               │
  │     → WebSocket 连接 ◄─────────────── Jupyter Server
  │                                      │
  │  7. resolve(ready Promise)           │
  │     保存 session 到 localStorage
```

### SSE 事件处理

```ts
const es = new EventSource(urls.build);

es.onmessage = async (evt: MessageEvent) => {
  const msg = JSON.parse(evt.data);
  const phase = msg.phase?.toLowerCase() ?? '';

  switch (phase) {
    case 'failed':
      es.close();
      // reject ready Promise
      break;
    case 'ready': {
      es.close();
      // msg.url: Jupyter Server URL
      // msg.token: 认证 token
      const serverSettings = ServerConnection.makeSettings({
        baseUrl: msg.url,
        wsUrl: 'ws' + msg.url.slice(4),
        token: msg.token,
        appendToken: true,
      });
      // 创建 KernelManager → SessionManager
      // 等待 sessionManager.ready
      // 保存到 localStorage（如果 enabled）
      // resolve ready Promise
      break;
    }
    default:
      // 中间状态（waiting/building/pushing/launching），触发 status 事件
  }
};

es.onerror = (evt) => {
  es.close();
  // reject ready Promise
};
```

### Binder URL 构建

`makeBinderUrls(config, repoProviders)` 根据 repoProvider 生成三个 URL：

```ts
interface BinderUrlSet {
  build: string;      // SSE 构建事件端点
  launch: string;     // （保留）
  storageKey: string; // localStorage key
}
```

内置的 `WELL_KNOWN_REPO_PROVIDERS` 支持四种仓库提供商：
- **github**：`{binderUrl}/build/gh/{repo}/{ref}`
- **gitlab**：`{binderUrl}/build/gl/{repo}/{ref}`
- **gist**：`{binderUrl}/build/gist/{repo}/{ref}`
- **git**：`{binderUrl}/build/git/{url-encoded-repo}/{ref}`

支持通过 `customRepoProviders` 参数传入自定义 RepoProviderSpec（包含 name 和 makeUrls 函数）。

### Binder 构建时间

Binder 首次构建可能需要数分钟（取决于仓库大小和依赖项），但构建好的镜像会被缓存，后续启动通常在几十秒内完成。通过 saved sessions 机制，同一浏览器在有效期内可直接复用已构建的服务器，几乎即时连接。

## Saved Sessions：会话持久化

Saved sessions 通过 localStorage 缓存 Binder 服务器信息，避免重复等待构建。

### 存储内容

```ts
interface SavedSessionInfo {
  id: string;
  baseUrl: string;
  token: string;
  wsUrl: string;
  lastUsed: Date;
}
```

存储在 `localStorage[storageKey]` 中，storageKey 由 `{storagePrefix}:{binderUrl}:{provider}:{repo}:{ref}` 组合而成。

### 检测存活

```ts
async function checkForSavedBinderSession() {
  const existingSettings = getExistingServer(config.savedSessions, storageKey);
  // getExistingServer 会 ping 服务器 /api/status 端点
  // 如果返回 ok → 服务器仍存活，返回 serverSettings
  // 如果失败 → 返回 null，触发新的 Binder 构建
}
```

### 有效期

`savedSessionOptions.maxAge`（默认 86400 秒 = 24小时）控制保存的 session 有效期。超过有效期的 session 信息会被忽略。

### 手动清除

```ts
server.clearSavedBinderSessions();
// 或
clearAllSavedSessions();
clearSavedSession(storageKey);
```

## 直连 Jupyter Server

`connectToJupyterServer()` 用于直接连接已运行的 Jupyter Server，跳过 Binder 构建。

### 流程

```
1. ServerConnection.makeSettings(serverSettings)
2. ping /api/status 端点 → 检查服务器可达
3. new KernelManager({ serverSettings })
4. new SessionManager({ kernelManager, serverSettings })
5. 监听 connectionFailure 和 runningChanged 事件
6. await sessionManager.ready
7. resolve(ready Promise)
```

```ts
async connectToJupyterServer(): Promise<void> {
  const serverSettings = ServerConnection.makeSettings(this.config.serverSettings);

  // 先 ping 服务器
  await ThebeServer.status(serverSettings);

  const kernelManager = new KernelManager({ serverSettings });
  this.sessionManager = new SessionManager({ kernelManager, serverSettings });

  // 连接失败事件
  this.sessionManager.connectionFailure.connect((_, err) => {
    this.events.triggerError({ status: 'error', message: `connection failure: ${err}` });
  });

  return this.sessionManager.ready.then(() => {
    this.userServerUrl = `${serverSettings.baseUrl}?token=${serverSettings.token}`;
    this.resolveReadyFn?.(this);
  });
}
```

### 本地服务器连接

本地开发时通常需要先启动 Jupyter Server：

```bash
jupyter lab --no-browser --ServerApp.token=dev-token --ServerApp.port=8888
```

然后配置 thebe 直连：

```ts
const config = makeConfiguration({
  serverSettings: {
    baseUrl: 'http://localhost:8888',
    token: 'dev-token',
  },
});
const server = connectToJupyter(config);
```

## 服务器就绪后的操作

一旦 `server.ready` Promise resolve，就可以创建 Session 和 Notebook：

```ts
await server.ready;

// 查询可用内核
const specs = await server.getKernelSpecs();
console.log(Object.keys(specs.kernelspecs));

// 创建会话
const rendermime = makeRenderMimeRegistry();
const session = await server.startNewSession(rendermime, {
  kernelName: 'python3',
  path: '/',
});

// 列出运行中的会话
const sessions = await server.listRunningSessions();
```

## 服务器状态事件

ThebeServer 通过 EventEmitter 触发状态和错误事件：

```ts
config.events.on('status', (data) => {
  // data.subject: 'server'
  // data.status: 'launching' | 'ready'
  // data.message: 描述信息
});

config.events.on('error', (data) => {
  // data.status: 'error' | 'server'
  // data.message: 错误信息
});
```

连接过程中的关键状态：
- Binder 模式下，每个构建阶段（waiting/building/pushing/launching）都会触发 status 事件
- 服务器就绪后触发 `{ status: 'ready', message: 'Server connection ready' }`
- 连接失败触发 error 事件，reject ready Promise

## 静态状态检查

`ThebeServer.status()` 静态方法可独立用于检查服务器是否存活：

```ts
import { ServerConnection } from '@jupyterlab/services';

const serverSettings = ServerConnection.makeSettings({
  baseUrl: 'http://localhost:8888',
  token: '...',
});

const response = await ThebeServer.status(serverSettings);
if (response.ok) {
  console.log('Server is alive');
}
```

## 清理与销毁

```ts
// 关闭所有会话并断开连接
await server.shutdownAllSessions();
server.dispose();
```

`dispose()` 会同时清理 serviceManager 和 sessionManager。

## 相关概念

- [03-thebe-core-api.md](03-thebe-core-api.md)：核心 API 对象层次
- [04-thebe-configuration.md](04-thebe-configuration.md)：BinderOptions 和 ServerSettings 配置
- [06-thebe-lite-pyodide.md](06-thebe-lite-pyodide.md)：JupyterLite 无服务器模式
- [02-thebe-interactive.md](../examples/02-thebe-interactive.md)：Binder 和直连示例
