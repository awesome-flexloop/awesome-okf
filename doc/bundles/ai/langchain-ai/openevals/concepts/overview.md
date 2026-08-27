---
type: concept
scope: openevals
name: overview
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: OpenEvals 总览——LangChain 生态的开源 LLM 应用评测库
---

# OpenEvals 总览

## 什么是 OpenEvals

OpenEvals 是 LangChain AI 团队开发的开源 LLM 应用评测库，提供从精确匹配到 LLM-as-Judge 的多种评测器，支持 JavaScript/TypeScript 和 Python 双语言。它设计为与 LangSmith 可观测平台无缝集成，可用于离线评测、在线监控和 CI/CD 质量门禁。

- **Python 版本**：0.2.1（`pyproject.toml`）
- **JS 版本**：0.2.2（`src/index.ts`）
- **许可证**：MIT
- **Python 要求**：>= 3.10
- **核心依赖**：LangChain >= 0.3.18、LangChain-OpenAI >= 0.3.6、LangSmith >= 0.3.32

## 解决的问题

LLM 应用的输出是非确定性的自然语言，传统软件测试的精确断言难以适用。OpenEvals 提供了一套分层评测工具：

1. **确定性评测**：精确匹配、编辑距离、嵌入相似度——适用于结构化输出和事实性回答
2. **LLM-as-Judge**：用另一个 LLM 按指定标准评分——适用于开放式质量评估
3. **预置 Prompt 库**：28+ 个覆盖质量、RAG、安全、对话等场景的评测 prompt
4. **轨迹评测**：评估 Agent 的工具调用序列和推理轨迹
5. **多轮模拟**：用 LLM 模拟用户与应用多轮交互，自动评测

## 核心架构

```
┌─────────────────────────────────────────────────┐
│                   用户代码                        │
│  evaluator({ inputs, outputs, referenceOutputs })│
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│           _runEvaluator / _run_evaluator         │
│  ┌─────────────────────────────────────────┐    │
│  │ 1. 调用 scorer 获取原始分数               │    │
│  │ 2. 标准化为 EvaluatorResult              │    │
│  │ 3. LangSmith traceable / wrapEvaluator  │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌──────────┬───────────┬───────────┬──────────────┐
│ exact    │ string    │ json      │ llm          │
│ Match    │ levenshtein│ match    │ as judge     │
│          │ embedding │           │              │
└──────────┴───────────┴───────────┴──────────────┘
```

所有评测器遵循统一协议：接收 `{ inputs, outputs, referenceOutputs, ... }`，返回 `EvaluatorResult`（含 `key`、`score`、`comment`、`metadata`）。详见 评测器协议洞察。

## 评测器分类

### 确定性评测器

| 评测器 | JS 函数 | Python 函数 | 评分方式 |
|---|---|---|---|
| 精确匹配 | `exactMatch` | `exact_match` / `exact_match_async` | JSON 序列化比较 |
| Levenshtein 距离 | `levenshteinDistance` | — | 归一化编辑距离 0-1 |
| 嵌入相似度 | `createEmbeddingSimilarityEvaluator` | — | cosine / dot_product |
| JSON 匹配 | `createJsonMatchEvaluator` | — | deepEqual + 可选 LLM rubric |

详见 精确评测器。

### LLM-as-Judge 评测器

| 评测器 | JS 函数 | Python 函数 | 说明 |
|---|---|---|---|
| 通用 LLM 评判 | `createLLMAsJudge` | `create_llm_as_judge` / `_async` | 自定义 prompt + schema |
| 代码评判 | `createCodeLLMAsJudge` | — | 含代码提取策略 |
| 轨迹评判 | `createTrajectoryLLMAsJudge` | `create_trajectory_llm_as_judge` / `_async` | Agent 轨迹评估 |
| JSON 评判 | `createJsonMatchEvaluator`（rubric 模式） | — | 结构化字段语义评判 |

详见 LLM-as-Judge。

### 轨迹匹配评测器

| 评测器 | 说明 |
|---|---|
| `createTrajectoryMatchEvaluator` | 比较 Agent 工具调用轨迹 |
| 匹配模式 | `strict`、`subset`、`superset`、`unordered` |

### 模拟器

| 组件 | 说明 |
|---|---|
| `multiturn` | 多轮对话模拟框架 |
| `createLLMSimulatedUser` | 预置 LLM 模拟用户 |

## 预置 Prompt 库

OpenEvals 提供 8 大类预置 prompt 常量，可直接传入 `createLLMAsJudge`：

- **质量（quality）**：正确性、简洁性、幻觉、答案相关性、代码正确性、计划遵循、惰性
- **RAG**： groundedness、helpfulness、retrieval relevance
- **安全（safety）**：毒性、公平性
- **安保（security）**：PII 泄露、prompt 注入、代码注入
- **轨迹（trajectory）**：准确性、工具选择
- **对话（conversation）**：感知错误、任务完成、知识保留、用户满意度、语气、语言检测、支持意图、wins
- **图像（image）**： explicit content、sensitive imagery
- **语音（voice）**：音频质量、转录准确性、用户中断、情感影响

## 双语言支持

JS/TS 和 Python 实现具有对称的模块结构和 API 设计：

```
JS (js/src/)              Python (python/openevals/)
├── exact.ts ↔───────────├── exact.py
├── llm.ts  ↔───────────├── llm.py
├── types.ts ↔──────────├── types.py
├── utils.ts ↔──────────├── utils.py
├── code/   ↔───────────├── code/
├── json/   ↔───────────├── json/
├── prompts/ ↔──────────├── prompts/
├── simulators/ ↔───────├── simulators/
├── string/ ↔───────────├── string/
└── trajectory/ ↔───────└── trajectory/
```

主要差异：Python 提供同步/异步双版本，JS 统一为 async；Python 支持 Pydantic/TypedDict schema，JS 支持 Zod schema。详见 双语言架构洞察。

## 快速开始

```typescript
import { exactMatch, createLLMAsJudge } from "openevals";

// 精确匹配
const result = await exactMatch({
  outputs: { answer: "42" },
  referenceOutputs: { answer: "42" },
});
// result.score === true

// LLM-as-Judge
const evaluator = createLLMAsJudge({
  prompt: "Rate the quality from 0 to 1: {outputs}",
  model: "openai:gpt-4o",
  continuous: true,
});
const score = await evaluator({
  outputs: "The sky is blue.",
});
```

```python
from openevals import exact_match, create_llm_as_judge

# 精确匹配
result = exact_match(
    outputs={"answer": "42"},
    reference_outputs={"answer": "42"},
)

# LLM-as-Judge
evaluator = create_llm_as_judge(
    prompt="Rate the quality from 0 to 1: {outputs}",
    model="openai:gpt-4o",
    continuous=True,
)
result = evaluator(outputs="The sky is blue.")
```

详见 基础评测示例 和 API 参考。

## 进一步阅读

- 精确评测器 — exactMatch、Levenshtein、嵌入相似度、JSON 匹配的实现机制
- LLM-as-Judge — 评分模式、prompt 格式化、judge 后端、结构化输出
- API 参考 — 全部公共函数签名与参数说明
