---
type: Reference
title: P5Kernel 类 API 信源
description: P5Kernel 类的完整 API 登记，包含构造函数、方法、私有字段、命名空间接口
tags: [p5-kernel, kernel-api, typescript, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-src
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel/src/kernel.ts
    title: packages/p5-kernel/src/kernel.ts
---

## 类继承关系

```
P5Kernel extends JavaScriptKernel (from @jupyterlite/javascript-kernel)
```

## 构造函数

```typescript
constructor(options: P5Kernel.IOptions)
```

构造函数行为：
1. 调用 `super()` 传入 `{ ...options, runtime: 'iframe', executorFactory: (globalScope) => new P5Executor(globalScope) }`
2. 从 options 中提取 `p5Url`
3. 设置 `this._displayId = this.id`（使用 kernel id 作为 display id）
4. 生成 `_bootstrap` 代码字符串（动态 import p5.js + 创建全局 p5 实例）

### P5Kernel.IOptions 接口

```typescript
interface IOptions extends JavaScriptKernel.IOptions {
  p5Url: string;       // 必填：p5.js 的 CDN URL
  runtime?: 'iframe';  // 可选：固定为 'iframe'
}
```

继承自 `JavaScriptKernel.IOptions`（包含 id、name、location、sendMessage 等标准内核选项）。

## 公共方法

### kernelInfoRequest()

```typescript
override async kernelInfoRequest(): Promise<KernelMessage.IInfoReplyMsg['content']>
```

返回内核信息：

| 字段 | 值 |
|------|-----|
| implementation | `'p5.js'` |
| implementation_version | `'0.1.0'` |
| language_info.name | `'p5js'` |
| language_info.codemirror_mode.name | `'javascript'` |
| language_info.file_extension | `'.js'` |
| language_info.mimetype | `'text/javascript'` |
| language_info.nbconvert_exporter | `'javascript'` |
| language_info.pygments_lexer | `'javascript'` |
| language_info.version | `'es2017'` |
| protocol_version | `'5.3'` |
| status | `'ok'` |
| banner | `'A p5.js kernel'` |
| help_links | `[{ text: 'p5.js Kernel', url: 'https://github.com/jupyterlite/p5-kernel' }]` |

### executeRequest()

```typescript
override async executeRequest(
  content: KernelMessage.IExecuteRequestMsg['content']
): Promise<KernelMessage.IExecuteReplyMsg['content']>
```

执行流程：
1. 从 content 中提取 `code`
2. 构造 `transient = { display_id: this._displayId }`
3. 若 code 以 `%show` 开头：调用 `_magics(code)` 处理 magic，通过 `displayData()` 发送结果，记录 `_parentHeaders`，返回 ok
4. 否则调用 `super.executeRequest(content)` 执行 JavaScript 代码
5. 若执行结果不是 ok，直接返回
6. 若 code 不以 `%` 开头且 executor 和 codeRegistry 存在：
   - 调用 `_p5Executor.registerCode(code, this._codeRegistry)` 注册代码
   - 调用 `executor.extractImports(code)` 提取 import 语句，去重后追加到 `_imports`
7. 调用 `_magics()` （无参数）重新生成渲染数据，通过 `updateDisplayData()` 更新所有已显示的 iframe
8. 返回 reply

## 保护方法

### onRuntimeReady()

```typescript
protected override async onRuntimeReady(
  context: JavaScriptKernel.IRuntimeReadyContext
): Promise<void>
```

运行时就绪回调：
1. 断言 `context.runtime === 'iframe'`，否则抛出 Error
2. 将 `context.executor` 赋值给 `this._p5Executor`（类型转换为 P5Executor）
3. 调用 `this._p5Executor.createCodeRegistry()` 创建代码注册表
4. 执行 `context.execute(this._bootstrap)` 加载 p5.js 并创建全局实例

## 私有方法

### _magics()

```typescript
private async _magics(
  code = ''
): Promise<KernelMessage.IExecuteResultMsg['content']>
```

magic 处理逻辑：
1. 从 `_p5Executor` 生成 import 加载代码（`executor.generateImportCode(this._imports)`）
2. 从 codeRegistry 生成去重后的合并代码（`executor.generateCodeFromRegistry(this._codeRegistry)`），基于 AST，后定义覆盖前定义
3. 构造 async wrapper script：先执行 bootstrap，再加载 imports，再执行合并代码，最后调用 `window.__globalP5._start()`
4. 解析 `%show` 正则 `/^%show(?: (.+)\s+(.+))?\s*$/` 提取 width/height 参数（默认 `100%` / `400px`）
5. 构造 iframe srcdoc：`<body style="overflow: hidden; margin: 0; padding: 0;"><script>${script}</script></body>`
6. HTML 转义 srcdoc（& → &amp;, ' → &#39;, " → &quot;）
7. 返回 `{ execution_count, data: { 'text/html': `<iframe ...>` }, metadata: {} }`

## 私有字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `_displayId` | `string` | 用于 update_display_data 的 display id，初始化为 kernel id |
| `_bootstrap` | `string` | p5.js 引导代码字符串，动态 import p5Url 并创建 `window.__globalP5 = new p5()` |
| `_codeRegistry` | `ICodeRegistry \| undefined` | 代码注册表（来自 JavaScriptKernel），AST 管理用户代码 |
| `_imports` | `IImportInfo[]` | 提取的 import 语句列表，去重存储 |
| `_parentHeaders` | `KernelMessage.IHeader<KernelMessage.MessageType>[]` | 已发送 display_data 的父消息头列表，用于 update_display_data |
| `_p5Executor` | `P5Executor \| undefined` | P5Executor 实例，在 onRuntimeReady 中赋值 |

## Bootstrap 代码模板

```javascript
import('${p5Url}').then(() => {
  // create the p5 global instance
  window.__globalP5 = new p5();
  return Promise.resolve();
})
```

## _magics 生成的 Script 模板

```javascript
${this._bootstrap}.then(async () => {
  ${importCode}
  ${combinedCode}
  window.__globalP5._start();
}).catch(e => console.error(e));
```
