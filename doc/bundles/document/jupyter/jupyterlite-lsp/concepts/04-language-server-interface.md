---
type: Concept
title: IJSONRPCLanguageServer 接口与 Session 管理
description: 语言服务器统一接口（IJSONRPCLanguageServer）定义、Session 类的双向消息桥接机制、LanguageServers 注册中心
tags: [interface, session, async-generator, language-server, websocket]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
  - id: yaml
    resource: /references/yaml-plugin-source.md
    title: YAML语言服务器包源码引用
---

## IJSONRPCLanguageServer 接口

所有浏览器端语言服务器必须实现 `IJSONRPCLanguageServer` 接口，定义在 `packages/lsp/src/tokens.ts`：

```typescript
export interface IJSONRPCLanguageServer {
  initialize(): Promise<void>;
  write(msg: string | ArrayBuffer | Blob | ArrayBufferView): Promise<void>;
  read(): AsyncGenerator<string>;
}
```

### 三个方法的职责

| 方法 | 方向 | 说明 |
|------|------|------|
| `initialize()` | - | 初始化语言服务器（启动 Worker、加载资源等），在 WebSocket 连接建立后调用 |
| `write(msg)` | 客户端→服务器 | 向语言服务器发送消息（来自前端的 LSP 请求） |
| `read()` | 服务器→客户端 | 返回 AsyncGenerator，yield 语言服务器产生的响应消息 |

这是一个极简的接口——它只关心消息的读写，不关心消息格式（JSON-RPC 2.0 由语言服务器自身和前端协商）、不关心连接生命周期（由 Session 管理）。

### write 的消息类型

`write()` 接收的参数类型是 `string | ArrayBuffer | Blob | ArrayBufferView`，这与 WebSocket 的 `send()` 方法参数类型一致，确保消息可以直接在 MockWebSocket 和语言服务器之间传递。

### read 的 AsyncGenerator 模式

`read()` 返回 `AsyncGenerator<string>` 是本接口设计的关键。使用异步生成器（for await...of）消费消息流：

```typescript
for await (const msg of langServer.read()) {
  socket.send(msg);  // 将语言服务器消息转发给前端
}
```

相比事件监听模式（如 `on('message', callback)`），AsyncGenerator 模式：
- 天然支持异步迭代，无需手动管理监听器注册/注销
- 与 Web Worker 的消息传递模型（onmessage 事件）通过 WaitQueue 桥接
- 循环退出时自动清理（当 `_worker` 为 null 时循环终止）

## IAddServerOptions 与 IServerFactory

语言服务器注册时传入的选项：

```typescript
export interface IAddServerOptions {
  spec: SCHEMA.LanguageServerSpec;
  createNewServer: IServerFactory;
}

export interface IServerFactory {
  (): Promise<IJSONRPCLanguageServer>;
}
```

- `spec`：语言服务器的元数据（显示名、支持的语言、MIME 类型等），遵循 jupyterlab-lsp 的 schema 定义
- `createNewServer`：工厂函数，返回 Promise（支持异步动态 import），每次连接时调用创建新的服务器实例

## LanguageServers 注册中心

LanguageServers 类实现 ILanguageServers 接口，是语言服务器的注册中心和状态管理器：

```typescript
export class LanguageServers implements ILanguageServers {
  _specs = new Map<string, SCHEMA.LanguageServerSpec>();
  _sessions = new Map<string, Session>();

  addLanguageServer(id: string, options: IAddServerOptions): void {
    this._specs.set(id, options.spec);
    this._sessions.set(id, new Session(id, options));
  }

  async status(): Promise<SCHEMA.ServersResponse> {
    const response: SCHEMA.ServersResponse = { version: 2, sessions: {}, specs: {} };
    for (const [id, session] of this._sessions.entries()) {
      response.sessions[id] = session.toJSON();
    }
    for (const [id, spec] of this._specs.entries()) {
      response.specs![id] = spec;
    }
    return response;
  }
}
```

