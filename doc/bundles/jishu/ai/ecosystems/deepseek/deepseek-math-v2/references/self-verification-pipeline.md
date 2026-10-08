---
type: reference
scope: deepseek-math-v2
name: self-verification-pipeline
description: DeepSeekMath-V2 自验证推理管线配置与参数说明
---

# 自验证推理管线

DeepSeekMath-V2 的核心创新是**自验证数学推理**——模型不仅生成证明，还能验证自身推理的正确性，并通过迭代精炼提高答案质量。仓库提供了完整的多轮生成-验证-精炼推理管线。

## 管线流程

```
初始生成 (n_best_proofs_to_sample 份)
    ↓
验证 (每证明 n_verification_per_proof 次)
    ↓
元验证 (可选)
    ↓
精炼 (n_proofs_to_refine 份)
    ↓
重复多轮 (max_rounds)
    ↓
聚合 (n_agg_trials 次)
```

## 管线参数（run.sh）

| 参数 | 示例值 | 说明 |
|---|---|---|
| `--input_paths` | `../IMO2025.json,../CMO2024.json` | 输入题目路径（逗号分隔） |
| `--output_dirname` | 自定义 | 结果输出目录 |
| `--proof_pool_dirname` | `{output}/proof_pool` | 每题的证明池，存储生成过的所有证明 |
| `--n_best_proofs_to_sample` | 32 | 初始采样的最佳证明数量 |
| `--n_proofs_to_refine` | 1 | 每轮选择精炼的证明数量 |
| `--n_agg_trials` | 32 | 最终答案聚合采样次数 |
| `--n_parallel_proof_gen` | 128 | 并行证明生成数 |
| `--n_verification_per_proof` | 64 | 每个证明的验证采样次数（多数投票） |
| `--skip_meta_verification` | flag | 跳过元验证步骤（加速推理） |
| `--start_round` | 1 | 起始轮次（用于断点续跑） |
| `--max_rounds` | 16 | 最大迭代精炼轮数 |

## 核心机制

### 1. 验证器（Verifier）

验证器使用 `proof_verification` 模板对每个证明打分（0/0.5/1）：
- 每次验证独立采样，通过多次采样（`n_verification_per_proof=64`）取多数投票
- 这缓解了单次验证的随机性

### 2. 元验证器（Meta-Verifier）

使用 `meta_verification` 模板评估验证器的判定质量：
- 检查验证器指出的缺陷是否合理
- 检查验证器的评分是否与发现的缺陷一致
- 可以跳过以加速推理

### 3. 生成-验证差距（Generation-Verification Gap）

核心训练策略：
- 训练一个准确的验证器作为奖励模型
- 使用验证器奖励训练证明生成器
- 随着生成器变强，通过扩展验证计算自动标注新的难验证证明
- 这些新标注数据用于进一步训练验证器，维持差距

### 4. 迭代精炼

每轮选择最优证明进行精炼：
- 综合验证分数和元验证分数选择候选
- 使用 `proof_refinement` 模板，结合已有证明和评估意见生成改进版
- 精炼结果放回证明池，进入下一轮验证

## 输入数据格式

输入为 JSON 文件（如 `inputs/IMO2025.json`），每题包含：

```json
{
  "problem_id": "IMO2025-P1",
  "question": "Let n be a positive integer...",
  "answer": "(expected answer if known)"
}
```

## 输出数据格式

输出为 JSONL 文件，每题包含原始信息加上：
- `output`：模型完整输出（含 `<think>` 推理链和解答）
- `finish_reason`：生成终止原因

已提供的输出示例（`outputs/` 目录）：
- `IMO2025.jsonl` — IMO 2025 解答
- `CMO2024.jsonl` — CMO 2024 解答
- `Putnam2024.jsonl` — Putnam 2024 解答（118/120 分）
- `IMO-ProofBench-Basic.jsonl` — IMO-ProofBench 基础版
- `IMO-ProofBench-Advanced.jsonl` — IMO-ProofBench 高级版
