---
type: example
scope: openevals
name: basic-evaluation
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: OpenEvals 基础评测示例——精确匹配、LLM-as-Judge、JSON 混合评测与预置 Prompt
---

# 基础评测示例

本示例演示 OpenEvals 的核心使用方式，涵盖精确匹配、LLM-as-Judge、JSON 混合评测和预置 Prompt。

## 前置条件

### JavaScript/TypeScript

```bash
npm install openevals @langchain/openai
# 或
yarn add openevals @langchain/openai
```

需要设置 OpenAI API Key：

```bash
export OPENAI_API_KEY="sk-..."
```

### Python

```bash
pip install openevals langchain-openai
```

```bash
export OPENAI_API_KEY="sk-..."
```

## 1. 精确匹配

适用于结构化输出或事实性回答的确定性验证。

### TypeScript

```typescript
import { exactMatch } from "openevals";

// 基本用法
const result = await exactMatch({
  outputs: { answer: "42", confidence: 0.95 },
  referenceOutputs: { confidence: 0.95, answer: "42" },
});

console.log(result.key);    // "exact_match"
console.log(result.score);  // true（键顺序不同但排序后相等）

// 不匹配的情况
const mismatch = await exactMatch({
  outputs: { answer: "42" },
  referenceOutputs: { answer: "43" },
});
console.log(mismatch.score);  // false
```

### Python

```python
from openevals import exact_match

result = exact_match(
    outputs={"answer": "42", "confidence": 0.95},
    reference_outputs={"confidence": 0.95, answer: "42"},
)

print(result["key"])    # "exact_match"
print(result["score"])  # True
```

## 2. LLM-as-Judge 基础用法

使用 LLM 按自定义标准评估开放式输出。

### TypeScript

```typescript
import { createLLMAsJudge } from "openevals";

// 布尔评分（默认）
const correctnessEvaluator = createLLMAsJudge({
  prompt: `Is the following answer correct?
Question: {inputs}
Answer: {outputs}
Reference: {reference_outputs}`,
  model: "openai:gpt-4o",
});

const result = await correctnessEvaluator({
  inputs: "What is the capital of France?",
  outputs: "Paris",
  referenceOutputs: "Paris",
});

console.log(result.score);    // true
console.log(result.comment);  // LLM 的推理过程
```

### Python

```python
from openevals import create_llm_as_judge

correctness_evaluator = create_llm_as_judge(
    prompt="""Is the following answer correct?
Question: {inputs}
Answer: {outputs}
Reference: {reference_outputs}""",
    model="openai:gpt-4o",
)

result = correctness_evaluator(
    inputs="What is the capital of France?",
    outputs="Paris",
    reference_outputs="Paris",
)

print(result["score"])    # True
print(result["comment"])  # reasoning
```

## 3. 连续评分与离散评分

### 连续评分（0-1 浮点数）

```typescript
const qualityEvaluator = createLLMAsJudge({
  prompt: "Rate the quality of this response from 0 to 1: {outputs}",
  model: "openai:gpt-4o",
  continuous: true,
});

const result = await qualityEvaluator({
  outputs: "The sky appears blue due to Rayleigh scattering.",
});
console.log(result.score);  // 0.0 ~ 1.0 之间的浮点数
```

### 离散选择评分

```typescript
const ratingEvaluator = createLLMAsJudge({
  prompt: "Rate from 1 to 5: {outputs}",
  model: "openai:gpt-4o",
  choices: [1, 2, 3, 4, 5],
});
```

## 4. 使用预置 Prompt

OpenEvals 提供 28+ 个预置评估 prompt，覆盖质量、RAG、安全等场景。

### TypeScript

```typescript
import { createLLMAsJudge, CORRECTNESS_PROMPT, HALLUCINATION_PROMPT } from "openevals";

// 正确性评估
const correctnessEval = createLLMAsJudge({
  prompt: CORRECTNESS_PROMPT,
  model: "openai:gpt-4o",
});

// 幻觉检测
const hallucinationEval = createLLMAsJudge({
  prompt: HALLUCINATION_PROMPT,
  model: "openai:gpt-4o",
});

const result = await hallucinationEval({
  inputs: "What is the speed of light?",
  outputs: "The speed of light is approximately 300,000 km/s.",
  referenceOutputs: "The speed of light in vacuum is 299,792,458 m/s.",
});
```

### Python

```python
from openevals.prompts.quality import CORRECTNESS_PROMPT
# 注意：Python 中 prompt 常量需从对应子模块导入
```

## 5. Few-Shot 示例

提供示例评分引导 LLM 理解评估标准：

