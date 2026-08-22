---
type: Concept
title: Token 依赖注入系统
description: JupyterLab 的 Token 依赖注入机制在 Plugin Playground 中的实现：字符串 Token 名到 Token 实例的映射、Proxy 属性拦截、requires/optional/provides 的工作原理。
tags: [jupyterlab, plugin-playground, token, dependency-injection, lumino, proxy]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: resolver-api
    resource: /references/resolver-api.md
    title: ImportResolver API 参考
  - id: loader-api
    resource: /references/loader-transpiler-api.md
    title: PluginLoader 与 PluginTranspiler API 参考
---

## 什么是 Token

在 JupyterLab（基于 Lumino）中，Token 是服务的唯一标识符，用于依赖注入。每个可被其他插件依赖的服务都会定义一个 Token，其他插件通过在 `requires`/`optional` 中引用该 Token 来获取服务实例。

```typescript
import { Token } from '@lumino/coreutils';

// 定义一个服务 Token
export const IMyService = new Token<IMyService>('my-package:IMyService');

// 插件提供该服务
const plugin = {
  id: 'my-package:plugin',
  provides: IMyService,
  activate: (app) => new MyService()
};

// 其他插件依赖该服务
const otherPlugin = {
  id: 'other:plugin',
  requires: [IMyService],
  activate: (app, myService) => {
    myService.doSomething();
  }
};
```

## Plugin Playground 中的 Token 映射

在常规 JupyterLab 扩展开发中，你通过 `import { ICommandPalette } from '@jupyterlab/apputils'` 获取 Token 实例。Plugin Playground 支持这种方式，但也支持使用字符串形式的 Token 名。

### 双轨Token获取机制

PluginLoader 和 ImportResolver 协同工作，确保以下两种写法都能正确获取依赖：

**方式1：直接 import Token（推荐）**

```typescript
import { ICommandPalette } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'test:plugin',
  autoStart: true,
  requires: [ICommandPalette],  // 直接使用Token实例
  activate: (app, palette) => {
    palette.addItem({ command: 'test:cmd', category: 'Test' });
  }
};
```

**方式2：使用字符串 Token 名**

```typescript
// 不import Token，直接在requires中使用字符串
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'test:plugin',
  autoStart: true,
  requires: ['@jupyterlab/apputils:ICommandPalette'],  // 字符串形式
  activate: (app, palette) => {
    palette.addItem({ command: 'test:cmd', category: 'Test' });
  }
};
```

### 字符串 Token 名的格式

字符串 Token 名的格式为 `'{包名}:{Token名}'`，例如：

| Token | 字符串名 |
|-------|---------|
| `ICommandPalette` (from @jupyterlab/apputils) | `'@jupyterlab/apputils:ICommandPalette'` |
| `IEditorTracker` (from @jupyterlab/fileeditor) | `'@jupyterlab/fileeditor:IEditorTracker'` |
| `ILauncher` (from @jupyterlab/launcher) | `'@jupyterlab/launcher:ILauncher'` |
| `ISettingRegistry` (from @jupyterlab/settingregistry) | `'@jupyterlab/settingregistry:ISettingRegistry'` |

你可以通过 Extension Points 侧边栏（TokenSidebar）浏览所有可用的 Token 名称。

## Token 解析流程

### 阶段1：ImportResolver 的 Proxy 拦截

当代码执行 `import { ICommandPalette } from '@jupyterlab/apputils'` 时，TypeScript 转译后变为：

```javascript
const { ICommandPalette } = await require("@jupyterlab/apputils");
```

这等价于从模块对象上解构 `ICommandPalette` 属性。ImportResolver 通过 Proxy 拦截属性访问：

```typescript
new Proxy(targetModule, {
  get: (target, prop, receiver) => {
    if (typeof prop !== 'string') {
      return Reflect.get(target, prop, receiver);
    }
    // 构造Token查找键
    const tokenName = `${module}:${prop}`;
    // 优先从tokenMap查找Token
    if (this._options.tokenMap.has(tokenName)) {
      return this._options.tokenMap.get(tokenName);
    }
    // 合成默认导入
    if (prop === 'default' && !(prop in target)) {
      return target;
    }
    return Reflect.get(target, prop, receiver);
  }
});
```

Proxy 的 `get` 陷阱（trap）在每次访问模块属性时触发：
1. 构造 `'{模块名}:{属性名}'` 作为查找键
2. 如果 tokenMap 中有该键，返回 Token 实例（而非模块的实际导出）
3. 如果访问 `default` 且模块没有 default 导出，返回模块本身
4. 否则返回模块的实际导出

