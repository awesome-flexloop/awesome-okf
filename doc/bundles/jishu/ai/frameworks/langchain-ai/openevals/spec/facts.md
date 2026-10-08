---
type: spec
title: "OpenEvals 事实清单"
---

# OpenEvals 事实清单

## 项目元信息

F-001: 文件 `python/pyproject.toml` 第1-7行，Python 包名称为 `openevals`，版本 `0.2.1`，许可证 MIT，描述为 "Open-source evaluators for LLM applications"，要求 Python >= 3.10。

F-002: 文件 `python/pyproject.toml` 第8-13行，Python 核心依赖包括 `langchain>=0.3.18`、`langchain-openai>=0.3.6`、`langsmith>=0.3.32`、`rich>=13.9.4`。

F-003: 文件 `js/src/index.ts` 第18行，JS 包版本常量 `__version__ = "0.2.2"`。

F-004: 文件 `js/src/index.ts` 第1-16行，JS 公共导出包括：`exactMatch`（from exact.js）、`createEmbeddingSimilarityEvaluator`（from string/embedding_similarity.js）、`levenshteinDistance`（from string/levenshtein.js）、`createJsonMatchEvaluator`（from json/match.js）、`createLLMAsJudge`（from llm.js）、`createCodeLLMAsJudge`（from code/llm.js）、`createLLMSimulatedUser`（from simulators/prebuilts.js），以及 `prompts/index.js`、`trajectory/index.js`、`types.js` 的全部导出。

## 核心类型（types.ts / types.py）

F-005: 文件 `js/src/types.ts` 第3-9行，类型 `EvaluatorResult` 包含字段：`key: string`、`score: number | boolean`、`comment?: string`、`metadata?: Record<string, unknown>`、`sourceRunId?: string`。

F-006: 文件 `python/openevals/types.py` 第18-23行，Python `EvaluatorResult` 为 `TypedDict`，字段：`key: str`、`score: ScoreType`（`Union[float, bool]`）、`comment: Optional[str]`、`metadata: Optional[dict]`、`source_run_id: Optional[str]`。

F-007: 文件 `js/src/types.ts` 第11-19行，类型 `SimpleEvaluator` 为函数类型，接收 `{ inputs?, outputs, reference_outputs?, ...kwargs }`，返回 `Promise<EvaluatorResult | EvaluatorResult[]> | EvaluatorResult | EvaluatorResult[]`。

F-008: 文件 `js/src/types.ts` 第21-25行，类型 `SingleResultScorerReturnType` 为联合类型：`boolean | number | [boolean | number, string, Record<string, unknown>?] | readonly [...]`，支持单分数或带 reasoning/metadata 的元组。

F-009: 文件 `js/src/types.ts` 第27-32行，类型 `MultiResultScorerReturnType` 为字典类型，键为评分项名称，值为 `boolean | number | { score, reasoning?, sourceRunId? }`。

F-010: 文件 `js/src/types.ts` 第65-70行，类型 `FewShotExample` 包含 `inputs: unknown`、`outputs: unknown`、`score: number | boolean`、`reasoning?: string`。

F-011: 文件 `js/src/types.ts` 第81-83行，接口 `ModelClient` 具有 `chat: ModelChatClient` 属性，其中 `ModelChatClient` 具有 `completions: ChatCompletionsClient`，`ChatCompletionsClient.create(params)` 返回 `Promise<ChatCompletion>`。这是 OpenAI 客户端的结构子集。

F-012: 文件 `python/openevals/types.py` 第95行，`ToolArgsMatchMode = Literal["exact", "ignore", "subset", "superset"]`，定义工具参数匹配的四种模式。

## 精确匹配（exact.ts / exact.py）

F-013: 文件 `js/src/exact.ts` 第3-31行，内部函数 `_scorer(params)` 执行精确匹配：当 `outputs` 或 `referenceOutputs` 为 null 时抛出错误；使用 `processNestedStructures` 递归处理嵌套结构（将 undefined 转为 null、对对象键按 `localeCompare` 排序、递归处理数组和对象）；最终通过 `JSON.stringify` 比较序列化结果。

F-014: 文件 `js/src/exact.ts` 第39-43行，导出异步函数 `exactMatch(params: { outputs, referenceOutputs? })`，调用 `_runEvaluator("exact_match", _scorer, "exact_match", params)`。

F-015: 文件 `python/openevals/exact.py` 第8-14行，Python `_scorer(outputs, reference_outputs)` 使用 `json.dumps(outputs, sort_keys=True)` 序列化后比较，当任一为 None 时抛出 `ValueError`。

F-016: 文件 `python/openevals/exact.py` 第17-39行，导出同步函数 `exact_match(*, outputs, reference_outputs, **kwargs)`，通过 `_runEvaluator` 包装，若结果为 list 则取首元素。

