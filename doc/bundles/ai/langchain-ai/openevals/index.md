---
type: bundle
okf_version: "0.2"
scope: openevals
name: openevals
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: OpenEvals——LangChain 开源的 LLM 应用评测库，提供精确匹配、Levenshtein 距离、嵌入相似度、JSON 混合匹配、LLM-as-Judge、轨迹评估、多轮模拟等评测器，支持 JS/TS 和 Python 双语言
---

# OpenEvals

**OpenEvals** 是 LangChain AI 团队开发的开源 LLM 应用评测库，提供从确定性精确匹配到 LLM-as-Judge 语义评判的分层评测工具集。它支持 JavaScript/TypeScript 和 Python 双语言，与 LangSmith 可观测平台无缝集成，适用于离线评测、在线监控和 CI/CD 质量门禁。

- **Python 版本**：0.2.1
- **JS 版本**：0.2.2
- **许可证**：MIT
- **Python 要求**：>= 3.10
- **核心依赖**：LangChain >= 0.3.18、LangChain-OpenAI >= 0.3.6、LangSmith >= 0.3.32

## 核心特性

- **统一评测器协议**：所有评测器遵循 `(params) → EvaluatorResult` 协议，通过 `_runEvaluator` 统一包装，自动注入 LangSmith trace 和 metadata
- **精确匹配**：JSON 规范化后序列化比较，自动处理键顺序和 undefined/null 差异
- **字符串相似度**：Levenshtein 编辑距离归一化分数、嵌入向量 cosine/dot_product 相似度
- **JSON 混合评测**：逐键评估，精确字段用 `_deepEqual`，语义字段用 LLM rubric，支持 average/all 聚合和多种列表匹配模式
- **LLM-as-Judge**：支持布尔/连续/离散三种评分模式，few-shot 示例，自定义输出 schema（Zod/Pydantic），多模态附件（图片/PDF/音频）
- **预置 Prompt 库**：8 大类 28+ 个评测 prompt，覆盖质量、RAG、安全、安保、对话、轨迹、图像、语音
- **轨迹评估**：Agent 工具调用轨迹匹配（strict/subset/superset/unordered）和 LLM 轨迹评判
- **多轮模拟**：LLM 模拟用户与应用多轮交互，自动运行轨迹评估器
- **双语言对称**：JS/TS 和 Python 保持模块结构和 API 对称，Python 提供同步/异步双版本

## 快速开始

### TypeScript

```typescript
import { exactMatch, createLLMAsJudge } from "openevals";

// 精确匹配
const exactResult = await exactMatch({
  outputs: { answer: "42" },
  referenceOutputs: { answer: "42" },
});

// LLM-as-Judge
const evaluator = createLLMAsJudge({
  prompt: "Rate quality from 0 to 1: {outputs}",
  model: "openai:gpt-4o",
  continuous: true,
});
const llmResult = await evaluator({
  outputs: "The sky is blue due to Rayleigh scattering.",
});
```

### Python

```python
from openevals import exact_match, create_llm_as_judge

# 精确匹配
exact_result = exact_match(
    outputs={"answer": "42"},
    reference_outputs={"answer": "42"},
)

# LLM-as-Judge
evaluator = create_llm_as_judge(
    prompt="Rate quality from 0 to 1: {outputs}",
    model="openai:gpt-4o",
    continuous=True,
)
llm_result = evaluator(outputs="The sky is blue due to Rayleigh scattering.")
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/openevals/concepts/overview) — OpenEvals 是什么、解决什么问题、核心架构与评测器分类
- [精确评测器](/ai/langchain-ai/openevals/concepts/exact-evaluators) — exactMatch、Levenshtein、嵌入相似度、JSON 混合匹配的实现机制
- [LLM-as-Judge](/ai/langchain-ai/openevals/concepts/llm-as-judge) — 评分模式、prompt 格式化、judge 后端、结构化输出与多模态

### API 参考

- [API 参考](/ai/langchain-ai/openevals/references/api) — 精确匹配、LLM-as-Judge、JSON 匹配、字符串相似度、代码评估、轨迹评估等全部公共函数

### 使用示例

- [基础评测](/ai/langchain-ai/openevals/examples/basic-evaluation) — 精确匹配、LLM-as-Judge、连续/离散评分、预置 Prompt、Few-Shot、JSON 混合评测、自定义 Schema

### 设计洞察

- [事实清单](/ai/langchain-ai/openevals/spec/facts) — 从源码中提取的 50 条编号事实
- [架构洞察](/ai/langchain-ai/openevals/spec/insights) — 评测器协议、双模式评测光谱、JS+Python 双语言对称架构

## 目录结构

```
openevals/
├── spec/
│   ├── facts.md           # 源码事实验证清单（50 条）
│   └── insights.md        # 设计决策与架构洞察
├── concepts/              # 核心概念（3 篇）
│   ├── overview.md
│   ├── exact-evaluators.md
│   └── llm-as-judge.md
├── references/            # API 参考（1 篇）
│   └── api.md
├── examples/              # 使用示例（1 篇）
│   └── basic-evaluation.md
├── log.md                 # 构建日志
└── index.md               # 本文件
```

## 评测器分类速查

| 类别 | 评测器 | 评分类型 | 确定性 |
|---|---|---|---|
| 精确匹配 | `exactMatch` | boolean | 完全确定 |
| 编辑距离 | `levenshteinDistance` | number 0-1 | 完全确定 |
| 嵌入相似度 | `createEmbeddingSimilarityEvaluator` | number | 完全确定 |
| JSON 匹配 | `createJsonMatchEvaluator` | boolean/number | 混合（精确键确定，rubric 键 LLM） |
| LLM 评判 | `createLLMAsJudge` | boolean/number | 非确定 |
| 代码评判 | `createCodeLLMAsJudge` | boolean/number | 非确定 |
| 轨迹匹配 | `createTrajectoryMatchEvaluator` | boolean | 完全确定 |
| 轨迹评判 | `createTrajectoryLLMAsJudge` | boolean/number | 非确定 |
| 多轮模拟 | `multiturn` | EvaluatorResult[] | 非确定 |
