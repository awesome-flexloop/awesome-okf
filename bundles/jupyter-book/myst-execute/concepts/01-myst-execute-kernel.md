---
type: concept
title: "myst-execute 内核管理"
description: "详解 myst-execute 的 Jupyter 内核连接创建、代码执行请求、IOPub 消息收集、内联表达式求值等核心机制"
tags: [myst-execute, kernel, jupyter, execution, iopub, inline-expression]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-execute-src.md"
    facts: [F-011, F-012, F-013, F-016, F-017, F-018, F-019, F-020, F-021, F-041, F-042, F-043, F-044]
---

# myst-execute 内核管理

myst-execute 通过 `@jupyterlab/services` 的 Kernel.IKernelConnection 接口与 Jupyter 内核通信，完成代码单元格的执行和内联表达式的求值。内核管理模块（kernel.ts）负责连接创建、超时重试、消息处理等底层细节。

## 内核连接创建

`createKernelConnection()` 函数负责建立 Jupyter 内核会话连接：

```ts
async function createKernelConnection(
  sessionManager: SessionManager,
  basePath: string,
  kernelspec: KernelSpec,
  vfile: VFile,
  log?: Logger,
): Promise<ISessionConnectionWithKernel | undefined>
```

### 关键行为

1. **路径规范化**：将 `vfile.path` 相对于 `basePath` 的路径使用正斜杠（`/`）拼接，避免 Windows 反斜杠导致 Jupyter Server 回退到根目录的问题
2. **Session 配置**：使用 `type: 'console'` 创建 console 类型 session（非 notebook 类型），kernel.name 从 frontmatter 的 kernelspec 获取
3. **就绪超时与重试**：
   - `KERNEL_READY_TIMEOUT_MS = 10000`（10秒）：通过 `Promise.race` 竞态 `kernel.info` 和超时
   - `KERNEL_READY_ATTEMPTS = 3`：超时后 shutdown 当前连接并重试，最多3次
4. **返回值**：成功时返回带 kernel 属性的 session 连接，3次失败后返回 undefined

```ts
const sessionOpts = {
  path: sessionPath,         // 正斜杠规范化的相对路径
  name: path.basename(vfile.path),
  type: 'console',
  kernel: { name: kernelspec.name },
};

for (let attempt = 1; attempt <= KERNEL_READY_ATTEMPTS; attempt++) {
  const connection = await sessionManager.startNew(sessionOpts);
  const ready = await Promise.race([
    connection.kernel.info.then(() => true),
    delay(KERNEL_READY_TIMEOUT_MS, false, { ref: false }),
  ]);
  if (ready) return connection as any;
  await connection.shutdown().catch(() => undefined);
}
```

## 代码单元格执行

`executeCodeCell()` 函数向内核发送执行请求并收集输出：

```ts
async function executeCodeCell(
  kernel: Kernel.IKernelConnection,
  code: string,
): Promise<{ status: string; outputs: IOutput[] }>
```

### 执行请求参数

```ts
const future = kernel.requestExecute({
  code,                    // 代码字符串
  allow_stdin: false,      // 禁止 stdin 输入（构建时无人交互）
  stop_on_error: false,    // 不停止队列中的后续请求
});
```

### IOPub 消息处理

通过 `future.onIOPub` 回调监听内核消息，按消息类型分类处理：

| msg_type | 处理方式 |
|----------|---------|
| `status` | 忽略（空闲/繁忙状态跟踪由 future.done 处理） |
| `execute_input` | 忽略 |
| `clear_output` | TODO：尚未实现 |
| `stream` | 收集到 outputs 数组（stdout/stderr 文本输出） |
| `execute_result` | 收集（表达式的求值结果） |
| `display_data` | 收集（图表、HTML、图片等 MIME bundle 输出） |
| `error` | 收集（异常错误，含 traceback） |
| `update_display_data` | 通过 display_id 查找已有 display_data 输出并更新其 data/metadata |
| `comm_*` | 忽略（ipywidgets 等通信消息） |

消息过滤机制确保只收集当前执行请求的回复：通过比较 `msg.parent_header.msg_id` 与 `future.msg.header.msg_id`。

### `update_display_data` 处理

