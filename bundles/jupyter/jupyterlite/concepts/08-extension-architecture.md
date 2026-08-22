---
type: Concept
title: 扩展架构
description: JupyterLite基于JupyterLab插件系统的扩展机制、Token/Provider依赖注入、内核扩展点与自定义内容Provider
tags: [extension, plugin, jupyterlab, token, lumino, kernel-factory, content-provider]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:28:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: app-source
    resource: /references/app-source.md
    title: 应用框架信源
  - id: kernel-source
    resource: /references/kernel-source.md
    title: 内核系统信源
---

## JupyterLab 插件系统

JupyterLite 完全复用 JupyterLab 的插件（Plugin）架构，基于 Lumino 的 `Application` 框架，使用 Token/Provider 模式实现依赖注入和模块化。

### Token/Provider 模式

JupyterLab 插件系统的核心概念：

- **Token**：唯一标识符（Symbol），代表一个可注入的服务接口。例如 `ICommandPaletteToken` 代表命令面板服务
- **Plugin**：提供或消费Token的模块单元
- **Provider**：提供（provides）Token实现的插件
- **Consumer**：依赖（requires/optional）Token的插件

插件通过声明 `requires`、`optional`、`provides` 来建立依赖关系，JupyterLab的插件加载器按照拓扑顺序激活插件。

### 插件定义格式

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const myPlugin: JupyterFrontEndPlugin<void> = {
  id: '@myorg/my-extension:plugin',
  autoStart: true,
  requires: [ICommandPalette],       // 必需依赖（不存在则报错）
  optional: [ILayoutRestorer],     // 可选依赖（不存在则传入undefined）
  provides: IMyService,            // 提供的Token（其他插件可依赖）
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    restorer?: ILayoutRestorer,
  ) => {
    // 插件激活逻辑
    const service = new MyService();
    app.commands.addCommand('my-command', {
      label: 'My Command',
      execute: () => { /* ... */ }
    });
    palette.addItem({ command: 'my-command', category: 'My Extension' });
    return service;  // provides对应返回服务实例
  }
};

export default myPlugin;
```

## @jupyterlite 核心扩展包

JupyterLite 内置以下核心扩展包：

| 包名 | 职责 |
|------|------|
| `@jupyterlite/application` | JupyterLite 应用基类（基于JupyterLab的JupyterFrontEnd） |
| `@jupyterlite/application-extension` | 默认应用扩展：内核管理、内容管理、会话管理等核心服务注册 |
| `@jupyterlite/services` | 核心服务实现（内核、内容、会话、设置、NBConvert） |
| `@jupyterlite/services-extension` | 将服务注册到JupyterLab的依赖注入容器 |
| `@jupyterlite/apputils` | 应用工具函数 |
| `@jupyterlite/apputils-extension` | 主题、命令、工具栏等工具扩展 |
| `@jupyterlite/notebook-application-extension` | Notebook应用专用扩展 |
| `@jupyterlite/repl-extension` | REPL控制台界面扩展 |
| `@jupyterlite/localforage` | LocalForage（IndexedDB）封装 |

## 内核扩展点

自定义内核是最常见的扩展场景。注册新内核需要：

1. 继承 `BaseKernel` 实现内核类
2. 在 Web Worker 中启动内核运行时
3. 通过插件注册到 `IKernelSpecs`

### BaseKernel 子类实现

```typescript
import { BaseKernel } from '@jupyterlite/services';

export class MyCustomKernel extends BaseKernel {
  async kernelInfoRequest() {
    return {
      protocol_version: '5.3',
      implementation: 'my-kernel',
      implementation_version: '1.0.0',
      language_info: {
        name: 'mylang',
        version: '1.0',
        mimetype: 'text/x-mylang',
        file_extension: '.my',
      },
      banner: 'My Custom Kernel',
      status: 'ok',
    };
  }

  async executeRequest(content: { code: string; ... }) {
    // 执行代码逻辑
    const result = this._executeCode(content.code);
    // 发布输出
    this.publishExecuteResult({
      execution_count: this.executionCount,
      data: { 'text/plain': result },
      metadata: {},
    });
    return { status: 'ok', execution_count: this.executionCount, ... };
  }

  // ... 实现其他抽象方法
}
```

### 内核注册插件

```typescript
import { IKernelSpecs } from '@jupyterlite/services';

