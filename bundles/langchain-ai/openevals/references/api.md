---
type: reference
scope: openevals
name: api
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: OpenEvals 公共 API 参考——精确匹配、LLM-as-Judge、JSON 匹配、字符串相似度等核心函数
---

# API 参考

## 精确匹配

### exactMatch（JS）

```typescript
exactMatch(params: {
  outputs: unknown;
  referenceOutputs?: unknown;
}): Promise<EvaluatorResult>
```

比较 `outputs` 和 `referenceOutputs` 的规范化 JSON 表示是否完全相等。规范化包括：undefined 转 null、对象键按字典序排序、递归处理嵌套结构。

- **feedbackKey**：`"exact_match"`
- **返回 score**：`boolean`
- **异常**：当 `outputs` 或 `referenceOutputs` 为 null 时抛出错误

### exact_match / exact_match_async（Python）

```python
exact_match(*, outputs: Any, reference_outputs: Any, **kwargs: Any) -> EvaluatorResult
async exact_match_async(*, outputs: Any, reference_outputs: Any, **kwargs: Any) -> EvaluatorResult
```

使用 `json.dumps(..., sort_keys=True)` 序列化后比较。

---

## LLM-as-Judge

### createLLMAsJudge（JS）

```typescript
createLLMAsJudge(params: {
  prompt: string | RunnableInterface | ((...args: unknown[]) => ChatCompletionMessage[] | Promise<ChatCompletionMessage[]>);
  feedbackKey?: string;
  model?: string;
  system?: string;
  judge?: ModelClient | BaseChatModel;
  continuous?: boolean;
  choices?: number[];
  useReasoning?: boolean;
  fewShotExamples?: FewShotExample[];
  outputSchema?: Record<string, unknown> | ZodObjectAny;
}): (params: Record<string, unknown>) => Promise<EvaluatorResult | Record<string, unknown>>
```

创建 LLM-as-Judge 评测器。

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `prompt` | `string \| RunnableInterface \| Function` | — | 评估提示。字符串使用 `{inputs}`、`{outputs}`、`{reference_outputs}` 占位符 |
| `feedbackKey` | `string` | `"score"` | 结果中 `key` 字段的值。非默认值时 runName 为 `llm_as_{feedbackKey}_judge` |
| `model` | `string` | — | LangChain 模型标识符（如 `"openai:gpt-4o"`）。judge 未提供时必填 |
| `system` | `string` | — | 系统消息，仅在 prompt 为字符串时有效 |
| `judge` | `ModelClient \| BaseChatModel` | — | LLM 后端。OpenAI client 或 LangChain 模型 |
| `continuous` | `boolean` | `false` | true 时 score 为 0.0-1.0 浮点数，false 时为 boolean |
| `choices` | `number[]` | — | 离散分数选项列表（如 `[1,2,3,4,5]`） |
| `useReasoning` | `boolean` | `true` | 是否要求 LLM 输出推理过程 |
| `fewShotExamples` | `FewShotExample[]` | — | 少样本示例，追加到最后一条 user 消息 |
| `outputSchema` | `Record \| ZodObject` | — | 自定义输出 schema。提供时返回原始对象而非 EvaluatorResult |

**返回值**：无 `outputSchema` 时返回 `EvaluatorResult`（`{ key, score, comment? }`），有 `outputSchema` 时返回符合 schema 的原始对象。

### create_llm_as_judge / create_async_llm_as_judge（Python）

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

Python 版本参数与 JS 对应，差异：`output_schema` 支持 JSON Schema dict、Pydantic model 或 TypedDict；异步版本为 `create_async_llm_as_judge`。

### FewShotExample 类型

```typescript
type FewShotExample = {
  inputs: unknown;
  outputs: unknown;
  score: number | boolean;
  reasoning?: string;
};
```

---

## JSON 匹配

### createJsonMatchEvaluator（JS）

```typescript
createJsonMatchEvaluator(options: {
  aggregator?: "average" | "all";
  listAggregator?: "average" | "all";
  rubric?: Record<string, string>;
  excludeKeys?: string[];
  judge?: ModelClient | BaseChatModel;
  model?: string;
  useReasoning?: boolean;
  listMatchMode?: "superset" | "subset" | "same_elements" | "ordered";
}): (params: { outputs?: any; referenceOutputs?: any }) => Promise<EvaluatorResult | EvaluatorResult[]>
```

