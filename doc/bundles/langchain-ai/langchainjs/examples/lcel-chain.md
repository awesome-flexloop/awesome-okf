---
type: example
scope: langchainjs
name: lcel-chain
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: 构建 LCEL 链——使用 PromptTemplate、ChatModel、OutputParser 通过 pipe 组合 RAG 管道
---

# 构建 LCEL 链

本示例演示如何使用 LangChain.js 的 LCEL（LangChain Expression Language）通过 `pipe` 组合 Prompt、Model 和 Parser，构建一个可流式、可批处理、自动追踪的处理链。

## 前置条件

- Node.js ≥ 20
- 安装 `@langchain/core` 和至少一个模型 provider 包（如 `@langchain/openai`）

```bash
npm install @langchain/core @langchain/openai
```

## 基础链：Prompt → Model → Parser

最简单的 LCEL 链将提示模板、聊天模型和输出解析器串联：

```typescript
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatOpenAI } from "@langchain/openai";

// 1. 定义提示模板
const prompt = PromptTemplate.fromTemplate(
  "请用中文为以下主题写一个简短的介绍：{topic}"
);

// 2. 创建模型
const model = new ChatOpenAI({ model: "gpt-4o-mini", temperature: 0.7 });

// 3. 创建输出解析器（提取 AIMessage.content 字符串）
const parser = new StringOutputParser();

// 4. 通过 pipe 组合为链
const chain = prompt.pipe(model).pipe(parser);

// 5. 调用
const result = await chain.invoke({ topic: "LangChain.js" });
console.log(result);
```

### 发生了什么

`prompt.pipe(model)` 创建一个 `RunnableSequence`，将 prompt 的输出（PromptValue）自动传给 model。`.pipe(parser)` 再将 model 的输出（AIMessage）传给 parser，parser 提取字符串内容。

因为三个组件都是 `Runnable`，chain 自动获得：
- **invoke**：单次调用
- **batch**：批量并发调用
- **stream**：流式输出 token
- **回调追踪**：自动触发 LangSmith 追踪事件

## 流式输出

```typescript
const stream = await chain.stream({ topic: "人工智能" });

for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

`StringOutputParser` 配合模型的流式能力，逐 token 输出字符串。底层通过 `_streamIterator` 和 `transform` 实现跨 Runnable 的流传播。

## 批量调用

```typescript
const topics = [
  { topic: "向量数据库" },
  { topic: "RAG" },
  { topic: "Agent" },
];

const results = await chain.batch(topics, {
  maxConcurrency: 3,
});

results.forEach((r, i) => {
  console.log(`--- ${topics[i].topic} ---`);
  console.log(r);
});
```

默认实现使用 `AsyncCaller` 控制并发。

## 并行分支：RunnableParallel

使用 `RunnableParallel`（或 `RunnableMap`）并行执行多个链：

```typescript
import { RunnableParallel } from "@langchain/core/runnables";

const jokeChain = PromptTemplate.fromTemplate(
  "讲一个关于{topic}的笑话"
).pipe(model).pipe(parser);

const poemChain = PromptTemplate.fromTemplate(
  "写一首关于{topic}的短诗"
).pipe(model).pipe(parser);

const parallelChain = RunnableParallel.from({
  joke: jokeChain,
  poem: poemChain,
});

const result = await parallelChain.invoke({ topic: "猫" });
console.log(result.joke);
console.log(result.poem);
// { joke: "...", poem: "..." }
```

## 带配置调用

通过 `RunnableConfig` 控制超时、标签、元数据和回调：

```typescript
const result = await chain.invoke(
  { topic: "TypeScript" },
  {
    tags: ["example", "production"],
    metadata: { userId: "123", environment: "dev" },
    timeout: 30000,        // 30 秒超时
    maxConcurrency: 5,
    configurable: {       // 自定义运行时参数
      style: "正式",
    },
  }
);
```

## 使用 withRetry 和 withFallbacks

```typescript
import { AIMessage } from "@langchain/core/messages";

// 重试：失败后最多重试 2 次
const retryingChain = chain.withRetry({ stopAfterAttempt: 3 });

// 回退：主模型失败时使用备用模型
const backupModel = new ChatOpenAI({ model: "gpt-4o" });
const fallbackChain = new PromptTemplate({
  inputVariables: ["topic"],
  template: "简短介绍：{topic}",
}).pipe(backupModel).pipe(parser);

const chainWithFallback = chain.withFallbacks([fallbackChain]);
```

## 函数作为 Runnable

普通函数通过 `RunnableLambda` 自动包装，可以直接 `pipe`：

```typescript
const analyzeChain = prompt
  .pipe(model)
  .pipe(parser)
  .pipe((text: string) => ({
    summary: text.slice(0, 100),
    length: text.length,
    containsKeyword: text.includes("LangChain"),
  }));

const analysis = await analyzeChain.invoke({ topic: "LangChain" });
console.log(analysis);
// { summary: "...", length: 42, containsKeyword: true }
```

## ChatPromptTemplate 与消息历史

```typescript
import {
  ChatPromptTemplate,
  MessagesPlaceholder,
} from "@langchain/core/prompts";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";

const chatPrompt = ChatPromptTemplate.fromMessages([
  new SystemMessage("你是一个有帮助的助手，用中文回答。"),
  new MessagesPlaceholder("history"),
  ["human", "{input}"],
]);

const chatChain = chatPrompt.pipe(model).pipe(parser);

const reply = await chatChain.invoke({
  history: [
    new HumanMessage("我叫小明"),
    new AIMessage("你好，小明！有什么可以帮你的？"),
  ],
  input: "我叫什么名字？",
});
```

## 关键 API 速查

| API | 来源 | 说明 |
|---|---|---|
| `PromptTemplate.fromTemplate()` | `@langchain/core/prompts` | 从字符串创建提示模板 |
| `ChatPromptTemplate.fromMessages()` | `@langchain/core/prompts` | 创建聊天提示 |
| `MessagesPlaceholder` | `@langchain/core/prompts` | 消息列表占位符 |
| `StringOutputParser` | `@langchain/core/output_parsers` | 提取 AIMessage.content 字符串 |
| `RunnableParallel.from()` | `@langchain/core/runnables` | 并行执行多个 Runnable |
| `.pipe()` | Runnable 方法 | 序列组合 |
| `.withRetry()` | Runnable 方法 | 添加重试 |
| `.withFallbacks()` | Runnable 方法 | 添加回退 |
| `.withConfig()` | Runnable 方法 | 绑定配置 |

## 相关文档

- [Runnable 接口概念](/langchain-ai/langchainjs/concepts/runnable-interface)
- [提示模板概念](/langchain-ai/langchainjs/concepts/prompt-templates)
- [Runnable 核心 API](/langchain-ai/langchainjs/references/core-runnable)
- [创建 ReAct Agent 示例](/langchain-ai/langchainjs/examples/react-agent)