这意味着，即使 `@jupyterlab/apputils` 模块实际上导出的 `ICommandPalette` 不是 Token 实例（或者在运行时模块结构不同），Proxy 也会从 tokenMap 中返回正确的 Token。

### 阶段2：PluginLoader 的 Token 解析

在提取插件对象后，PluginLoader._resolvePluginTokens() 进行第二轮解析：

```typescript
plugin.requires = plugin.requires?.map(value => {
  if (typeof value !== 'string') return value;  // 已经是Token实例
  const token = tokenMap.get(value);
  if (!token) throw Error(`Required token ${value} not found`);
  return token;
});

plugin.optional = plugin.optional?.map(value => {
  if (typeof value !== 'string') return value;
  const token = tokenMap.get(value);
  if (!token) console.log(`Optional token ${value} not found`);
  return token;
}).filter(token => token != null);
```

这一步处理 `requires`/`optional` 数组中的字符串值，将其替换为对应的 Token 实例。两个阶段共同确保：
- 通过 import 解构获取的 Token（Proxy拦截）正确
- 直接在 requires 数组中写字符串的 Token 也正确

### 为什么需要两个阶段

1. **Proxy阶段**处理 `import { Token } from 'pkg'` 语法——这种情况下Token作为模块属性被访问，需要Proxy拦截
2. **resolvePluginTokens阶段**处理 `requires: ['pkg:Token']` 语法——这种情况下字符串直接在requires数组中，不经过模块属性访问

## 默认导入合成

Proxy 还处理了 CommonJS/ES Module 互操作问题：

```typescript
if (prop === 'default' && !(prop in target)) {
  return target;  // 返回模块本身作为default
}
```

当代码使用 `import pkg from 'some-cjs-package'`（默认导入）而该模块没有 `default` 导出时，Proxy 返回模块对象本身作为 default。这使得 CommonJS 模块可以用 ES module 默认导入语法使用。

## tokenMap 的构建

tokenMap 是一个 `Map<string, Token<any>>`，在 PluginPlayground 类初始化时构建。它通过遍历 JupyterLab 应用的私有服务注册表收集所有已注册的 Token。TokenSidebar 也通过这个 Map 展示可用 Token 列表。

## 在插件中使用 Token

### 必需依赖（requires）

```typescript
import { ICommandPalette } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-ext:with-command-palette',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    // palette 永远不会是 null/undefined
    // 如果 ICommandPalette 不可用，插件加载失败
    app.commands.addCommand('my-ext:hello', {
      label: 'Say Hello',
      execute: () => alert('Hello!')
    });
    palette.addItem({ command: 'my-ext:hello', category: 'My Ext' });
  }
};

export default plugin;
```

### 可选依赖（optional）

```typescript
import { ILauncher } from '@jupyterlab/launcher';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-ext:with-launcher',
  autoStart: true,
  optional: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher | null) => {
    if (launcher) {
      // ILauncher 可用，添加启动器项
      launcher.add({
        command: 'my-ext:hello',
        category: 'Other'
      });
    }
    // 如果 launcher 为 null，跳过相关逻辑，插件正常加载
  }
};

export default plugin;
```

### 提供服务（provides）

```typescript
import { Token } from '@lumino/coreutils';

// 定义服务接口和Token
interface IMyService {
  greet(name: string): string;
}
const IMyService = new Token<IMyService>('my-ext:IMyService');

class MyService implements IMyService {
  greet(name: string) {
    return `Hello, ${name}!`;
  }
}

const plugin: JupyterFrontEndPlugin<IMyService> = {
  id: 'my-ext:service',
  autoStart: true,
  provides: IMyService,
  activate: (app): IMyService => {
    return new MyService();
  }
};

export default plugin;
```

### 混合使用

```typescript
requires: [ICommandPalette, IMainMenu],
optional: [ILauncher, IFileBrowserFactory],
activate: (app, palette, menu, launcher, browser) => {
  // 参数顺序：app, ...requires, ...optional
  // requires 一定可用，optional 可能为 null
}
```

## 命令自动补全

CommandCompletionProvider 为编辑器中的命令 ID 提供自动补全。当你在 `app.commands.execute('...')` 或 `palette.addItem({ command: '...' })` 中输入命令 ID 时，编辑器会弹出可用命令列表。

补全支持两种触发模式：
- **引号内补全**：`app.commands.execute('p|')` → 弹出以 "p" 开头的命令
- **裸标识符补全**：`app.commands.execute(p|)` → 弹出匹配命令并自动添加引号

## 相关概念

- [模块解析系统](/concepts/04-module-resolution.md)
- [插件加载流程](/concepts/05-plugin-loader.md)
- [JupyterLab 插件基础结构](/concepts/02-plugin-basics.md)
- [Token 注入示例](/examples/02-token-injection.md)
