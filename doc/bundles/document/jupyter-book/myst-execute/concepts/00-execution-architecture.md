---
type: concept
title: "执行架构：构建时 vs 运行时"
description: "理解 myst-execute 的构建时预执行与 thebe 的运行时交互执行两种模式的架构分工、数据流和适用场景"
tags: [myst-execute, thebe, architecture, build-time, runtime]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-execute-src.md"
    facts: [F-001, F-004, F-010, F-015, F-034, F-035]
  - path: "/references/thebe-core-src.md"
    facts: [F-005, F-051, F-053, F-057]
  - path: "/references/thebe-lite-src.md"
    facts: [F-071, F-074]
---

# 执行架构：构建时 vs 运行时

MyST 生态中有两种截然不同的代码执行机制，分别服务于不同阶段和场景：**myst-execute** 负责构建时预执行，**thebe** 负责运行时交互式执行。理解二者的分工是掌握 MyST 可执行文档能力的基础。

## 两种执行模式对比

| 维度 | myst-execute（构建时） | thebe（运行时） |
|------|----------------------|----------------|
| 执行时机 | `myst build` 构建过程中 | 读者在浏览器中点击"运行"按钮时 |
| 运行环境 | 本地 Python/Jupyter Server（构建机器） | Binder 远程服务器、本地 Jupyter Server、或浏览器内 Pyodide |
| 执行结果 | 预计算输出缓存到磁盘（JSON/ipynb），嵌入静态 HTML | 实时输出到浏览器 DOM |
| 交互性 | 无交互（结果固定） | 完全交互（可修改代码重新运行） |
| 内核管理 | SessionManager 自动启动/关闭内核（finally 块 shutdown） | 长连接 Session，支持多次执行 |
| 缓存策略 | MD5 哈希键多级缓存 | localStorage 保存 Binder session 信息 |
| 核心抽象 | unified 插件（kernelExecutionTransform） | ThebeServer → ThebeSession → ThebeNotebook |

## myst-execute：构建时执行管线

myst-execute 作为 unified 插件（`kernelExecutionPlugin`）嵌入 MyST 构建管线。其工作流程：

1. **节点发现**：通过 `getExecutableNodes(tree)` 遍历 MDAST，选出标记为 `kind=code` 的 block 节点和 `inlineExpression` 节点，过滤掉标记 `skip-execution` 的节点
2. **缓存检查**：基于 kernelspec 名称 + 代码内容 + raises-exception 标志 + 环境变量计算 MD5 缓存键，检查本地磁盘缓存
3. **内核启动**：缓存未命中时，通过 SessionFactory 创建 Jupyter SessionManager，`createKernelConnection()` 启动内核（10秒超时，最多重试3次）
4. **顺序执行**：`computeExecutableNodes()` 按文档顺序逐 cell 执行 code block 和 inline expression，遇到未标记 raises-exception 的错误立即终止
5. **输出写回**：`applyComputedOutputsToNodes()` 将 Jupyter IOPub 消息转换为 MDAST output 节点（`jupyter_data` 字段），inline expression 结果写入 `node.result`
6. **缓存写入**：执行成功后将结果写入缓存（NotebookExecutionCache 存为 ipynb 格式），finally 块确保内核 shutdown

```
MDAST 树 → getExecutableNodes() → [CodeBlock, InlineExpression, ...]
                                           ↓
                                    缓存键计算（MD5）
                                           ↓
                                    ┌─ 命中 → applyComputedOutputsToNodes() → 完成
                                    │
                                    └─ 未命中 → createKernelConnection()
                                                      ↓
                                              computeExecutableNodes()
                                                      ↓
                                              applyComputedOutputsToNodes()
                                                      ↓
                                              cache.set() → session.shutdown()
```

## thebe：运行时交互执行

thebe 在浏览器端运行，提供三种服务器连接模式：

1. **Binder 连接**（`connectToServerViaBinder()`）：通过 EventSource/SSE 连接 mybinder.org 等 BinderHub 服务，等待远程环境构建完成后获取 Jupyter Server 地址
2. **直连 Jupyter**（`connectToJupyterServer()`）：直接连接已运行的 Jupyter Server（如本地 `jupyter lab` 启动的服务器），通过 WebSocket 与内核通信
3. **JupyterLite/Pyodide**（`connectToJupyterLiteServer()`）：在浏览器内通过 WebAssembly 运行 Pyodide 内核，无需任何远程服务器

连接建立后，ThebeSession 管理内核会话，ThebeNotebook/ThebeCodeCell 负责单元格的执行请求和输出渲染（基于 JupyterLab 的 rendermime 注册表）。

```
浏览器                                          执行环境
  │                                                │
  ├─ ThebeServer.connectTo*()                       │
  │    ├─ Binder: SSE → 等待构建 → WebSocket ──→ BinderHub Jupyter
  │    ├─ Direct: WebSocket ───────────────────→ 本地 Jupyter
  │    └─ Lite:   WebWorker Pyodide ──→ （浏览器内）
  │                                                │
  ├─ ThebeSession(startNewSession)                  │
  │    └─ Kernel.IKernelConnection                 │
  │                                                │
  ├─ ThebeCodeCell.execute(code)                    │
  │    └─ kernel.requestExecute() → IOPub 消息 ──→ 内核执行
  │                                                │
  └─ PassiveCellRenderer.render(outputs)            │
       └─ IRenderMimeRegistry 渲染 MIME bundle      │
```

## 数据契约：jupyter_data 格式

两种执行模式的输出通过共同的格式约定衔接：

```ts
// myst-execute 写入 MDAST 的 output 节点
{
  type: 'output',
  children: [],
  jupyter_data: {
    output_type: 'execute_result' | 'display_data' | 'stream' | 'error',
    data?: { 'text/plain': '...', 'text/html': '...', ... },  // MIME bundle
    text?: string,    // stream 输出
    traceback?: string[],  // error 回溯
    ...
  }
}
```

thebe 运行时执行产生的 IOutput 对象（@jupyterlab/nbformat 格式）与 jupyter_data 存储的格式一致，这意味着：
- myst-execute 预计算的输出可以被 thebe 的渲染组件直接显示
- 用户点击"运行"后，新的输出会替换预计算输出

## 适用场景

- **myst-execute 适合**：教程文档、可复现论文、数据分析报告——代码和数据稳定，每次构建结果一致，读者不需要修改代码
- **thebe 适合**：交互式教学、在线实验、演示文档——读者需要修改参数、即时看到结果
- **二者结合**：构建时预执行提供初始输出（读者即使不启动内核也能看到结果），thebe 提供可选的"启动交互"按钮供需要动手的读者使用

## 相关概念

- [01-myst-execute-kernel.md](01-myst-execute-kernel.md)：myst-execute 内核连接和执行机制详解
- [02-execution-cache.md](02-execution-cache.md)：构建时缓存系统设计
- [03-thebe-core-api.md](03-thebe-core-api.md)：thebe 核心 API 链式调用
- [05-thebe-binder.md](05-thebe-binder.md)：Binder 远程连接机制
- [06-thebe-lite-pyodide.md](06-thebe-lite-pyodide.md)：Pyodide 无服务器执行
