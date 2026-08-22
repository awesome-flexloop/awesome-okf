---
type: Concept
title: EchoKernel 类实现详解
description: EchoKernel类的完整实现分析，kernelInfoRequest、executeRequest核心逻辑，publishExecuteResult输出机制
tags: [echokernel, implementation, execute, kernel-info, publish-result, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:16:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel-src
    resource: /references/kernel-source.md
    title: EchoKernel 类源码信源
---

## EchoKernel 类定义

```typescript
export class EchoKernel extends BaseKernel {
  // 实现BaseKernel的抽象方法
}
```

EchoKernel继承自 `@jupyterlite/services` 的 `BaseKernel`，是整个包的核心实现类。它只有153行代码，却完整展示了自定义JupyterLite内核所需的全部实现。

## kernelInfoRequest() — 内核信息响应

当JupyterLab前端连接到内核后，首先发送 `kernel_info_request` 消息获取内核信息。EchoKernel的响应：

```typescript
async kernelInfoRequest(): Promise<KernelMessage.IInfoReplyMsg['content']> {
  const content: KernelMessage.IInfoReply = {
    implementation: 'Text',
    implementation_version: '0.1.0',
    language_info: {
      codemirror_mode: { name: 'text/plain' },
      file_extension: '.txt',
      mimetype: 'text/plain',
      name: 'echo',
      nbconvert_exporter: 'text',
      pygments_lexer: 'text',
      version: 'es2017'
    },
    protocol_version: '5.3',
    status: 'ok',
    banner: 'An echo kernel running in the browser',
    help_links: [
      { text: 'Echo Kernel', url: 'https://github.com/jupyterlite/echo-kernel' }
    ]
  };
  return content;
}
```

### language_info 字段详解

`language_info` 是最关键的部分，它告诉前端如何处理这个内核的代码：

| 字段 | 值 | 对前端的影响 |
|------|-----|-------------|
| `name` | `'echo'` | 语言标识名 |
| `mimetype` | `'text/plain'` | 代码cell的MIME类型 |
| `file_extension` | `'.txt'` | 保存Notebook时的关联文件扩展名 |
| `codemirror_mode.name` | `'text/plain'` | CodeMirror编辑器的语法高亮模式（纯文本无高亮） |
| `pygments_lexer` | `'text'` | Pygments语法高亮器（用于nbconvert导出） |
| `nbconvert_exporter` | `'text'` | nbconvert导出器类型 |
| `version` | `'es2017'` | 语言版本标识 |

### 其他重要字段

| 字段 | 值 | 说明 |
|------|-----|------|
| `implementation` | `'Text'` | 内核实现名称 |
| `implementation_version` | `'0.1.0'` | 内核版本 |
| `protocol_version` | `'5.3'` | Jupyter协议版本（必须与前端兼容） |
| `status` | `'ok'` | 请求成功状态 |
| `banner` | `'An echo kernel running in the browser'` | 内核启动时显示的欢迎信息 |
| `help_links` | GitHub链接 | 帮助菜单中显示的链接 |

## executeRequest() — 代码执行逻辑

这是内核的核心方法，处理 `execute_request` 消息：

```typescript
async executeRequest(
  content: KernelMessage.IExecuteRequestMsg['content']
): Promise<KernelMessage.IExecuteReplyMsg['content']> {
  const { code } = content;

  this.publishExecuteResult({
    execution_count: this.executionCount,
    data: {
      'text/plain': code
    },
    metadata: {}
  });

  return {
    status: 'ok',
    execution_count: this.executionCount,
    user_expressions: {}
  };
}
```

### 执行流程

1. **提取代码**：从 `content.code` 获取用户输入的代码字符串
2. **发布结果**：调用 `publishExecuteResult()` 将结果发送到前端
3. **返回回复**：返回execute_reply消息，告知前端执行完成

### publishExecuteResult() 参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `execution_count` | `this.executionCount` | 当前执行序号（从BaseKernel继承） |
| `data` | `{ 'text/plain': code }` | 输出数据，MIME类型为键，内容为值 |
| `metadata` | `{}` | 输出元数据（空对象） |

### data 字段的MIME类型

`data` 是一个MIME类型字典，键是MIME类型，值是该类型的数据：

```typescript
data: {
  'text/plain': 'Hello World',                    // 纯文本
  'text/html': '<b>Hello</b>',                   // HTML
  'image/png': 'base64编码的图片数据',             // PNG图片
  'application/json': { result: 42 },            // JSON数据
}
```

Echo Kernel只输出 `text/plain` 类型，将输入代码原样返回。真实内核（如Pyodide）会输出多种MIME类型（如matplotlib图表输出 `image/png`）。

### execute_reply 返回值

| 字段 | 值 | 说明 |
|------|-----|------|
| `status` | `'ok'` | 执行状态（`'ok'` 或 `'error'`） |
| `execution_count` | `this.executionCount` | 本次执行的序号 |
| `user_expressions` | `{}`` | 用户表达式求值结果（Echo Kernel不支持） |

## 未实现的方法

其余8个方法全部抛出 `Error('Not implemented')`：

```typescript
async completeRequest(content) {
  throw new Error('Not implemented');
}

async inspectRequest(content) {
  throw new Error('Not implemented');
}

async isCompleteRequest(content) {
  throw new Error('Not implemented');
}

async commInfoRequest(content) {
  throw new Error('Not implemented');
}

inputReply(content): void {
  throw new Error('Not implemented');
}

async commOpen(msg) {
  throw new Error('Not implemented');
}

async commMsg(msg) {
  throw new Error('Not implemented');
}

async commClose(msg) {
  throw new Error('Not implemented');
}
```

### 这些方法为什么可以不实现

| 方法 | 功能 | 不实现的影响 |
|------|------|-------------|
| `completeRequest` | Tab代码补全 | 用户按Tab不会有补全建议 |
| `inspectRequest` | Shift+Tab对象检视 | 无法查看对象文档/源码 |
| `isCompleteRequest` | 多行输入完整性判断 | 控制台可能无法正确处理多行输入 |
| `commInfoRequest` | 查询comm通道 | Widgets等双向通信功能不可用 |
| `inputReply` | 标准输入回复 | `input()` 函数不可用 |
| `commOpen/Msg/Close` | Widgets通信 | ipywidgets等不可用 |

对于一个"回声"内核来说，这些功能都不需要。但如果你要实现一个完整功能的内核（如Python内核），则需要实现其中一些方法。

## Echo Kernel的执行效果

当用户在Echo内核的Notebook中输入：

```python
print("Hello, World!")
```

输出区域会显示：

```
print("Hello, World!")
```

即原样输出输入的代码文本，不会执行print函数。

## 如何扩展Echo Kernel实现真实内核

要基于Echo Kernel实现一个有实际功能的内核，只需修改 `executeRequest()` 方法：

```typescript
async executeRequest(content) {
  const { code } = content;

  try {
    // 在这里执行你的代码逻辑
    const result = this.executeCode(code); // 自定义执行逻辑

    this.publishExecuteResult({
      execution_count: this.executionCount,
      data: {
        'text/plain': String(result)
        // 可以添加更多MIME类型：'text/html', 'image/png'等
      },
      metadata: {}
    });

    return {
      status: 'ok',
      execution_count: this.executionCount,
      user_expressions: {}
    };
  } catch (err) {
    // 处理错误
    this.publishExecuteError({
      execution_count: this.executionCount,
      ename: err.name,
      evalue: err.message,
      traceback: [err.stack]
    });

    return {
      status: 'error',
      execution_count: this.executionCount,
      user_expressions: {}
    };
  }
}
```

BaseKernel还提供了 `stream()` 方法用于发布stdout/stderr输出：

```typescript
this.stream({ name: 'stdout', text: 'Hello from stdout\n' });
this.stream({ name: 'stderr', text: 'Warning message\n' });
```

## 相关概念

- [Echo Kernel简介](/concepts/00-introduction.md)
- [JupyterLite内核架构](/concepts/01-kernel-architecture.md)
- [插件注册机制](/concepts/02-plugin-registration.md)
- [构建与打包](/concepts/04-build-and-packaging.md)
