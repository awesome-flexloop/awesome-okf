---
type: Concept
title: 浏览器端 TypeScript 转译机制
description: 深入理解 PluginTranspiler 如何在浏览器中使用 TypeScript Compiler API 实时转译代码，以及三个自定义 Transformer 的工作原理。
tags: [jupyterlab, plugin-playground, typescript, transpiler, compiler, transformer]
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
---

## 为什么需要浏览器端转译

传统的 JupyterLab 插件开发依赖 Node.js 构建链：TypeScript 源码 → tsc 编译 → webpack 打包 → 安装到 JupyterLab → 重启。Plugin Playground 的核心创新在于将 TypeScript 转译放到浏览器中实时完成，使得代码修改后无需构建步骤即可运行。

这一能力由 `PluginTranspiler` 类提供，它使用 TypeScript 官方 Compiler API（`ts.transpileModule`）在浏览器中执行代码转换。

## PluginTranspiler 的构造

### 编译器选项

创建 PluginTranspiler 实例时需要传入编译器选项：

```typescript
import ts from 'typescript';
import { PluginTranspiler } from './transpiler';

const transpiler = new PluginTranspiler({
  compilerOptions: {
    target: ts.ScriptTarget.ES2018,
    // 不要设置 module —— module 是转译器的内部实现细节
    // 其他选项如 strict, jsx 等可以按需设置
  }
});
```

**重要**：`module` 选项由转译器内部强制设置为 `ts.ModuleKind.CommonJS`。如果你在 `compilerOptions` 中设置了 `module`，构造函数会抛出错误：`"The module setting is an implementation detail of transpiler."`

### importFunctionName

PluginTranspiler 有一个只读属性：

```typescript
readonly importFunctionName = 'require';
```

这是 AsyncFunction 中用于导入模块的参数名。转译后的代码中所有 `import` 语句会被转换为 `const ... = await require(...)` 调用。

## transpile() 方法

```typescript
transpile(
  code: string,
  requireDefaultExport: boolean,
  fileName?: string
): string
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `code` | `string` | TypeScript/JavaScript 源代码 |
| `requireDefaultExport` | `boolean` | 是否要求存在 `export default` |
| `fileName` | `string` | 可选文件名，用于 Source Map |

**行为差异：**

- `requireDefaultExport: true`（插件加载）：启用 default export 检测转换器，找不到 default export 时抛出 `NoDefaultExportError`
- `requireDefaultExport: false`（文件加载）：不检测 default export，仅做 CommonJS 转换和 await 包装

## 三个自定义 Transformer

PluginTranspiler 使用 TypeScript Transformer API 在转译过程中插入自定义转换。这些转换器在 `ts.transpileModule` 的 `transformers` 选项中注册。

### Transformer 1: _requireDefaultExportTransformer（before）

这个转换器仅在 `requireDefaultExport: true` 时运行，在标准 TypeScript 转译**之前**执行。

**作用**：遍历 AST，查找 `export default` 语句，记录 default export 的表达式。

```typescript
// 它会识别：
export default plugin;              // ✅ 找到 default export
export default function() { ... }   // ✅ 找到 default export
export { something };               // ❌ 不是 default export，输出警告
```

如果遍历完整个 AST 都没找到 `export default`，抛出 `NoDefaultExportError: 'Default export not found'`。

这个错误被 PluginLoader 捕获后触发回退机制——尝试用旧的对象风格加载插件。

### Transformer 2: _awaitRequireTransformer（after）

这个转换器始终运行，在 TypeScript 转译为 CommonJS **之后**执行。

**作用**：将所有 `require()` 调用包装为 `await require()`。

TypeScript 将 `import { X } from 'pkg'` 转译为 CommonJS 后，会生成类似：

```javascript
const { X } = require("pkg");
```

但在 Plugin Playground 中，模块解析是异步的（需要从网络或本地文件系统加载），`require` 函数返回 Promise。`_awaitRequireTransformer` 将上述代码转换为：

```javascript
const { X } = await require("pkg");
```

实现原理是访问 AST 中所有 CallExpression 节点，当被调用函数是名为 `require` 的 Identifier 时，用 `AwaitExpression` 包装它：

```typescript
if (ts.isCallExpression(node)) {
  const expression = node.expression;
  if (ts.isIdentifier(expression) && expression.text === 'require') {
    return ts.factory.createAwaitExpression(node);
  }
}
```

### Transformer 3: _exportWrapperTransformer（after）

这个转换器始终运行，在 `_awaitRequireTransformer` 之后执行。

**作用**：在转译后的代码外层包装 exports 对象和 return 语句，使代码可作为 AsyncFunction 体执行。

转换逻辑：

1. 如果代码以 `'use strict'` 开头，将其提取到最前面
2. 创建 `const exports = {};` 变量声明
3. 将原始转译语句放在 exports 声明之后
4. 在末尾添加 `return exports;`

**转换示例：**

输入（TypeScript 源码）：
```typescript
import { JupyterFrontEnd } from '@jupyterlab/application';

