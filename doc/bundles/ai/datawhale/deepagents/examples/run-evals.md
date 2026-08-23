---
title: 运行评估试验
type: example
bundle: /datawhale/deepagents
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/evals/AGENTS.md
---

# 运行评估试验

使用 `deepagents-evals` 对 Deep Agents SDK 进行端到端行为评估。

## 前置条件

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=...
export ANTHROPIC_API_KEY=...  # 或其他提供商密钥
```

## 单次试验

```bash
deepagents-evals run --model claude-opus-4-7
```

限制类别和层级并输出报告：

```bash
deepagents-evals run \
    --model openai:gpt-5.5 \
    --eval-category memory \
    --eval-tier baseline \
    --report evals_report.json
```

## 多次试验聚合

```bash
deepagents-evals trials --model openai:gpt-5.5 --trials 3
```

## 设置默认模型

```bash
export DEEPAGENTS_EVALS_MODEL=claude-sonnet-4-6
deepagents-evals run
deepagents-evals trials --trials 3
```

## 发现可用内容

```bash
deepagents-evals list categories
deepagents-evals list tiers
deepagents-evals list models --json
deepagents-evals list evals --category memory
```

## 重跑失败项

```bash
deepagents-evals trials \
    --model openai:gpt-5.5 \
    --trials 1 \
    --retry-failed trial_runs/trials_summary.json
```

## 聚合 CI 产物

```bash
deepagents-evals aggregate ./downloaded-artifacts --summary-out summary.json
```

## 生成雷达图

```bash
deepagents-evals radar
```

## 退出码

- `0`：成功
- `1`：评估失败
- `2`：配置错误
- `3`：无可用报告

## 相关概念

- [Evals评估套件](/ai/datawhale/deepagents/concepts/evals-suite)
