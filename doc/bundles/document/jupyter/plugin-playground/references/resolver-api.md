---
type: Reference
title: ImportResolver API 参考
description: ImportResolver 类的完整API签名、模块解析策略链、CDN策略、CSS样式管理与版本协商。
tags: [jupyterlab, plugin-playground, resolver, modules, cdn, api]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: resolver-source
    resource: /references/resolver-api.md
    title: ImportResolver API Reference
---

## ImportResolver

ImportResolver 负责解析插件代码中的 `import` 语句，将模块说明符（specifier）解析为实际的模块对象或 Token。实现了四级回退解析策略链和CSS样式的事务管理。

### 构造函数

```typescript
new ImportResolver(options: ImportResolver.IOptions)
```

**ImportResolver.IOptions**

| 属性 | 类型 | 说明 |
|------|------|------|
| `loadKnownModule` | `(name: string) => Promise<IModule \| null>` | 已知模块加载函数，通常传入 modules.ts 的 loadKnownModule |
| `tokenMap` | `Map<string, Token<any>>` | Token名称到Token实例的映射 |
| `requirejs` | `IRequireJS` | 隔离iframe中的RequireJS实例 |
| `settings` | `ISettingRegistry.ISettings` | JupyterLab设置，用于读取CDN策略配置 |
| `serviceManager` | `ServiceManager.IManager \| null` | Jupyter服务管理器，用于本地文件解析 |
| `dynamicLoader` | `(transpiledCode: string) => Promise<IModule>` | 可选，本地.ts/.tsx/.js文件动态转译加载器 |
| `basePath` | `string \| null` | 当前模块路径，用于解析相对导入 |

### 公开属性

```typescript
loadedLocalStylePaths: ReadonlySet<string>
```

返回当前 resolver 实例已加载的本地CSS文件路径集合（只读）。

### 公开方法

#### resolve()

```typescript
async resolve(
  module: string
): Promise<Token<any> | IModule | IModuleMember>
```

解析模块说明符，返回模块对象、Token实例或模块成员。

**模块解析策略链（按优先级）：**

1. **Runtime Known Module** - 通过 `loadKnownModule` 加载内置已知模块（如 `@jupyterlab/application`），失败后尝试从 webpack shared scope 加载
2. **Federated Extension Module** - 通过 `window._JUPYTERLAB[module].get('./extension')` 加载已安装的联邦扩展
3. **Local File** - 解析以 `.` 开头的相对路径，支持 `.ts`/`.tsx`/`.js`/`.css`/`.svg` 文件及 `index.*` 文件
4. **CDN AMD Module** - 经用户同意后通过 RequireJS 从CDN加载AMD模块

**特殊处理：**
- CSS文件：注入 `<style>` 标签，返回 `{ default: path }`
- SVG文件：返回 `{ __esModule: true, default: content }`
- 默认导入合成：当模块无 `default` 导出时，`import mod from 'pkg'` 返回模块本身
- Token感知：通过Proxy拦截属性访问，`import { TokenName } from 'package'` 优先从tokenMap查找

**抛出：**
- Error - CDN未授权、模块无法解析、本地文件解析失败等

#### rollbackLocalStyleMutations()

```typescript
rollbackLocalStyleMutations(): void
```

回滚本次 resolver 实例加载的所有CSS样式变更到加载前状态。用于插件卸载或加载失败时清理样式。

#### commitLocalStyleMutations()

```typescript
commitLocalStyleMutations(): void
```

提交本次 resolver 实例加载的CSS样式变更，确认样式持久化。用于插件成功加载后确认样式保留。

#### dynamicLoader setter

```typescript
set dynamicLoader(loader: (transpiledCode: string) => Promise<IModule>)
```

设置动态加载器，用于本地 TypeScript/JavaScript 文件的实时转译执行。通常设置为 `PluginLoader.loadFile`。

### 静态方法

```typescript
static removeLocalStyles(paths: Iterable<string>): void
```

移除指定路径的本地样式元素。

---

## CDN 策略

CDN加载受用户设置控制，有三种策略状态：

