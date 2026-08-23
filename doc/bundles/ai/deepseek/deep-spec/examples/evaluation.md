---
type: example
scope: deep-spec
name: 投机解码评估示例
version: "1.0.0"
source: eval.py, deepspec/eval/base_evaluator.py, scripts/eval/eval.sh
description: 使用 DeepSpec 评估框架对训练好的草稿模型进行投机解码评估，涵盖9个评测任务、指标解读与置信度校准
---

# 投机解码评估示例

本文档展示如何使用 DeepSpec 的评估框架对训练好的草稿模型进行投机解码评估，包括评估命令、参数配置、指标解读和置信度校准分析。

---

## 一、评估概述

DeepSpec 的评估系统实现了完整的投机解码验证流程：
- 草稿模型生成候选 token（propose）
- 目标模型并行验证（verify，拒绝采样）
- 统计接受率、验证率等关键指标
- 覆盖 9 个标准评测任务

---

## 二、基础评估

### 2.1 命令行评估

```bash
# 8 GPU 评估 DSpark 模型（贪婪解码）
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path ~/checkpoints/deepspec/dspark_block7_qwen3_8b/step_5000 \
    --max-new-tokens 2048 \
    --temperature 0.0 \
    --seed 980406
```

### 2.2 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `--target_name_or_path` | str | 必填 | 目标模型路径或 HuggingFace 名称 |
| `--draft_name_or_path` | str | 必填 | 草稿模型 Checkpoint 路径 |
| `--max-new-tokens` | int | 2048 | 最大生成 token 数 |
| `--temperature` | float | 1.0 | 采样温度（0=贪婪，1=标准采样） |
| `--confidence-threshold` | float | 0.0 | 置信度早停阈值（0=收集校准指标） |
| `--tensorboard-dir` | str | None | TensorBoard 日志目录 |
| `--step` | int | None | TensorBoard 记录的训练步数 |
| `--seed` | int | 980406 | 随机种子 |

### 2.3 使用评估脚本

```bash
bash scripts/eval/eval.sh \
    --target Qwen/Qwen3-8B \
    --draft ~/checkpoints/.../step_5000 \
    --temperature 0.0 \
    --max-new-tokens 2048
```

---

## 三、评估任务

评估自动遍历 9 个评测任务：

| 任务 | 样本数 | 能力域 | 评估方式 |
|---|---|---|---|
| **GSM8K** | 500 | 小学数学推理 | 精确匹配（EM） |
| **MATH-500** | 500 | 竞赛数学 | 精确匹配 |
| **AIME25** | 30 | 高级数学竞赛 | 精确匹配 |
| **HumanEval** | 164 | Python 代码生成 | 单元测试通过 |
| **MBPP** | 256 | 基础 Python 编程 | 单元测试通过 |
| **LiveCodeBench** | 500 | 竞赛级代码生成 | 单元测试通过 |
| **MT-Bench** | 80 | 多轮对话 | GPT-4 评分 |
| **Alpaca** | 500 | 指令跟随 | 参考回答比对 |
| **Arena-Hard v2** | 500 | 挑战性对话 | 胜率评估 |

---

## 四、评估指标

### 4.1 投机解码核心指标

评估输出以下关键指标：

| 指标 | 含义 | 理想值 | 说明 |
|---|---|---|---|
| **acceptance_length** | 平均每次验证接受的 token 数 | 越高越好 | 反映草稿模型质量，典型值 2-5 |
| **draft_tokens_per_proposal** | 平均每次提议的 draft token 数 | 接近 block_size/ttt_length | 反映早停效果 |
| **verify_rate** | 目标模型调用率（每生成 1 token 需要几次前向） | 越低越好 | verify_rate = 1/(acceptance_length+1) |
| **accept_rate@k** | 第 k 个位置的接受率 | 越高越好 | 逐位置统计，通常越靠后越低 |
| **speedup** | 理论加速比 | 越高越好 | ≈ acceptance_length + 1（忽略草稿成本） |

