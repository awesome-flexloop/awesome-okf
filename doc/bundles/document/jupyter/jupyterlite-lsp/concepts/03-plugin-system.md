---
type: Concept
title: 三插件体系
description: "@jupyterlite/lsp 核心包的三个插件（hacksPlugin、serverPlugin、routesPlugin）的职责、依赖关系与启动机制"
tags: [plugin, jupyterlite, hacks, server, routes, token]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: core
    resource: /references/core-plugin-source.md
    title: 核心LSP包源码引用
  - id: hacks
    resource: /references/hacks-source.md
    title: Monkey-patch 源码引用
---

## 插件总览

`@jupyterlite/lsp` 核心包导出三个 JupyterLiteServerPlugin，在 plugin.ts 中以数组形式默认导出：

```typescript
export default [hacksPlugin, serverPlugin, routesPlugin];
```

| 插件 | ID | provides | requires | autoStart | 职责 |
|------|-----|----------|----------|-----------|------|
| hacksPlugin | `@jupyterlite/lsp:hacks` | ILSPHacks | 无 | true | Monkey-patch 运行时环境 |
| serverPlugin | `@jupyterlite/lsp:plugin` | ILanguageServers | 无 | true | 创建并持有 LanguageServers 实例 |
| routesPlugin | `@jupyterlite/lsp:routes` | 无 | ILanguageServers | true | 注册 REST API 路由 |

## hacksPlugin

```typescript
const hacksPlugin: JupyterLiteServerPlugin<ILSPHacks> = {
  id: HACKS_PLUGIN_ID,
  provides: ILSPHacks,
  autoStart: true,
  activate: (app: JupyterLiteServer): ILSPHacks => {
    return applyHacks(app);
  },
};
```

hacksPlugin 是系统启动的第一个插件，负责执行运行时环境的 Monkey-patch：

1. **hackServerConnection(app)**：替换 `ServerConnection.makeSettings`，将 JupyterLab 的 fetch 请求绑定到 JupyterLiteServer 的 app.fetch，使 REST API 调用通过 Service Worker 处理
2. **hoistMockSocket()**：将 mock-socket 的 WebSocket 类挂载到 `window.MockWebSocket`，供构建时 patched 的 jupyterlab-lsp 前端代码使用

applyHacks 返回 `{ hacked: true }`，但 ILSPHacks 接口定义为空接口，该返回值不被其他插件直接使用——Token 本身的存在标记了 hacks 已执行。

## serverPlugin

```typescript
const serverPlugin: JupyterLiteServerPlugin<ILanguageServers> = {
  id: SERVER_PLUGIN_ID,
  provides: ILanguageServers,
  autoStart: true,
  activate: (app: JupyterLiteServer) => {
    const server = new LanguageServers();
    return server;
  },
};
```

serverPlugin 创建 LanguageServers 实例并通过 ILanguageServers Token 提供给其他插件。LanguageServers 维护两个 Map：

- `_specs: Map<string, LanguageServerSpec>`：语言服务器规格描述
- `_sessions: Map<string, Session>`：活跃的语言服务器会话

其他插件（包括外部语言服务器包如 lsp-yaml）通过注入 ILanguageServers Token 来注册语言服务器。

## routesPlugin

```typescript
const routesPlugin: JupyterLiteServerPlugin<void> = {
  id: ROUTES_PLUGIN_ID,
  autoStart: true,
  requires: [ILanguageServers],
  activate: (app: JupyterLiteServer, lsp: ILanguageServers) => {
    app.router.get('/lsp/status', async (req, filename) => {
      const res = await lsp.status();
      return new Response(JSON.stringify(res));
    });
  },
};
```

routesPlugin 依赖 ILanguageServers Token，在 JupyterLiteServer 的 router 上注册 REST 端点。当前版本仅实现了一个端点：

- **GET `/lsp/status`**：返回所有已注册语言服务器的规格（specs）和会话状态（sessions），响应格式为 `{ version: 2, sessions: {}, specs: {} }`

## Token 系统

jupyterlite-lsp 使用 Lumino 的 Token 机制实现依赖注入：

```typescript
export const ILanguageServers = new Token<ILanguageServers>(`${NS}:ILSPServer`);
export const ILSPHacks = new Token<ILSPHacks>(`${NS}:ILSPHacks`);
```

Token 是唯一标识符，JupyterLite 插件系统通过 Token 类型查找对应的提供者。外部语言服务器包在 plugin 的 requires 数组中声明 `[ILanguageServers]` 依赖，activate 函数即可接收到 LanguageServers 实例。

从 `@jupyterlite/lsp` 包的导出（index.ts）：

```typescript
export * from './plugin';   // 默认导出插件数组
export * from './tokens';   // 导出 Token 和接口
export * from './servers';  // 导出 LanguageServers 类
```

外部语言服务器包从 `@jupyterlite/lsp` 导入 ILanguageServers Token 和 IJSONRPCLanguageServer 等接口。

## 外部语言服务器插件模式

以 lsp-yaml 为例，语言服务器包的插件遵循以下模式：

```typescript
const plugin: JupyterLiteServerPlugin<void> = {
  id: SERVER_PLUGIN_ID,
  autoStart: true,
  requires: [ILanguageServers],  // 注入核心 LSP 注册中心
  activate: (app, lsp) => {
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

关键点：
- 使用动态 `import()` 延迟加载服务器实现，避免初始加载时的性能开销
- spec 遵循 jupyterlab-lsp 的 ServerSpecProperties schema
- 服务器 ID 在当前实现中为 `'json'`（尽管 SPEC.display_name 为 `'YAML'`）

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [IJSONRPCLanguageServer 接口](/concepts/04-language-server-interface.md)
- [LanguageServers 与 Session](/concepts/04-language-server-interface.md#sessions-管理)
- [核心包源码引用](/references/core-plugin-source.md)
