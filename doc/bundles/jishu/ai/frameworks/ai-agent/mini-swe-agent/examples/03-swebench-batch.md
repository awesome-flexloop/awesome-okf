---
type: Example
title: "示例三：SWE-bench 批处理与单实例调试"
description: "mini-extra swebench 批处理、swebench-single 单实例、Docker 架构限制、预测文件与评测边界；官方文档命令，未在本机实测"
tags: [SWE-bench, 批处理, swebench-single, Docker, 评测]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:03:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-mini-swe-agent
    resource: /references/repo-source.md
    title: "仓库事实清单（F-035 ~ F-090）"
  - id: official-swebench
    resource: https://mini-swe-agent.com/latest/usage/swebench/
    title: "官方文档：SWE-bench"
---

# 示例三：SWE-bench 批处理与单实例调试

> ⚠️ **执行边界**：以下命令来自官方 `usage/swebench.md`（F-068、F-069），**未在本机执行**。真实运行需要 Docker（x86 Linux 镜像）、模型 API Key，并会产生费用。

## 1. 两个脚本

| 脚本 | 用途 | 输出 |
|---|---|---|
| `mini-extra swebench` | 批量跑整个子集，多 worker 并行 | `preds.json` |
| `mini-extra swebench-single` | 单实例交互式调试 | 终端轨迹，不产出 preds |

两者都通过 `mini-extra` 入口暴露（F-047）。

## 2. 批处理

```bash
mini-extra swebench \
  --model anthropic/claude-sonnet-4-5-20250929 \
  --subset verified \
  --split test \
  --workers 4
```

常用参数（F-068）：

| 参数 | 作用 | 默认 |
|---|---|---|
| `-o/--output` | 输出目录 | 当前目录 |
| `-m/--model` | 模型名 | 环境变量 |
| `-c/--config` | 配置文件 | `swebench.yaml` |
| `-w/--workers` | 并行 worker 数 | 1 |
| `--subset` | 数据集子集或路径 | `lite` |
| `--split` | 数据 split | `dev` |
| `--slice` | 切片，如 `0:5` | 全部 |
| `--filter` | 按实例 ID 正则过滤 | 无 |
| `--shuffle` | 打乱顺序 | False |
| `--redo-existing` | 重跑已存在实例 | False |
| `--environment-class` | 环境类型 | `docker` 推荐 |

## 3. 单实例调试

```bash
mini-extra swebench-single \
  --subset verified \
  --split test \
  -m anthropic/claude-sonnet-4-5-20250929 \
  -i sympy__sympy-15599
```

也可以用索引：

```bash
mini-extra swebench-single --subset verified --split test -m ... -i 0
```

加 `--exit-immediately` 可跳过退出确认（F-069）。

## 4. 预测文件与评分

1. 批处理成功后，每个实例的补丁会汇总到预测文件（官方称 `preds.json`）。
2. 这个文件**不是分数**；要用 SWE-bench 官方评测器（或 `sb-cli`）提交，才能得到 resolved 率。
3. 官方文档给了 `sb-cli submit swe-bench_verified test --predictions_path preds.json --run_id ...` 的示例流程（F-068 同页）。

## 5. 环境与架构限制

1. 官方 Docker 镜像默认按 **x86 Linux** 构建；ARM/Apple Silicon 可能无法直接运行（F-068 的 warning）。
2. 需要 Docker 守护进程；HPC 环境可换 `--environment-class singularity`（F-057）。
3. 批量并行会同时起多个容器，注意 CPU/内存/磁盘与 API 限流。
4. 每个实例默认 `cost_limit=3.0`（F-048），强模型跑复杂实例可能触顶。

## 6. 一次典型调试流程

```text
1. 选一个实例（--filter 或 -i）
2. 用 swebench-single 跑，观察轨迹
3. 看 exit_status：Submitted / LimitsExceeded / TimeExceeded / RepeatedFormatError
4. 如果是格式错误，换 textbased 或检查模型 tool calling
5. 如果是步数/成本触顶，调 step_limit/cost_limit 或换更强模型
6. 单实例通过后，再跑 --slice 0:5 小批
7. 最后跑全量 --workers 4
```

## 7. 结果解读的边界

1. **74% 是 Gemini 3 Pro 的单点成绩**（F-070、F-088），不是你的模型/配置的预期值。
2. SWE-bench verified 是人工校验子集，不等同于 full；博客表中的 full 数字为单源（F-015、F-016、F-018）。
3. 预测补丁的格式、测试环境、超时设置都会影响最终 resolved 率。
4. 不要用“跑通脚本”代替“分数提升”；脚本成功只说明预测文件生成了。

## 8. 成本控制建议

| 措施 | 作用 |
|---|---|
| 先 `--slice 0:5` | 用 5 个实例估算单价与耗时 |
| 设 `--workers 2~4` | 避免并发过高触发限流 |
| 设 `agent.cost_limit` | 单实例硬上限 |
| 设 `MSWEA_GLOBAL_COST_LIMIT` | 全局硬上限（F-059） |
| 固定模型快照 | 避免“同一实验”跨版本漂移 |

## 9. 下一步

- 理解评测含义：[concepts/06-benchmarks-and-boundaries](../concepts/06-benchmarks-and-boundaries.md)
- 理解环境后端：[concepts/03-execution-environments](../concepts/03-execution-environments.md)
