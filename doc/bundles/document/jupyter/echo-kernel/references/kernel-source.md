---
type: Reference
title: EchoKernel 类源码信源
description: src/kernel.ts 中 EchoKernel 类的完整API登记，继承BaseKernel，实现10个抽象方法
tags: [kernel, basekernel, execute, messaging, typescript, jupyterlite]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:02:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-ts
    resource: /references/kernel-source.md
    title: src/kernel.ts
---

## 源码位置

- `src/kernel.ts` — EchoKernel 类实现，约153行

## 类定义

### EchoKernel（L11）

```typescript
export class EchoKernel extends BaseKernel
```

继承自 `@jupyterlite/services` 的 `BaseKernel` 抽象类。

## 实现的方法

### 1. kernelInfoRequest() — L15-L41

```typescript
async kernelInfoRequest(): Promise<KernelMessage.IInfoReplyMsg['content']>
```

返回内核信息对象：

| 字段 | 值 | 说明 |
|------|-----|------|
| `implementation` | `'Text'` | 实现名称 |
| `implementation_version` | `'0.1.0'` | 实现版本 |
| `language_info.codemirror_mode.name` | `'text/plain'` | CodeMirror编辑器模式 |
| `language_info.file_extension` | `'.txt'` | 文件扩展名 |
| `language_info.mimetype` | `'text/plain'` | MIME类型 |
| `language_info.name` | `'echo'` | 语言名称 |
| `language_info.nbconvert_exporter` | `'text'` | nbconvert导出器 |
| `language_info.pygments_lexer` | `'text'` | Pygments语法高亮器 |
| `language_info.version` | `'es2017'` | 语言版本 |
| `protocol_version` | `'5.3'` | Jupyter协议版本 |
| `status` | `'ok'` | 响应状态 |
| `banner` | `'An echo kernel running in the browser'` | 内核欢迎横幅 |
| `help_links` | `[{text: 'Echo Kernel', url: '...'}]` | 帮助链接列表 |

### 2. executeRequest(content) — L48-L66

```typescript
async executeRequest(
  content: KernelMessage.IExecuteRequestMsg['content']
): Promise<KernelMessage.IExecuteReplyMsg['content']>
```

核心执行逻辑：

1. 从 `content` 中解构 `code` 字段（用户输入的代码字符串）
2. 调用 `this.publishExecuteResult()` 发布执行结果：
   - `execution_count`: `this.executionCount`（继承自BaseKernel的执行计数器）
   - `data`: `{ 'text/plain': code }` — 将输入代码原样作为纯文本输出
   - `metadata`: `{}`（空元数据）
3. 返回执行回复：`{ status: 'ok', execution_count: this.executionCount, user_expressions: {} }`

### 3. completeRequest(content) — L73-L77

```typescript
async completeRequest(content): Promise<KernelMessage.ICompleteReplyMsg['content']>
```

抛出 `Error('Not implemented')` — 不支持代码补全。

### 4. inspectRequest(content) — L86-L90

```typescript
async inspectRequest(content): Promise<KernelMessage.IInspectReplyMsg['content']>
```

抛出 `Error('Not implemented')` — 不支持代码检视（object inspection）。

### 5. isCompleteRequest(content) — L99-L103

```typescript
async isCompleteRequest(content): Promise<KernelMessage.IIsCompleteReplyMsg['content']>
```

抛出 `Error('Not implemented')` — 不支持代码完整性检查。

### 6. commInfoRequest(content) — L112-L116

```typescript
async commInfoRequest(content): Promise<KernelMessage.ICommInfoReplyMsg['content']>
```

抛出 `Error('Not implemented')` — 不支持comm信息查询。

### 7. inputReply(content) — L123-L125

```typescript
inputReply(content: KernelMessage.IInputReplyMsg['content']): void
```

抛出 `Error('Not implemented')` — 不支持标准输入回复。

### 8. commOpen(msg) — L132-L134

```typescript
async commOpen(msg: KernelMessage.ICommOpenMsg): Promise<void>
```

抛出 `Error('Not implemented')` — 不支持comm打开。

### 9. commMsg(msg) — L141-L143

```typescript
async commMsg(msg: KernelMessage.ICommMsgMsg): Promise<void>
```

抛出 `Error('Not implemented')` — 不支持comm消息。

### 10. commClose(msg) — L150-L152

```typescript
async commClose(msg: KernelMessage.ICommCloseMsg): Promise<void>
```

抛出 `Error('Not implemented')` — 不支持comm关闭。

## 导入依赖

| 导入来源 | 导入项 | 用途 |
|----------|--------|------|
| `@jupyterlab/services` | `KernelMessage`（type） | Jupyter内核消息类型定义 |
| `@jupyterlite/services` | `BaseKernel` | 内核抽象基类 |

## 继承的关键成员（来自BaseKernel）

EchoKernel 通过继承获得以下能力，无需自行实现：

| 成员 | 用途 |
|------|------|
| `executionCount` | 执行计数器getter |
| `publishExecuteResult()` | 发布执行结果到前端 |
| `stream()` | 发布流式输出（stdout/stderr） |
| `displayData()` | 发布显示数据 |
| `publishExecuteError()` | 发布执行错误 |
| `clearOutput()` | 清除输出 |
| `handleMessage()` | 消息路由分发（模板方法） |
| `ready` | 内核就绪Promise |
| `dispose()` | 资源清理 |

## 核心数据流

```
用户在Notebook中输入代码
  → JupyterLab前端发送 execute_request 消息
    → BaseKernel.handleMessage() 路由消息
      → EchoKernel.executeRequest(content)
        → publishExecuteResult({ data: { 'text/plain': code } })
          → 前端显示输出（即输入的代码本身）
        → 返回 { status: 'ok', execution_count, user_expressions: {} }
```
