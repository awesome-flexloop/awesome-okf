---
type: Example
title: 基础 ReAct Agent 示例
description: 使用 StateGraph、MessagesAnnotation 和工具节点构建一个可持久化的 ReAct Agent
tags: [example, agent, react, tools, getting-started]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Examples
---

# 基础 ReAct Agent 示例

本例演示如何用 LangGraphJS 构建一个带工具调用、循环执行和持久化的基础 ReAct Agent。

## 完整代码

```typescript
import { StateGraph, MessagesAnnotation, START, END } from "@langchain/langgraph";
import { MemorySaver } from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod/v4";

// 1. 定义工具
const searchTool = tool(
  async ({ query }: { query: string }) => {
    return `搜索结果：关于「${query}」的信息...`;
  },
  {
    name: "search",
    description: "搜索网络信息",
    schema: z.object({ query: z.string() }),
  }
);

const tools = [searchTool];
const toolNode = new ToolNode(tools);

// 2. 绑定工具到模型
const model = new ChatOpenAI({ model: "gpt-4o" }).bindTools(tools);

// 3. 定义路由函数
function shouldContinue(state: typeof MessagesAnnotation.State) {
  const lastMessage = state.messages[state.messages.length - 1];
  if (lastMessage.tool_calls?.length) {
    return "tools";
  }
  return END;
}

// 4. 定义 Agent 节点
async function callModel(state: typeof MessagesAnnotation.State) {
  const response = await model.invoke(state.messages);
  return { messages: [response] };
}

// 5. 构建图
const workflow = new StateGraph(MessagesAnnotation)
  .addNode("agent", callModel)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue, {
    tools: "tools",
    [END]: END,
  })
  .addEdge("tools", "agent");

// 6. 编译并启用持久化
const checkpointer = new MemorySaver();
const agent = workflow.compile({ checkpointer });

// 7. 运行
const config = { configurable: { thread_id: "session-1" } };

const result = await agent.invoke(
  { messages: [{ role: "user", content: "LangGraphJS 是什么？" }] },
  config
);

console.log(result.messages.at(-1)?.content);

// 同线程继续对话（自动加载历史）
const followUp = await agent.invoke(
  { messages: [{ role: "user", content: "它有哪些核心特性？" }] },
  config
);
```

## 关键点说明

### MessagesAnnotation

`MessagesAnnotation` 是预构建的状态定义，等价于：

```typescript
Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),
});
```

`messagesStateReducer`（别名 `addMessages`）智能处理消息 ID——相同 ID 的消息会被更新而非重复追加。

### 循环结构

图形成 `agent → tools → agent` 的循环：

1. `agent` 节点调用 LLM
2. 若 LLM 返回 `tool_calls`，路由到 `tools` 执行
3. `tools` 完成后回到 `agent`，LLM 看到工具结果继续推理
4. 若无工具调用，路由到 `END` 终止

默认递归限制 25 个超步，防止无限循环。

### 持久化

传入 `MemorySaver` 后，每个超步自动 checkpoint。使用相同 `thread_id` 再次调用会自动加载完整消息历史，实现多轮对话记忆。

生产环境可替换为 Postgres、SQLite、Redis 等 checkpointer，代码无需改动。

### 流式输出

将 `invoke` 换为 `stream` 即可获得 token 级流式：

```typescript
for await (const [mode, chunk] of agent.stream(inputs, {
  ...config,
  streamMode: ["messages", "updates"],
})) {
  if (mode === "messages") {
    const [message, metadata] = chunk;
    if (message.content) process.stdout.write(message.content);
  }
}
```

## 相关概念

- [状态图与工作流](/ai/langchain-ai/langgraphjs/concepts/state-graph)
- [Annotation 状态定义](/ai/langchain-ai/langgraphjs/concepts/annotation)
- [Checkpoint 持久化](/ai/langchain-ai/langgraphjs/concepts/checkpointing)
- [Pregel 执行引擎](/ai/langchain-ai/langgraphjs/concepts/pregel-execution)
