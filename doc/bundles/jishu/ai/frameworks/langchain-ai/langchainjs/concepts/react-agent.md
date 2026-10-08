---
type: concept
scope: langchainjs
name: react-agent
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js ReactAgent——基于 LangGraph StateGraph 的 ReAct Agent 编排与图拓扑
---

# ReAct Agent

## ReAct 模式

ReAct（Reasoning + Acting）是一种 Agent 范式，模型在推理（Reasoning）和行动（Acting）之间交替：模型先思考需要做什么，选择调用工具，观察工具结果，再继续思考，直到得出最终答案。

LangChain.js 的 `ReactAgent`（`agents/ReactAgent.ts:164`）是这一范式的生产级实现，它不是一个简单的 while 循环，而是编译为 LangGraph `StateGraph`，获得状态持久化、流式传输、检查点、中断恢复等图执行能力。

## 创建 Agent

通过 `createAgent` 工厂（`agents/index.ts:672`）创建：

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

const search = tool(
  async ({ query }) => `搜索结果: ${query}`,
  {
    name: "search",
    description: "搜索网络获取信息",
    schema: z.object({ query: z.string() }),
  }
);

const agent = createAgent({
  model: "openai:gpt-4o",
  tools: [search],
  systemPrompt: "你是一个有帮助的研究助手",
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "LangChain 是什么？" }],
});
```

## 图拓扑结构

ReactAgent 内部构建的 StateGraph 拓扑如下（`ReactAgent.ts:257-550`）：

```
                         ┌─────────────────┐
                   START │ beforeAgent[0]  │  (仅执行一次)
                         └────────┬────────┘
                                  ↓
                         ┌─────────────────┐
                         │ beforeAgent[n]  │
                         └────────┬────────┘
                                  ↓
    ┌─────────────────────────────────────────────┐
    │  (循环入口)                                   │
    │         ┌─────────────────┐                  │
    │         │ beforeModel[0]  │                  │
    │         └────────┬────────┘                  │
    │                  ↓                           │
    │         ┌─────────────────┐                  │
    │         │ beforeModel[n]  │                  │
    │         └────────┬────────┘                  │
    │                  ↓                           │
    │         ┌─────────────────┐                  │
    │         │   AgentNode     │ ← 模型调用       │
    │         │  (model_request)│                  │
    │         └────────┬────────┘                  │
    │                  ↓                           │
    │         ┌─────────────────┐                  │
    │         │ afterModel[n]   │ (逆序执行)       │
    │         └────────┬────────┘                  │
    │                  ↓                           │
    │         ┌─────────────────┐                  │
    │         │ afterModel[0]   │                  │
    │         └────────┬────────┘                  │
    │                  ↓                           │
    │     有 tool_calls?                           │
    │      ├─ 是 → ToolNode → 回到循环入口 ────────┤
    │      └─ 否                                    │
    └────────────────┬─────────────────────────────┘
                     ↓
            ┌─────────────────┐
            │ afterAgent[0]   │  (仅执行一次)
            └────────┬────────┘
                     ↓
            ┌─────────────────┐
            │ afterAgent[n]   │
            └────────┬────────┘
                     ↓
                    END
```

### 两个核心节点

- **AgentNode**（`nodes/AgentNode.ts`）：绑定工具到模型、注入系统提示、处理 `wrapModelCall` middleware、调用模型。模型返回 AIMessage。
- **ToolNode**（`nodes/ToolNode.ts`）：遍历 AIMessage 的 `tool_calls`，并行执行对应工具，为每个调用生成 ToolMessage。支持 `wrapToolCall` middleware 包装。

### 路由决策

AgentNode 执行后，根据 AIMessage 是否包含 `tool_calls` 条件路由：
- 有 tool_calls → 路由到 `TOOLS_NODE_NAME`（"tools"）
- 无 tool_calls → 路由到出口（afterAgent 或 END）

ToolNode 执行后，无条件回到循环入口（beforeModel 或 AgentNode），开始下一轮推理。

### 可跳转目标

`BaseGraphDestination`（`ReactAgent.ts:94`）限制 middleware 的 `jumpTo` 只能跳转到三个目标：

```typescript
type BaseGraphDestination =
  | typeof TOOLS_NODE_NAME   // "tools"
  | typeof AGENT_NODE_NAME   // "model_request"
  | typeof END;