const plugin = { id: 'test', autoStart: true, activate: () => {} };
export default plugin;
```

经过 TypeScript 标准转译 + _awaitRequireTransformer 后：
```javascript
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const application_1 = await require("@jupyterlab/application");
const plugin = { id: 'test', autoStart: true, activate: () => {} };
exports.default = plugin;
```

经过 _exportWrapperTransformer 后（最终输出）：
```javascript
"use strict";
const exports = {};
Object.defineProperty(exports, "__esModule", { value: true });
const application_1 = await require("@jupyterlab/application");
const plugin = { id: 'test', autoStart: true, activate: () => {} };
exports.default = plugin;
return exports;
```

## AsyncFunction 沙箱执行

转译后的代码作为 `AsyncFunction` 的函数体执行：

```typescript
const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor;

const module = new AsyncFunction(
  transpiler.importFunctionName,  // 'require'
  transpiledCode                   // 转译后的代码
)(importFunction);                 // 传入实际的模块解析函数

// 获取 default export
const pluginSource = module.default;
```

`AsyncFunction` 创建一个异步函数，其第一个参数名为 `'require'`，函数体是转译后的代码。调用时传入 `ImportResolver.resolve` 作为 require 函数，这样代码中所有 `await require('...')` 都会调用 ImportResolver 进行模块解析。

AsyncFunction 执行后返回 `exports` 对象，PluginLoader 从 `exports.default` 获取插件定义。

## 旧格式回退机制

当 `requireDefaultExport: true` 且代码中没有 `export default` 时，PluginTranspiler 抛出 `NoDefaultExportError`。PluginLoader 捕获这个错误后，使用旧格式执行：

```typescript
// 回退到对象风格
functionBody = `'use strict';\nreturn (${code})`;
transpiled = false;

// 使用普通 Function 而非 AsyncFunction
pluginSource = new Function(
  'require', 'requirejs', 'define',
  functionBody
)(requirejs.require, requirejs.require, requirejs.define);
```

旧格式下：
- 代码被包装在 `'use strict'; return (...)` 中，直接返回括号内的对象/值
- 使用普通 `Function`（非 AsyncFunction），在 RequireJS 环境中执行
- 传入 `require`、`requirejs`、`define` 三个全局函数
- 不经过 TypeScript 转译，代码需是有效的 ES5/ES6 JavaScript

## TypeScript 支持的特性

由于使用 `ts.transpileModule`（而非完整的 `ts.createProgram`），转译支持以下特性：

- 类型注解（type annotations）
- 接口（interfaces）
- 泛型（generics）
- ES module 语法（import/export）
- async/await
- 解构赋值
- 箭头函数
- 可选链（?.）和空值合并（??）
- JSX（如果配置了 jsx 选项）

不支持的特性（因为没有类型检查）：
- 跨文件类型检查
- const enum（需要完整程序分析）
- 装饰器的元数据反射
- paths/baseUrl 模块解析（由 ImportResolver 处理）

## 相关概念

- [插件加载流程](05-plugin-loader.md)
- [模块解析系统](04-module-resolution.md)
- [JupyterLab 插件基础结构](02-plugin-basics.md)
- [PluginLoader API 参考](../references/loader-transpiler-api.md)
