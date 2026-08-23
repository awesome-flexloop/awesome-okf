---
type: Concept
title: 联邦扩展与共享模块
description: Plugin Playground 如何通过 Webpack Module Federation 共享作用域和 window._JUPYTERLAB 容器动态发现并加载已安装的 JupyterLab 扩展。
tags: [jupyterlab, plugin-playground, federated-extensions, module-federation, shared-scope, webpack]
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
  - id: resolver-api
    resource: /references/resolver-api.md
    title: ImportResolver API 参考
---

## 联邦扩展（Federated Extensions）概述

JupyterLab 4.x 使用 Webpack Module Federation（或 Rspack 的兼容实现）构建扩展系统。每个预构建的扩展（federated extension）作为独立的容器注册到全局作用域，运行时可以动态加载其他扩展暴露的模块而无需重新构建。

Plugin Playground 充分利用了这一机制，允许你在 Playground 插件中 import 已安装的其他 JupyterLab 扩展提供的 Token 和模块。

## 模块发现机制

### 已知模块注册

Plugin Playground 启动时，`registerCoreKnownModules()` 为约80个核心 JupyterLab/Lumino 包注册已知模块：

- **@jupyterlab/\*** 包：自动生成 JupyterLab ReadTheDocs 文档链接、npm 链接、GitHub 源码链接
- **@lumino/\*** 包：自动生成 Lumino ReadTheDocs 文档链接
- **其他已知包**：react, react-dom, yjs, @codemirror/\* 等

注册的元数据包括：
- 包名（name）
- 加载函数（load，默认为动态 import）
- URL集合（文档页、npm页、GitHub仓库、package.json地址）
- 描述文本
- 来源标记（origin: 'jupyterlab-core'/'lumino-core'/'core-known-module'）

### 联邦扩展自动发现

`discoverFederatedKnownModules()` 在应用恢复后自动发现当前环境中已安装的联邦扩展：

1. 从 `PageConfig.getOption('federated_extensions')` 获取扩展列表
2. 对每个扩展，从 labextensions URL 目录 fetch 其 `package.json`
3. 解析 package.json 中的 name、description、homepage、repository
4. 注册扩展包和其 `jupyterlab.sharedPackages` 中声明的共享包
5. 生成对应的文档、npm、仓库链接

URL 候选来自 PageConfig 中的 `fullLabextensionsUrl` 和 `labextensionsUrl`。

### 动态发现的时机

联邦扩展发现发生在 `app.restored` 之后，且是幂等的（`_federatedDiscoveryComplete` 标志防止重复发现）。可以通过传入 `{force: true}` 参数强制重新发现。

## 从共享作用域加载模块

### Webpack Shared Scope

Webpack/Rspack 的 Module Federation 允许不同 bundle 共享依赖。共享模块通过全局变量暴露：

- `__webpack_require__.S`（或 `__webpack_require__.I` 用于初始化）
- `__webpack_share_scopes__`
- `window.__webpack_share_scopes__`

`loadSharedScopeModule()` 函数从这些共享作用域加载模块：

1. 调用 `__webpack_require__.I('default')` 初始化默认共享作用域
2. 从三个来源收集作用域（合并去重）
3. 按包名查找所有可用版本的提供者（providers）
4. 使用 semver 的 `maxSatisfying` 选择满足版本范围的最高版本
5. 优先选择稳定版，无稳定版时使用预发布版
6. 调用 provider.get() 获取模块工厂或模块对象
7. 如果返回函数则调用，否则直接使用

### 版本范围协商

ImportResolver 在解析运行时模块时，会从最近的 `package.json` 中读取依赖版本范围：

1. 从 basePath 向上遍历目录树
2. 查找 `package.json` 并解析其 `dependencies` 和 `peerDependencies`
3. 提取目标包的版本范围字符串
4. 传递给 `loadSharedScopeModule` 进行 semver 匹配

支持的版本格式：
- 标准 semver: `^4.5.0`, `~4.5.0`, `>=4.0.0`, `*`
- workspace协议: `workspace:^1.0.0`, `workspace:*`
- npm协议: `npm:package@^1.0.0`（提取@后的版本）

