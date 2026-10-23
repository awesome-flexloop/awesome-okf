---
type: concept
title: "工具系统——注册表、作用域与执行流水线"
description: "dsh 工具系统：defineTool 的类型安全定义、作用域化注册与限制（restrict/guard）、三段瀑布执行流水线、工具结果的一等地位与并发调度。"
tags: [deepseek-harness, tools, define-tool, scope, waterfall, sandbox]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 packages/core/tools 与 docs/tool-execution-pipeline
---

# 工具系统：注册表、作用域与执行流水线

## 1. defineTool：类型安全的工具定义

```ts
import { defineTool } from '@deepseek-ai/dsh-tools'
```

- Schema DSL：`ValueSchemaSpec`（string / number / integer / boolean / null / array / object / json / oneOf）
- 类型推导：`InferValue<S>` 精确到 16 层容器后回落 `JsonValue`；`InferArgs<P>` 给出参数类型
- 转换器：`valueSchemaSpecToJsonSchema()` / `parameterSchemaSpecToJsonSchema()`
- 校验错误：`ToolArgsError`（`INVALID_ARGS`）、`ToolOutputError`（`INVALID_TOOL_OUTPUT`）

`ToolDefinition` 的关键成员：

| 成员 | 作用 |
|---|---|
| `output` | `ToolOutputDefinition`：`schema` + `render(args, value): ContentBlock[]` + 可选 `presentationMeta` |
| `execute(args, exec)` | 工具主体 |
| `projectContent?` | 执行后策略之前安装准备好的内容 |
| `finalizeContent?` | 最后的内容不变式 |
| `timeoutMs?` / `isConcurrencySafe?` | 执行约束 |
| `presentCall?` / `presentResult?` | 呈现层定制 |

> **规范值 vs 模型可见内容**：程序逻辑看到的是规范值；模型看到的是 `render` 产出的 ContentBlock。替换内容不改变规范值——这是"策略可以改写给模型看的输出，但不改事实"的实现方式。

## 2. 作用域化注册

注册表服务是 `ToolRuntime extends Service`（`ctx.tools`）：

```ts
ctx.tools.register(definition)   // 注册
ctx.tools.restrict(filter)       // 限制（强制要求 scoped context）
ctx.tools.guard(guard)           // 单调守卫
ctx.tools.get(name, scope)       // 按作用域取
```

- `restrict()` 强制要求 scoped context，否则抛错（"a context-global restriction would mask every agent"）；也禁止命名保留的 PTC 传输 `RUN_CODE_NAME`，并拒绝未知全局工具名
- `ToolRestriction = { allow?: string[]; deny?: string[] }`；**多个限制取交集**；仅 deny 的过滤器允许未列出的继承工具通过
- **作用域自身的注册不受约束**——被委派的子 agent 保留其依赖工具
- 作用域原语库在 `packages/core/scope`：`createScope()` / `scopeOf()` / `bindScopeParent()` 等；`ScopedLayers` 持有"立即构造的全局层 + 惰性创建的精确作用域层"，读取不创建层

> ⚠️ `ctx.tools.register` 是**可信同进程约定**，本身不做沙箱；作用域能力由 `dsh-scope` 提供，但**不是权限边界**。真正的边界见 [安全模型](09-security-model.md)。

## 3. 执行流水线

```text
tool/call（记录后执行）
 → tools/pre-execute（水瀑布：allow / deny / ask）
 → ctx.approval（一次性批准；不可答 → deny）
 → 已注册单调守卫（deny 或 abstain；身份受保护）
 → tools/execute（水瀑布：环绕分发，包装 timeout/retry/metrics）
 → 工具 execute() 主体 → fs/write-intent | fs/edit-intent → 工具自有事件
 → ToolDefinition.projectContent
 → tools/post-execute（水瀑布：accept / block / replace / add context）
 → 注册表外层归一化（快照失败 → isError）
 → ToolDefinition.finalizeContent
 → tools/result（同步通知，冻结的权威结果）
 → tool/result（会话事件，单一模型可见结果）
 → Active-batch additionalContexts FIFO（在已记录的工具结果之后注入 user/message）
```

事件签名与派发模式：

| 事件 | 模式 | 返回 |
|---|---|---|
| `tools/pre-execute` | waterfall | `PreToolDecision` |
| `tools/execute` | waterfall | `ToolExecutionResult`（**只有此视图可替换必需的 signal**） |
| `tools/post-execute` | waterfall | `PostToolDecision` |
| `tools/ptc-dispatch-log` | waterfall | — |
| `tools/result` | emit | 仅观测冻结结果 |
| `tools/change` | emit | 注册表主题通知（**非作用域过滤**） |

**单调守卫**：`ToolGuard = (execution) => string | undefined`，返回理由即拒绝，**后续监听器无法把拒绝改回允许**。这是"策略只减不增"的实现点。

## 4. tool/call 与 tool/result

```ts
tool/call   { turn, step, callId: ToolCallId, name: string, arguments: string }
tool/result { turn, step, message: ToolResultMessage, error?: {name, code, reason?}, meta?: JsonValue }
```

- `arguments` 是模型产出的**原始未解析 JSON 字符串**
- `error` **仅当** `message.isError === true` 时允许
- `meta` 必须 JSON 可序列化（`Session.append` 用 `isJsonValue` 运行时校验）

工具结果是**一等 `ToolResultMessage`**，不是 ContentBlock。

## 5. 并发与顺序

- 调度上限 `maxParallelToolCalls` 默认 **10**，在**下一个工具组开始时**读取（volatile 配置字段）
- 后到的调用在启动前会**重新分类**；独占重分类需等当前池排空
- **策略、持久结果与结果上下文保持模型顺序（model order）**——并行执行不改变结果回填的顺序

## 6. 工具体系全景

工具目录由 `scripts/gen-tool-catalog.ts` **实际启动**每个工具插件并读取 `ctx.tools.schemas()` 生成（`docs/tool-catalog.zh.md`），当前为 **33 个工具包 / 68 个唯一模型可见工具名**。主要分类：

| 类别 | 代表工具 |
|---|---|
| 文件与代码编辑 | `read`、`write`、`edit`、`read_image`、`str_replace_editor`、`glob`、`grep` |
| Shell 与进程 | `bash`、`pwsh`（含持久版）、`terminal_open/read/send/...` |
| 委派与编排 | `subagent`、`send_message`、`interrupt_agent`、`list_agents`、`workflow`、`ralph` |
| 导航与语义 | `lsp`、`web_search`、`web_fetch` |
| 状态与计划 | `todo_write`、`working_directory`、`create_goal`、`exit_plan_mode` |
| 任务与提醒 | `job_list`、`job_output`、`job_kill`、`schedule_create/list/update/delete` |
| 交互与外部 | `ask_user_question`、`stagehand_*`、`list_mcp_resources` |
| 平台与自我观测 | `plugin_manager`、`plugin_market`、`run_code`、`cordis_inspect_*`、`session_search`/`session_trace` |

## 下一步

- [写自定义工具实战](../examples/02-custom-tool.md)
- [安全模型](09-security-model.md)——沙箱与审批怎么插进这条流水线
