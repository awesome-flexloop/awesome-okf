---
type: concept
scope: openevals
name: llm-as-judge
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: LLM-as-Judge——用大模型按指定标准评估输出质量的机制、评分模式与实现细节
---

# LLM-as-Judge

LLM-as-Judge 是 OpenEvals 的语义评测核心，通过调用另一个 LLM（"裁判"）按指定评估标准对应用输出进行评分。它适用于精确匹配无法覆盖的开放式质量评估，如正确性、连贯性、安全性等。

## 核心函数

### JavaScript/TypeScript

```typescript
createLLMAsJudge(params: {
  prompt: string | RunnableInterface | ((...args) => ChatCompletionMessage[]);
  feedbackKey?: string;        // 默认 "score"
  model?: string;              // 如 "openai:gpt-4o"
  system?: string;             // 系统消息
  judge?: ModelClient | BaseChatModel;
  continuous?: boolean;        // true: 0-1 浮点评分
  choices?: number[];          // 离散分数选项
  useReasoning?: boolean;      // 默认 true，要求输出推理过程
  fewShotExamples?: FewShotExample[];
  outputSchema?: Record<string, unknown> | ZodObjectAny;
}): (params) => Promise<EvaluatorResult | Record<string, unknown>>
```

### Python

```python
create_llm_as_judge(
    *,
    prompt: Union[str, Runnable, Callable[..., list[ChatCompletionMessage]]],
    feedback_key: str = "score",
    judge: Optional[Union[ModelClient, BaseChatModel]] = None,
    model: Optional[str] = None,
    system: Optional[str] = None,
    continuous: bool = False,
    choices: Optional[list[float]] = None,
    use_reasoning: bool = True,
    few_shot_examples: Optional[list[FewShotExample]] = None,
    output_schema: Optional[Union[dict, type]] = None,
) -> Union[SimpleEvaluator, Callable[..., Any]]
```

Python 还提供异步版本 `create_async_llm_as_judge`，参数相同。

## 评分模式

通过 `continuous` 和 `choices` 参数控制评分类型，由 `constructDefaultOutputJsonSchema` 生成对应的 JSON Schema：

### 布尔模式（默认）

```typescript
createLLMAsJudge({
  prompt: "Is this answer correct? {outputs}",
  model: "openai:gpt-4o",
  // continuous 和 choices 均未设置
});
// score: boolean — true 表示满足标准，false 表示不满足
```

生成的 Schema：
```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "reasoning": { "type": "string", "description": "...Thus, the score should be: SCORE_YOU_ASSIGN." },
    "score": { "type": "boolean", "description": "A score that is true if criteria..." }
  },
  "required": ["reasoning", "score"]
}
```

### 连续模式

```typescript
createLLMAsJudge({
  prompt: "Rate quality from 0 to 1: {outputs}",
  model: "openai:gpt-4o",
  continuous: true,
});
// score: number — 0.0（完全不满足）到 1.0（完美满足）
```

### 离散选择模式

```typescript
createLLMAsJudge({
  prompt: "Rate from 1-5: {outputs}",
  model: "openai:gpt-4o",
  choices: [1, 2, 3, 4, 5],
});
// score: number — 必须是 [1, 2, 3, 4, 5] 之一
```

### 关闭推理

```typescript
createLLMAsJudge({
  prompt: "Is this correct? {outputs}",
  model: "openai:gpt-4o",
  useReasoning: false,
});
// 仅返回 score，不要求 reasoning
```

## Prompt 格式化

`prompt` 参数支持三种形式：

### 1. 字符串模板

```typescript
const evaluator = createLLMAsJudge({
  prompt: "Rate the answer.\nQuestion: {inputs}\nAnswer: {outputs}",
  model: "openai:gpt-4o",
});
```

使用 LangChain `ChatPromptTemplate.fromTemplate` 格式化，可用变量包括 `inputs`、`outputs`、`reference_outputs` 以及任意额外 kwargs。

**附件占位符**：字符串模板支持 `{attachments}` 占位符，用于在多模态评测中插入图片/音频/PDF：

```typescript
const evaluator = createLLMAsJudge({
  prompt: "Describe this image: {attachments}\nExpected: {referenceOutputs}",
  model: "openai:gpt-4o",
});
```

模板被拆分为 `{attachments}` 前后两部分，附件内容块插入中间。

### 2. LangChain Runnable

```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts";

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a strict evaluator."],
  ["human", "Rate: {outputs}"],
]);

const evaluator = createLLMAsJudge({
  prompt,
  model: "openai:gpt-4o",
});
```

若 prompt 是 `StructuredPrompt`（自带 schema），则其 schema 会被用作输出 schema，此时不能同时传入 `outputSchema`。

### 3. 函数

```typescript
const evaluator = createLLMAsJudge({
  prompt: ({ inputs, outputs, reference_outputs }) => [
    { role: "user", content: `Compare "${outputs}" with "${reference_outputs}"` },
  ],
  model: "openai:gpt-4o",
});
```

函数直接返回 `ChatCompletionMessage[]`，给予完全的消息构建控制。

## Judge 后端

支持两种 LLM 后端，通过 `judge` 参数指定：

### LangChain BaseChatModel

```typescript
import { ChatOpenAI } from "@langchain/openai";

const evaluator = createLLMAsJudge({
  prompt: "Rate: {outputs}",
  judge: new ChatOpenAI({ model: "gpt-4o" }),
});
```

