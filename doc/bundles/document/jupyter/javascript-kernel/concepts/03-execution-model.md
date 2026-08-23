---
type: Concept
title: 执行模型
description: JavaScript 代码的 AST 转换、Magic Imports、异步函数包装、MIME 富输出和错误处理
tags: [execution, ast, meriyah, magic-imports, mime, async, error]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-executor
    title: executor.ts
  - id: jk-evaluator
    title: runtime_evaluator.ts
  - id: jk-errors
    title: errors.ts
---

# 执行模型

JavaScript Kernel 的代码执行由 `JavaScriptExecutor` 和 `JavaScriptRuntimeEvaluator` 两个类协作完成。执行流程包含 AST 解析、代码转换、异步执行和结果格式化四个阶段。

## 执行流程总览

```
用户代码 (string)
    │
    ▼
meriyah parseScript()  ──► AST
    │
    ├─► _addToGlobalScope()      处理顶层变量声明
    ├─► _handleLastStatement()   末尾表达式自动 return
    └─► _rewriteImportStatements()  ES import → 动态 CDN import
    │
    ▼
组合代码 (string)
    │
    ▼
_createScopedFunction()  ──► async function
    │
    ▼
asyncFunction.call(globalScope)  ──► 执行结果
    │
    ├─► Widget? → displayWidget()
    └─► 其他值 → getMimeBundle() → execute_result
```

## AST 解析

