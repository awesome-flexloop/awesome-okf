---
type: Concept
title: JupyterLab 插件基础结构
description: 了解 JupyterLab 插件的基本结构：JupyterFrontEndPlugin 对象、id、autoStart、requires/optional/provides、activate 函数的签名与用法。
tags: [jupyterlab, plugin, basics, jupyterfrontendplugin, activate]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: source-index
    resource: /references/source-index.md
    title: Plugin Playground 源码索引
  - id: loader-api
    resource: /references/loader-transpiler-api.md
    title: PluginLoader 与 PluginTranspiler API 参考
---

## JupyterLab 插件是什么

JupyterLab 插件是一个遵循 `JupyterFrontEndPlugin` 接口的 JavaScript/TypeScript 对象。它通过 `activate` 函数与 JupyterLab 应用交互，可以注册命令、添加 UI 组件、扩展菜单和工具栏、监听事件等。

在 Plugin Playground 中，你编写的 TypeScript 代码需要 `export default` 一个插件对象（或插件数组），PluginLoader 会提取这个对象并激活它。

## 插件对象结构

一个最基本的 JupyterLab 插件对象包含以下字段：

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-plugin:main',
  autoStart: true,
  requires: [],
  optional: [],
  provides: undefined,
  activate: (app: JupyterFrontEnd) => {
    // 插件逻辑
  }
};

export default plugin;
```

### id（必需）

```typescript
id: string
```

插件的唯一标识符，格式通常为 `包名:功能名`（如 `'hello-world:plugin'`）。ID 在 JupyterLab 中必须唯一，重复 ID 的插件会互相覆盖。

在 Plugin Playground 中，ID 还用于匹配 JSON schema 文件——多插件场景下 schema 文件按 ID 冒号后的后缀命名（如 ID `'my-plugin:advanced'` 对应 `advanced.json`）。

### autoStart

```typescript
autoStart?: boolean
```

是否自动启动。设置为 `true` 时，JupyterLab 加载后自动调用 `activate` 函数。设置为 `false`（或省略）时，插件仅在被其他插件依赖或用户手动激活时启动。

在 Plugin Playground 中，你通常需要设置 `autoStart: true`，否则插件不会自动运行。

### activate（必需）

```typescript
activate: (app: JupyterFrontEnd, ...deps: any[]) => void | Promise<void> | any
```

插件的激活函数，是插件逻辑的入口点。第一个参数始终是 `JupyterFrontEnd` 实例（即 `app` 对象），后续参数是 `requires` 和 `optional` 中声明的依赖。

activate 函数可以：
- 返回 `void` 或 `Promise<void>`
- 返回一个实现了 `provides` Token 接口的对象
- 是异步函数（async），可以 await 异步操作

### requires

```typescript
requires?: Token<any>[]
```

必需依赖列表，是一个 Token 数组。JupyterLab 在激活插件时会解析这些 Token 对应的服务，并按顺序传入 activate 函数。

在 Plugin Playground 中，你可以使用字符串形式的 Token 名（如 `'@jupyterlab/apputils:ICommandPalette'`），PluginLoader 会自动将字符串解析为 Token 实例。你也可以直接从包中 import Token：

```typescript
import { ICommandPalette } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-plugin:with-deps',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    // 使用 palette
  }
};
```

### optional

```typescript
optional?: Token<any>[]
```

可选依赖列表。与 `requires` 类似，但如果 Token 不可用不会导致插件加载失败，而是传入 `null`。

### provides

```typescript
provides?: Token<any>
```

插件提供的服务 Token。如果插件实现了某个 Token 接口并希望被其他插件依赖，通过 provides 声明。此时 activate 函数应返回实现了该接口的对象。

## activate 函数参数详解

activate 函数接收的参数顺序为：

1. `app: JupyterFrontEnd` - JupyterLab 前端应用实例
2. `requires` 中声明的所有 Token 对应服务（按顺序）
3. `optional` 中声明的所有 Token 对应服务（按顺序，不可用时为 null）

### JupyterFrontEnd（app 对象）

`app` 是最核心的对象，提供了访问 JupyterLab 各个子系统的入口：

| 属性/方法 | 用途 |
|-----------|------|
| `app.commands` | 命令注册与执行 |
| `app.shell` | 界面布局管理（添加 widget 到左/右/主区域） |
| `app.serviceManager` | 服务管理器（文件、会话、内核等） |
| `app.docRegistry` | 文档类型注册 |
| `app.restored` | Promise，在应用恢复完成后 resolve |
| `app.started` | Promise，在应用启动完成后 resolve |
| `app.contextMenu` | 右键菜单 |
| `app.commands.addCommand()` | 注册新命令 |

## 插件导出格式

Plugin Playground 支持两种插件导出格式：

### 新格式：ES Module Default Export（推荐）

```typescript
const plugin: JupyterFrontEndPlugin<void> = { /* ... */ };
export default plugin;
```

也支持默认导出数组（多插件）：

```typescript
const plugin1: JupyterFrontEndPlugin<void> = { /* ... */ };
const plugin2: JupyterFrontEndPlugin<void> = { /* ... */ };
export default [plugin1, plugin2];
```

还支持工厂函数和异步工厂：

```typescript
// 工厂函数
export default () => {
  return { id: 'factory:plugin', autoStart: true, activate: () => {} };
};

// 异步工厂
export default async () => {
  const data = await fetchSomeConfig();
  return { id: 'async:plugin', autoStart: true, activate: () => { /* use data */ } };
};
```

### 旧格式：RequireJS 对象返回

当代码中没有 `export default` 时，PluginLoader 会回退到旧格式：

```javascript
// 直接返回插件对象（不是ES module，没有import/export）
({
  id: 'old-style:plugin',
  autoStart: true,
  activate: function(app) {
    alert('Hello from old style!');
  }
})
```

旧格式使用 `requirejs`/`define`/`require` 作为全局函数，不支持 ES module 的 `import`/`export` 语法。建议使用新格式。

## 多插件导出

一个文件可以导出多个插件，它们会被依次激活：

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin1: JupyterFrontEndPlugin<void> = {
  id: 'multi:first',
  autoStart: true,
  activate: (app) => { console.log('first loaded'); }
};

const plugin2: JupyterFrontEndPlugin<void> = {
  id: 'multi:second',
  autoStart: true,
  requires: [],
  activate: (app) => { console.log('second loaded'); }
};

export default [plugin1, plugin2];
```

## 最小可运行插件

这是你能在 Plugin Playground 中运行的最小插件：

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'minimal:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('Plugin activated!');
  }
};

export default plugin;
```

它会在浏览器控制台输出 "Plugin activated!"。打开浏览器开发者工具（F12）即可看到输出。

## 相关概念

- [整体架构与数据流](01-architecture-overview.md)
- [TypeScript 转译机制](03-typescript-transpilation.md)
- [插件加载流程](05-plugin-loader.md)
- [Token 依赖注入系统](06-token-system.md)
- [Hello World 示例](../examples/01-hello-world.md)
