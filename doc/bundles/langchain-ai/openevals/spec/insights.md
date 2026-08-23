---
type: spec
scope: openevals
name: insights
version: "0.2.0"
source: https://github.com/langchain-ai/openevals
description: OpenEvals 深度洞察——从源码中提炼的评测器协议、双模式评测与双语言架构设计
---

# OpenEvals 深度洞察

## 1. 统一评测器协议：从 scorer 到 EvaluatorResult

OpenEvals 的核心抽象是一个**极简的评测器协议**，所有评测器（无论精确匹配还是 LLM-as-Judge）都遵循同一模式：

```
评测器函数(params) → _runEvaluator(runName, scorer, feedbackKey, params) → EvaluatorResult
```

- **scorer**：纯函数，接收 `{ inputs, outputs, referenceOutputs, ... }`，返回原始分数（`boolean | number`）、带 reasoning 的元组（`[score, reasoning, metadata?]`）、或多键字典（`MultiResultScorerReturnType`）。
- **_runEvaluator**（`utils.ts`）：通用执行包装器，负责三件事：(1) 调用 scorer 获取原始分数；(2) 将原始分数标准化为统一的 `EvaluatorResult` 结构（含 `key`、`score`、`comment`、`metadata`、`sourceRunId`）；(3) 通过 LangSmith 的 `traceable` 或 `wrapEvaluator` 将评测过程记录为可观测的 trace。

这一协议设计带来两个关键优势：

1. **可组合性**：任意 scorer 都可以被 `_runEvaluator` 包装，JSON 匹配评估器内部复用 `_createLLMAsJudgeScorer` 而不经过外层包装，代码评估器也复用同一 scorer 工厂。
2. **可观测性内建**：metadata 中自动注入 `__ls_framework: "openevals"`、`__ls_evaluator: <runName>`、`__ls_language: "js"|"python"`，使评测结果在 LangSmith UI 中可按框架、评估器名称、语言筛选。

Python 侧的协议设计与 JS 完全对称，但额外提供同步/异步双版本（`_run_evaluator` / `_arun_evaluator`），因为 Python 生态中同步和异步 I/O 有明确区分。JS 侧因天然 async，统一为异步函数。

## 2. Exact 与 LLM-as-Judge 双模式：确定性与语义性的光谱

OpenEvals 在精确匹配和 LLM 评测之间构建了一条**连续的评测光谱**，而非二选一：

| 模式 | 代表评测器 | 判定方式 | 确定性 | 适用场景 |
|---|---|---|---|---|
| 精确匹配 | `exactMatch` | JSON 序列化后字符串比较 | 完全确定 | 结构化输出、工具调用参数 |
| 距离/相似度 | `levenshteinDistance`、`createEmbeddingSimilarityEvaluator` | 编辑距离/余弦相似度 | 完全确定 | 文本近似匹配、语义相似度 |
| 结构化精确匹配 | `createJsonMatchEvaluator`（无 rubric） | `_deepEqual` 递归深度比较 | 完全确定 | JSON 输出按键精确匹配 |
| 混合模式 | `createJsonMatchEvaluator`（有 rubric） | 精确键用 deepEqual，rubric 键用 LLM | 部分确定 | 结构化输出中部分字段需语义判断 |
| LLM-as-Judge | `createLLMAsJudge` | LLM 结构化输出评分 | 非确定性 | 开放式质量评估、正确性、安全性 |

JSON 匹配评估器是这一光谱的巧妙中点（`json/match.ts`）：它先将输出和参考输出按键拆分，对于不在 `rubric` 中的键使用确定性的 `_deepEqual`，对于在 `rubric` 中的键才调用 LLM 按指定标准评估。这种混合策略在保证结构化字段精确匹配的同时，允许语义字段灵活评判，且显著降低 LLM 调用成本。

LLM-as-Judge 本身也有三种评分模式（由 `constructDefaultOutputJsonSchema` 控制）：
- **布尔模式**（默认）：score 为 boolean，判断标准是否满足
- **连续模式**（`continuous: true`）：score 为 0.0-1.0 的浮点数
- **离散选择模式**（`choices: [...]`）：score 必须从指定数值列表中选择

`useReasoning`（默认 true）要求 LLM 先输出推理过程再给出分数，且推理必须以固定句式 "Thus, the score should be: SCORE_YOU_ASSIGN." 结尾，这一约束有助于提高评分一致性。

## 3. JS + Python 双语言对称架构

OpenEvals 最显著的工程特征是 **JS/TypeScript 和 Python 的双语言实现**，两者保持高度的 API 对称和模块结构对称：

```
JS (js/src/)              Python (python/openevals/)
├── exact.ts              ├── exact.py
├── llm.ts                ├── llm.py
├── types.ts              ├── types.py
├── utils.ts              ├── utils.py
├── code/                 ├── code/
├── json/                 ├── json/
├── prompts/              ├── prompts/
├── simulators/           ├── simulators/
├── string/               ├── string/
└── trajectory/           └── trajectory/
```

这种对称不是简单的代码翻译，而是**共享设计契约、各自 idiomatic 实现**：

- **共享契约**：`EvaluatorResult` 结构、prompt 模板内容、评分模式语义、MIME 类型处理逻辑在两种语言中完全一致。预置的 28+ 个 prompt 常量（quality、rag、safety、security 等）在 JS 和 Python 中导出相同的常量名。
- **idiomatic 差异**：
  - Python 提供同步/异步双版本函数（`exact_match` / `exact_match_async`），JS 统一为 async
  - Python schema 支持 Pydantic model 和 TypedDict，JS 支持 Zod schema（通过 `toJsonSchema` 转换）
  - Python 使用 `langchain_core` 的 `convert_to_openai_messages`，JS 使用 `@langchain/openai` 的 `_convertMessagesToOpenAIParams` shim
  - Python 的测试框架集成通过 `langsmith.testing._internal._TEST_CASE`，JS 通过 `langsmith/utils/jestlike` 的 `isInTestContext`
- **生态桥接**：两个实现都支持两种 judge 后端——LangChain `BaseChatModel`（通过 `withStructuredOutput`）和原生 OpenAI client（通过 `response_format: json_schema`），使用户可以在各自生态中选择最熟悉的方式。

双语言架构的战略意义在于：OpenEvals 定位为 LangChain 生态的评测层，而 LangChain 本身同时服务于 Python 和 JS/TS 开发者。对称的 API 使得团队可以在 Python 侧训练/评测原型、在 JS 侧部署线上监控，评测逻辑保持一致。
