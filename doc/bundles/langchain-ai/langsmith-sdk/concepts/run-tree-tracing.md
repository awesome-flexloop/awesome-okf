---
type: concept
title: RunTree 追踪模型
description: RunTree 如何组织 run 字段、trace_id、dotted_order、父子节点，以及 postRun/patchRun 如何落到 Client API。
tags: [langsmith, run-tree, trace, dotted-order]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: source-core
    resource: /references/source-core.md
    title: langsmith-sdk JS 核心源码索引
---

# RunTree 追踪模型

`RunTree` 是 SDK 在内存中表示一次执行节点的类。它实现 `BaseRun`，保存 name、run type、inputs、outputs、tags、events、parent、children、trace id 和 dotted order。`traceable` 创建和结束 run，`Client` 发送 run，二者之间的数据载体就是 RunTree。

## 核心字段

| 字段 | 含义 |
|---|---|
| `id` | 当前 run 的唯一 ID；未传入时由开始时间生成 UUID7 |
| `name` | run 名称 |
| `run_type` | 运行类型，默认 `chain` |
| `project_name` | 项目名，默认来自 `getDefaultProjectName()` |
| `parent_run` / `parent_run_id` | 父节点对象或父 run id |
| `child_runs` | 内存中的子 RunTree 列表 |
| `inputs` / `outputs` | 输入输出对象 |
| `extra` / `metadata` | metadata 存储在 `extra.metadata` |
| `events` | 运行事件，例如 stream token 事件 |
| `trace_id` | 整条 trace 的根 ID |
| `dotted_order` | 可排序的层级执行顺序串 |
| `attachments` | run 附件 |
| `replicas` | 多项目写入配置 |

`metadata` 的 getter 和 setter 会读写 `extra.metadata`。构造函数会合并显式传入的 `metadata` 与 `extra.metadata`，子节点也会继承父节点 metadata，并让子节点自身 metadata 覆盖同名键。

## ID、trace_id 与 dotted_order

RunTree 构造时按以下规则补齐标识：

1. 如果没有 `id`，用 `_serialized_start_time` 或 `start_time` 生成 UUID7。
2. 如果没有 `trace_id`，有父节点则继承 `parent_run.trace_id ?? this.id`，没有父节点则使用当前 `id`。
3. 如果没有 `dotted_order`，用微秒精度时间串和当前 run id 生成一段 dotted order。
4. 有父节点时，当前 dotted order 为 `parent_run.dotted_order + "." + dottedOrder`；没有父节点时直接使用当前段。

`convertToDottedOrderFormat(epoch, runId, executionOrder)` 返回 `{ dottedOrder, microsecondPrecisionDatestring }`。这让父、子、孙 run 可以通过字符串排序恢复执行顺序，而不需要在客户端维护全局计数器。

## 创建子节点

`createChild(config)` 会设置：

- `parent_run: this`
- `project_name: this.project_name`
- `client: this.client`
- `tracingEnabled: this.tracingEnabled`
- `execution_order` 和 `child_execution_order` 都为父节点 `child_execution_order + 1`
- 子节点 replicas 继承父节点配置，但会去掉父节点的 `reroot`

子节点创建后被推入父节点的 `child_runs`。这解释了为什么 `traceable` 只要拿到当前 RunTree，再调用 `createChild()` 就能把嵌套函数调用连成树。

## 生命周期方法

### end

`end(outputs?, error?, endTime?, metadata?)` 只在字段尚未设置时赋值：`outputs`、`error`、`end_time` 使用首次值，metadata 会合并到 `extra.metadata`。这允许 wrapper 在多个阶段调用 end 相关逻辑而不覆盖已有结果。

### postRun

`postRun(excludeChildRuns = true)` 把 RunTree 转为 `RunCreate`：

- `_convertToCreate()` 写入 `id`、`name`、`start_time`、`run_type`、`extra`、`inputs`、`outputs`、`session_name`、`parent_run_id`、`trace_id`、`dotted_order`、`tags`、`attachments`、`events`。
- 如果配置了 replicas，则对每个 replica 调用 `_remapForProject(...)`，并通过 replica 自己的 client 或当前 client 调 `createRun()`。
- 否则直接调用 `this.client.createRun(runCreate)`。
- 方法最后清空 `child_runs`。

`postRun()` 内部捕获并打印错误，不会把错误继续抛给被追踪函数。

### patchRun

`patchRun(options?)` 构造 `RunUpdate` 并调用 `this.client.updateRun(this.id, runUpdate)`。默认是否包含 inputs 由 `getExcludeInputsOnPatch()` 控制；如果 inputs 被排除，update payload 中不会出现 `inputs` 字段，避免 create/update 批量合并时覆盖已创建的输入。

replicas 存在时，patch 会分别构造每个项目的 update payload，并合并 replica 的 `updates` 字段。

## Replicas：同一 run 写多项目

`WriteReplica` 支持为同一 run 指定额外的 `projectName`、`apiUrl`、`apiKey`、`workspaceId`、`updates` 和独立 `client`。RunTree 在 post/patch 时通过 `_remapForProject(...)` 处理 reroot 与 deterministic id remapping。

这使得一次执行可以同时写入主项目和镜像项目，而调用方不需要手动复制 run tree。

## 与 schema 的对应关系

RunTree 的内存模型对应 `schemas.ts` 中的三层类型：

- `BaseRun`：name、run_type、inputs、outputs、trace_id、dotted_order 等通用字段。
- `RunCreate`：在 `BaseRun` 上增加 `session_name`、`revision_id`、嵌套 `child_runs`。
- `RunUpdate`：所有字段可选，用于结束 run、写 outputs/error/events/tags。

## 手动使用 RunTree

```ts
import { Client, RunTree } from "langsmith";

const client = new Client();
const parent = new RunTree({ name: "parent", client });
const child = parent.createChild({ name: "child", inputs: { x: 1 } });

child.outputs = { doubled: 2 };
await child.postRun();
await child.patchRun();

parent.outputs = { ok: true };
await parent.postRun();
await parent.patchRun();
await client.awaitPendingTraceBatches();
```

多数场景不需要手动管理 RunTree；`traceable` 会自动完成这些步骤。手动 RunTree 更适合框架集成、测试或需要精确控制上报时机的场景。

## 相关概念

- [traceable 装饰器](/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md)
- [SDK 总览](/langchain-ai/langsmith-sdk/concepts/overview.md)
- [评测运行器](/langchain-ai/langsmith-sdk/concepts/evaluation.md)
- [核心源码参考](/langchain-ai/langsmith-sdk/references/source-core.md)
