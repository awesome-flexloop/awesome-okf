---
title: Evals 评估套件
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/core-sdk
  - /datawhale/deepagents/concepts/code-module
  - /datawhale/deepagents/concepts/monorepo-architecture
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/evals/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/evals/AGENTS.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/evals/EVAL_CATALOG.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/evals/MODEL_GROUPS.md
---

# Evals 评估套件

`deepagents-evals`（位于 `libs/evals/`）是 Deep Agents SDK 的端到端行为评估套件。每个评估针对真实 LLM 运行 Agent，捕获完整轨迹（工具调用、文件变更、最终响应），并从正确性和效率两个维度评分。

## 规范入口点

评估套件的规范接口是 `deepagents-evals` 控制台脚本。Makefile 目标仍可用于与 CI 保持一致，但控制台脚本是严格超集。

### 子命令

| 子命令 | 用途 |
|--------|------|
| `run` | 运行评估套件一次（单次试验） |
| `trials` | 运行 N 次并聚合指标 |
| `aggregate` | 聚合先前写入的试验报告 |
| `radar` | 从结果生成雷达图 |
| `catalog` | 重新生成或检查 `EVAL_CATALOG.md` |
| `model-groups` | 重新生成或检查 `MODEL_GROUPS.md` |
| `list` | 发现类别/层级/模型/评估 |

大多数子命令接受 `--json`（机器可读输出）和 `--dry-run`（打印底层调用而不执行）。

## 发现命令

在运行前，可通过 CLI 发现可用内容，无需搜索源码：

```bash
deepagents-evals list categories                  # 评估类别
deepagents-evals list tiers                       # 例如 baseline | hillclimb
deepagents-evals list models --json               # 完整评估标记注册表
deepagents-evals list models --group set0         # 一个预设组
deepagents-evals list models --provider anthropic # 一个提供商
deepagents-evals list evals --category memory     # 一个类别中的评估函数
```

## 常用工作流

```bash
# 针对一个模型单次试验
deepagents-evals run --model claude-opus-4-7

# 限制类别和层级，写入 JSON 报告
deepagents-evals run \
    --model openai:gpt-5.5 \
    --eval-category memory \
    --eval-tier baseline \
    --report evals_report.json

# 三次试验并聚合统计
deepagents-evals trials --model openai:gpt-5.5 --trials 3

# 仅重跑先前试验中的失败项
deepagents-evals trials \
    --model openai:gpt-5.5 \
    --trials 1 \
    --retry-failed trial_runs/trials_summary.json

# 在 fan-out 工作流后聚合 CI 产物
deepagents-evals aggregate ./downloaded-artifacts --summary-out summary.json
```

## 默认模型环境变量

设置 `DEEPAGENTS_EVALS_MODEL` 后可省略 `--model`：

```bash
export DEEPAGENTS_EVALS_MODEL=claude-sonnet-4-6
deepagents-evals run
deepagents-evals trials --trials 3
```

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 成功 |
| 1 | 评估失败（`run` 的 pytest 非零退出；`trials`/`aggregate` 的 `counts.failed.mean > 0`；`radar` 失败） |
| 2 | 配置错误（缺少 `--model`、模型注册表导入失败、`--check` 漂移检测发现生成文件过期） |
| 3 | 无可用报告 |

> 注意：`pytest_reporter` 插件将每次试验的 pytest 退出状态重写为 0（即使个别评估失败），因此 CLI 读取 `trials_summary.json` 的 `counts.failed.mean` 判断是否返回 1，而非 `pytest_returncode`。

## 必需环境

评估套件拒绝在未启用 LangSmith tracing 的情况下启动：

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=...
```

提供商密钥（`OPENAI_API_KEY`、`ANTHROPIC_API_KEY` 等）需与所选模型匹配。

## 指标体系

### 核心指标

- **correctness** — 正确性
- **solve_rate** — 解决率
- **step_ratio** — 步骤比率
- **tool_call_ratio** — 工具调用比率
- **median_duration_s** — 中位持续时间（秒）

### 类别分数

按评估类别聚合，包括但不限于：
- `memory` — 记忆能力
- `tool_use` — 工具使用
- `file_operations` — 文件操作

### 统计量

每个指标提供 n、mean、median、stdev、min、max。

## 试验摘要 Schema

`trials_summary.json` 包含：
- `n_trials`、`model`、`sdk_version`
- `metrics`：核心指标统计
- `counts`：passed/failed/skipped/total 统计
- `category_scores`：按类别分数
- `trials`：每次试验详情（trial_index、created_at、各项指标、experiment_urls、pytest_returncode）

每次试验的 `evals_report_trial_NNN.json` 额外包含 `failures` 数组，记录失败测试名、类别和失败消息，用于 `--retry-failed`。

## Harbor 集成

套件包含 [Harbor](https://github.com/laude-institute/harbor) 集成，用于运行沙箱基准测试，如 [Terminal Bench 2.0](https://github.com/laude-institute/terminal-bench-2)。

### Harbor 适配器

- **drbench** — Deep Research Bench 适配器，位于 `harbor_adapters/drbench/`
- **contextbench** — 上下文检索基准适配器，位于 `harbor_adapters/contextbench/`

每个适配器包含 Docker 模板、judge 脚本和 vendored 数据集。

### Harbor LangGraph Agent

`deepagents_harbor/langgraph_project/langgraph.json` 是 Agent 环境安装包的权威来源。修改依赖时需同步更新 `.github/scripts/evals/prune_agent_deps.py` 中的 `PROVIDER_TO_PACKAGE`。

## 评估类别与数据集

- 评估类别定义在 `deepagents_evals/categories.json`
- 模型组定义在 `MODEL_GROUPS.md`
- 评估目录在 `EVAL_CATALOG.md`
- Vendored 数据包括 `tests/evals/tau2_airline/`（来自 tau-bench，必须保持字节一致）
- 外部基准数据在 `tests/evals/data/`（BFCL API 模拟、基准样本）
- 数据集定义在 `datasets/`（drbench-evals、context-retrieval-evals）

## CI 编排

`.github/scripts/evals/` 包含大量编排脚本：
- `shard_matrix.py` — 分片矩阵
- `unified_prep.py` — 统一准备
- `aggregate_unified.py` — 统一聚合
- `aggregate_shards.py` — 分片聚合
- `prune_agent_deps.py` — Agent 依赖修剪
- `experiment_name.py` — 实验命名
- `enumerate_tasks.py` — 任务枚举
- `analyze_eval_failures.py` — 失败分析

CI 工作流包括 `evals.yml`、`harbor.yml`、`unified_evals.yml`。

## 与其他概念的关系

- [核心SDK与三层架构](/datawhale/deepagents/concepts/core-sdk) 是被评估的对象。
- [Code终端编码Agent](/datawhale/deepagents/concepts/code-module) 的编码能力通过评估套件验证。
- [Monorepo 架构](/datawhale/deepagents/concepts/monorepo-architecture) 描述了 evals 包在仓库中的位置。