F-017: 文件 `python/openevals/exact.py` 第42-63行，导出异步函数 `exact_match_async(*, outputs, reference_outputs, **kwargs)`，通过 `_arun_evaluator` 包装。

## LLM-as-Judge 核心（llm.ts / llm.py）

F-018: 文件 `js/src/llm.ts` 第27-42行，类型 `LLMAsJudgeScorerParams` 包含参数：`prompt`（string | RunnableInterface | 函数）、`system?`、`schema?`（JSON Schema 或 Zod）、`judge?`（ModelClient | BaseChatModel）、`model?`、`continuous?`、`choices?`、`useReasoning?`、`fewShotExamples?`。

F-019: 文件 `js/src/llm.ts` 第124-187行，函数 `constructDefaultOutputJsonSchema({ continuous, choices, useReasoning })` 构造默认输出 JSON Schema：当 `choices` 存在时 score 为带 enum 的 number；当 `continuous` 为 true 时 score 为 0-1 的 number；否则 score 为 boolean。`useReasoning` 为 true 时添加 `reasoning: string` 字段并要求以 "Thus, the score should be: SCORE_YOU_ASSIGN." 结尾。

F-020: 文件 `js/src/llm.ts` 第78-122行，函数 `appendFewShotExamples({ messages, fewShotExamples })` 找到最后一条 user 消息，将 few-shot 示例以 `<example><input>...</input><output>...</output><reasoning>...</reasoning><score>...</score></example>` XML 格式追加到内容末尾。

F-021: 文件 `js/src/llm.ts` 第215-481行，函数 `_createLLMAsJudgeScorer(params)` 返回 `LLMAsJudgeScorer` 函数。核心流程：(1) 字符串化 inputs/outputs/referenceOutputs；(2) 根据 prompt 类型（Runnable/string/函数）格式化消息；(3) 处理 attachments（支持 `{attachments}` 占位符拆分模板）；(4) 添加 system 消息和 few-shot 示例；(5) 若无 judge 则通过 `initChatModel(model)` 创建；(6) 若为 BaseChatModel 则用 `withStructuredOutput` 调用，若为 OpenAI client 则用 `response_format: { type: "json_schema" }` 调用；(7) 返回 score 或 [score, reasoning]。

F-022: 文件 `js/src/llm.ts` 第523-628行，导出函数 `createLLMAsJudge(params)` 有两个重载：无 `outputSchema` 时返回 `Promise<EvaluatorResult & Record<string, unknown>>`，有 `outputSchema` 时返回 `Promise<Record<string, unknown>>`。内部创建 scorer 后通过 `_runEvaluatorUntyped` 包装，`feedbackKey` 默认为 `"score"`，runName 为 `"llm_as_judge"` 或 `"llm_as_{feedbackKey}_judge"`。当 `outputSchema` 与 `StructuredPrompt` 同时提供时抛出错误。

F-023: 文件 `python/openevals/llm.py` 第145-343行，函数 `_create_llm_as_judge_scorer(...)` 为同步版本，逻辑与 JS 对应：支持 Runnable/string/callable 三种 prompt 类型、attachments 处理、few-shot 示例、BaseChatModel 和 ModelClient 两种 judge、`with_structured_output` 和 OpenAI `json_schema` 两种结构化输出方式。

F-024: 文件 `python/openevals/llm.py` 第346-544行，函数 `_create_async_llm_as_judge_scorer(...)` 为异步版本，使用 `ainvoke` 和 `await judge.chat.completions.create(...)`。

F-025: 文件 `python/openevals/llm.py` 第547-647行，导出 `create_llm_as_judge(...)` 同步工厂函数，参数包括 `prompt`、`feedback_key="score"`、`judge`、`model`、`system`、`continuous=False`、`choices`、`use_reasoning=True`、`few_shot_examples`、`output_schema`。

F-026: 文件 `python/openevals/llm.py` 第650-750行，导出 `create_async_llm_as_judge(...)` 异步工厂函数，参数与同步版本一致。

## 评估器运行框架（utils.ts / utils.py）

F-027: 文件 `js/src/utils.ts` 第24-57行，导出函数 `_deepEqual(a, b)` 实现递归深度相等比较：处理原始值、null、数组（逐元素比较）、对象（按键集合和递归值比较）。

F-028: 文件 `js/src/utils.ts` 第211-244行，函数 `processScore(_, value)` 处理评分数值：若为对象且含 `score` 键，返回 `[score, reasoning, metadata, sourceRunId]`；否则返回 `[value]`。

F-029: 文件 `js/src/utils.ts` 第251-406行，泛型函数 `_runEvaluator(runName, scorer, feedbackKey, extra?, ls_framework?)` 和 `_runEvaluatorUntyped(...)` 是评估器执行核心：执行 scorer，将结果标准化为 `EvaluatorResult` 或 `EvaluatorResult[]`；在测试上下文中通过 `wrapEvaluator` 包装（langsmith/utils/jestlike），否则通过 `traceable` 包装；metadata 包含 `__ls_framework`（默认 "openevals"）、`__ls_evaluator`（runName）、`__ls_language: "js"`。

