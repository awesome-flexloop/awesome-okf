---
type: Example
title: Map-Reduce 与 Command 控制流示例
description: 使用 Send 实现动态 fan-out 并行处理，用 Command 组合状态更新与路由
tags: [example, map-reduce, send, command, parallel, fanout]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS Examples
---

# Map-Reduce 与 Command 控制流示例

本例演示两个高级模式：

1. **Map-Reduce**：用 `Send` 动态 fan-out 并行处理多个项目，结果通过 reducer 聚合
2. **Command 路由**：节点返回 `Command` 同时更新状态并决定下一步

## Map-Reduce：并行生成笑话

```typescript
import { StateGraph, Annotation, Send, START, END } from "@langchain/langgraph";

// 状态定义
const State = Annotation.Root({
  subjects: Annotation<string[]>({
    reducer: (a, b) => a.concat(b),
    default: () => [],
  }),
  jokes: Annotation<string[]>({
    reducer: (a, b) => a.concat(b),
    default: () => [],
  }),
});

// 条件边：为每个 subject 创建一个 Send（fan-out）
function continueToJokes(state: typeof State.State) {
  return state.subjects.map(
    (subject) => new Send("generate_joke", { subjects: [subject] })
  );
}

// 工作节点：为单个 subject 生成笑话
async function generateJoke(state: { subjects: string[] }) {
  const subject = state.subjects[0];
  // 实际场景中调用 LLM
  const joke = `为什么 ${subject} 要过马路？因为它要并行！`;
  return { jokes: [joke] };
}

// 构建图
const graph = new StateGraph(State)
  .addNode("generate_joke", generateJoke)
  .addConditionalEdges(START, continueToJokes, ["generate_joke"])
  .addEdge("generate_joke", END)
  .compile();

// 执行：两个 subject 并行处理
const result = await graph.invoke({
  subjects: ["猫咪", "程序员"],
});

console.log(result.jokes);
// [
//   "为什么 猫咪 要过马路？因为它要并行！",
//   "为什么 程序员 要过马路？因为它要并行！"
// ]
```

### Send 的工作机制

- `new Send(nodeName, args)` 携带**独立于主图状态**的自定义输入
- 条件边返回 `Send[]` 时，Pregel 在同一超步为每个 `Send` 创建一个并行任务
- 每个任务独立执行，返回值通过 `jokes` 通道的 `reducer`（数组 concat）自动聚合
- `Send` 还支持第三个参数 `{ timeout }` 设置单任务超时

## Command：状态更新与路由合一

传统方式中，条件边决定路由、节点返回值决定状态更新，两者分离。`Command` 让节点自己同时决定两者：

```typescript
import { StateGraph, Annotation, Command, START, END } from "@langchain/langgraph";

const State = Annotation.Root({
  value: Annotation<string>,
  stage: Annotation<string>,
});

function nodeA(state: typeof State.State) {
  const next = Math.random() > 0.5 ? "nodeB" : "nodeC";
  return new Command({
    update: { value: state.value + "|a", stage: `routed-to-${next}` },
    goto: next,
  });
}

function nodeB(state: typeof State.State) {
  return { value: state.value + "|b" };
}

function nodeC(state: typeof State.State) {
  return { value: state.value + "|c" };
}

const graph = new StateGraph(State)
  .addNode("nodeA", nodeA, { ends: ["nodeB", "nodeC"] })
  .addNode("nodeB", nodeB)
  .addNode("nodeC", nodeC)
  .addEdge(START, "nodeA")
  .addEdge("nodeB", END)
  .addEdge("nodeC", END)
  .compile();

await graph.invoke({ value: "" });
// 随机返回 { value: "|a|b", stage: "routed-to-nodeB" }
// 或       { value: "|a|c", stage: "routed-to-nodeC" }
```

### Command 的字段

| 字段 | 作用 |
|---|---|
| `update` | 状态更新（对象或 `[key, value]` 元组数组） |
| `goto` | 下一个节点（节点名、`Send`、或数组） |
| `resume` | 中断恢复值（配合 `interrupt()` 使用） |
| `graph` | 目标图，`Command.PARENT` 表示父图 |

### 子图向父图发命令

在子图节点中返回 `new Command({ graph: Command.PARENT, update: {...}, goto: "parentNode" })` 可突破子图边界控制父图流程。

## Overwrite：绕过 Reducer

当需要直接替换（而非归约）一个有 reducer 的通道值时：

```typescript
import { Overwrite } from "@langchain/langgraph";

function resetNode() {
  return {
    jokes: new Overwrite(["全新开始"]),  // 不 concat，直接替换
  };
}
```

## 结合 HITL（Human-in-the-loop）

`Command` 的 `resume` 字段配合 `interrupt()` 实现人机协作：

```typescript
import { interrupt, Command } from "@langchain/langgraph";

function reviewNode(state) {
  const decision = interrupt({
    question: "是否批准此操作？",
    action: state.proposedAction,
  });

  return new Command({
    update: { approved: decision === "yes" },
    goto: decision === "yes" ? "execute" : "cancel",
  });
}

// 首次调用在 interrupt 处暂停，返回中断信息
const result = await graph.invoke(inputs, config);
// result: { __interrupt__: [{ value: { question: "...", action: "..." } }] }

// 人工审批后恢复
await graph.invoke(
  new Command({ resume: "yes" }),
  config
);
```

## 相关概念

- [状态图与工作流](/langchain-ai/langgraphjs/concepts/state-graph)
- [Pregel 执行引擎](/langchain-ai/langgraphjs/concepts/pregel-execution)
- [Checkpoint 持久化](/langchain-ai/langgraphjs/concepts/checkpointing)
- [Graph 核心 API 参考](/langchain-ai/langgraphjs/references/graph-core)
