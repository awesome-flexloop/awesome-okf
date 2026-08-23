---
type: concept
scope: openevals
name: exact-evaluators
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: 精确评测器——exactMatch、Levenshtein 距离、嵌入相似度与 JSON 匹配的实现机制
---

# 精确评测器

精确评测器是 OpenEvals 中的确定性评测层，不依赖 LLM，结果完全可复现。它们适用于结构化输出验证、事实性问答匹配和近似文本比较。

## exactMatch：JSON 精确匹配

`exactMatch`（JS）/ `exact_match`（Python）是最基础的评测器，比较 `outputs` 和 `referenceOutputs` 是否完全相等。

### JS 实现（exact.ts）

```typescript
const _scorer = (params: { outputs: unknown; referenceOutputs?: unknown }) => {
  const { outputs, referenceOutputs } = params;
  if (outputs === null || referenceOutputs === null) {
    throw new Error("Exact match requires both outputs and referenceOutputs");
  }

  const processNestedStructures = (value: unknown): unknown => {
    if (value === undefined) return null;
    if (Array.isArray(value)) return value.map(processNestedStructures);
    if (typeof value === "object" && value !== null) {
      return Object.fromEntries(
        Object.entries(value)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([k, v]) => [k, processNestedStructures(v)])
      );
    }
    return value;
  };

  return JSON.stringify(processNestedStructures(outputs)) ===
         JSON.stringify(processNestedStructures(referenceOutputs));
};
```

关键处理：

1. **undefined → null 转换**：JavaScript 中 `undefined` 在 `JSON.stringify` 中会被省略，而 `null` 会保留。统一转换为 null 保证比较一致性。
2. **对象键排序**：嵌套对象通过 `Object.entries` + `sort(([a], [b]) => a.localeCompare(b))` 按键名字典序排序，消除键顺序差异。
3. **递归处理**：数组和对象递归处理，确保深层嵌套结构也被规范化。

### Python 实现（exact.py）

Python 版本更简洁，利用 `json.dumps(sort_keys=True)` 一步完成排序和序列化：

```python
def _scorer(outputs: Any, reference_outputs: Any) -> bool:
    if outputs is None or reference_outputs is None:
        raise ValueError("Exact match requires both outputs and reference_outputs")
    outputs_json = json.dumps(outputs, sort_keys=True)
    reference_outputs_json = json.dumps(reference_outputs, sort_keys=True)
    return outputs_json == reference_outputs_json
```

Python 的 `json.dumps(sort_keys=True)` 会递归排序所有字典键，等效于 JS 的手动排序。

### 使用

```typescript
import { exactMatch } from "openevals";

const result = await exactMatch({
  outputs: { name: "Alice", age: 30 },
  referenceOutputs: { age: 30, name: "Alice" },
});
// result.key === "exact_match"
// result.score === true  (键顺序不同但排序后相等)
```

```python
from openevals import exact_match

result = exact_match(
    outputs={"name": "Alice", "age": 30},
    reference_outputs={"age": 30, "name": "Alice"},
)
# result["score"] is True
```

## levenshteinDistance：编辑距离相似度

Levenshtein 距离衡量两个字符串之间的差异程度，计算将一个字符串转换为另一个所需的最少单字符编辑数（插入、删除、替换）。

### 实现（levenshtein.ts）

```typescript
const m = outputStr.length;
const n = referenceStr.length;
const dp: number[][] = Array(m + 1).fill(null)
  .map(() => Array(n + 1).fill(0));

for (let i = 0; i <= m; i++) dp[i][0] = i;
for (let j = 0; j <= n; j++) dp[0][j] = j;

for (let i = 1; i <= m; i++) {
  for (let j = 1; j <= n; j++) {
    if (outputStr[i - 1] === referenceStr[j - 1]) {
      dp[i][j] = dp[i - 1][j - 1];
    } else {
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,      // deletion
        dp[i][j - 1] + 1,      // insertion
        dp[i - 1][j - 1] + 1   // substitution
      );
    }
  }
}

const distance = dp[m][n];
const maxLength = Math.max(m, n);
return maxLength > 0 ? 1.0 - distance / maxLength : 1.0;
```

- **归一化分数**：`1.0 - distance / maxLength`，范围 [0, 1]，1.0 表示完全相同
- **空串处理**：两个空串返回 1.0
- **非字符串输入**：自动 `JSON.stringify` 转为字符串

### 使用

```typescript
import { levenshteinDistance } from "openevals";

const result = await levenshteinDistance({
  outputs: "hello world",
  referenceOutputs: "hello worlb",
});
// result.score ≈ 0.91 (1/11 编辑距离)
```

## createEmbeddingSimilarityEvaluator：嵌入相似度

通过文本嵌入向量计算语义相似度，支持 cosine 和 dot_product 两种算法。

### 实现（embedding_similarity.ts）

```typescript
const cosineSimilarity = (v1: number[], v2: number[]): number => {
  const dotProd = dotProduct(v1, v2);
  const magnitude1 = vectorMagnitude(v1);
  const magnitude2 = vectorMagnitude(v2);
  return dotProd / (magnitude1 * magnitude2);
};

const similarity = algorithm === "cosine"
  ? cosineSimilarity(receivedEmbedding, expectedEmbedding)
  : dotProduct(receivedEmbedding, expectedEmbedding);

return Number(similarity.toFixed(2));
```