代码解析使用 [meriyah](https://github.com/meriyah/meriyah) 解析器，配置为 ES module 模式：

```typescript
const ast = parseScript(code, {
  ranges: true,   // 包含位置信息
  module: true    // ES module 模式（支持 import/export）
});
```

解析失败（语法错误）时，直接返回语法错误响应，不进入执行阶段。

## 三重代码转换

### 1. 顶层变量作用域处理 (`_addToGlobalScope`)

用户代码中的 `var`/`let`/`const`/`function`/`class` 声明会被包装在 async function 内部，默认不会泄漏到全局。`_addToGlobalScope` 会将顶层声明的变量通过赋值注入到 `globalScope`，使得跨单元格的变量访问成为可能。

```javascript
// 单元格1
const x = 42;
function greet(name) { return `Hello, ${name}!`; }

// 单元格2 可以访问 x 和 greet
greet("World")  // 输出: 'Hello, World!'
```

### 2. 末尾表达式自动返回 (`_handleLastStatement`)

检测代码的最后一条语句：如果是表达式语句（非赋值、非声明），自动添加 `return` 关键字，使表达式值作为单元格输出。

```javascript
// 代码: 1 + 2
// 转换后: return 1 + 2
// 输出: 3

// 代码: console.log("hi"); 42
// 转换后: console.log("hi"); return 42
// 输出: 42

// 代码: const x = 1;
// 转换后: const x = 1; (无 return)
// 无输出（赋值语句不是表达式语句）
```

### 3. Magic Imports (`_rewriteImportStatements`)

ES module `import` 语句被转换为动态 `await import()` 调用。裸模块名自动映射到 jsdelivr CDN。

```javascript
// 用户代码
import confetti from 'canvas-confetti';
import { useState } from 'react';
import * as d3 from 'd3';
import 'some-polyfill';

// 转换后（概念性）
const { default: confetti } = await import('https://cdn.jsdelivr.net/npm/canvas-confetti/+esm');
const { useState } = await import('https://cdn.jsdelivr.net/npm/react/+esm');
const d3 = await import('https://cdn.jsdelivr.net/npm/d3/+esm');
await import('https://cdn.jsdelivr.net/npm/some-polyfill/+esm');

// 并赋值到 globalThis
globalThis["confetti"] = confetti;
globalThis["useState"] = useState;
globalThis["d3"] = d3;
```

Magic Imports 配置（默认值）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `enabled` | `true` | 是否启用 Magic Imports |
| `baseUrl` | `'https://cdn.jsdelivr.net/'` | CDN 基础 URL |
| `enableAutoNpm` | `true` | 是否自动映射裸模块名到 npm CDN |

### 模块导入规则

| 导入形式 | 转换目标 |
|---------|---------|
| 裸模块名 `'lodash'` | `https://cdn.jsdelivr.net/npm/lodash/+esm` |
| 相对路径 `'./utils.js'` | 保持原样（相对于 runtime baseUrl） |
| 绝对 URL `'https://...'` | 保持原样 |

## 异步函数包装

转换后的代码被包装在 async function 中执行：

```typescript
const combinedCode = `
  ${finalCode}           // 用户代码（已转换）
  ${codeAddToGlobalScope} // 全局赋值
  ${extraReturnCode}      // return 语句
`;

const asyncFunctionFactory = new Function(`
  return async function() {
    ${combinedCode}
  };
`);
const asyncFunction = asyncFunctionFactory.call(this._globalScope);
```

这意味着：
- ✅ 所有单元格支持顶层 `await`
- ✅ `import` 语句被转换为 `await import()`
- ⚠️ 顶层 `var` 不会成为全局变量（通过 `_addToGlobalScope` 显式处理）
- ✅ 执行上下文绑定到隔离的 globalScope

## MIME 富输出 (getMimeBundle)

执行结果通过 `getMimeBundle(value)` 转换为 MIME bundle，支持丰富的输出类型。

### 类型处理规则

| 类型 | 输出 MIME 类型 | 显示效果 |
|------|---------------|---------|
| `null` | `text/plain: 'null'` | `null` |
| `undefined` | `text/plain: 'undefined'` | `undefined` |
| `string`（非HTML） | `text/plain: "'value'"` | `'value'`（带引号） |
| `string`（HTML） | `text/html` + `text/plain` | 渲染为 HTML |
| `number`/`boolean` | `text/plain: String(value)` | 原值 |
| `bigint` | `text/plain: '42n'` | 带 `n` 后缀 |
| `symbol` | `text/plain: 'Symbol(desc)'` | 符号描述 |
| `function` | `text/plain` + `text/html` | `[Function: name]` + 高亮源码 |
| `Error` | `text/plain`（stack）+ `application/json` | 错误堆栈 |
| `Date` | `text/plain`（ISO）+ `application/json` | ISO 时间字符串 |
| `RegExp` | `text/plain: '/pattern/flags'` | 正则字面量 |
| `Map` | `text/plain`（预览）+ `application/json` | Map 内容预览 |
| `Set` | `text/plain`（预览）+ `application/json` | Set 内容预览 |
| `Array` | `application/json` + `text/plain`（预览） | JSON + 文本预览 |
| `TypedArray` | `text/plain: 'Uint8Array(42)'` | 类型名+长度 |
| `Promise` | `text/plain: 'Promise { <pending> }'` | pending 状态 |
| DOM 元素 | 专用 DOM MIME bundle | 渲染 DOM 元素 |
| 普通对象 | `application/json` + `text/plain`（预览） | JSON + 文本预览 |
| Widget 实例 | `application/vnd.jupyter.widget-view+json` | 渲染 Widget |

### HTML 字符串检测

字符串是否被识别为 HTML，使用正则检测：

```
/^<(?:[a-zA-Z][a-zA-Z0-9-]*[\s/>]|!(?:DOCTYPE|--))/
```

要求：trim 后以标签开头（`<tag`、`<!DOCTYPE`、`<!--`）且以 `>` 结尾。这避免了 `"<a, b>"` 等非 HTML 内容被误判。

### 自定义 MIME 输出方法

对象可以定义以下方法来自定义输出：

| 方法 | 返回类型 | MIME 类型 |
|------|---------|----------|
| `_toHtml()` | `string` | `text/html` |
| `_toSvg()` | `string` | `image/svg+xml` |
| `_toPng()` | `string`（base64） | `image/png` |
| `_toJpeg()` | `string`（base64） | `image/jpeg` |
| `_toMime()` | `IMimeBundle` | 自定义 MIME bundle |
| `inspect()` | `any` | `text/plain`（Node.js 风格） |

## 代码补全

代码补全基于运行时对象自省，不需要类型定义文件。

### 补全流程

1. 定位光标所在行，提取光标前的代码
2. 解析 stop 字符（`{}()=+-*/%&|^~<>,:;!?@#`）找到补全起始位置
3. 解析 `.` 或 `]` 分割表达式，找到根对象
4. 使用 `with(scope) { return expr; }` 在 globalScope 中求值根对象
5. 遍历原型链收集所有属性，过滤匹配前缀

```javascript
// 示例：输入 "console.l"
// 根对象: console（求值全局 console 对象）
// 匹配: "l" 前缀
// 补全: ["log", "info", "warn", "error", ...]（所有以 l 开头的属性）
```

补全支持多行代码，正确计算 cursor_start 和 cursor_end 位置（包括已输入的部分匹配文本）。

## 代码完整性检查 (isComplete)

用于多行输入模式，判断代码是否可以执行：

- **complete**：AST 解析成功，代码完整
- **incomplete**：遇到 "unexpected end of input"、"unterminated string"、"unterminated template" 等模式，返回建议缩进
- **invalid**：其他语法错误，不等待更多输入

```javascript
// incomplete 示例（建议缩进）
function foo() {
  // 光标在这里 → indent: '  '
```

不完整代码检测到开括号（`{`、`(`、`[`）结尾时，建议增加缩进（+2 空格）。

## 对象检查 (inspect)

按 Shift+Tab 触发对象检查，返回对象的文档和类型信息：

1. 提取光标处的表达式
2. 在 globalScope 中求值表达式
3. 构建检查数据（类型、属性、值预览）
4. 附加内置文档（如果有）
5. 求值失败时回退到内置文档和相似名称建议

## 错误处理

### 跨 Realm 错误归一化

IFrame 模式下，iframe 中抛出的 Error 对象在主窗口中 `instanceof Error` 为 false（不同 JavaScript realm）。`normalizeError()` 函数处理这种情况：

```typescript
function normalizeError(error: unknown, fallbackName = 'Error'): Error {
  if (error instanceof Error) return error;

  // 跨 realm Error：有 name/message/stack 属性
  if (isErrorLike(error)) {
    const normalized = new Error(error.message);
    normalized.name = error.name || fallbackName;
    normalized.stack = error.stack;
    return normalized;
  }

  // 非 Error 抛出值
  return new Error(String(error));
}
```

### 堆栈清理

`cleanStackTrace(error)` 过滤内部执行器帧，只显示用户代码相关帧：

- 移除 `makeAsyncFromCode`、`new Function`、`asyncFunction` 等内部帧
- 保留包含 `eval` 或 `<anonymous>` 的用户帧
- 语法错误只显示 `Name: message`（无堆栈）
- 运行时错误包含清理后的用户堆栈

```
// 用户看到的错误：
// ReferenceError: x is not defined
//     at eval (eval at <anonymous>:2:3)

// （内部帧已被过滤）
```

## 代码注册表 (ICodeRegistry)

执行器提供代码注册和去重生成功能，用于代码重构场景（如 Sketch 导出）：

```typescript
interface ICodeRegistry {
  functions: Map<string, any>;   // 函数声明（后定义覆盖先定义）
  variables: Map<string, any>;   // 变量声明
  classes: Map<string, any>;     // 类声明
  statements: any[];             // 其他语句（按执行顺序）
}
```

- `registerCode(code, registry)`：解析代码并注册声明到 registry
- `generateCodeFromRegistry(registry)`：从 registry 生成去重代码（variables→classes→functions→statements 顺序）
- `extractImports(code)`：提取 import 信息（不执行代码）
- `generateImportCode(imports)`：生成 import 赋值代码

## 相关文档

- [04-运行时后端](04-runtime-backends.md) — IFrame/Worker 执行环境
- [07-富媒体输出](07-display-system.md) — display() 函数和 DisplayHelper
- [01-快速开始](01-getting-started.md) — 基础执行示例
