---
type: concept
scope: langchainjs
name: middleware
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js Middleware 系统——Agent 横切关注点的钩子织入、洋葱模型与内置中间件
---

# Middleware 系统

## 为什么需要 Middleware

ReAct Agent 的核心循环很简单：模型决策 → 工具执行 → 模型决策 → ...直到完成。但生产环境需要大量横切关注点：

- 人类审批（HITL）
- PII 检测与脱敏
- 工具调用次数限制
- 模型失败重试与回退
- 上下文摘要压缩
- 动态系统提示
- TODO 列表管理

如果通过继承 `ReactAgent` 来实现这些功能，会导致类爆炸和脆弱的继承链。LangChain.js 的解法是 **Middleware 系统**：将这些横切关注点实现为独立的中间件，通过钩子（hook）织入 Agent 的图拓扑。

## 核心接口

**源码位置**：`agents/middleware/types.ts`

```typescript
interface AgentMiddleware<TSchema, TContextSchema, ...> {
  name: string;
  stateSchema?: StateDefinitionInit;
  contextSchema?: InteropZodObject;
  tools?: readonly (ClientTool | ServerTool)[];
  streamTransformers?: ReadonlyArray<() => StreamTransformer>;

  beforeAgent?: BeforeAgentHook;
  beforeModel?: BeforeModelHook;
  afterModel?: AfterModelHook;
  afterAgent?: AfterAgentHook;
  wrapModelCall?: WrapModelCallHook;
  wrapToolCall?: WrapToolCallHook;
}
```

### 六个钩子

| 钩子 | 执行时机 | 执行次数 | 图节点 |
|---|---|---|---|
| `beforeAgent` | Agent 启动时 | 一次 | `${name}.before_agent` |
| `beforeModel` | 每次模型调用前 | 循环内多次 | `${name}.before_model` |
| `afterModel` | 模型调用后 | 循环内多次（逆序） | `${name}.after_model` |
| `afterAgent` | Agent 结束时 | 一次 | `${name}.after_agent` |
| `wrapModelCall` | 包装模型调用 | 每次模型调用 | 注入 AgentNode 内部 |
| `wrapToolCall` | 包装工具调用 | 每次工具调用 | 注入 ToolNode 内部 |

### 钩子返回值

`MiddlewareResult<TState>`（types.ts:135）：

```typescript
type MiddlewareResult<TState> =
  | (TState & { jumpTo?: JumpToTarget })
  | void;
```

- 返回 `void` 或 `undefined`：不修改状态，继续默认流程
- 返回部分状态对象：合并到 Agent 状态
- 返回 `{ jumpTo: "model_request" | "tools" | "end" }`：控制流跳转

## 图织入机制

ReactAgent 构造函数（`ReactAgent.ts:304-377`）遍历 middleware 数组，为每个有钩子的 middleware 创建独立图节点：

```typescript
for (let i = 0; i < middleware.length; i++) {
  const m = middleware[i];
  if (m.beforeAgent) {
    const node = new BeforeAgentNode(m);
    workflow.addNode(`${m.name}.before_agent`, node);
    beforeAgentNodes.push({ index: i, name, ... });
  }
  if (m.beforeModel) { /* 创建 BeforeModelNode */ }
  if (m.afterModel) { /* 创建 AfterModelNode */ }
  if (m.afterAgent) { /* 创建 AfterAgentNode */ }
  if (m.wrapModelCall) { wrapModelCallHookMiddleware.push(m); }
}
```

### 节点连接顺序

- **beforeAgent / beforeModel**：按 middleware 数组顺序**正序**连接
- **afterModel**：**逆序**连接（`ReactAgent.ts:529`），形成洋葱模型的返回路径
- **afterAgent**：按数组顺序正序连接

这种设计使得：
- `beforeModel` 中 A 先于 B 执行
- `afterModel` 中 B 先于 A 执行
- 形成 A → B → 模型 → B' → A' 的洋葱环绕

### 条件路由

每个钩子节点可以声明 `allowed` 跳转目标（通过 `getHookConstraint` 获取）。当声明了 allowed 时，使用条件边而非普通边，允许钩子通过 `jumpTo` 跳转到指定目标：

```typescript
if (node.allowed && node.allowed.length > 0) {
  workflow.addConditionalEdges(
    current,
    createRouter(...),
    destinations
  );
} else {
  workflow.addEdge(current, nextDefault);
}
```

跳转到 `TOOLS_NODE_NAME` 时会检查是否有可用工具（`hasToolsAvailable`），无工具时该目标被过滤。

## wrapModelCall 与 wrapToolCall

这两个钩子不创建独立图节点，而是作为**包装器**注入到 AgentNode/ToolNode 内部：