结构化输出混合评测器。非 rubric 键使用 `_deepEqual` 精确比较，rubric 键使用 LLM 按指定标准评估。

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `aggregator` | `"average"` \| `"all"` | undefined | 多键聚合。undefined 时每键返回独立 EvaluatorResult |
| `listAggregator` | `"average"` \| `"all"` | `"all"` | 列表元素跨索引聚合方式 |
| `rubric` | `Record<string, string>` | `{}` | 键到评估标准的映射。非空时需提供 judge/model |
| `excludeKeys` | `string[]` | `[]` | 不参与评估的键 |
| `judge` / `model` | — | — | LLM 后端，rubric 非空时必需 |
| `useReasoning` | `boolean` | `true` | rubric 键是否要求推理过程 |
| `listMatchMode` | `"same_elements"` \| `"subset"` \| `"superset"` \| `"ordered"` | `"same_elements"` | 列表元素匹配策略 |

**约束**：`judge`/`model` 与 `rubric` 必须同时提供或同时不提供。

**listMatchMode 说明：**

| 模式 | 行为 |
|---|---|
| `same_elements` | 双向匹配：输出和参考的每个元素都要找到最佳对应 |
| `subset` | 输出元素需在参考中找到对应（输出是参考的子集） |
| `superset` | 参考元素需在输出中找到对应（输出是参考的超集） |
| `ordered` | 按索引位置一一对应 |

---

## 字符串相似度

### levenshteinDistance（JS）

```typescript
levenshteinDistance(params: {
  outputs: unknown;
  referenceOutputs?: unknown;
}): Promise<EvaluatorResult>
```

计算 Levenshtein 编辑距离的归一化相似度分数。分数 = `1.0 - distance / maxLength`，范围 [0, 1]。非字符串输入自动 `JSON.stringify`。

- **feedbackKey**：`"levenshtein_distance"`
- **返回 score**：`number`（0.0-1.0）

### createEmbeddingSimilarityEvaluator（JS）

```typescript
createEmbeddingSimilarityEvaluator(options: {
  embeddings: Embeddings;
  algorithm?: "cosine" | "dot_product";
}): (params: { outputs: unknown; referenceOutputs?: unknown }) => Promise<EvaluatorResult>
```

通过文本嵌入向量计算语义相似度。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `embeddings` | `Embeddings` | — | LangChain Embeddings 实例，需有 `embedQuery` 方法 |
| `algorithm` | `"cosine"` \| `"dot_product"` | `"cosine"` | 相似度算法 |

- **feedbackKey**：`"embedding_similarity"`
- **返回 score**：`number`（cosine 为 [-1, 1]，结果保留两位小数）

---

## 代码评估

### createCodeLLMAsJudge（JS）

```typescript
createCodeLLMAsJudge(config: {
  prompt: string;
  codeExtractionStrategy?: "none" | "llm" | "markdown_code_blocks";
  codeExtractor?: (outputs: string | Record<string, unknown>) => string;
  model?: string;
  client?: BaseChatModel;
  feedbackKey?: string;
  // 其余参数同 createLLMAsJudge
}): EvaluatorFunction
```

在 LLM-as-Judge 基础上增加代码提取步骤。先从输出中提取代码，再进行评估。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `codeExtractionStrategy` | — | 代码提取策略：不提取/LLM提取/Markdown代码块提取 |
| `codeExtractor` | — | 自定义代码提取函数，优先级高于 strategy |
| `feedbackKey` | `"code_correctness"` | 结果键名 |

---

## 轨迹评估

### createTrajectoryMatchEvaluator（JS/Python）

```typescript
// JS
createTrajectoryMatchEvaluator(options: {
  trajectoryMatchMode?: TrajectoryMatchMode;
  toolArgsMatchMode?: ToolArgsMatchMode;
  toolArgsMatchOverrides?: ToolArgsMatchOverrides;
}): EvaluatorFunction
```

```python
# Python
create_trajectory_match_evaluator(...)
create_async_trajectory_match_evaluator(...)
```

比较 Agent 工具调用轨迹。`TrajectoryMatchMode` 支持 strict/subset/superset/unordered 等模式。