```

## 状态管理

### createAgentState

**源码位置**：`agents/annotation.ts:24`

Agent 状态由 `createAgentState` 函数生成，合并三个来源：

1. **内置状态**：
   - `messages: MessagesValue` — 对话消息列表，使用消息 reducer 自动追加而非替换
   - `jumpTo: UntrackedValue` — 瞬态控制流信号，不参与检查点
2. **用户自定义 stateSchema**
3. **Middleware 的 stateSchema**

生成三个 StateSchema：
- **state**：完整状态（含私有字段），用于图执行
- **input**：输入通道（仅非私有字段）
- **output**：输出通道（仅非私有字段 + structuredResponse）

### 私有状态

下划线前缀的字段（如 `_internal`）持久化在 state 中，但不暴露为输入/输出通道。适用于 middleware 内部使用的中间状态。

### Reducer

状态字段可以使用 `ReducedValue` 定义自定义合并逻辑：

```typescript
import { StateSchema, ReducedValue } from "@langchain/langgraph";
import { z } from "zod";

const AgentState = new StateSchema({
  count: z.number().default(0),
  history: new ReducedValue(
    z.array(z.string()).default([]),
    {
      inputSchema: z.string(),
      reducer: (current, next) => [...current, next],
    }
  ),
});
```

Zod v4 schema 还可通过 `schemaMetaRegistry` 声明 reducer，自动包装为 ReducedValue。

## 结构化输出

通过 `responseFormat` 参数获取类型化响应：

```typescript
const ContactInfo = z.object({
  name: z.string(),
  email: z.string(),
  phone: z.string(),
});

const agent = createAgent({
  model: "openai:gpt-4o",
  responseFormat: ContactInfo,
});

const result = await agent.invoke({ messages: [...] });
console.log(result.structuredResponse);
// { name: "...", email: "...", phone: "..." }
```

`responseFormat` 支持多种形式（13个重载）：Zod schema、Zod schema 数组（联合类型）、JSON Schema、`ToolStrategy`、`ProviderStrategy` 等。

## 系统提示

`systemPrompt` 支持三种形式：

1. **字符串**：静态系统提示
2. **SystemMessage**：消息实例
3. **函数**：`(state) => string | SystemMessage | Promise<...>`，根据状态动态生成

## 流式传输

Agent 支持多种 streamMode：

```typescript
const stream = await agent.stream(
  { messages: [{ role: "user", content: "你好" }] },
  { streamMode: "values" }
);

for await (const chunk of stream) {
  console.log(chunk.messages);
}
```

还支持 `streamEvents` 获取更细粒度的事件（模型 token、工具开始/结束等）。

## 类型袋模式

`ReactAgent` 的泛型参数 `Types extends AgentTypeConfig` 将六个类型参数捆绑为一个类型袋：

```typescript
interface AgentTypeConfig<Response, State, Context, Middleware, Tools, StreamTransformers> {
  Response: Response;
  State: State;
  Context: Context;
  Middleware: Middleware;
  Tools: Tools;
  StreamTransformers: StreamTransformers;
}
```

幻影属性 `"~agentTypes"`（`ReactAgent.ts:179`）允许从实例类型中提取这些类型参数。这使得 `createAgent` 的重载可以精确推断 middleware 注入的状态字段和工具名称联合类型，同时避免泛型参数列表爆炸。

## 相关文档

- Middleware — Agent 横切扩展系统
- 消息系统 — AIMessage 与 ToolMessage
- 工具定义 — 工具创建
- Agent 与 Middleware API — API 参考
- 创建 ReAct Agent 示例