```typescript
const sentimentEvaluator = createLLMAsJudge({
  prompt: "Is this text positive? {outputs}",
  model: "openai:gpt-4o",
  fewShotExamples: [
    {
      inputs: "Review text",
      outputs: "I love this product!",
      score: true,
      reasoning: "Explicitly expresses positive sentiment.",
    },
    {
      inputs: "Review text",
      outputs: "Terrible experience, would not buy again.",
      score: false,
      reasoning: "Explicitly expresses negative sentiment.",
    },
    {
      inputs: "Review text",
      outputs: "It arrived on time.",
      score: true,
      reasoning: "Neutral-to-positive factual statement about delivery.",
    },
  ],
});
```

## 6. JSON 混合评测

对结构化输出逐键评估：精确字段用深度比较，语义字段用 LLM rubric。

```typescript
import { createJsonMatchEvaluator } from "openevals";

const evaluator = createJsonMatchEvaluator({
  rubric: {
    summary: "Does the summary accurately capture the key findings without hallucination?",
    sentiment: "Is the sentiment classification correct based on the content?",
  },
  excludeKeys: ["id", "timestamp"],
  aggregator: "average",
  listMatchMode: "same_elements",
  model: "openai:gpt-4o",
});

const result = await evaluator({
  outputs: {
    id: "doc-001",
    timestamp: "2024-01-01T00:00:00Z",
    summary: "The study found significant improvement in treatment outcomes.",
    sentiment: "positive",
  },
  referenceOutputs: {
    id: "doc-001",
    timestamp: "2024-01-01T12:00:00Z",
    summary: "Research demonstrated notable improvements in patient results.",
    sentiment: "positive",
  },
});

// id: _deepEqual → 1
// timestamp: excludeKeys → 跳过
// summary: LLM rubric 评估 → 0.9（语义一致但措辞不同）
// sentiment: LLM rubric 评估 → 1
// aggregator: average → 0.95
console.log(result.score);
```

## 7. 自定义输出 Schema

需要更丰富的评估输出时，使用 `outputSchema` 自定义结构：

```typescript
import { z } from "zod";

const detailedEvaluator = createLLMAsJudge({
  prompt: `Evaluate this answer in detail.
Question: {inputs}
Answer: {outputs}`,
  model: "openai:gpt-4o",
  outputSchema: z.object({
    overallScore: z.number().min(0).max(1),
    accuracy: z.number().min(0).max(1),
    completeness: z.number().min(0).max(1),
    clarity: z.number().min(0).max(1),
    issues: z.array(z.string()),
    suggestions: z.string(),
  }),
});

const result = await detailedEvaluator({
  inputs: "Explain quantum computing.",
  outputs: "Quantum computing uses qubits...",
});

// result: {
//   overallScore: 0.85,
//   accuracy: 0.9,
//   completeness: 0.7,
//   clarity: 0.95,
//   issues: ["Lacks discussion of error correction"],
//   suggestions: "Add a section on quantum error correction codes."
// }
```

## 8. 字符串相似度

### Levenshtein 距离

```typescript
import { levenshteinDistance } from "openevals";

const result = await levenshteinDistance({
  outputs: "hello world",
  referenceOutputs: "hello worlt",
});
console.log(result.score);  // ≈ 0.91
```

### 嵌入相似度

```typescript
import { createEmbeddingSimilarityEvaluator } from "openevals";
import { OpenAIEmbeddings } from "@langchain/openai";

const evaluator = createEmbeddingSimilarityEvaluator({
  embeddings: new OpenAIEmbeddings(),
  algorithm: "cosine",
});

const result = await evaluator({
  outputs: "The cat sat on the mat",
  referenceOutputs: "A feline rested on the rug",
});
console.log(result.score);  // ≈ 0.85（语义相似）
```

## 9. Python 异步评测

```python
import asyncio
from openevals import create_async_llm_as_judge

async def evaluate():
    evaluator = create_async_llm_as_judge(
        prompt="Rate this response: {outputs}",
        model="openai:gpt-4o",
        continuous=True,
    )
    result = await evaluator(outputs="This is a good response.")
    return result

result = asyncio.run(evaluate())
print(result["score"])
```

## 评测结果结构

所有标准评测器返回统一的 `EvaluatorResult`：

```typescript
{
  key: string;           // 反馈键名，如 "exact_match"、"score"
  score: number | boolean;  // 评分
  comment?: string;      // LLM 推理过程（useReasoning=true 时）
  metadata?: Record<string, unknown>;  // 额外元数据
  sourceRunId?: string;  // LangSmith run ID
}
```

## 进一步阅读

- [精确评测器概念](/langchain-ai/openevals/concepts/exact-evaluators) — 各确定性评测器的实现细节
- [LLM-as-Judge 概念](/langchain-ai/openevals/concepts/llm-as-judge) — 评分模式、prompt 格式化与 judge 后端
- [API 参考](/langchain-ai/openevals/references/api) — 完整函数签名
