---
type: Concept
title: 插件加载流程
description: PluginLoader 的完整加载流程：从转译代码到激活插件的七个步骤，包括默认导出回退、Token解析、Schema发现和样式声明发现。
tags: [jupyterlab, plugin-playground, loader, plugin-lifecycle, activation]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: loader-api
    resource: /references/loader-transpiler-api.md
    title: PluginLoader 与 PluginTranspiler API 参考
  - id: source-index
    resource: /references/source-index.md
    title: Plugin Playground 源码索引
---

## PluginLoader 概述

PluginLoader 是插件加载的核心协调者。它接收用户编写的源代码和文件路径，完成从代码转译到提取插件对象的全过程，最终返回可被 JupyterLab 激活的 IPlugin 数组及相关元数据。

```
用户代码 (string)
     ↓
[1] TypeScript 转译（或回退旧格式）
     ↓
[2] 创建沙箱执行环境
     ↓
[3] 执行代码（解析 import）
     ↓
[4] 提取插件对象
     ↓
[5] 解析 Token 依赖
     ↓
[6] 发现 JSON Schema
     ↓
[7] 发现声明的 CSS 样式
     ↓
PluginLoader.IResult { plugins, code, transpiled, schemas, declaredStylePaths }
```

## 步骤详解

### 步骤1：代码转译

PluginLoader.load() 首先调用 `transpiler.transpile(code, true)` 进行 TypeScript→CommonJS 转译。

**成功路径**：转译器处理代码，输出包含 `return exports` 的函数体。

**失败回退**：如果抛出 `NoDefaultExportError`（代码中没有 `export default`），则回退到旧格式：

```javascript
functionBody = `'use strict';\nreturn (${code})`;
transpiled = false;
```

其他错误直接抛出，不回退。

### 步骤2：创建沙箱执行环境

根据是否转译成功，创建不同的执行环境：

**转译成功（transpiled = true）**：

```typescript
const module = new AsyncFunction(
  'require',           // 参数名，对应 importFunctionName
  functionBody         // 转译后的代码
)(importFunction);      // 传入 ImportResolver.resolve 作为 require 函数
```

AsyncFunction 通过 `Object.getPrototypeOf(async () => {}).constructor` 获取，创建一个异步函数。函数体中所有 `await require(...)` 调用都会使用传入的 importFunction 解析模块。

**回退旧格式（transpiled = false）**：

```typescript
const pluginSource = new Function(
  'require', 'requirejs', 'define',
  functionBody
)(requirejs.require, requirejs.require, requirejs.define);
```

使用普通 Function 构造函数，在 RequireJS 环境中执行。传入三个参数：
- `require`：RequireJS 的 require 函数
- `requirejs`：同 require
- `define`：RequireJS 的 define 函数

### 步骤3：执行代码并提取插件源

**转译模式**：
- AsyncFunction 返回 `exports` 对象
- 插件源从 `module.default` 获取（因为 export default 会编译为 exports.default）

**回退模式**：
- Function 返回括号中表达式的值
- 该值直接作为插件源

执行失败时抛出 `PluginLoadingError`，包含原始错误和部分结果（已转译的code、空schemas、空declaredStylePaths、transpiled标志），可用于错误诊断对话框。

### 步骤4：解析插件对象

`_resolvePlugins(pluginSource)` 方法将插件源规范化为 IPlugin 数组：

```typescript
let plugin = pluginSource;

// 如果是函数，调用它（支持插件工厂函数）
if (typeof plugin === 'function') {
  plugin = plugin();
}

// await Promise（支持异步工厂）
const loaded = await Promise.resolve(plugin);

// 单个对象包装为数组，数组保持不变
return (Array.isArray(loaded) ? loaded : [loaded])
  .map(item => item as IPlugin<any, any>);
```

支持的插件源形式：

| 形式 | 示例 |
|------|------|
| 直接对象 | `{ id: 'test', activate: ... }` |
| 工厂函数 | `() => ({ id: 'test', activate: ... })` |
| 异步工厂 | `async () => ({ id: 'test', activate: ... })` |
| 插件数组 | `[plugin1, plugin2]` |
| Promise | `Promise.resolve(plugin)` |

### 步骤5：解析 Token 依赖

`_resolvePluginTokens(plugin)` 方法遍历插件的 `requires` 和 `optional` 数组，将字符串 Token 名解析为 Token 实例：