const kernelPlugin: JupyterFrontEndPlugin<void> = {
  id: '@myorg/my-kernel-extension:kernel',
  autoStart: true,
  requires: [IKernelSpecs],
  activate: (app: JupyterFrontEnd, kernelspecs: IKernelSpecs) => {
    kernelspecs.register({
      spec: {
        name: 'mylang',
        display_name: 'My Language',
        language: 'mylang',
        argv: [],
        resources: { 'logo-64x64': 'path/to/logo.png' },
      },
      create: async (options: IKernel.IOptions): Promise<IKernel> => {
        // 创建Worker并桥接
        return new MyCustomKernel(options);
      }
    });
  }
};
```

`KernelSpecs.factories` 是 `Map<string, IKernelFactory>`，LiteKernelClient.startNew() 通过内核名称查找工厂创建实例。

## 内容 Provider 扩展

BrowserStorageDrive 支持 `ContentProviderRegistry`（实验性API），允许注册额外的内容提供者：

```typescript
// 注册自定义内容提供者
const contentPlugin: JupyterFrontEndPlugin<void> = {
  id: '@myorg/my-content-provider',
  autoStart: true,
  requires: [IBrowserStorageDrive],  // 或通过Token获取drive实例
  activate: (app, drive) => {
    drive.contentProviderRegistry.registerProvider({
      id: 'my-remote-provider',
      async get(path: string, options?: IFetchOptions): Promise<IModel> {
        // 从远程API获取文件
        const response = await fetch(`https://my-api.com/files/${path}`);
        return response.json();
      },
      async save(path: string, options: Partial<IModel>): Promise<IModel> {
        // 保存到远程
        const response = await fetch(`https://my-api.com/files/${path}`, {
          method: 'PUT',
          body: JSON.stringify(options),
        });
        return response.json();
      },
    });
  }
};
```

使用时通过 `contentProviderId` 选项路由：
```typescript
const model = await drive.get('remote-file.py', { content: true, contentProviderId: 'my-remote-provider' });
```

## 多应用架构

JupyterLite 在 `app/` 目录下构建多个前端应用，每个应用有独立的插件集合和入口：

| 应用 | 路径 | 界面特点 |
|------|------|----------|
| Lab | `app/lab/` | 完整JupyterLab：启动器、多标签面板、侧边栏、菜单 |
| Notebook | `app/notebooks/` | 经典Notebook界面（单文档模式） |
| REPL | `app/repl/` | 交互式控制台（单输入框+输出） |
| Consoles | `app/consoles/` | 代码控制台面板 |
| Edit | `app/edit/` | 文本编辑器 |
| Tree | `app/tree/` | 文件浏览器 |

所有应用共享核心服务（@jupyterlite/services），但加载不同的UI扩展来呈现不同界面。

### Rspack 构建

前端使用 [Rspack](https://rspack.dev/)（Rust实现的Webpack兼容构建工具）构建：
- 多入口配置：每个应用作为独立入口
- 代码分割：共享JupyterLab和Lumino依赖
- WASM处理：支持Pyodide/Xeus的WASM文件加载
- Public Path：支持部署到任意子路径（通过`publicpath.js`）

## 配置系统（jupyter-lite.json）

站点级配置通过 `jupyter-lite.json` 文件控制：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My JupyterLite",
    "appUrl": "/lab",
    "baseUrl": "/",
    "defaultKernelName": "python",
    "disabledExtensions": [
      "@jupyterlab/extensionmanager-extension"
    ],
    "federated_extensions": [],
    "settingsOverrides": {}
  }
}
```

构建时（Python端）也可通过 traitlets 配置 LiteManager，控制哪些 addon 启用、哪些插件禁用。

## 第三方扩展兼容性

| 扩展类型 | 兼容性 | 说明 |
|----------|--------|------|
| 纯UI扩展（主题、菜单、命令） | ✅ 兼容 | 不依赖后端API的扩展通常直接可用 |
| 渲染器扩展（plotly、viz等） | ✅ 兼容 | MIME渲染器扩展通常可用 |
| Widget扩展（ipywidgets） | ✅ 兼容 | 需要WASM端也有对应包 |
| 服务器API扩展（Git、Terminal） | ⚠️ 需要适配 | 需要Service Worker模拟或前端替代 |
| 文件系统扩展 | ⚠️ 需要适配 | 需要对接DriveFS/BrowserStorageDrive |

## 相关概念

- [内核系统](/concepts/02-kernel-system.md)
- [内核类型](/concepts/07-kernel-types.md)
- [内容管理与文件系统](/concepts/03-contents-and-filesystem.md)
- [Python构建系统](/concepts/06-build-system.md)
