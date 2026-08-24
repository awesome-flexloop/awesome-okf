---
type: Reference
title: YAML语言服务器包源码引用（@jupyterlite/lsp-yaml）
description: "@jupyterlite/lsp-yaml 语言服务器包的 plugin.ts、server.ts、tokens.ts、worker.ts 源码引用"
tags: [source, yaml, json, language-server, worker]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: yaml-plugin
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/plugin.ts
    title: packages/lsp-yaml/src/plugin.ts
  - id: yaml-server
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/server.ts
    title: packages/lsp-yaml/src/server.ts
  - id: yaml-tokens
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/tokens.ts
    title: packages/lsp-yaml/src/tokens.ts
  - id: yaml-worker
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/worker.ts
    title: packages/lsp-yaml/src/worker.ts
  - id: yaml-package
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/package.json
    title: packages/lsp-yaml/package.json
---

## lsp-yaml 包文件清单

`@jupyterlite/lsp-yaml` 包位于 `packages/lsp-yaml/`，提供 YAML/JSON 语言服务器支持：

| 文件 | 职责 |
|------|------|
| `src/index.ts` | 统一导出 tokens、server、plugin |
| `src/tokens.ts` | 定义常量（NS、SERVER_PLUGIN_ID、SPEC） |
| `src/plugin.ts` | 定义 JupyterLiteServerPlugin，向 ILanguageServers 注册 json 服务器 |
| `src/server.ts` | JSONLanguageServer 类，实现 IJSONRPCLanguageServer 接口 |
| `src/worker.ts` | 一行导入，用于 webpack 打包 yaml-language-server worker |

## tokens.ts SPEC 定义

```typescript
export const SPEC: SCHEMA.ServerSpecProperties = {
  display_name: 'YAML',
  languages: ['yaml', 'json'],
  mime_types: ['text/x-yaml', 'text/yaml', 'application/json'],
  version: 2,
};
```

注意：虽然注册名为 `json`，display_name 为 `YAML`，同时支持 yaml 和 json 两种语言。

## plugin.ts 插件定义

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

使用动态 `import('./server')` 延迟加载服务器实现。

## server.ts JSONLanguageServer 完整实现

```typescript
import type WaitQueue from 'wait-queue';
import { DEBUG, IJSONRPCLanguageServer } from '@jupyterlite/lsp';

export class JSONLanguageServer implements IJSONRPCLanguageServer {
  private _worker: Worker | null = null;
  private _readQueue: WaitQueue<any> | null = null;

  async initialize(): Promise<void> {
    const { default: WaitQueue } = await import('wait-queue');
    this._readQueue = new WaitQueue();
    this._worker = new Worker(
      new URL('yaml-language-server/lib/esm/webworker/yamlServerMain', import.meta.url)
    );
    this._worker.onmessage = this.onWorkerMessage;
  }

  onWorkerMessage(msg: MessageEvent) {
    this._readQueue?.unshift(msg.data);
  }

  async *read(): AsyncGenerator<string> {
    let msg: any;
    while (this._worker) {
      msg = await this._readQueue?.pop();
      yield msg;
    }
  }

  async write(msg: string) {
    this._worker?.postMessage(msg);
  }
}
```

消息桥接流程：
1. **客户端→服务端**：`Session.onMessage` → `langServer.write(msg)` → `worker.postMessage(msg)` → yaml-language-server worker
2. **服务端→客户端**：yaml-language-server worker → `worker.onmessage` → `_readQueue.unshift(data)` → `read()` AsyncGenerator yield → `socket.send(msg)` → 前端

## worker.ts

```typescript
import 'yaml-language-server/lib/esm/webworker/yamlServerMain';
```

这一行确保 webpack 将 yaml-language-server 的 web worker 入口打包进 bundle。

## npm 依赖

| 包 | 版本 | 用途 |
|---|---|---|
| `@jupyterlite/lsp` | ^0.1.0a0 | 核心 LSP 抽象（接口、Token） |
| `@jupyterlite/server` | ^0.1.0-beta.15 | JupyterLite 服务端插件 API |
| `jsonc-parser` | ^3.2.0 | JSON with Comments 解析器（yaml-language-server 依赖） |
| `wait-queue` | ^1.1.4 | 异步等待队列，用于 Worker 消息到 AsyncGenerator 的桥接 |
| `yaml-language-server` | ^1.10.0 | Red Hat 出品的 YAML/JSON 语言服务器 |

## 相关概念

- [YAML/JSON 语言服务器](/concepts/06-yaml-server.md)
- [IJSONRPCLanguageServer 接口](/concepts/04-language-server-interface.md)
- [核心包源码引用](/references/core-plugin-source.md)
- [添加自定义语言服务器示例](/examples/add-custom-language-server.md)