`update_display_data` 是 Jupyter 的 display_id 机制：同一 display_id 的输出可以被后续消息更新。代码中：
1. 克隆消息并将 msg_type 改为 `display_data`
2. 从 `transient.display_id` 提取 display ID
3. 遍历已有 outputs，找到匹配 display_id 的条目，更新其 `data` 和 `metadata`
4. 如果找不到匹配的 display_id，则丢弃该消息（避免视觉错误）

### 执行完成

通过 `future.onReply` 捕获 execute_reply 的 status（'ok' | 'error'），await `future.done` 等待所有 IOPub 消息到达。

## 内联表达式求值

`evaluateInlineExpression()` 函数利用 Jupyter 的 `user_expressions` 机制执行内联表达式：

```ts
async function evaluateInlineExpression(
  kernel: Kernel.IKernelConnection,
  expr: string,
): Promise<{ status: string; result: IExpressionResult }>
```

```ts
const future = kernel.requestExecute({
  code: '',  // 空代码单元
  user_expressions: {
    expr: expr,  // 将表达式作为 user_expressions 发送
  },
  allow_stdin: false,
  stop_on_error: false,
});
```

Jupyter 内核会对 `user_expressions` 中的每个表达式求值，并在 execute_reply 中返回结果。结果从 `msg.content.user_expressions['expr']` 中提取，包含 status（'ok' | 'error'）、data（MIME bundle）或 traceback。

> **注意**：内联表达式和代码单元不会同时发送——computeExecutableNodes 按节点类型分别处理。这是因为 code cell 的执行可能改变内核状态（变量定义等），影响后续 inline expression 的结果。

## 可执行节点发现与过滤

`getExecutableNodes(tree)` 使用 unist-util-select 从 MDAST 中选择可执行节点：

```ts
return (
  selectAll(`block[kind=${NotebookCell.code}],inlineExpression`, tree)
    .filter((node) => !(isCodeBlock(node) && codeBlockSkipsExecution(node)))
);
```

节点类型判断工具函数（utils.ts）：

| 函数 | 判断条件 |
|------|---------|
| `isCodeBlock(node)` | `node.type === 'block' && node.kind === NotebookCell.code` |
| `isInlineExpression(node)` | `node.type === 'inlineExpression'` |
| `codeBlockRaisesException(node)` | `node.data.tags` 包含 `raises-exception` |
| `codeBlockSkipsExecution(node)` | `node.data.tags` 包含 `skip-execution` |

## 执行控制：错误处理

`computeExecutableNodes()` 中的错误处理逻辑：

1. **Code block 错误**：检查 `codeBlockRaisesException(node)`（即是否标记 `raises-exception` 标签）
   - 如果 `status === 'error'` 且未标记 raises-exception → 调用 fileError 报告错误，设置 errorOccurred=true，break 终止执行
   - 如果标记了 raises-exception → 错误输出被正常收集，继续执行后续单元
2. **Inline expression 错误**：任何 error 状态都导致终止（内联表达式通常不预期抛出异常）
3. 错误信息从 traceback 数组拼接，通过 vfile 的 fileError 记录

```ts
if (status === 'error' && !allowErrors) {
  const errorMessage = outputs
    .map((item) => item.traceback)
    .flat()
    .join('\n');
  fileError(opts.vfile, `An exception occurred...`, { node: matchedNode, ruleId: RuleId.codeCellExecutes });
  errorOccurred = true;
  break;
}
```

## 服务器生命周期管理

manager.ts 提供两个函数管理本地 Jupyter Server：

| 函数 | 用途 |
|------|------|
| `findExistingJupyterServer(session)` | 通过 `python -m jupyter_server list --json` 查找已运行的服务器，fetch 检测存活 |
| `launchJupyterServer(contentPath, log)` | spawn 新的 Jupyter Server 进程，自动获取空闲端口，从 stderr 提取 URL 和 token |

`launchJupyterServer` 返回的 settings 对象包含 `dispose()` 方法，调用 `killProcessTree(proc)` 终止服务器进程树。

## 相关概念

- [00-execution-architecture.md](/concepts/00-execution-architecture.md)：构建时 vs 运行时执行全景
- [02-execution-cache.md](/concepts/02-execution-cache.md)：执行缓存机制
- [01-configure-notebook-execution.md](/examples/01-configure-notebook-execution.md)：配置 kernelspec 和执行选项