### 4.2 输出示例

```
=== Evaluation Results ===

Task: gsm8k (500 samples)
  acceptance_length: 3.42
  draft_tokens_per_proposal: 6.85
  verify_rate: 0.227
  accept_rate@1: 0.89
  accept_rate@2: 0.78
  accept_rate@3: 0.67
  accept_rate@4: 0.55
  accept_rate@5: 0.44
  accept_rate@6: 0.33
  accept_rate@7: 0.25
  Task Score: 0.742

Task: humaneval (164 samples)
  acceptance_length: 2.85
  draft_tokens_per_proposal: 6.52
  verify_rate: 0.260
  ...
  Task Score: 0.683

=== Summary ===
  Average acceptance_length: 3.14
  Average verify_rate: 0.242
  Theoretical speedup: 4.13x
```

### 4.3 指标解读

- **acceptance_length = 3.14**：平均每次目标模型前向接受 3.14 个 draft token
- **verify_rate = 0.242**：每生成 1 个 token 只需要 0.242 次目标模型前向（4.13x 加速）
- **accept_rate@k 递减**：越靠后的 draft token 接受率越低，符合直觉
- **任务差异**：数学/代码任务接受率通常低于对话任务（更难预测）

---

## 五、不同温度设置

### 5.1 贪婪解码（temperature=0）

```bash
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path <draft_path> \
    --temperature 0.0 \
    --max-new-tokens 2048
```

适用于需要确定性输出的场景（代码生成、数学推理）。

### 5.2 采样解码（temperature=1.0）

```bash
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path <draft_path> \
    --temperature 1.0 \
    --max-new-tokens 2048
```

适用于创造性生成（对话、写作）。注意：采样温度下接受率通常低于贪婪解码。

---

## 六、置信度校准与早停

### 6.1 收集校准指标

默认 `--confidence-threshold 0.0` 时，DSpark 评估器会收集置信度校准数据：

```bash
# 收集校准指标（早停禁用）
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path <draft_path> \
    --confidence-threshold 0.0 \
    --tensorboard-dir ~/tensorboard/confidence_calib \
    --step 5000
```

校准指标包括：
- 每个置信度区间的实际接受率
- ECE（Expected Calibration Error）
- 置信度-接受率曲线

### 6.2 使用置信度早停

```bash
# 使用置信度早停（阈值=0.5）
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path <draft_path> \
    --confidence-threshold 0.5
```

早停机制：
- 当 confidence_head 预测当前位置接受概率低于阈值时，停止生成后续 draft token
- 阈值越高，draft 越保守，每次提议 token 数减少但浪费更少
- 典型阈值范围：0.3-0.7

### 6.3 阈值选择建议

| 阈值 | draft_tokens/proposal | 接受率 | 适用场景 |
|---|---|---|---|
| 0.0（关闭） | ≈ block_size | 基准 | 校准分析、最大接受率 |
| 0.3 | 4-5 | 略提升 | 平衡速度和接受率 |
| 0.5 | 3-4 | 明显提升 | 保守策略，减少浪费 |
| 0.7 | 2-3 | 高 | 极低延迟优先 |

---

## 七、评估 Eagle3 模型

```bash
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path ~/checkpoints/deepspec/eagle3_ttt7_qwen3_8b/step_5000 \
    --max-new-tokens 2048 \
    --temperature 0.0
```

Eagle3 评估器的差异：
- `max_proposal_tokens = ttt_length`（通常为7）
- 提议阶段使用 TTT 自回归（1层 draft model，KV cache 复用）
- 初始化时用 shifted prompt ids 预填充 draft KV cache
- 更新时裁剪 draft cache 并 extend 已验证 token

---

## 八、评估 Gemma4 模型

```bash
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path google/gemma-4-12b-it \
    --draft_name_or_path <gemma4_draft_path> \
    --max-new-tokens 2048 \
    --temperature 0.0
```