使用 `judge.withStructuredOutput(schema).invoke(messages)` 调用，自动处理结构化输出。支持所有 LangChain 聊天模型（OpenAI、Anthropic、Google 等）。

### 原生 OpenAI Client

```typescript
import OpenAI from "openai";

const evaluator = createLLMAsJudge({
  prompt: "Rate: {outputs}",
  judge: new OpenAI(),
  model: "gpt-4o",  // 使用 OpenAI client 时 model 为必填
});
```

使用 `judge.chat.completions.create({ response_format: { type: "json_schema", ... } })` 调用。model 字符串若以 `"openai:"` 开头会自动去掉前缀。

### 自动初始化

若不提供 `judge`，则必须提供 `model` 字符串，通过 `initChatModel(model)` 自动创建 LangChain 模型：

```typescript
const evaluator = createLLMAsJudge({
  prompt: "Rate: {outputs}",
  model: "openai:gpt-4o",  // 自动创建 ChatOpenAI
});
```

## Few-Shot 示例

`fewShotExamples` 允许提供示例评分，追加到最后一条 user 消息末尾：

```typescript
const evaluator = createLLMAsJudge({
  prompt: "Rate the sentiment: {outputs}",
  model: "openai:gpt-4o",
  fewShotExamples: [
    {
      inputs: "I love this!",
      outputs: "Positive",
      score: true,
      reasoning: "Explicitly expresses positive emotion.",
    },
    {
      inputs: "I hate this.",
      outputs: "Positive",
      score: false,
      reasoning: "Expresses negative emotion, not positive.",
    },
  ],
});
```

示例以 XML 格式追加：

```xml
<example>
<input>"I love this!"</input>
<output>"Positive"</output>
<reasoning>Explicitly expresses positive emotion.</reasoning>
<score>true</score>
</example>
```

## 自定义输出 Schema

默认情况下评测器返回 `EvaluatorResult`（`{ key, score, comment, metadata }`）。通过 `outputSchema` 可以自定义输出结构：

```typescript
import { z } from "zod";

const evaluator = createLLMAsJudge({
  prompt: "Evaluate: {outputs}",
  model: "openai:gpt-4o",
  outputSchema: z.object({
    score: z.number(),
    issues: z.array(z.string()),
    suggestions: z.string(),
  }),
});

const result = await evaluator({ outputs: "..." });
// result: { score: number, issues: string[], suggestions: string }
```

当提供 `outputSchema` 时：
- 返回类型变为 `Promise<Record<string, unknown>>`（原始 LLM 输出）
- 不再包装为 `EvaluatorResult`
- JS 侧 Zod schema 通过 `toJsonSchema` 转换为 JSON Schema
- Python 侧支持 JSON Schema dict、Pydantic model 或 TypedDict

## 执行流程

```
用户调用 evaluator({ inputs, outputs, referenceOutputs, ... })
        │
        ▼
┌───────────────────────────────┐
│ 1. 字符串化参数                │
│    _stringifyPromptParam      │
│    (BaseMessage→JSON, etc.)   │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 2. 格式化 prompt              │
│    • Runnable → .invoke()     │
│    • string → ChatPromptTemplate│
│    • function → 直接调用       │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 3. 添加 system 消息           │
│ 4. 追加 few-shot 示例         │
│ 5. 处理 attachments           │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 6. 初始化 judge（如需）        │
│    initChatModel(model)       │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 7. 调用 LLM 结构化输出         │
│    BaseChatModel:             │
│      .withStructuredOutput()  │
│    OpenAI client:             │
│      response_format:json_schema│
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 8. 解析响应                   │
│    默认: [score, reasoning]   │
│    自定义 schema: 原始对象     │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 9. _runEvaluator 包装         │
│    → EvaluatorResult          │
│    → LangSmith trace          │
└───────────────────────────────┘
```

## 多模态支持

`_attachmentToContentBlock` 支持三类附件：

| MIME 类型 | 输出格式 | 说明 |
|---|---|---|
| `image/*` | `{ type: "image_url", image_url: { url: data } }` | 图片 URL 或 base64 |
| `application/pdf` | `{ type: "file", file: { filename, file_data: data } }` | PDF 文件 |
| `audio/*` | `{ type: "input_audio", input_audio: { data, format } }` | 音频 base64 |

附件通过 `attachments` 参数传入，可以是字符串 URL、单个附件对象或附件数组。MIME 别名会被规范化（如 `audio/mpeg` → `audio/mp3`）。

## 与预置 Prompt 配合

OpenEvals 提供的预置 prompt 常量可直接使用：

```typescript
import { createLLMAsJudge, CORRECTNESS_PROMPT, HALLUCINATION_PROMPT } from "openevals";

const correctnessEvaluator = createLLMAsJudge({
  prompt: CORRECTNESS_PROMPT,
  model: "openai:gpt-4o",
});

const hallucinationEvaluator = createLLMAsJudge({
  prompt: HALLUCINATION_PROMPT,
  model: "openai:gpt-4o",
});
```

预置 prompt 覆盖质量、RAG、安全、安保、对话、图像、语音、轨迹 8 大场景，共 28+ 个常量。

## 进一步阅读

- [精确评测器](/ai/langchain-ai/openevals/concepts/exact-evaluators) — 确定性评测，无需 LLM
- [API 参考](/ai/langchain-ai/openevals/references/api) — `createLLMAsJudge` 完整参数说明
- [基础评测示例](/ai/langchain-ai/openevals/examples/basic-evaluation) — 包含 LLM-as-Judge 的完整代码
