# OpenEvals Bundle 构建日志

## 2026-08-23 v0.2.0

### R（阅读）

- 阅读参考 bundle `deepseek/lplb/` 的目录结构和 frontmatter 规范
- 阅读 JS 核心模块：`exact.ts`（44行）、`llm.ts`（628行）、`types.ts`（129行）、`utils.ts`（434行）、`index.ts`（18行）
- 阅读 JS 扩展模块：`json/match.ts`（831行）、`string/embedding_similarity.ts`、`string/levenshtein.ts`、`code/llm.ts`、`trajectory/index.ts`、`prompts/index.ts`、`simulators/multiturn.ts`
- 阅读 Python 核心模块：`__init__.py`、`exact.py`、`llm.py`（750行）、`types.py`、`utils.py`（475行）
- 阅读 Python `pyproject.toml` 确认版本和依赖
- 提取 50 条编号事实写入 `spec/facts.md`

### I（洞察）

提炼 3 个架构洞察写入 `spec/insights.md`：

1. **统一评测器协议**：scorer → _runEvaluator → EvaluatorResult 的三层抽象，可组合性与内建可观测性
2. **Exact 与 LLM-as-Judge 双模式光谱**：从精确匹配到 LLM 评判的连续光谱，JSON 匹配作为混合中点
3. **JS + Python 双语言对称架构**：共享设计契约、各自 idiomatic 实现，同步/异步差异、Zod vs Pydantic schema 差异

### E（执行）

创建文件清单：

- `spec/facts.md` — 50 条源码事实
- `spec/insights.md` — 3 个架构洞察
- `concepts/index.md` — 概念导航
- `concepts/overview.md` — 总览
- `concepts/exact-evaluators.md` — 精确评测器
- `concepts/llm-as-judge.md` — LLM-as-Judge
- `references/index.md` — 参考导航
- `references/api.md` — 完整 API 参考
- `examples/index.md` — 示例导航
- `examples/basic-evaluation.md` — 基础评测示例
- `index.md` — Bundle 首页（含 okf_version: "0.2"）
- `log.md` — 本文件

### V（验证）

- Grep 验证导出函数名在 .ts/.py 源码中存在
- frontmatter 字段完整性检查
- 交叉链接路径检查（均以 /langchain-ai/openevals/ 开头）
