---
type: Concept
title: 模块解析系统
description: ImportResolver 的四级回退解析策略链：运行时已知模块、联邦扩展、本地文件、CDN AMD 模块，以及CSS样式管理和版本协商机制。
tags: [jupyterlab, plugin-playground, module-resolution, import, resolver, cdn]
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
  - id: source-index
    resource: /references/source-index.md
    title: Plugin Playground 源码索引
---

## 模块解析概述

当插件代码中的 `import` 语句被转译为 `await require('...')` 后，实际的模块查找和加载由 `ImportResolver` 类完成。ImportResolver 实现了一个**四级回退解析策略链**，按优先级依次尝试每种解析方式，直到找到模块或全部失败。

```
import { X } from 'some-module'
         ↓
await require('some-module')
         ↓
┌─────────────────────────────────┐
│ 1. Runtime Known Module         │ ← 内置JupyterLab/Lumino包
│    loadKnownModule()            │
│    loadSharedScopeModule()      │ ← Webpack共享作用域
├─────────────────────────────────┤
│ 2. Federated Extension Module   │ ← 已安装的其他扩展
│    window._JUPYTERLAB[name]     │
├─────────────────────────────────┤
│ 3. Local File                   │ ← 相对路径导入
│    .ts/.tsx/.js/.css/.svg       │
│    index.* files                │
├─────────────────────────────────┤
│ 4. CDN AMD Module               │ ← 需用户同意
│    require.js via iframe        │
└─────────────────────────────────┘
         ↓
  模块对象 / Token / 抛出错误
```

## 第一级：运行时已知模块（Runtime Known Module）

这是最高优先级的解析方式，处理 JupyterLab 核心包和已加载的共享模块。

### 硬编码已知模块

`modules.ts` 中的 `loadKnownModule()` 函数包含约80个已知包名的 `import()` 映射。这些包包括：

- **@jupyterlab/\***：application, apputils, codemirror, completer, notebook, services, settingregistry, docmanager, filebrowser, launcher, mainmenu, terminal 等
- **@lumino/\***：algorithm, application, commands, coreutils, disposable, messaging, signaling, widgets, virtualdom 等
- **第三方**：react, react-dom, yjs, @codemirror/state, @codemirror/view, @codemirror/language, @lezer/common, @rjsf/utils 等

当 import 的包名匹配这些已知模块时，直接通过动态 `import()` 加载。

### Webpack 共享作用域

如果硬编码列表中没有找到，ImportResolver 会尝试从 Webpack/Rspack 的 Module Federation 共享作用域加载：

1. 从 import 路径解析包名（处理 @scope/name 格式）
2. 向上遍历目录查找最近的 `package.json`，从 `dependencies`/`peerDependencies` 提取版本范围
3. 调用 `loadSharedScopeModule()` 从共享作用域中选择满足 semver 范围的版本
4. 优先选择稳定版，无稳定版时使用预发布版

共享作用域从三个来源收集：
- `__webpack_require__.S?.default`（Webpack 运行时）
- `__webpack_share_scopes__?.default`
- `window.__webpack_share_scopes__?.default`

支持的版本范围格式：标准 semver range（`^4.0.0`）、workspace 协议、npm 协议。不支持 file:/link:/github: 等本地协议。

## 第二级：联邦扩展模块（Federated Extension Module）

如果运行时模块解析失败，ImportResolver 尝试从 JupyterLab 的联邦扩展系统加载模块。

JupyterLab 4.x 使用 Module Federation 构建，已安装的扩展会注册到 `window._JUPYTERLAB` 全局对象：

```typescript
const container = window._JUPYTERLAB?.[moduleName];
if (container && typeof container.get === 'function') {
  const exposed = await container.get('./extension');
  const factory = typeof exposed === 'function' ? exposed : () => exposed;
  const resolved = factory();
  return resolved as IModule;
}
```

联邦扩展模块的特点：
- 模块名通常是扩展包名（如 `@jupyterlab/celltags`）
- 通过 `get('./extension')` 获取模块工厂或模块对象
- 如果返回函数则调用以获取实际模块
- 必须返回对象或函数类型

联邦扩展的元数据（描述、仓库URL、npm链接等）通过 `discoverFederatedKnownModules()` 在启动时从 `PageConfig` 的 `federated_extensions` 配置中发现，并注册到已知模块列表中。

## 第三级：本地文件（Local File）

仅当 import 路径以 `.` 开头（相对路径）时触发本地文件解析。

### 路径候选

给定基础路径和导入路径，ImportResolver 生成文件候选：

```typescript
// 有扩展名：直接使用
import './foo' → base/foo.ts, base/foo.tsx, base/foo.js, base/foo.css,
                 base/foo/index.ts, base/foo/index.tsx, base/foo/index.js, base/foo/index.css
```

### 文件类型处理

不同文件类型有不同的处理方式：