### createTrajectoryLLMAsJudge（JS/Python）

使用 LLM 评估 Agent 轨迹质量。Python 提供同步/异步双版本。

---

## 模拟器

### multiturn（JS）

```typescript
multiturn(params: {
  app: (params: { inputs: ChatCompletionMessage; threadId: string }) => Promise<ChatCompletionMessage | BaseMessage>;
  user: ((params: { trajectory: ChatCompletionMessage[]; turnCounter: number }) => Promise<ChatCompletionMessage | BaseMessage>) | (string | Messages)[];
  maxTurns?: number;
  trajectoryEvaluators?: SimpleEvaluator[];
  stoppingCondition?: (params: { trajectory: ChatCompletionMessage[]; turnCounter: number; threadId: string }) => boolean | Promise<boolean>;
  referenceOutputs?: unknown;
  threadId?: string;
}): Promise<MultiturnSimulationResult>
```

多轮对话模拟。`app` 为被测应用，`user` 为模拟用户（函数或预设消息列表），可在每轮后运行 `trajectoryEvaluators` 评估轨迹。

### createLLMSimulatedUser（JS）

创建 LLM 驱动的模拟用户，用于多轮对话测试。

---

## 核心类型

### EvaluatorResult

```typescript
type EvaluatorResult = {
  key: string;
  score: number | boolean;
  comment?: string;
  metadata?: Record<string, unknown>;
  sourceRunId?: string;
};
```

```python
class EvaluatorResult(TypedDict):
    key: str
    score: Union[float, bool]
    comment: Optional[str]
    metadata: Optional[dict]
    source_run_id: Optional[str]
```

### SimpleEvaluator（JS）

```typescript
type SimpleEvaluator = (params: {
  inputs?: unknown;
  outputs: unknown;
  reference_outputs?: unknown;
  [key: string]: unknown;
}) => Promise<EvaluatorResult | EvaluatorResult[]> | EvaluatorResult | EvaluatorResult[];
```

### ModelClient（OpenAI 兼容接口）

```typescript
interface ModelClient {
  chat: {
    completions: {
      create(params: Record<string, any>): Promise<{ choices: { message: ChatCompletionMessage }[] }>;
    };
  };
}
```

---

## 预置 Prompt 常量

| 类别 | 常量名 |
|---|---|
| quality | `CORRECTNESS_PROMPT`、`CONCISENESS_PROMPT`、`HALLUCINATION_PROMPT`、`ANSWER_RELEVANCE_PROMPT`、`CODE_CORRECTNESS_PROMPT`、`CODE_CORRECTNESS_PROMPT_WITH_REFERENCE_OUTPUTS`、`PLAN_ADHERENCE_PROMPT`、`LAZINESS_PROMPT` |
| rag | `RAG_GROUNDEDNESS_PROMPT`、`RAG_HELPFULNESS_PROMPT`、`RAG_RETRIEVAL_RELEVANCE_PROMPT` |
| safety | `TOXICITY_PROMPT`、`FAIRNESS_PROMPT` |
| security | `PII_LEAKAGE_PROMPT`、`PROMPT_INJECTION_PROMPT`、`CODE_INJECTION_PROMPT` |
| trajectory | `TRAJECTORY_ACCURACY_PROMPT`、`TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE`、`TOOL_SELECTION_PROMPT` |
| conversation | `PERCEIVED_ERROR_PROMPT`、`WINS_PROMPT`、`TASK_COMPLETION_PROMPT`、`KNOWLEDGE_RETENTION_PROMPT`、`USER_SATISFACTION_PROMPT`、`AGENT_TONE_PROMPT`、`LANGUAGE_DETECTION_PROMPT`、`SUPPORT_INTENT_PROMPT` |
| image | `EXPLICIT_CONTENT_PROMPT`、`SENSITIVE_IMAGERY_PROMPT` |
| voice | `AUDIO_QUALITY_PROMPT`、`TRANSCRIPTION_ACCURACY_PROMPT`、`USER_INTERRUPTS_PROMPT`、`VOCAL_AFFECT_PROMPT` |

所有常量从 `openevals/prompts`（JS）或 `openevals.prompts`（Python）导出，可直接作为 `createLLMAsJudge` 的 `prompt` 参数。