- `wrapModelCall`：包装模型调用，可修改请求、缓存结果、实现限流等。多个 wrapModelCall middleware 按嵌套顺序包装
- `wrapToolCall`：包装工具执行，可实现工具重试、错误处理、参数修改等。通过 `wrapToolCall(middleware)` 函数组合后传入 ToolNode

## createMiddleware 工厂

**源码位置**：`agents/middleware.ts:76`

推荐使用 `createMiddleware` 创建中间件，它提供自动 schema 推断：

```typescript
import { createMiddleware } from "langchain";

const authMiddleware = createMiddleware({
  name: "AuthMiddleware",
  stateSchema: z.object({
    isAuthenticated: z.boolean().default(false),
  }),
  beforeModel: async (state) => {
    if (!state.isAuthenticated) {
      throw new Error("未认证");
    }
  },
});
```

支持 Zod schema 或 LangGraph `StateSchema` 作为 stateSchema。

## 内置 Middleware

`agents/middleware/index.ts` 导出丰富的内置中间件：

### 核心中间件

| 中间件 | 工厂 | 用途 |
|---|---|---|
| HITL | — | 人类在环审批，在关键节点暂停等待人工确认 |
| Summarization | `summarizationMiddleware` | 当上下文过长时自动摘要压缩历史消息 |
| Dynamic System Prompt | `dynamicSystemPromptMiddleware` | 根据状态动态生成系统提示 |
| LLM Tool Selector | `llmToolSelectorMiddleware` | 用 LLM 从大量工具中选择相关工具子集 |
| Context Editing | `contextEditingMiddleware` | 编辑/清理对话上下文，如删除旧工具调用 |
| TODO List | `todoListMiddleware` | 维护任务列表，引导模型按计划执行 |

### 安全与合规

| 中间件 | 工厂 | 用途 |
|---|---|---|
| PII | `piiMiddleware` | 检测邮件、信用卡、IP、MAC、URL 等 PII |
| PII Redaction | `piiRedactionMiddleware` | 自动脱敏检测到的 PII |
| OpenAI Moderation | `openAIModerationMiddleware` | OpenAI 内容审核 |

### 限流与容错

| 中间件 | 工厂 | 用途 |
|---|---|---|
| Tool Call Limit | `toolCallLimitMiddleware` | 限制总工具调用次数，超限抛出 `ToolCallLimitExceededError` |
| Model Call Limit | `modelCallLimitMiddleware` | 限制模型调用次数 |
| Model Retry | `modelRetryMiddleware` | 模型调用失败自动重试 |
| Model Fallback | `modelFallbackMiddleware` | 模型失败时切换到备用模型 |
| Tool Retry | `toolRetryMiddleware` | 工具调用失败自动重试 |
| Tool Error | `toolErrorMiddleware` | 自定义工具错误处理逻辑 |
| Tool Emulator | `toolEmulatorMiddleware` | 模拟工具调用（用于测试） |

### Provider 特定

| 中间件 | 工厂 | 用途 |
|---|---|---|
| Anthropic Prompt Caching | `anthropicPromptCachingMiddleware` | Anthropic 提示缓存优化 |
| Bedrock Prompt Caching | `bedrockPromptCachingMiddleware` | AWS Bedrock 提示缓存 |
| Provider Tool Search | `providerToolSearchMiddleware` | Provider 端工具搜索 |

## Middleware 状态合并

每个 middleware 可通过 `stateSchema` 定义自己的状态字段。`createAgentState`（`annotation.ts:24`）负责合并：

1. 初始化 stateFields，包含内置的 `jumpTo: UntrackedValue`
2. 先应用用户自定义 stateSchema
3. 再按顺序应用每个 middleware 的 stateSchema
4. 重复字段跳过（先到先得）
5. 下划线前缀字段为私有，不暴露为输入/输出通道

这允许 middleware 透明地添加自己的状态（如 TODO 列表、计数器、标志位），无需用户手动管理。

## 工具注册

Middleware 可通过 `tools` 字段注册额外工具：

```typescript
const middleware = createMiddleware({
  name: "MyMiddleware",
  tools: [tool1, tool2],
  beforeModel: async (state) => { ... },
});
```

ReactAgent 构造函数（`ReactAgent.ts:225-228`）自动收集 middleware 工具，与 `options.tools` 合并：

```typescript
const middlewareTools = middleware
  .filter((m) => m.tools)
  .flatMap((m) => m.tools);
const toolClasses = [...(options.tools ?? []), ...middlewareTools];
```

## 相关文档

- [ReAct Agent](/langchain-ai/langchainjs/concepts/react-agent) — Agent 图拓扑
- [工具定义](/langchain-ai/langchainjs/concepts/tool-definition) — middleware 工具注册
- [Agent 与 Middleware API](/langchain-ai/langchainjs/references/agents-middleware) — API 参考
- [创建 ReAct Agent 示例](/langchain-ai/langchainjs/examples/react-agent)