| 策略 | 行为 |
|------|------|
| `awaiting-decision` | 默认状态，首次加载CDN模块时弹出对话框让用户选择 |
| `always-insecure` | 用户选择"Allow"后，始终允许CDN加载 |
| `never` | 用户选择"Forbid"后，禁止所有CDN加载 |
| `abort-to-investigate` | 用户选择"Abort"，中止当前加载操作 |

设置项存储在 `settings.composite.allowCDN` 中。CDN URL从 `settings.composite.requirejsCDN` 读取。

---

## CSS 样式事务管理

ImportResolver 实现了基于快照栈的CSS样式事务机制：

### 快照机制

- 每个 resolver 实例有唯一的 `_localCssSnapshotId`（自增整数）
- 加载CSS时通过 `_snapshotLocalStyle(path)` 保存加载前的CSS内容到栈中
- 多个插件加载同一CSS文件时，快照栈记录每层版本
- 静态Map `_localCssStyles` 存储路径→style元素映射
- 静态Map `_localCssSnapshotStacks` 存储路径→快照栈

### 回滚（Rollback）

- 回滚时从栈中移除当前快照
- 如果当前快照在栈顶，直接恢复之前的CSS内容
- 如果不在栈顶，将旧CSS传递给栈顶的上一条快照
- 空栈时删除style元素

### 提交（Commit）

- 提交时从栈中移除当前快照但不恢复CSS
- 更新前一条快照的previousCss为当前CSS值（传播当前状态）

### CSS @import 重写

`_rewriteRelativeCssImports()` 将CSS中相对路径的 `@import` 重写为 Jupyter files/ URL：

```
基础URL: {baseUrl}files/
@import './foo.css' → @import '{baseUrl}files/{path/to}/foo.css'
```

仅重写相对路径的import，绝对URL、协议URL、`#`开头的import保持不变。

---

## 本地文件解析

### 路径候选生成

`_localImportCandidates(basePath, module)` 为相对导入生成以下候选路径：

- 有扩展名时：直接使用原路径
- 无扩展名时：尝试 `.ts`, `.tsx`, `.js`, `.css`, `index.ts`, `index.tsx`, `index.js`, `index.css`

### 版本范围协商

解析运行时模块时，ImportResolver会向上遍历目录查找最近的 `package.json`，从 `dependencies` 和 `peerDependencies` 中提取版本范围，传递给 `loadSharedScopeModule` 进行 semver 匹配。

支持的版本范围格式：
- 标准 semver range: `^4.0.0`, `~4.5.0`, `>=4.0.0`
- workspace协议: `workspace:*`, `workspace:^1.0.0`
- npm协议: `npm:package@^1.0.0`

不支持的格式（返回null，不做版本约束）：
- `file:`, `link:`, `github:`, `git+`, `git:` 协议

---

## 联邦扩展解析

联邦扩展模块通过 `window._JUPYTERLAB` 全局对象访问：

```typescript
window._JUPYTERLAB[moduleName]?.get('./extension')
```

- 容器必须暴露 `get(key: string)` 方法
- 加载 `./extension` 键获取模块工厂或模块对象
- 工厂函数需要调用以获取实际模块
- 模块必须返回对象或函数类型

---

## Webpack 共享作用域加载

通过 `loadSharedScopeModule` 从 webpack/rspack 的 Module Federation 共享作用域加载模块：

- 初始化默认共享作用域：`__webpack_require__.I('default')`
- 从三个来源收集共享作用域：`__webpack_require__.S.default`、`__webpack_share_scopes__.default`、`window.__webpack_share_scopes__.default`
- 使用 semver `maxSatisfying` 选择满足版本范围的最高版本
- 优先选择稳定版，无稳定版时使用预发布版
- 版本不满足时抛出明确错误

## 相关概念

- [模块解析系统](/concepts/04-module-resolution.md)
- [联邦扩展与共享模块](/concepts/07-federated-extensions.md)
- [样式处理与CSS隔离](/concepts/08-style-handling.md)
- [插件加载流程](/concepts/05-plugin-loader.md)
