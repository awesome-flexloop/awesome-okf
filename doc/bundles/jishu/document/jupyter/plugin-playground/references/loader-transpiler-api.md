---
type: Reference
title: PluginLoader 与 PluginTranspiler API 参考
description: PluginLoader 和 PluginTranspiler 类的完整API签名、构造参数、返回值类型与错误处理。
tags: [jupyterlab, plugin-playground, loader, transpiler, api]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: loader-source
    resource: /references/loader-transpiler-api.md
    title: PluginLoader & PluginTranspiler API
---

## PluginLoader

PluginLoader 负责将用户编写的插件代码（TypeScript/JavaScript）转译、执行并提取 JupyterLab 插件对象。

### 构造函数

```typescript
new PluginLoader(options: PluginLoader.IOptions)
```

**PluginLoader.IOptions**

| 属性 | 类型 | 说明 |
|------|------|------|
| `transpiler` | `PluginTranspiler` | TypeScript转译器实例 |
| `importFunction` | `(statement: string) => Promise<Token<any> \| IModule \| IModuleMember>` | 模块导入函数，通常传入 ImportResolver.resolve |
| `tokenMap` | `Map<string, Token<any>>` | Token名称到Token实例的映射表 |
| `requirejs` | `IRequireJS` | 隔离iframe中的RequireJS实例，用于旧风格插件兼容 |
| `serviceManager` | `ServiceManager.IManager \| null` | Jupyter服务管理器，用于文件系统访问和schema发现 |

### 公开方法

#### load()

```typescript
async load(
  code: string,
  basePath: string | null
): Promise<PluginLoader.IResult>
```

加载并执行插件代码。

**参数：**
- `code` - 插件源代码字符串（TypeScript或JavaScript）
- `basePath` - 插件文件路径，用于解析相对导入和发现schema/样式；为null时禁用本地文件解析

**返回：** `PluginLoader.IResult`

| 属性 | 类型 | 说明 |
|------|------|------|
| `plugins` | `IPlugin<any, any>[]` | 解析出的JupyterLab插件数组 |
| `code` | `string` | 转译后的代码（或原始代码的函数包装） |
| `transpiled` | `boolean` | 是否经过TypeScript转译 |
| `schemas` | `Record<string, string>` | 发现的JSON schema，键为插件ID |
| `declaredStylePaths` | `string[]` | package.json中声明的CSS文件路径 |

**行为：**
1. 首先尝试 `transpiler.transpile(code, true)` 进行ES module模式转译
2. 若抛出 `NoDefaultExportError`，回退到对象风格：`'use strict';\nreturn (${code})`
3. transpiled模式下通过 `AsyncFunction` 执行，从 `module.default` 获取插件源
4. 非transpiled模式下通过 `new Function('require','requirejs','define', body)` 在RequireJS环境中执行
5. 解析插件数组，将字符串Token名解析为Token实例
6. 自动发现JSON schema文件和声明的CSS样式

**抛出：** `PluginLoadingError` - 包含原始错误和部分结果

#### loadFile()

```typescript
async loadFile(code: string): Promise<IModule>
```

加载任意模块文件（非插件），使用 `transpiler.transpile(code, false)` 转译（不要求default export）。

### PluginLoader.IResult

```typescript
interface IResult {
  plugins: IPlugin<any, any>[];
  code: string;
  transpiled: boolean;
  schemas: Record<string, string>;
  declaredStylePaths: string[];
}
```

### PluginLoadingError

```typescript
class PluginLoadingError extends Error {
  constructor(
    public error: Error,
    public partialResult: Omit<PluginLoader.IResult, 'plugins'>
  );
}
```

加载失败时抛出的错误，包含原始错误对象和部分加载结果（code、schemas、declaredStylePaths、transpiled），可用于错误诊断。

---

## PluginTranspiler

PluginTranspiler 使用 TypeScript Compiler API 在浏览器中将 TypeScript/ES6+ 代码转译为可在 AsyncFunction 中执行的 CommonJS 代码。

### 构造函数

```typescript
new PluginTranspiler(options: PluginTranspiler.IOptions)
```

**PluginTranspiler.IOptions**

| 属性 | 类型 | 说明 |
|------|------|------|
| `compilerOptions` | `ts.CompilerOptions & { target: ts.ScriptTarget }` | TypeScript编译选项 |

**注意：** 构造函数会检查 `options.compilerOptions.module` 是否已设置，若已设置则抛出错误——module选项是转译器的内部实现细节，强制使用 `ts.ModuleKind.CommonJS`。

### 公开属性

```typescript
readonly importFunctionName = 'require';
```

异步函数中用于导入模块的参数名，在转译输出中对应AsyncFunction的第一个参数。

### 公开方法

#### transpile()

```typescript
transpile(
  code: string,
  requireDefaultExport: boolean,
  fileName?: string
): string
```

转译TypeScript/JavaScript代码。

**参数：**
- `code` - 源代码字符串
- `requireDefaultExport` - 是否要求存在 `export default`；true时若找不到default export抛出 `NoDefaultExportError`
- `fileName` - 可选文件名，用于Source Map

**转译管道（Transformers）：**

**before 转换器（仅 requireDefaultExport=true 时）：**
- `_requireDefaultExportTransformer()` - 遍历AST查找 `export default` 语句，记录defaultExport表达式；未找到时抛出 `NoDefaultExportError`

**after 转换器（始终执行）：**
- `_awaitRequireTransformer()` - 将所有 `require(...)` 调用包装为 `await require(...)`，使模块导入异步化
- `_exportWrapperTransformer()` - 创建 `exports = {}` 对象，在所有语句后添加 `return exports`；将 `'use strict'` 置顶

**转译输出示例：**

输入（TypeScript）：
```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'hello:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => { console.log('hello'); }
};

export default plugin;
```

输出（CommonJS + async wrapper）：
```javascript
'use strict';
const exports = {};
const { JupyterFrontEnd, JupyterFrontEndPlugin } = await require("@jupyterlab/application");
const plugin = {
  id: 'hello:plugin',
  autoStart: true,
  activate: (app) => { console.log('hello'); }
};
exports.default = plugin;
return exports;
```

---

## NoDefaultExportError

```typescript
class NoDefaultExportError extends Error
```

当 `transpile()` 的 `requireDefaultExport` 参数为 true 但代码中未找到 `export default` 语句时抛出。PluginLoader 捕获此错误并自动回退到旧风格插件加载。

## 相关概念

- [整体架构与数据流](../concepts/01-architecture-overview.md)
- [TypeScript 转译机制](../concepts/03-typescript-transpilation.md)
- [插件加载流程](../concepts/05-plugin-loader.md)
- [模块解析系统](../concepts/04-module-resolution.md)
