---
type: example
scope: deepseek-math-v2
name: self-verification-pipeline
description: 运行 DeepSeekMath-V2 多轮自验证推理管线进行竞赛级证明生成
---

# 自验证管线运行示例

本文展示如何使用仓库提供的自验证推理管线进行高质量数学证明生成。

## 准备环境

```bash
cd DeepSeek-Math-V2/inference
pip install openai aiohttp tqdm
```

## 配置 API Key

编辑 `generate.py`，填入你的 API 信息：

```python
self.client = AsyncOpenAI(
    api_key="your-deepseek-api-key",
    timeout=300000,
    base_url="https://api.deepseek.com"
)
```

## 准备输入数据

创建 JSONL 格式的题目文件：

```json
{"id": "problem-1", "question": "Let n be a positive integer...", "answer": ""}
{"id": "problem-2", "question": "Prove that for any triangle...", "answer": ""}
```

仓库 `inputs/` 目录提供了示例数据集：
- `IMO2025.json` — IMO 2025 竞赛题
- `CMO2024.json` — CMO 2024 竞赛题
- `CMO2025.json` — CMO 2025 竞赛题
- `Putnam2024.json` — Putnam 2024 竞赛题

## 运行自验证管线

编辑 `run.sh`，设置输入路径和输出目录：

```bash
set -f

input_path=../inputs/IMO2025.json
output_dirname=./results/imo2025
proof_pool_dirname=${output_dirname}/proof_pool

python main.py \
    --input_paths ${input_path} \
    --output_dirname ${output_dirname} \
    --proof_pool_dirname ${proof_pool_dirname} \
    --n_best_proofs_to_sample 32 \
    --n_proofs_to_refine 1 \
    --n_agg_trials 32 \
    --n_parallel_proof_gen 128 \
    --n_verification_per_proof 64 \
    --skip_meta_verification \
    --start_round 1 \
    --max_rounds 16

set +f
```

```bash
cd inference
bash run.sh
```

## 参数调节指南

### 快速验证模式

```bash
python main.py \
    --n_best_proofs_to_sample 4 \
    --n_verification_per_proof 8 \
    --n_agg_trials 4 \
    --n_parallel_proof_gen 8 \
    --skip_meta_verification \
    --max_rounds 2
```

适合快速测试，速度快但准确率较低。

### 竞赛级模式（默认）

```bash
--n_best_proofs_to_sample 32 \
--n_verification_per_proof 64 \
--n_agg_trials 32 \
--n_parallel_proof_gen 128 \
--max_rounds 16
```

对应 Putnam 118/120 的配置级别。

### 极限模式（接近满分）

增加采样和精炼轮次：

```bash
--n_best_proofs_to_sample 64 \
--n_verification_per_proof 128 \
--n_agg_trials 64 \
--max_rounds 32
```

耗时显著增加，但可能在难题上获得更好结果。

## 断点续跑

管线支持断点续跑：
- 已完成批次记录在 `{output}.meta` 文件中
- 重新运行会自动跳过已完成的批次
- 如果更改了 `n`（每题采样数）或 `batch_size`，需要删除旧的 `.meta` 文件
- 使用 `--start_round` 参数可以从指定轮次继续

## 输出格式

输出为 JSONL 文件，每行包含：

```json
{
  "id": "problem-1",
  "question": "...",
  "output": "<think>\n[推理过程]\n</think>\n[最终证明]",
  "finish_reason": "stop",
  "score": 1,
  "round": 16
}
```

`outputs/` 目录包含官方运行结果示例，可直接参考模型输出格式和质量。