- **cosine**：余弦相似度，范围 [-1, 1]，衡量方向相似性（不受向量长度影响）
- **dot_product**：点积，受向量长度和方向共同影响
- **精度**：结果保留两位小数
- **依赖**：需要传入 LangChain `Embeddings` 实例，调用 `embedQuery` 获取向量

### 使用

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
// result.score ≈ 0.85 (语义相似但用词不同)
```

## createJsonMatchEvaluator：结构化输出混合评测

JSON 匹配评估器是精确评测和 LLM 评测的桥梁，可以对结构化输出逐键评估，精确键用深度比较，语义键用 LLM rubric。

### 核心选项

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `aggregator` | `"average"` \| `"all"` | undefined | 多键聚合方式。undefined 时每键独立返回结果 |
| `listAggregator` | `"average"` \| `"all"` | `"all"` | 列表元素聚合方式 |
| `rubric` | `Record<string, string>` | `{}` | 需要 LLM 评估的键及其标准 |
| `excludeKeys` | `string[]` | `[]` | 排除评估的键 |
| `judge` / `model` | — | — | LLM 后端（rubric 非空时必需） |
| `useReasoning` | `boolean` | `true` | LLM 评估是否输出推理过程 |
| `listMatchMode` | `"same_elements"` \| `"subset"` \| `"superset"` \| `"ordered"` | `"same_elements"` | 列表匹配模式 |

### 混合评测机制

```
outputs/referenceOutputs
        │
        ▼
┌─────────────────────────┐
│ 按 rubric/excludeKeys   │
│ 将键分为两类：           │
│  • 精确键 → _deepEqual  │
│  • rubric 键 → LLM      │
└────────┬────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
 精确分数   LLM 分数
    │         │
    └────┬────┘
         ▼
┌─────────────────────────┐
│ 聚合（average/all/独立） │
└─────────────────────────┘
```

- **非 rubric 键**：使用 `_deepEqual` 递归深度比较，完全确定
- **rubric 键**：通过 `_createLLMAsJudgeScorer` 调用 LLM，按指定标准评判
- **列表匹配**：`same_elements` 双向匹配（输出和参考的每个元素都要找到对应）；`subset` 仅匹配输出元素；`superset` 仅匹配参考元素；`ordered` 按索引位置匹配
- **聚合**：`average` 取所有键分数均值，`all` 为 AND 逻辑（任一为 0 则整体为 0）

### 使用

```typescript
import { createJsonMatchEvaluator } from "openevals";

const evaluator = createJsonMatchEvaluator({
  rubric: {
    summary: "Does the summary accurately capture the main points?",
  },
  excludeKeys: ["timestamp"],
  aggregator: "average",
  model: "openai:gpt-4o",
});

const result = await evaluator({
  outputs: {
    id: 123,
    summary: "The experiment showed positive results.",
    timestamp: "2024-01-01",
  },
  referenceOutputs: {
    id: 123,
    summary: "Results were positive in the experiment.",
    timestamp: "2024-01-02",
  },
});
// id: _deepEqual → 1 (精确匹配)
// summary: LLM rubric → 0.9 (语义相近)
// timestamp: excluded → 跳过
// aggregator average → 0.95
```

## _deepEqual：递归深度比较

所有精确评测的基础原语，实现在 `utils.ts` 中：

```typescript
export function _deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (a === null || b === null || typeof a !== "object" || typeof b !== "object")
    return false;
  if (Array.isArray(a) || Array.isArray(b)) {
    return Array.isArray(a) && Array.isArray(b) &&
      a.length === b.length &&
      a.every((value, index) => _deepEqual(value, b[index]));
  }
  const aKeys = Object.keys(a as Record<string, unknown>);
  const bKeys = Object.keys(b as Record<string, unknown>);
  return aKeys.length === bKeys.length &&
    aKeys.every((key) =>
      Object.prototype.hasOwnProperty.call(b, key) &&
      _deepEqual(a[key], b[key])
    );
}
```

与 `exactMatch` 的区别：`_deepEqual` 是内存中的对象深度比较（不经过 JSON 序列化），不排序键、不转换 undefined，因此对键顺序敏感。`exactMatch` 则先规范化（排序键、undefined→null）再比较。

## 选择指南

| 场景 | 推荐评测器 | 理由 |
|---|---|---|
| 结构化 JSON 输出完全匹配 | `exactMatch` | 规范化后比较，消除键顺序 |
| 工具调用参数验证 | `exactMatch` | 确定性强，适合 CI |
| 文本近似匹配（拼写容错） | `levenshteinDistance` | 编辑距离直观 |
| 语义相似度（同义不同词） | `createEmbeddingSimilarityEvaluator` | 嵌入捕捉语义 |
| JSON 部分字段需语义评判 | `createJsonMatchEvaluator` + rubric | 混合模式兼顾精确与灵活 |
| 列表顺序无关的集合比较 | `createJsonMatchEvaluator` + `listMatchMode: "same_elements"` | 双向匹配 |

## 进一步阅读

- [LLM-as-Judge](/ai/langchain-ai/openevals/concepts/llm-as-judge) — 当精确匹配不够时，使用 LLM 进行语义评判
- [API 参考](/ai/langchain-ai/openevals/references/api) — 精确评测器的完整函数签名
- [基础评测示例](/ai/langchain-ai/openevals/examples/basic-evaluation) — 精确匹配和 LLM 评判的代码示例
