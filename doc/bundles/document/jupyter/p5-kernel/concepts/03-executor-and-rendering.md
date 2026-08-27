---
type: Concept
title: P5Executor 与渲染机制
description: P5Executor 如何扩展 JavaScriptExecutor，实现 p5.Graphics 自动渲染为 PNG、内置 API 文档支持，以及 p5-docs 自动生成机制
tags: [p5executor, mime-rendering, p5-graphics, png, code-inspection, p5-docs, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: executor
    resource: /references/executor-source.md
    title: P5Executor 类 API 信源
---

## P5Executor 概述

`P5Executor` 继承自 `JavaScriptExecutor`（来自 `@jupyterlite/javascript-kernel`），是 p5-kernel 对代码执行器的特化。它通过覆写两个方法实现了 p5.js 专属能力：

1. **p5.Graphics 自动渲染为 PNG 图像**：让离屏画布直接作为 cell 输出
2. **p5.js 内置 API 文档**：Shift+Tab 代码内省显示函数签名和描述

整个类只有约 50 行代码，体现了最小化扩展的设计哲学。

## p5.Graphics → PNG 自动渲染

### 为什么需要这个功能

在 p5.js 中，`createGraphics(w, h)` 创建一个离屏画布（p5.Graphics 对象），常用于分层绘制、后处理等场景。在普通 JavaScript 内核中，执行 `createGraphics(200, 200)` 只会输出 `[object Object]` 或无意义的文本，无法看到画布内容。

P5Executor 覆写了 `getMimeBundle()` 方法，自动检测 p5.Graphics 对象并将其渲染为 PNG 图像。

### getMimeBundle() 实现

```typescript
override getMimeBundle(value: any): IMimeBundle {
  if (
    value &&
    typeof value === 'object' &&
    value.constructor?.name === 'p5.Graphics' &&
    typeof value.elt !== 'undefined'
  ) {
    try {
      const canvas = value.elt as HTMLCanvasElement;
      const dataUrl = canvas.toDataURL('image/png');
      const base64 = dataUrl.split(',')[1];
      return {
        'image/png': base64,
        'text/plain': `p5.Graphics(${canvas.width}x${canvas.height})`
      };
    } catch {
      return { 'text/plain': 'p5.Graphics' };
    }
  }
  return super.getMimeBundle(value);
}
```

**检测条件**（需同时满足）：
- value 存在且为 object
- 构造函数名称为 `'p5.Graphics'`（通过 `constructor.name` 鸭子类型检测）
- 具有 `elt` 属性（p5.Graphics 的底层 HTMLCanvasElement）

**渲染流程**：
1. 将 `value.elt` 断言为 `HTMLCanvasElement`
2. 调用 `canvas.toDataURL('image/png')` 获取 PNG 格式的 data URL（格式：`data:image/png;base64,...`）
3. 提取 base64 数据部分（逗号后的内容）
4. 返回 MIME bundle，包含 `image/png`（base64 图像数据）和 `text/plain`（尺寸描述文本）
5. 异常时 fallback 为纯文本 `'p5.Graphics'`
6. 非 p5.Graphics 对象调用父类 `super.getMimeBundle(value)` 处理

**效果**：在 cell 中执行 `let pg = createGraphics(200, 200); pg.background(255, 0, 0); pg`，输出区域会直接显示一张 200x200 的红色图片，而不是无意义的对象文本。

> **鸭子类型检测说明**：使用 `constructor.name === 'p5.Graphics'` 而非 `instanceof` 检查，是因为 iframe 中的 p5.Graphics 构造函数与 Worker 中的可能不是同一个引用（iframe 沙箱隔离），`instanceof` 在跨 realm 场景下不可靠。

## 内置 API 文档（P5_DOCS）

### 为什么需要内置文档

p5.js 在全局模式（global mode）下将所有 API 绑定到全局对象上，这些函数是 `bound function`。在运行时使用 `console.log(createCanvas)` 只会输出 `function bound ()`，无法看到函数签名和参数信息。这导致 Jupyter 的 Shift+Tab 代码内省功能无法提供有用的信息。

P5Executor 通过 `getBuiltinDocumentation()` 方法，从预先生成的 `P5_DOCS` 映射中查找文档。

### getBuiltinDocumentation() 实现

```typescript
protected override getBuiltinDocumentation(
  expression: string
): string | null {
  return P5_DOCS[expression] ?? super.getBuiltinDocumentation(expression);
}
```

逻辑很简单：
1. 在 `P5_DOCS` 映射中查找 `expression`（即光标所在的表达式）
2. 找到则返回对应的文档字符串
3. 找不到则 fallback 到父类的文档查询

### P5_DOCS 的结构

`P5_DOCS` 是 `Record<string, string>` 类型，每个条目的值格式为：

```
描述文本. Usage: 函数名(必选参数, [可选参数])
```

例如：

```typescript
P5_DOCS = {
  circle: 'Draws a circle to the screen. Usage: circle(x, y, d)',
  createCanvas: 'Creates a canvas element. Usage: createCanvas(w, h, [renderer])',
  frameCount: 'The number of frames displayed since the program started.',
  mouseX: 'Current horizontal mouse position.',
  // ...
}
```

对于函数，包含描述和 Usage 签名（可选参数用方括号标记）；对于变量（如 mouseX、frameCount），只包含描述。

## p5-docs 自动生成机制

`P5_DOCS` 不是手写的，而是在构建时由 `scripts/generate-p5-docs.mjs` 脚本自动从 `@types/p5` 的 TypeScript 类型定义生成。

### 生成脚本工作流程

```
@types/p5/global.d.ts
    │
    ▼
TypeScript Compiler API (ts.createSourceFile)
    │
    ├─ 遍历 FunctionDeclaration（函数声明）
    │     ├─ 提取函数名
    │     ├─ 提取 JSDoc 注释第一句话
    │     ├─ 提取参数列表
    │     ├─ 重载函数：保留参数最多的版本
    │     └─ 格式化签名：name(req, [opt])
    │
    ├─ 遍历 VariableStatement（变量声明）
    │     ├─ 提取变量名
    │     ├─ 提取 JSDoc 注释
    │     └─ 记录描述
    │
    ▼
字母序排序
    │
    ▼
生成 src/p5-docs.ts（TypeScript 源文件）
```

### 关键生成逻辑

1. **描述提取**：JSDoc 注释中提取第一句话（匹配正则 `/^(.+?\.)\s/`，即第一个句号后跟空格的位置）
2. **重载处理**：同一函数名有多个重载声明时，保留参数最多的版本（提供最丰富的签名信息）
3. **参数格式化**：有 `questionToken` 或 `initializer` 的参数标记为可选（方括号包裹）
4. **描述继承**：如果某个重载缺少 JSDoc，复用之前重载的描述
5. **转义处理**：描述中的单引号转义为 `\'`，避免生成的 TypeScript 语法错误

### 构建集成

在 `package.json` 的 build 脚本中，`generate:docs` 步骤在 `tsc` 编译前执行：

```json
{
  "scripts": {
    "build": "npm run generate:docs && tsc -b",
    "generate:docs": "node scripts/generate-p5-docs.mjs"
  }
}
```

开发依赖中包含 `@types/p5: ^1.7.7`，提供 p5.js 的完整 TypeScript 类型定义。执行 `jlpm generate:docs` 或 `npm run generate:docs` 即可手动重新生成文档。

## 继承自 JavaScriptExecutor 的能力

P5Executor 从父类继承了以下对 p5-kernel 至关重要的方法：

| 方法 | 用途 | P5Kernel 中的调用位置 |
|------|------|---------------------|
| `createCodeRegistry()` | 创建代码注册表实例 | `onRuntimeReady()` |
| `registerCode(code, registry)` | 将代码 AST 分析后注册到注册表 | `executeRequest()` |
| `extractImports(code)` | 从代码中提取 ES import 语句 | `executeRequest()` |
| `generateImportCode(imports)` | 根据 import 信息生成实际加载代码 | `_magics()` |
| `generateCodeFromRegistry(registry)` | 从注册表生成去重合并代码 | `_magics()` |

这些方法构成了代码累积和 import 管理的基础。

## 相关概念

- [P5Kernel 实现详解](02-kernel-implementation.md)
- [%show 魔法命令详解](04-magic-commands.md)
- [构建与打包](06-build-and-packaging.md)
