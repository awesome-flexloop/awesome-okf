---
type: concept
scope: langchainjs
name: prompt-templates
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js 提示模板——BasePromptTemplate、PromptTemplate、ChatPromptTemplate 与 MessagesPlaceholder
---

# 提示模板

## 提示模板的作用

直接在代码中拼接 LLM 提示字符串容易出错且难以维护。提示模板（Prompt Template）将提示的**结构**与**变量**分离：模板定义固定格式和占位符，运行时填入变量值。

在 LangChain.js 中，所有提示模板都是 `Runnable`，因此可以直接 `pipe` 到模型，享受流式、批处理和回调追踪。

## 类层次

```
Runnable
└── BasePromptTemplate (abstract)
    ├── BaseStringPromptTemplate
    │   └── BaseStringPromptTemplate → PromptTemplate
    └── BaseMessagePromptTemplate (abstract)
        ├── MessagesPlaceholder
        ├── ChatMessagePromptTemplate
        ├── HumanMessagePromptTemplate
        ├── AIMessagePromptTemplate
        ├── SystemMessagePromptTemplate
        └── ChatPromptTemplate (组合容器)
```

## BasePromptTemplate

**源码位置**：`prompts/base.ts:48`

所有提示模板的抽象基类：

```typescript
abstract class BasePromptTemplate<RunInput, RunOutput, PartialVariableName>
  extends Runnable<RunInput, RunOutput> {
  inputVariables: string[];
  outputParser?: BaseOutputParser;
  partialVariables: PartialValues;

  abstract partial(values: PartialValues): Promise<BasePromptTemplate>;
  async invoke(input: RunInput, options?): Promise<RunOutput>;
}
```

关键设计：
- `lc_serializable = true`，支持序列化
- `lc_namespace = ["langchain_core", "prompts", ...]`
- 构造函数禁止 `inputVariables` 包含 `"stop"`（保留字）
- `invoke` 通过 `_callWithConfig` 调用 `formatPromptValue`，runType 为 `"prompt"`
- `partialVariables` 支持异步函数值（延迟计算），`mergePartialAndUserVariables` 自动 await

## PromptTemplate（字符串模板）

**源码位置**：`prompts/prompt.ts:110`

用于生成纯文本提示，是最简单的模板类型：

```typescript
import { PromptTemplate } from "@langchain/core/prompts";

const prompt = new PromptTemplate({
  inputVariables: ["topic", "style"],
  template: "请用{style}风格写一个关于{topic}的笑话",
});

const text = await prompt.format({ topic: "猫", style: "相声" });
// "请用相声风格写一个关于猫的笑话"
```

### 模板格式

`templateFormat` 支持两种格式（默认 `"f-string"`）：

- **f-string**：使用 `{variable}` 语法，支持校验
- **mustache**：使用 `{{variable}}` 语法，不支持校验

### 静态工厂方法

```typescript
const prompt = PromptTemplate.fromTemplate("讲一个关于{topic}的笑话");
// 自动从模板中提取 inputVariables
```

### template 可以是 MessageContent

`template` 字段类型为 `MessageContent`（`string | ContentBlock[]`），支持多模态内容块（如图片）。

## ChatPromptTemplate（聊天模板）

**源码位置**：`prompts/chat.ts:924`

用于构建多角色的聊天消息列表。它组合多个 `BaseMessagePromptTemplate`，格式化后返回 `ChatPromptValue`（包含 `BaseMessage[]`）：

```typescript
import {
  ChatPromptTemplate,
  MessagesPlaceholder,
} from "@langchain/core/prompts";

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "你是一个有帮助的助手"],
  new MessagesPlaceholder("history"),
  ["human", "{input}"],
]);

const value = await prompt.formatPromptValue({
  history: [new HumanMessage("我叫小明")],
  input: "我叫什么名字？",
});
```

### fromMessages 接受的消息格式

每个元素可以是：
- `[role, template]` 元组：`["human", "你好"]` 或 `["system", "你是{role}"]`
- `BaseMessagePromptTemplate` 实例
- `BaseMessage` 实例（静态消息）
- `MessagesPlaceholder` 实例

## 消息级模板

### BaseMessagePromptTemplate

**源码位置**：`prompts/chat.ts:50`

单个角色消息的抽象模板：

```typescript
abstract class BaseMessagePromptTemplate<RunInput, RunOutput>
  extends Runnable<RunInput, RunOutput> {
  abstract inputVariables: string[];
  abstract formatMessages(values): Promise<BaseMessage[]>;
}
```

### HumanMessagePromptTemplate / AIMessagePromptTemplate / SystemMessagePromptTemplate

**源码位置**：`prompts/chat.ts:707`、`724`、`751`

各自通过静态 `_messageClass()` 返回对应的消息类（HumanMessage/AIMessage/SystemMessage），格式化后产生该类型的消息。

### MessagesPlaceholder

**源码位置**：`prompts/chat.ts:101`

消息列表占位符，用于在聊天模板中插入动态的消息历史：

```typescript
class MessagesPlaceholder<RunInput> extends BaseMessagePromptTemplate {
  variableName: string;
  optional: boolean;  // 默认 false
}
```

- `formatMessages` 从 values 中取出 `variableName` 对应的消息数组
- `optional: true` 时，若值不存在返回空数组而非报错
- 常用于注入对话历史（chat history）或中间 Agent 步骤

## partial 机制

提示模板支持**部分变量**（partial variables），即预先填好部分变量，剩余的稍后提供：

```typescript
const prompt = new PromptTemplate({
  inputVariables: ["topic", "style"],
  template: "请用{style}风格写一个关于{topic}的笑话",
});

const partial = await prompt.partial({ style: "相声" });
const text = await partial.format({ topic: "猫" });
```

`partialVariables` 还支持异步函数，用于需要动态获取的值（如当前时间）：

```typescript
const prompt = new PromptTemplate({
  inputVariables: ["date", "query"],
  template: "今天是{date}。{query}",
  partialVariables: {
    date: async () => new Date().toISOString(),
  },
});
```

## 模板作为 Runnable

所有提示模板继承 `Runnable`，因此：

```typescript
// 直接 invoke 得到 PromptValue
const promptValue = await prompt.invoke({ topic: "猫" });

// pipe 到模型
const chain = prompt.pipe(model).pipe(new StringOutputParser());
const result = await chain.invoke({ topic: "猫" });

// 流式
const stream = await chain.stream({ topic: "猫" });

// 批量
const results = await chain.batch([
  { topic: "猫" },
  { topic: "狗" },
]);
```

`invoke` 内部设置 `runType: "prompt"`，回调系统可据此识别提示模板的执行。

## PromptValue

`formatPromptValue` 返回 `BasePromptValueInterface` 实例，它有两个核心方法：

- `toString(): string` — 转为纯文本（用于 LLM）
- `toChatMessages(): BaseMessage[]` — 转为消息数组（用于 Chat Model）

这使得同一个模板可以同时用于纯文本 LLM 和聊天模型。`ChatPromptValue` 是其聊天实现，内部持有 `BaseMessage[]`。

## 相关文档

- [Runnable 接口](/ai/langchain-ai/langchainjs/concepts/runnable-interface) — 模板作为 Runnable 的组合能力
- [消息系统](/ai/langchain-ai/langchainjs/concepts/message-system) — BaseMessage 类型
- [构建 LCEL 链示例](/ai/langchain-ai/langchainjs/examples/lcel-chain) — Prompt → Model → Parser
