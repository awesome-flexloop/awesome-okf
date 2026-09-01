---
type: Reference
title: P5Executor 类 API 信源
description: P5Executor 类的方法登记，包含 MIME 渲染覆写和内置文档提供机制
tags: [p5-executor, executor-api, mime-rendering, p5-docs, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: executor-src
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel/src/executor.ts
    title: packages/p5-kernel/src/executor.ts
  - id: docs-gen
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel/scripts/generate-p5-docs.mjs
    title: scripts/generate-p5-docs.mjs
---

## 类继承关系

```
P5Executor extends JavaScriptExecutor (from @jupyterlite/javascript-kernel)
```

P5Executor 是 JavaScriptExecutor 的 p5.js 特化版本，主要扩展了两个能力：
1. p5.Graphics 对象自动渲染为 PNG 图像
2. 提供 p5.js API 的内置文档供 Shift+Tab 代码内省使用

## 覆写方法

### getMimeBundle()

```typescript
override getMimeBundle(value: any): IMimeBundle
```

覆写父类的 MIME bundle 生成方法，增加 p5.Graphics 特殊处理：

**检测条件**（全部满足）：
- `value` 存在且为 object
- `value.constructor?.name === 'p5.Graphics'`
- `typeof value.elt !== 'undefined'`

**处理逻辑**：
1. 将 `value.elt` 转换为 `HTMLCanvasElement`
2. 调用 `canvas.toDataURL('image/png')` 获取 data URL
3. 提取 base64 数据部分（`dataUrl.split(',')[1]`）
4. 返回 MIME bundle：
   ```typescript
   {
     'image/png': base64,
     'text/plain': `p5.Graphics(${canvas.width}x${canvas.height})`
   }
   ```
5. 异常时 fallback 为 `{ 'text/plain': 'p5.Graphics' }`
6. 非 p5.Graphics 对象调用 `super.getMimeBundle(value)` 走默认逻辑

### getBuiltinDocumentation()

```typescript
protected override getBuiltinDocumentation(
  expression: string
): string | null
```

覆写父类的内置文档查询方法，为 p5.js 全局 API 提供文档字符串：

1. 在自动生成的 `P5_DOCS` 映射中查找 `expression` 键
2. 若找到，返回对应的文档字符串（包含描述和函数签名）
3. 若未找到，调用 `super.getBuiltinDocumentation(expression)` 使用父类默认文档

## P5_DOCS 文档映射

`P5_DOCS` 是 `Record<string, string>` 类型，由 `scripts/generate-p5-docs.mjs` 在构建时自动生成，来源是 `@types/p5/global.d.ts` 类型定义文件。

### 文档生成脚本行为（generate-p5-docs.mjs）

1. **输入**：解析 `@types/p5/global.d.ts`（通过 `require.resolve('@types/p5/global.d.ts')` 定位）
2. **处理函数声明**：
   - 提取函数名、JSDoc 注释、参数列表
   - 对于重载函数，保留参数最多的重载（最丰富的签名）
   - 提取 JSDoc 第一句话作为描述（以句号+空格分隔）
   - 格式化签名：`name(param1, [param2])`（可选参数加方括号）
3. **处理变量声明**：提取 mouseX、width、frameCount 等全局变量的 JSDoc 描述
4. **输出**：按字母序排序，生成 TypeScript 源文件 `src/p5-docs.ts`
5. **输出格式**：每个条目为 `key: 'description. Usage: signature'` 形式

### P5_DOCS 条目示例（生成格式）

```typescript
export const P5_DOCS: Record<string, string> = {
  circle:
    'Draws a circle to the screen. Usage: circle(x, y, d)',
  createCanvas:
    'Creates a canvas element in the document. Usage: createCanvas(w, h, [renderer])',
  frameCount:
    'The number of frames that have been displayed since the program started.',
  mouseX:
    'Current horizontal mouse position.',
  // ... 更多 p5.js API
};
```

> p5.js 在全局模式下将 API 绑定为全局函数，运行时 `console.log(createCanvas)` 只显示 `function bound ()`，无法获取签名和文档。P5_DOCS 映射解决了这个问题，让 Shift+Tab 内省能显示正确的 API 文档。

## 继承自 JavaScriptExecutor 的成员

P5Executor 从父类 JavaScriptExecutor 继承以下关键能力（用于 P5Kernel 调用）：

| 成员 | 说明 |
|------|------|
| `createCodeRegistry()` | 创建 ICodeRegistry 代码注册表实例 |
| `registerCode(code, registry)` | 将代码注册到 registry（AST 分析） |
| `extractImports(code)` | 从代码中提取 ES import 语句，返回 IImportInfo[] |
| `generateImportCode(imports)` | 根据 IImportInfo[] 生成 import 加载代码 |
| `generateCodeFromRegistry(registry)` | 从代码注册表生成去重合并后的完整代码 |
