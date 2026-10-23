---
type: example
title: "定义自定义工具"
description: "用 defineTool 写一个类型安全的 dsh 工具：schema DSL、execute 主体、render 输出投影、注册与作用域限制、并发与超时声明。"
tags: [deepseek-harness, tool, define-tool, example, plugin-dev]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 docs/cookbook/adding-a-tool.zh.md 与 packages/core/tools
---

# 定义自定义工具

> 场景：给 dsh 加一个自己的工具（比如查内部工单、算一次汇率、跑一条内部 API）。

## 1. 最小实现

```ts
import { defineTool } from '@deepseek-ai/dsh-tools'

export const ticketLookup = defineTool({
  name: 'ticket_lookup',
  description: '按工单号查询内部工单系统，返回标题、状态与负责人。',
  parameters: {
    ticketId: { type: 'string', description: '工单号，形如 TKT-12345' },
  },
  output: {
    schema: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        status: { type: 'string' },
        owner: { type: 'string' },
      },
      required: ['title', 'status'],
    },
    render: (args, value) => [
      { type: 'text', text: `# ${args.ticketId}\n${value.title}\n状态：${value.status}\n负责人：${value.owner ?? '未指派'}` },
    ],
  },
  async execute(args, exec) {
    const res = await fetch(`https://tickets.internal/api/${args.ticketId}`, {
      signal: exec.signal,
    })
    if (!res.ok) {
      throw new Error(`工单服务返回 ${res.status}`)
    }
    return await res.json()
  },
})
```

要点：

- **schema 用 DSL 写**，框架自动推导参数类型（`InferArgs<P>`）——不需要手写 TS 类型
- `execute(args, exec)` 里的 `exec.signal` 是**可取消信号**，必须透传给下游请求
- `output.render` 决定**模型看到什么**；`execute` 的返回值是**规范值**——程序逻辑用后者，模型用前者

## 2. 挂在插件里并注册

```ts
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'my-tools'
export const inject = ['tools']

export function apply(ctx: any, config: any) {
  ctx.tools.register(ticketLookup)

  // 可选：限定该会话可见的工具集合
  ctx.tools.restrict({
    allow: ['ticket_lookup', 'read', 'write', 'bash'],
  })
}
```

- `ctx.tools.register` 是**可信同进程约定**，本身不做沙箱
- `ctx.tools.restrict(filter)` **强制要求 scoped context**（否则会遮蔽所有 agent 的工具），多个限制取**交集**
- 作用域**自身**的注册不受限制约束——被委派的子 agent 保留其依赖工具

## 3. 加载方式

```sh
# 用 --patch 加载本地插件（插件路径必须是绝对路径）
dsh web --patch ./my-plugin/cordis.yml
```

patch 文件形如：

```yaml
- insert:
    - id: my-tools
      name: './index.js'      # 绝对路径
      config: {}
```

> 插件路径必须是**绝对路径**：patch 只贡献配置，不改变 loader 解析模块路径的 profile 目录。

## 4. 更细的控制

### 输出投影与收尾

```ts
export const tool = defineTool({
  // ...
  projectContent(content, exec) {
    // 执行后策略之前安装准备好的内容
    return content
  },
  finalizeContent(content) {
    // 最后的内容不变式
    return content.map((b) => (b.type === 'text' ? { ...b, text: b.text.slice(0, 4000) } : b))
  },
})
```

### 并发与超时

```ts
export const tool = defineTool({
  timeoutMs: 30_000,
  isConcurrencySafe: true,   // 可与其他工具并行
  // ...
})
```

### 呈现层定制

`presentCall` / `presentResult` 用于 UI 展示（而非模型可见内容）。

## 5. 错误与并发语义

- 参数不合法 → `ToolArgsError`（`INVALID_ARGS`）；输出不合法 → `ToolOutputError`（`INVALID_TOOL_OUTPUT`）
- 工具并发上限 `maxParallelToolCalls` 默认 10，在**下一个工具组开始时**读取
- **独占**工具（`ToolExecutionMode = { kind: 'exclusive' }`）需等当前池排空；后到的调用在启动前会**重新分类**
- 结果回填保持**模型顺序**，并行执行不改变顺序

## 6. 完整例子链

1. 工具被调用 → `tool/call` 记录（**记录后执行**）
2. `tools/pre-execute`（瀑布）→ 审批 / 守卫
3. `tools/execute`（瀑布）→ 你的 `execute`
4. `tools/post-execute`（瀑布）→ 内容策略
5. `tools/result`（emit）→ `tool/result`（会话事件，模型可见）

## 相关

- [工具系统](../concepts/06-tool-system.md)
- [写插件与组合包](03-custom-plugin-bundle.md)
- [安全模型](../concepts/09-security-model.md)