| 扩展名 | 处理方式 |
|--------|---------|
| `.ts`/`.tsx`/`.js` | 通过 dynamicLoader（即 PluginLoader.loadFile）实时转译执行，返回模块对象 |
| `.css` | 注入 `<style>` 标签到 `<head>`，返回 `{ default: path }` |
| `.svg` | 读取文件内容为字符串，返回 `{ __esModule: true, default: content }` |

### CSS 文件处理

本地 CSS 文件通过 `_loadLocalStyle()` 处理：

1. 保存当前样式快照（用于回滚）
2. 重写 CSS 中相对路径的 `@import` 为 Jupyter files/ URL
3. 创建或复用 `<style>` 元素，设置其 textContent
4. 记录已加载样式路径

CSS `@import` 重写规则：
- 仅重写相对路径的 import（不以 `/`、`//`、`#`、协议开头）
- 将相对路径解析为相对于当前CSS文件的绝对路径
- 转换为 `{baseUrl}files/{absolutePath}` 格式的URL

### 版本范围发现

解析本地文件的依赖时，ImportResolver 从当前文件路径向上遍历目录查找 `package.json`，从其中的 `dependencies` 和 `peerDependencies` 字段提取依赖版本范围，用于共享模块的 semver 匹配。

## 第四级：CDN AMD 模块（RequireJS）

当以上三级全部失败后，ImportResolver 会尝试通过 RequireJS 从 CDN 加载 AMD 格式的模块。

### CDN 安全策略

CDN 加载受用户设置控制，默认状态为 `'awaiting-decision'`：

1. 首次需要从CDN加载模块时，弹出对话框让用户选择
2. **Forbid**：设置 `allowCDN = 'never'`，禁止所有CDN加载
3. **Allow**：设置 `allowCDN = 'always-insecure'`，始终允许CDN加载
4. **Abort**：中止当前加载操作

CDN URL 从 `settings.composite.requirejsCDN` 配置获取。

### RequireJS 隔离

RequireJS 不在主 window 中加载，而是在隐藏 iframe 中隔离运行。这避免了 RequireJS 定义全局 `define`/`require` 与 JupyterLab 的模块系统冲突。

iframe 创建后不能从 DOM 移除，否则 RequireJS 的内部定时器无法执行。

## Token 感知的模块代理（Proxy）

无论通过哪一级解析成功获取到模块对象，ImportResolver 都会通过 `_createTokenAwareModule()` 用 ES6 Proxy 包装它：

```typescript
return new Proxy(targetModule, {
  get: (target, prop, receiver) => {
    if (typeof prop !== 'string') {
      return Reflect.get(target, prop, receiver);
    }
    // 优先从 tokenMap 查找 Token
    const tokenName = `${module}:${prop}`;
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

这个 Proxy 实现了两个关键功能：

1. **Token 映射**：当代码写 `import { INotebookTracker } from '@jupyterlab/notebook'` 时，`INotebookTracker` 不是从模块对象中获取的，而是从 tokenMap 中按 `@jupyterlab/notebook:INotebookTracker` 键查找对应的 Token 实例返回。

2. **默认导入合成**：当模块没有 `default` 导出但代码使用 `import mod from 'pkg'` 时，返回模块本身作为 default，兼容 CommonJS 模块的默认导入。

## CSS 样式事务

ImportResolver 实现了CSS样式的事务管理，支持回滚和提交：

### 快照机制

每个 ImportResolver 实例有唯一ID。加载CSS时：

1. 保存当前 style 元素的 textContent 作为快照
2. 将快照推入路径对应的快照栈
3. 更新 style 元素内容为新CSS

### 回滚（Rollback）

插件加载失败或停用时调用 `rollbackLocalStyleMutations()`：

- 如果当前快照在栈顶，直接恢复之前的CSS
- 如果不在栈顶（后续插件覆盖了同一路径），将旧CSS传递给上一层
- 空栈时移除 style 元素
- 清空当前实例的快照记录

### 提交（Commit）

插件成功加载后调用 `commitLocalStyleMutations()`：

- 从栈中移除当前快照但不恢复CSS
- 将当前CSS状态传播给栈中的前一条快照
- 多个插件加载同一CSS时形成版本链

## 错误处理

模块解析失败时，ImportResolver 调用 `handleImportError()` 显示错误对话框，包含错误堆栈和模块名。错误对话框由 `formatImportError()` React 组件渲染。

## 相关概念

- [整体架构与数据流](/concepts/01-architecture-overview.md)
- [插件加载流程](/concepts/05-plugin-loader.md)
- [Token 依赖注入系统](/concepts/06-token-system.md)
- [联邦扩展与共享模块](/concepts/07-federated-extensions.md)
- [样式处理与CSS隔离](/concepts/08-style-handling.md)
- [ImportResolver API 参考](/references/resolver-api.md)
