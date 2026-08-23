---
type: Reference
title: Monkey-patch 源码引用（hacks.ts）
description: hacks.ts 中 ServerConnection 和 WebSocket 的 Monkey-patch 实现
tags: [source, hacks, mock-socket, monkey-patch]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: lsp-hacks
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/hacks.ts
    title: packages/lsp/src/hacks.ts
  - id: dodo-py
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/dodo.py
    title: dodo.py（构建时 WebSocket patch）
---

## hacks.ts 完整源码

`packages/lsp/src/hacks.ts` 是 jupyterlite-lsp 能够在浏览器内运行 LSP 的关键文件，包含两个 Monkey-patch：

```typescript
import { WebSocket } from 'mock-socket';
import { ServerConnection } from '@jupyterlab/services';
import { JupyterLiteServer } from '@jupyterlite/server';
import { DEBUG, ILSPHacks } from './tokens';

function hackServerConnection(app: JupyterLiteServer) {
  const realMakeSettings = ServerConnection.makeSettings;

  function makeSettings(options?: Partial<ServerConnection.ISettings>) {
    const settings = realMakeSettings({
      ...(options || {}),
      fetch: app.fetch.bind(app),
    });
    DEBUG && console.debug('settings', settings);
    return settings;
  }

  ServerConnection.makeSettings = makeSettings;
}

function hoistMockSocket() {
  (window as any).MockWebSocket = WebSocket;
}

export function applyHacks(app: JupyterLiteServer): ILSPHacks {
  hackServerConnection(app);
  hoistMockSocket();
  return { hacked: true };
}
```

## 两个 Patch 的作用

### hackServerConnection

- 保存原始 `ServerConnection.makeSettings` 引用
- 替换为自定义版本，在 options 中注入 `app.fetch.bind(app)` 作为 fetch 实现
- 这使得 jupyterlab-lsp 前端发出的 REST 请求（如 `/lsp/status`）通过 JupyterLiteServer 的 service worker fetch 处理，而非真实网络请求

### hoistMockSocket

- 将 `mock-socket` 库的 `WebSocket` 类挂载到 `window.MockWebSocket`
- 构建时（dodo.py 中 task_hack），jupyterlab-lsp 的 connection.js 文件中的 `new WebSocket(...)` 被字符串替换为 `new window.MockWebSocket(...)`
- 这使得 jupyterlab-lsp 创建的 WebSocket 连接指向 mock-socket 的虚拟服务端，而非真实网络

## dodo.py 构建时 Patch

```python
class C:
    NATIVE_WEBSOCKET = "new WebSocket"
    HACKED_WEBSOCKET = "new window.MockWebSocket"

def task_hack():
    file_dep = U.expand_paths([*D.JS_TASKS["lite:build"]["targets"]])
    yield dict(
        name="connection.js",
        file_dep=file_dep,
        targets=[B.CONNECTION_JS],
        actions=[
            (U.patch_one, [C.NATIVE_WEBSOCKET, C.HACKED_WEBSOCKET, B.CONNECTION_JS])
        ],
    )
```

被 patch 的目标文件：`build/lite/extensions/@krassowski/jupyterlab-lsp/static/321.0176abf53bb1a24b854d.js`（jupyterlab-lsp 构建产物中的 connection 模块）。

## ILSPHacks 接口

```typescript
export interface ILSPHacks {
  // 空接口，仅作为 Token 标记
}
```

applyHacks 返回 `{ hacked: true }`，但调用方不使用返回值。

## 相关概念

- [Mock-Socket 桥接机制](/concepts/05-mock-socket-bridge.md)
- [三插件体系](/concepts/03-plugin-system.md)
- [构建系统](/concepts/07-build-system.md)
- [核心包源码引用](/references/core-plugin-source.md)