不支持的格式（不做版本约束，使用可用最高版本）：
- `file:`, `link:`, `github:`, `git+`, `git:` 等本地/远程协议

如果指定了版本范围但没有满足的版本，抛出错误：`No shared version of {name} satisfies required range "{range}".`

### 包名解析

`_packageNameForImportSpecifier()` 从 import 路径中提取包名：

```
'@jupyterlab/apputils' → '@jupyterlab/apputils'
'@jupyterlab/apputils/lib/someModule' → '@jupyterlab/apputils'
'react' → 'react'
'./local-file' → null (本地文件，不经过共享作用域)
'https://cdn.example.com/mod' → null (URL，不经过共享作用域)
```

如果直接以模块名（包名+子路径）查找共享模块失败，会回退到只使用包名查找。

## 从 window._JUPYTERLAB 容器加载

联邦扩展在加载时会将自己注册到 `window._JUPYTERLAB[packageName]` 容器。ImportResolver 通过 `_resolveFederatedExtensionModule()` 直接访问这些容器：

```typescript
const container = window._JUPYTERLAB?.[module];
if (!container || typeof container.get !== 'function') {
  return null;  // 不是联邦扩展
}

// 加载扩展的入口模块
const exposed = await container.get('./extension');
const factory = typeof exposed === 'function' ? exposed : () => exposed;
const resolved = factory();
return resolved;
```

关键点：
- 容器必须暴露 `get(key: string)` 方法
- 使用固定的 key `'./extension'` 获取扩展入口
- 返回值可能是模块对象或模块工厂函数，需要调用工厂函数
- 加载失败时抛出包含错误信息的异常
- 相对路径导入（以 `.` 开头）不会走联邦扩展路径

## 已知模块注册表（KNOWN_MODULES Map）

所有已知模块（核心包+发现的联邦扩展）存储在模块级别的 `KNOWN_MODULES` Map中。提供以下API：

### registerKnownModule(known)

注册单个模块，如果已存在则合并URL和描述信息（新信息优先，补充旧信息）。

### registerKnownModules(knownModules)

批量注册模块。

### listKnownModules()

返回按名称排序的所有已知模块数组，供TokenSidebar展示。

### IKnownModule 接口

```typescript
interface IKnownModule {
  name: string;
  load?: () => Promise<unknown>;
  urls?: {
    docHtml?: string;       // API文档URL
    sourceHtml?: string;    // 源码URL
    typeDocJson?: string;   // TypeDoc JSON URL
    npmHtml?: string;       // npm包页面URL
    packageJson?: string;   // package.json URL
    homepageHtml?: string;  // 首页URL
    repositoryHtml?: string; // 仓库URL
  };
  description?: string;
  origin?: string;         // 来源标记
}
```

URL 转换工具 `_gitUrlToHttp()` 支持多种 Git URL 格式：
- `github:user/repo` → `https://github.com/user/repo`
- `git@github.com:user/repo.git` → `https://github.com/user/repo`
- `ssh://git@github.com/user/repo` → `https://github.com/user/repo`
- `git+https://...`、`git:https://...`、`ssh://...` → 去除前缀转换为HTTPS
- 去除尾部 `.git`

## 使用其他扩展的 Token

在 Plugin Playground 中，你可以直接 import 已安装的联邦扩展的 Token。例如，如果安装了 `@jupyterlab/celltags` 扩展：

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICellTags } from '@jupyterlab/celltags'; // 如果该扩展导出此Token

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-ext:use-celltags',
  autoStart: true,
  requires: ['@jupyterlab/celltags:ICellTags'],  // 也可用字符串
  activate: (app, cellTags) => {
    console.log('CellTags available:', cellTags);
  }
};

export default plugin;
```

如果扩展没有提供 Token 或模块未找到，PluginLoader 会在 requires 中抛出错误，在 optional 中返回 null。

## 相关概念

- [模块解析系统](/concepts/04-module-resolution.md)
- [Token 依赖注入系统](/concepts/06-token-system.md)
- [整体架构与数据流](/concepts/01-architecture-overview.md)
- [ImportResolver API 参考](/references/resolver-api.md)