评估器自动根据 draft 模型 config 的 `architectures[0]` 选择对应评估器：
- `Gemma4DSparkModel` → `Gemma4DSparkEvaluator`
- `Gemma4Eagle3Model` → `Gemma4Eagle3Evaluator`

---

## 九、Python API 直接调用

除了命令行，也可以直接在 Python 中调用评估框架：

```python
import torch
import argparse
from deepspec.eval.dspark import Qwen3DSparkEvaluator

# 1. 构造参数
args = argparse.Namespace(
    target_name_or_path="Qwen/Qwen3-8B",
    draft_name_or_path="<draft_path>",
    max_new_tokens=2048,
    temperature=0.0,
    confidence_threshold=0.0,
    tensorboard_dir=None,
    step=None,
    seed=980406,
    tasks=[("gsm8k", 500), ("humaneval", 164)],
)

# 2. 单 GPU 初始化
evaluator = Qwen3DSparkEvaluator(local_rank=0, args=args)

# 3. 对单个样本生成
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
input_text = "Question: What is 2+2?\nAnswer:"
input_ids = tokenizer.encode(input_text, return_tensors="pt").cuda()

result = evaluator.generate_one_sample(input_ids[0])
print(f"Output: {tokenizer.decode(result.output_ids)}")
print(f"Acceptance lengths: {result.acceptance_lengths}")
print(f"Verify count: {result.verify_count}")
print(f"Total tokens: {len(result.output_ids) - len(input_ids[0])}")
print(f"Speedup: {(len(result.output_ids) - len(input_ids[0])) / result.verify_count:.2f}x")

evaluator.clean_up()
```

---

## 十、投机解码过程可视化

以下是一个投机解码步骤的示意（block_size=3）：

```
Step 1:
  Prefix: "The quick brown"
  Draft proposes: "fox jumps over" (3 tokens)
  Target verifies: "fox" ✓, "jumps" ✓, "over" ✗
  Residual samples: "dog"
  Accepted: "fox jumps" + bonus "dog"
  Output: "...fox jumps dog"

Step 2:
  Prefix: "The quick brown fox jumps dog"
  Draft proposes: "runs fast today" (3 tokens)
  Target verifies: "runs" ✓, "fast" ✓, "today" ✓
  Bonus token: "." 
  Accepted: "runs fast today" + bonus "."
  Output: "...runs fast today."

...
```

统计：2 次目标模型前向生成了 6 个 token，加速比 3x。

---

## 十一、常见问题

### Q1: 评估时 OOM？
- 使用更少 GPU 或减小 `max-new-tokens`
- 确保使用 `EVAL_ATTN_IMPLEMENTATION = "sdpa"`（而非 flex_attention）
- 评估时不需要 FSDP，单卡加载模型即可

### Q2: 接受率很低？
- 检查草稿模型是否训练充分（查看训练 loss 曲线）
- 确认 `target_layer_ids` 在训练和评估时一致
- 确认温度设置一致（训练时的数据分布与评估温度匹配）
- 尝试更大的草稿模型或更长的训练

### Q3: 生成质量下降？
- 投机解码是无损加速，生成质量应该与目标模型完全一致
- 如果质量下降，检查草稿模型和目标模型的词表是否一致
- 确认 stop token 处理正确

### Q4: 如何对比不同 checkpoint？
- 使用相同的 seed 和 temperature
- 对比 acceptance_length 和 verify_rate
- 在所有 9 个任务上取平均，避免单一任务波动

---

## 十二、相关链接

- [/deepseek/deep-spec/concepts/speculative-decoding-training](/ai/deepseek/deep-spec/concepts/speculative-decoding-training) — 投机解码原理详解
- [/deepseek/deep-spec/references/eval-api](/ai/deepseek/deep-spec/references/eval-api) — 评估 API 完整参考
- [/deepseek/deep-spec/examples/training-dspark](/ai/deepseek/deep-spec/examples/training-dspark) — 模型训练示例
- [/deepseek/flash-mla/](/ai/deepseek/flash-mla/) — FlashMLA 注意力核函数，可加速目标模型验证前向