F-030: 文件 `python/openevals/utils.py` 第179-300行，函数 `_run_evaluator(*, run_name, scorer, feedback_key, ls_framework="openevals", **kwargs)` 和 `_run_evaluator_untyped(...)` 为 Python 同步执行框架：通过 `@traceable(name=run_name)` 装饰；在测试用例上下文中（`_TEST_CASE.get()`）使用 `t.trace_feedback` 和 `t.log_feedback`；metadata 设置 `__ls_language: "python"`。

F-031: 文件 `python/openevals/utils.py` 第303-427行，函数 `_arun_evaluator(...)` 和 `_arun_evaluator_untyped(...)` 为异步版本，使用 `asyncio.iscoroutinefunction` 判断 scorer 是否为协程函数。

F-032: 文件 `js/src/utils.ts` 第163-209行，函数 `_attachmentToContentBlock(item)` 将附件转换为内容块：字符串 URL 转为 `image_url`；对象按 MIME 类型分发——`image/*` 转 `image_url`、`application/pdf` 转 `file`、`audio/*` 转 `input_audio`。MIME 别名规范化：`audio/mpeg` → `audio/mp3`，`audio/wave`/`audio/x-wav` → `audio/wav`。

F-033: 文件 `python/openevals/utils.py` 第79-132行，Python 版本 `_attachment_to_content_block(item)` 逻辑与 JS 一致，支持 image/*、application/pdf、audio/* 三类 MIME。

## 字符串评估器

F-034: 文件 `js/src/string/embedding_similarity.ts` 第46-93行，导出 `createEmbeddingSimilarityEvaluator({ embeddings, algorithm = "cosine" })`。支持 `"cosine"` 和 `"dot_product"` 两种算法，cosine 相似度 = 点积 / (|v1| × |v2|)，结果保留两位小数。需要 `Embeddings` 实例，调用 `embedQuery` 获取向量。

F-035: 文件 `js/src/string/levenshtein.ts` 第4-53行，内部 `scorer(outputs, referenceOutputs)` 使用动态规划计算 Levenshtein 编辑距离（删除/插入/替换代价均为1），归一化分数 = `1.0 - distance / maxLength`，完全相同返回 1.0，空串返回 1.0。导出异步函数 `levenshteinDistance(params)`。

## JSON 匹配评估器

F-036: 文件 `js/src/json/match.ts` 第17-26行，类型 `JsonMatchEvaluatorOptions` 包含：`aggregator?`（"average" | "all"）、`listAggregator?`（"average" | "all"，默认 "all"）、`rubric?`（键到评估标准的映射）、`excludeKeys?`、`judge?`、`model?`、`useReasoning?`（默认 true）、`listMatchMode?`（"superset" | "subset" | "same_elements" | "ordered"，默认 "same_elements"）。

F-037: 文件 `js/src/json/match.ts` 第39-55行，JSON 匹配使用两个 prompt：`SYSTEM_PROMPT` 指示 LLM 分别评估每个键、仅基于标准评估、None 与非 None 比较给 0 分；`USER_PROMPT` 模板包含 `{rubric}`、`{outputs}`、`{reference_outputs}`。

F-038: 文件 `js/src/json/match.ts` 第483-831行，导出 `createJsonMatchEvaluator(options)`：非 rubric 键使用 `_deepEqual` 精确匹配，rubric 键使用 `_createLLMAsJudgeScorer` 进行 LLM 评估；支持数组输出的四种匹配模式；聚合支持 "average"（均值）和 "all"（AND 逻辑）；无 aggregator 时每个键返回独立的 `EvaluatorResult`。

## 代码评估器

F-039: 文件 `js/src/code/llm.ts` 第7-16行，类型 `CodeLLMAsJudgeConfig` 继承 `createLLMAsJudge` 参数但 `prompt` 必须为 string，额外添加 `codeExtractionStrategy?`（"none" | "llm" | "markdown_code_blocks"）和 `codeExtractor?`（自定义提取函数）。

F-040: 文件 `js/src/code/llm.ts` 第33-44行，导出 `createCodeLLMAsJudge(config)`，内部先通过 `_createLLMAsJudgeScorer` 创建 scorer，再通过 `_createBaseCodeEvaluator` 包装，默认 feedbackKey 为 `"code_correctness"`，runName 为 `"code_llm_as_judge"`。

## 轨迹评估器

F-041: 文件 `js/src/trajectory/index.ts` 第1-9行，轨迹模块导出 `createTrajectoryMatchEvaluator`、`TrajectoryMatchMode` 类型、`createTrajectoryLLMAsJudge`、`TRAJECTORY_ACCURACY_PROMPT`、`TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE`。

F-042: 文件 `js/src/trajectory/` 目录包含 `match.ts`、`llm.ts`、`strict.ts`、`subset.ts`、`superset.ts`、`unordered.ts`、`utils.ts`，提供多种轨迹匹配策略。

## 预置 Prompt 库

F-043: 文件 `js/src/prompts/index.ts` 第1-37行，导出 7 大类共 28+ 个预置评估 prompt 常量：
- **quality**（7个）：`CORRECTNESS_PROMPT`、`CONCISENESS_PROMPT`、`HALLUCINATION_PROMPT`、`ANSWER_RELEVANCE_PROMPT`、`CODE_CORRECTNESS_PROMPT`、`CODE_CORRECTNESS_PROMPT_WITH_REFERENCE_OUTPUTS`、`PLAN_ADHERENCE_PROMPT`、`LAZINESS_PROMPT`
- **rag**（3个）：`RAG_GROUNDEDNESS_PROMPT`、`RAG_HELPFULNESS_PROMPT`、`RAG_RETRIEVAL_RELEVANCE_PROMPT`
- **safety**（2个）：`TOXICITY_PROMPT`、`FAIRNESS_PROMPT`
- **security**（3个）：`PII_LEAKAGE_PROMPT`、`PROMPT_INJECTION_PROMPT`、`CODE_INJECTION_PROMPT`
- **trajectory**（2+1个）：`TRAJECTORY_ACCURACY_PROMPT`、`TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE`、`TOOL_SELECTION_PROMPT`
- **conversation**（7个）：`PERCEIVED_ERROR_PROMPT`、`WINS_PROMPT`、`TASK_COMPLETION_PROMPT`、`KNOWLEDGE_RETENTION_PROMPT`、`USER_SATISFACTION_PROMPT`、`AGENT_TONE_PROMPT`、`LANGUAGE_DETECTION_PROMPT`、`SUPPORT_INTENT_PROMPT`
- **image**（2个）：`EXPLICIT_CONTENT_PROMPT`、`SENSITIVE_IMAGERY_PROMPT`
- **voice**（4个）：`AUDIO_QUALITY_PROMPT`、`TRANSCRIPTION_ACCURACY_PROMPT`、`USER_INTERRUPTS_PROMPT`、`VOCAL_AFFECT_PROMPT`

## 模拟器

F-044: 文件 `js/src/simulators/multiturn.ts` 第19-45行，类型 `MultiturnSimulationParams` 包含 `app`（应用函数）、`user`（用户模拟函数或消息列表）、`maxTurns?`、`trajectoryEvaluators?`（SimpleEvaluator 数组）、`stoppingCondition?`、`referenceOutputs?`、`threadId?`。

F-045: 文件 `js/src/simulators/multiturn.ts` 第17行，重新导出类型 `MultiturnSimulationResult`，包含 `evaluatorResults: EvaluatorResult[]` 和 `trajectory: ChatCompletionMessage[]`。

F-046: 文件 `js/src/index.ts` 第10行，导出 `createLLMSimulatedUser`（from simulators/prebuilts.js），提供预置的 LLM 模拟用户。

## Python 公共 API（__init__.py）

F-047: 文件 `python/openevals/__init__.py` 第1-19行，Python 顶层导出 8 个函数：`exact_match`、`exact_match_async`、`create_llm_as_judge`、`create_async_llm_as_judge`、`create_trajectory_match_evaluator`、`create_async_trajectory_match_evaluator`、`create_trajectory_llm_as_judge`、`create_async_trajectory_llm_as_judge`。

## Python 目录结构

F-048: Python 包 `openevals/` 包含子模块：`code/`（含 e2b/ 沙箱执行）、`json/`、`prompts/`（与 JS 对称的 8 个子目录）、`simulators/`、`string/`、`trajectory/`，以及核心文件 `exact.py`、`llm.py`、`types.py`、`utils.py`、`py.typed`。

F-049: 文件 `python/openevals/code/e2b/` 目录包含 `execution.py`、`pyright.py`、`typescript.py`（JS 侧）和 sandbox/files.py，提供基于 E2B 的代码执行和类型检查评估能力。

## JS/Python 双语言对称性

F-050: JS 和 Python 实现具有高度对称的模块结构：核心文件 `exact`/`llm`/`types`/`utils` 一一对应，子模块 `code/`、`json/`、`prompts/`、`simulators/`、`string/`、`trajectory/` 目录结构一致。主要差异：Python 提供同步/异步双版本函数（如 `create_llm_as_judge` / `create_async_llm_as_judge`），JS 统一为 async 函数；Python schema 支持 Pydantic model 和 TypedDict，JS 支持 Zod schema。
