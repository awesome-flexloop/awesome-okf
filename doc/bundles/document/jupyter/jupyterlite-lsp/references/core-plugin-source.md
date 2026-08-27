---
type: Reference
title: 核心LSP包源码引用（@jupyterlite/lsp）
description: "@jupyterlite/lsp 核心包的 plugin.ts、servers.ts、session.ts、tokens.ts 源码引用"
tags: [source, lsp, plugin, session, tokens]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: lsp-plugin
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/plugin.ts
    title: packages/lsp/src/plugin.ts
  - id: lsp-servers
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/servers.ts
    title: packages/lsp/src/servers.ts
  - id: lsp-session
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/session.ts
    title: packages/lsp/src/session.ts
  - id: lsp-tokens
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/tokens.ts
    title: packages/lsp/src/tokens.ts
  - id: lsp-index
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/index.ts
    title: packages/lsp/src/index.ts
  - id: lsp-package
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/package.json
    title: packages/lsp/package.json
---

## 核心包文件清单

`@jupyterlite/lsp` 包位于 `packages/lsp/`，包含以下源文件：

| 文件 | 职责 |
|------|------|
| `src/index.ts` | 统一导出 plugin、tokens、servers 三个模块 |
| `src/tokens.ts` | 定义 Token（ILanguageServers、ILSPHacks）和接口（IAddServerOptions、IServerFactory、IJSONRPCLanguageServer），以及常量（DEBUG、WS_BASE_URL） |
| `src/plugin.ts` | 定义三个 JupyterLiteServerPlugin：hacksPlugin、serverPlugin、routesPlugin |
| `src/servers.ts` | LanguageServers 类实现 ILanguageServers，管理 specs 和 sessions Map |
| `src/session.ts` | Session 类，封装单个语言服务器的 WebSocket 桥接 |
| `src/hacks.ts` | Monkey-patch 函数（不在本引用文件中，见 hacks-source.md） |

## tokens.ts 关键定义

```typescript
export const ILanguageServers = new Token<ILanguageServers>(`${NS}:ILSPServer`);

export interface ILanguageServers {
  addLanguageServer(id: string, options: IAddServerOptions): void;
  status(): Promise<SCHEMA.ServersResponse>;
}

export interface IAddServerOptions {
  spec: SCHEMA.LanguageServerSpec;
  createNewServer: IServerFactory;
}

export interface IServerFactory {
  (): Promise<IJSONRPCLanguageServer>;
}

export interface IJSONRPCLanguageServer {
  initialize(): Promise<void>;
  write(msg: string | ArrayBuffer | Blob | ArrayBufferView): Promise<void>;
  read(): AsyncGenerator<string>;
}

export const DEBUG = window.location.href.includes('LSP_LITE_DEBUG');
export const WS_BASE_URL = PageConfig.getBaseUrl().replace(/^http/, 'ws');
```

Plugin ID 常量：
- `HACKS_PLUGIN_ID = ${NS}:hacks`
- `SERVER_PLUGIN_ID = ${NS}:plugin`
- `ROUTES_PLUGIN_ID = ${NS}:routes`

## plugin.ts 三插件定义

```typescript
const hacksPlugin: JupyterLiteServerPlugin<ILSPHacks> = {
  id: HACKS_PLUGIN_ID,
  provides: ILSPHacks,
  autoStart: true,
  activate: (app: JupyterLiteServer): ILSPHacks => applyHacks(app),
};

const serverPlugin: JupyterLiteServerPlugin<ILanguageServers> = {
  id: SERVER_PLUGIN_ID,
  provides: ILanguageServers,
  autoStart: true,
  activate: (app: JupyterLiteServer) => new LanguageServers(),
};

const routesPlugin: JupyterLiteServerPlugin<void> = {
  id: ROUTES_PLUGIN_ID,
  autoStart: true,
  requires: [ILanguageServers],
  activate: (app: JupyterLiteServer, lsp: ILanguageServers) => {
    app.router.get('/lsp/status', async (req, filename) => {
      return new Response(JSON.stringify(await lsp.status()));
    });
  },
};
```

## servers.ts LanguageServers 类

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

## session.ts Session 类关键方法

```typescript
export class Session {
  constructor(id: string, options: IAddServerOptions) { ... }

  get url() { return `${WS_BASE_URL}lsp/ws/${this._id}`; }

  async initServer() {
    const wsServer = new WebSocketServer(this.url);
    wsServer.on('connection', async (socket) => {
      this._wsClient = socket;
      const _langServer = (this._langServer = await this._options.createNewServer());
      await _langServer.initialize();
      socket.on('message', this.onMessage);
      void this.read(_langServer, socket);
    });
  }

  async read(langServer: IJSONRPCLanguageServer, socket: WebSocketClient) {
    for await (const msg of langServer.read()) {
      socket.send(msg);
    }
  }

  onMessage = async (msg) => { this._langServer?.write(msg); };

  toJSON(): SCHEMA.LanguageServerSession {
    return {
      handler_count: this._handlerCount,
      last_handler_message_at: '',
      status: 'not_started',
      last_server_message_at: '',
      spec: this._options.spec,
    };
  }
}
```

Session 从 `mock-socket` 导入 `Client as WebSocketClient, Server as WebSocketServer`。

## 相关概念

- [三插件体系](../concepts/03-plugin-system.md)
- [IJSONRPCLanguageServer 接口](../concepts/04-language-server-interface.md)
- [Mock-Socket 桥接机制](../concepts/05-mock-socket-bridge.md)
- [Hack 源码引用](hacks-source.md)
