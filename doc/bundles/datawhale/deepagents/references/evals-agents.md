---
title: libs/evals/AGENTS.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/evals/AGENTS.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/evals/AGENTS.md
---

# libs/evals/AGENTS.md 引用

Deep Agents Evals 包的 Agent 快速参考指南。

## 核心内容

- **规范入口点**：`deepagents-evals` 控制台脚本，Makefile 目标用于 CI 一致性
- **子命令**：run（单次试验）、trials（N 次聚合）、aggregate（聚合报告）、radar（雷达图）、catalog（检查/生成 EVAL_CATALOG.md）、model-groups（检查/生成 MODEL_GROUPS.md）、list（发现类别/层级/模型/评估）
- **通用选项**：`--json`（机器可读输出）、`--dry-run`（打印调用不执行）
- **发现命令**：list categories/tiers/models/evals，支持 --group、--provider、--category 过滤
- **默认模型环境变量**：`DEEPAGENTS_EVALS_MODEL`
- **退出码**：0=成功，1=评估失败，2=配置错误，3=无可用报告
- **必需环境**：LANGSMITH_TRACING=true、LANGSMITH_API_KEY、提供商密钥
- **trials_summary.json Schema**：包含 n_trials、model、sdk_version、metrics（correctness/solve_rate/step_ratio/tool_call_ratio/median_duration_s）、counts（passed/failed/skipped/total）、category_scores、trials 数组
- **pytest_reporter 插件**：将 pytest 退出码重写为 0，CLI 通过 counts.failed.mean 判断失败
- **失败重试**：per-trial 报告包含 failures 数组，用于 --retry-failed
- **Vendored 数据**：tau2_airline/data/ 来自 tau-bench，必须保持字节一致
- **Harbor 依赖同步**：langgraph.json 的 dependencies 变更需同步 prune_agent_deps.py 的 PROVIDER_TO_PACKAGE
- **与 Makefile 关系**：控制台脚本是严格超集，Makefile 目标仍为 CI 调用形式

## 相关概念

- [Evals评估套件](/datawhale/deepagents/concepts/evals-suite)