注意：`addLanguageServer` 在注册时立即创建 Session 实例（`new Session(id, options)`），Session 构造函数中立即调用 `void this.initServer()` 启动 WebSocketServer——这意味着语言服务器在 JupyterLite 启动时就开始监听连接，而不是等待前端发起连接。

## Session 类

Session 类封装单个语言服务器的 WebSocket 桥接，是连接前端 MockWebSocket 和后端 IJSONRPCLanguageServer 的核心枢纽。

### 构造与初始化

```typescript
export class Session {
  constructor(id: string, options: IAddServerOptions) {
    this._id = id;
    this._options = options;
    void this.initServer();  // 异步启动，不阻塞构造
  }
```

### WebSocket URL

```typescript
get url() {
  return `${WS_BASE_URL}lsp/ws/${this._id}`;
}
```

WS_BASE_URL 由 `PageConfig.getBaseUrl().replace(/^http/, 'ws')` 生成。例如 JupyterLite 部署在 `http://localhost:8000/` 时，YAML 服务器的 WebSocket URL 为 `ws://localhost:8000/lsp/ws/json`。

### initServer：创建虚拟 WebSocket 服务端

```typescript
async initServer() {
  const wsServer = new WebSocketServer(this.url);

  wsServer.on('connection', async (socket: WebSocketClient) => {
    this._wsClient = socket;
    const _langServer = (this._langServer = await this._options.createNewServer());
    await _langServer.initialize();
    socket.on('message', this.onMessage);
    void this.read(_langServer, socket);
  });
}
```

连接建立后的流程：
1. 保存 socket 引用
2. 调用工厂函数创建语言服务器实例（动态 import + new）
3. 调用 `initialize()` 初始化服务器（启动 Worker 等）
4. 注册 message 事件监听（前端→服务器）
5. 启动 read 循环（服务器→前端），不 await 以避免阻塞

### 双向消息桥接

**前端→服务器**（onMessage 箭头函数）：

```typescript
onMessage = async (msg: string | ArrayBuffer | Blob | ArrayBufferView): Promise<void> => {
  this._langServer?.write(msg);
};
```

**服务器→前端**（read 方法）：

```typescript
async read(langServer: IJSONRPCLanguageServer, socket: WebSocketClient) {
  for await (const msg of langServer.read()) {
    socket.send(msg);
  }
}
```

注意 `onMessage` 使用箭头函数定义，确保 `this` 绑定正确；而 `read` 是普通方法，在 initServer 中通过 `void this.read(...)` 调用。

### toJSON：状态序列化

```typescript
toJSON(): SCHEMA.LanguageServerSession {
  return {
    handler_count: this._handlerCount,        // 始终为 0
    last_handler_message_at: '',               // 空字符串
    status: 'not_started',                     // 固定值
    last_server_message_at: '',                // 空字符串
    spec: this._options.spec,
  };
}
```

当前版本（0.1.0-alpha0）的状态报告非常简单，handler_count 未实际递增、时间戳字段为空、状态固定为 'not_started'。这是因为浏览器内 LSP 的会话状态管理尚未完整实现。

## 消息流总结

```
前端 (jupyterlab-lsp)
    │
    │ 1. MockWebSocket.send(msg)
    ▼
mock-socket WebSocketServer
    │
    │ 2. socket 'message' event
    ▼
Session.onMessage(msg)
    │
    │ 3. langServer.write(msg)
    ▼
IJSONRPCLanguageServer 实现（如 JSONLanguageServer）
    │
    │ 4. worker.postMessage(msg)
    ▼
Web Worker (yaml-language-server)
    │
    │ 5. worker.onmessage → _readQueue.unshift(data)
    │ 6. read() AsyncGenerator yields msg
    ▼
Session.read() for await loop
    │
    │ 7. socket.send(msg)
    ▼
mock-socket → MockWebSocket.onmessage
    │
    ▼
前端 (jupyterlab-lsp) 接收响应
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [三插件体系](03-plugin-system.md)
- [YAML/JSON 语言服务器实现](06-yaml-server.md)
- [Mock-Socket 桥接机制](05-mock-socket-bridge.md)
- [添加自定义语言服务器](../examples/add-custom-language-server.md)
