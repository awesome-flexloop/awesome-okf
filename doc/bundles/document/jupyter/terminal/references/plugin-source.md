---
type: Reference
title: 插件系统源码信源
description: 六个JupyterLab/Lite插件的定义、依赖关系和activate实现
tags: [plugin, jupyterlab, jupyterlite, token, dependency-injection]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: index-ts
    resource: /../../../../../../external/libs/jupyter/terminal/src/index.ts
    title: src/index.ts
---

# 插件系统源码信源

## 插件总览

src/index.ts 默认导出6个插件，具名导出4个标识符。

| # | 插件ID | 类型 | provides | requires | optional | autoStart |
|---|--------|------|----------|----------|----------|-----------|
| 1 | `@jupyterlite/terminal:client` | ServiceManagerPlugin | ILiteTerminalAPIClient | - | IServerSettings | true |
| 2 | `@jupyterlite/terminal:manager` | ServiceManagerPlugin | ITerminalManager | ILiteTerminalAPIClient | - | true |
| 3 | `@jupyterlite/terminal:contents` | JupyterFrontEndPlugin | void | ILiteTerminalAPIClient | - | true |
| 4 | `@jupyterlite/terminal:service-worker` | JupyterFrontEndPlugin | void | ILiteTerminalAPIClient | IServiceWorkerManager | true |
| 5 | `@jupyterlite/terminal:theme-change` | JupyterFrontEndPlugin | void | ILiteTerminalAPIClient, ISettingRegistry | IThemeManager | true |
| 6 | `@jupyterlite/terminal:exec` | JupyterFrontEndPlugin | void | ILiteTerminalAPIClient | - | true |

## 具名导出

| 导出标识符 | 类型 | 来源 |
|-----------|------|------|
| `ILiteTerminalAPIClient` | Token<ILiteTerminalAPIClient> | tokens.ts |
| `ITerminalShell` | interface | shell.ts |
| `LiteTerminalAPIClient` | class | client.ts |
| `TerminalShell` | class | shell.ts |

## 各插件实现详情

### terminalClientPlugin

```typescript
const terminalClientPlugin: ServiceManagerPlugin<Terminal.ITerminalAPIClient> = {
  id: '@jupyterlite/terminal:client',
  description: 'The client for Lite terminals',
  autoStart: true,
  provides: ILiteTerminalAPIClient,
  optional: [IServerSettings],
  activate: (_: null, serverSettings?: ServerConnection.ISettings): ILiteTerminalAPIClient => {
    return new LiteTerminalAPIClient({
      serverSettings: {
        ...ServerConnection.makeSettings(),
        ...serverSettings,
        WebSocket  // 来自mock-socket，替换原生WebSocket
      }
    });
  }
};
```

关键点：WebSocket被替换为mock-socket的实现，使得JupyterLab终端代码在浏览器内连接到本地WebSocketServer而非远程服务器。

### terminalManagerPlugin

```typescript
const terminalManagerPlugin: ServiceManagerPlugin<Terminal.IManager> = {
  id: '@jupyterlite/terminal:manager',
  autoStart: true,
  provides: ITerminalManager,
  requires: [ILiteTerminalAPIClient],
  activate: (_: null, terminalAPIClient: Terminal.ITerminalAPIClient): Terminal.IManager => {
    return new TerminalManager({
      terminalAPIClient,
      serverSettings: terminalAPIClient.serverSettings
    });
  }
};
```

关键点：使用JupyterLab标准的TerminalManager，但注入自定义的terminalAPIClient。

### terminalContentsPlugin

```typescript
activate: (app: JupyterFrontEnd, liteTerminalAPIClient: ILiteTerminalAPIClient): void => {
  const { contents: contentsManager } = app.serviceManager;
  liteTerminalAPIClient.contentsManager = contentsManager;
}
```

关键点：将app.serviceManager.contents注入到客户端，使shell可以访问虚拟文件系统。

### terminalServiceWorkerPlugin

```typescript
activate: (_, liteTerminalAPIClient, serviceWorkerManager?) => {
  if (serviceWorkerManager) {
    liteTerminalAPIClient.browsingContextId = serviceWorkerManager.browsingContextId;
    serviceWorkerManager.registerStdinHandler(
      'terminal',
      liteTerminalAPIClient.handleStdin.bind(liteTerminalAPIClient)
    );
  } else {
    console.warn('Service worker is not available for terminals');
  }
}
```

关键点：注册stdin处理器到Service Worker，key为'terminal'。

### terminalThemeChangePlugin

两部分监听：
1. `themeManager.themeChanged`信号：当terminalTheme为'inherit'时，同步暗色/亮色模式
2. `settingRegistry.load('@jupyterlab/terminal-extension:plugin')`的changed信号：监听终端主题设置变化

```typescript
themeManager?.themeChanged.connect(async (_, changedArgs) => {
  if (terminalTheme === 'inherit') {
    const isDarkMode = !themeManager.isLight(changedArgs.newValue);
    liteTerminalAPIClient.themeChange(isDarkMode);
  }
});

settingRegistry.load('@jupyterlab/terminal-extension:plugin').then(setting => {
  terminalTheme = setting.composite.theme as string;
  setting.changed.connect(() => {
    const newTerminalTheme = setting.composite.theme as string;
    if (newTerminalTheme !== terminalTheme) {
      liteTerminalAPIClient.themeChange();
      terminalTheme = newTerminalTheme;
    }
  });
});
```

### terminalExecPlugin

```typescript
activate: (app: JupyterFrontEnd, liteTerminalAPIClient: ILiteTerminalAPIClient): void => {
  const pool = new HeadlessShellPool(liteTerminalAPIClient);
  registerCommands(app.commands, pool);
}
```

关键点：创建HeadlessShellPool实例并注册4个编程式命令。详见exec-source.md。