```typescript
plugin.requires = plugin.requires?.map(value => {
  if (typeof value !== 'string') return value;  // 已经是 Token 实例
  const token = this._options.tokenMap.get(value);
  if (!token) throw Error(`Required token ${value} not found`);
  return token;
});

plugin.optional = plugin.optional?.map(value => {
  if (typeof value !== 'string') return value;
  const token = this._options.tokenMap.get(value);
  if (!token) console.log(`Optional token ${value} not found`);
  return token;
}).filter(token => token != null);  // 过滤掉找不到的可选依赖
```

关键区别：
- **requires** 中找不到的 Token 抛出错误，插件加载失败
- **optional** 中找不到的 Token 仅打印警告并从数组中移除（传入 null）

在 Plugin Playground 中，你可以直接使用字符串形式的 Token 名（如 `'@jupyterlab/apputils:ICommandPalette'`），也可以从包中 import Token。PluginLoader 会统一处理。

### 步骤6：发现 JSON Schema

仅在 transpiled 模式下执行（`_discoverSchema`）。Schema 发现逻辑：

1. 如果没有 basePath 或 serviceManager，返回空
2. 查找 package.json：先查找插件同目录的 package.json，再查找上级目录的 package.json
3. 从 package.json 读取 `jupyterlab.schemaDir` 字段，定位 schema 目录
4. 列出 schema 目录中所有 `.json` 文件
5. 根据插件数量匹配 schema 文件：
   - **单插件**：查找 `plugin.json`，或只有一个json文件时直接使用
   - **多插件**：按插件 ID 的冒号后缀匹配文件名（如插件 ID `'my-ext:advanced'` 对应 `advanced.json`）
6. 如果没有 package.json 或 schemaDir，对于单插件尝试直接读取同目录的 `plugin.json`

Schema 内容读取后存入结果的 `schemas` 对象，键为插件 ID。

### 步骤7：发现声明的 CSS 样式

`_discoverDeclaredStyles(pluginPath)` 方法从 package.json 发现声明的 CSS：

1. 查找 package.json（同目录和上级目录）
2. 读取 `style` 字段
3. 验证 style 字段是字符串、非空、以 `.css` 结尾
4. 解析 style 路径为相对于 package.json 的绝对路径
5. 返回 CSS 文件路径数组

与schema发现不同，样式发现不依赖transpiled模式，始终执行。

## 加载结果

PluginLoader.load() 返回 `PluginLoader.IResult`：

```typescript
interface IResult {
  plugins: IPlugin<any, any>[];    // 可被JupyterLab激活的插件数组
  code: string;                    // 转译后的代码（用于错误调试）
  transpiled: boolean;             // 是否经过TypeScript转译
  schemas: Record<string, string>; // 发现的JSON schema（键为插件ID）
  declaredStylePaths: string[];    // 声明的CSS文件路径
}
```

## 错误处理

### PluginLoadingError

加载失败时抛出的错误类型：

```typescript
class PluginLoadingError extends Error {
  constructor(
    public error: Error,
    public partialResult: Omit<PluginLoader.IResult, 'plugins'>
  );
}
```

`partialResult` 包含已完成的部分工作（转译后的code、空schemas、空declaredStylePaths、transpiled标志），可用于在错误对话框中显示转译后的代码帮助调试。

### Token 解析错误

必需 Token 找不到时抛出 Error，消息格式：`'Required token{name}not found in the token map'`。注意消息中缺少空格（源码中直接拼接字符串），这是源码中的实际行为。

## loadFile() 方法

除了 `load()` 方法外，PluginLoader 还提供 `loadFile(code: string): Promise<IModule>` 方法。它用于加载非插件的模块文件（如相对导入的 .ts/.js 文件）：

- 使用 `transpiler.transpile(code, false)`，不要求 default export
- 始终通过 AsyncFunction 执行
- 返回模块的 exports 对象
- 不进行插件解析、Token解析、Schema发现、样式发现

这个方法被 ImportResolver 用作 `dynamicLoader`，处理本地文件相对导入。

## 相关概念

- [TypeScript 转译机制](03-typescript-transpilation.md)
- [模块解析系统](04-module-resolution.md)
- [Token 依赖注入系统](06-token-system.md)
- [JupyterLab 插件基础结构](02-plugin-basics.md)
- [PluginLoader API 参考](../references/loader-transpiler-api.md)
