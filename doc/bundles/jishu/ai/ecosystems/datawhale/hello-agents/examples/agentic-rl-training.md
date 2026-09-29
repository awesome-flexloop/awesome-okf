---
title: Agentic-RL训练Pipeline
type: example
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/agentic-rl
  - /datawhale/hello-agents/concepts/evaluation-methods
  - /datawhale/hello-agents/references/chapter11-agentic-rl
sources:
  - https://github.com/datawhalechina/hello-agents/tree/main/code/chapter11
---

# Agentic-RL训练Pipeline

本示例展示从SFT到GRPO的完整Agent强化学习训练流程，代码位于`code/chapter11/`目录。

## 代码结构

| 文件 | 内容 |
|------|------|
| `00_quick_test.py` | 快速环境验证 |
| `01_dataset_loading.py` | 数据集加载与预处理 |
| `02_reward_functions.py` | 奖励函数定义 |
| `03_lora_configuration.py` | LoRA参数配置 |
| `04_sft_training.py` | 监督微调训练 |
| `05_grpo_training.py` | GRPO强化学习训练 |
| `06_complete_pipeline.py` | 完整端到端pipeline |
| `07_model_evaluation.py` | 模型评估 |
| `08_distributed_training.py` | 分布式训练 |
| `accelerate_configs/` | DeepSpeed配置 |

## 环境配置

```bash
pip install torch transformers datasets peft trl accelerate
```

`.env`配置：
```bash
LLM_API_KEY="YOUR-API-KEY"
LLM_MODEL_ID="YOUR-MODEL"
LLM_BASE_URL="YOUR-URL"
```

## 训练流程

### 第一步：SFT监督微调

```python
# 04_sft_training.py 核心结构
from transformers import TrainingArguments
from trl import SFTTrainer

training_args = TrainingArguments(
    output_dir="./sft_output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    peft_config=lora_config,  # LoRA参数高效微调
)
trainer.train()
```

SFT阶段让模型学会指令遵循和基本的Agent输出格式（Thought/Action/Observation结构）。

### 第二步：GRPO强化学习

GRPO的核心思想是对每个问题采样一组回答，用组内相对奖励作为优势估计，无需critic网络：

```python
# 05_grpo_training.py 核心结构
from trl import GRPOTrainer, GRPOConfig

grpo_config = GRPOConfig(
    output_dir="./grpo_output",
    num_generations=8,       # 每个问题采样8个回答
    max_completion_length=1024,
    learning_rate=1e-6,
    beta=0.04,               # KL惩罚系数
)

trainer = GRPOTrainer(
    model=model,
    args=grpo_config,
    train_dataset=dataset,
    reward_funcs=[reward_function],  # 奖励函数
)
trainer.train()
```

### 奖励函数设计

```python
# 02_reward_functions.py
def math_reward(completions, **kwargs):
    """数学问题奖励：答案正确+1，错误0"""
    rewards = []
    for completion, answer in zip(completions, kwargs["answer"]):
        predicted = extract_answer(completion)
        rewards.append(1.0 if predicted == answer else 0.0)
    return rewards

def format_reward(completions, **kwargs):
    """格式奖励：遵循Agent输出格式+0.1"""
    rewards = []
    for completion in completions:
        has_thought = "Thought:" in completion
        has_action = "Action:" in completion
        rewards.append(0.1 if (has_thought and has_action) else 0.0)
    return rewards

def tool_use_reward(completions, **kwargs):
    """工具使用奖励：正确调用工具+0.2"""
    ...
```

Agentic RL的奖励可以是多维度的组合：正确性奖励（稀疏）+ 格式奖励（密集）+ 工具使用奖励（密集）。

### LoRA配置

```python
# 03_lora_configuration.py
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,                     # 低秩矩阵维度
    lora_alpha=32,            # 缩放系数
    target_modules=[          # 目标模块
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)
```

LoRA只训练少量低秩矩阵（通常<1%原模型参数量），大幅降低显存需求。

## 分布式训练

```bash
# 多GPU DDP
accelerate launch --config_file accelerate_configs/multi_gpu_ddp.yaml 08_distributed_training.py

# DeepSpeed ZeRO2
accelerate launch --config_file accelerate_configs/deepspeed_zero2.yaml 08_distributed_training.py

# DeepSpeed ZeRO3（分片模型参数）
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml 08_distributed_training.py
```

### DeepSpeed ZeRO层级
- **ZeRO2**：分割优化器状态和梯度，模型参数仍复制
- **ZeRO3**：分割模型参数、梯度和优化器状态，支持更大模型

## 完整Pipeline

`06_complete_pipeline.py`串联全流程：
```
数据加载 → SFT训练 → 保存SFT模型 → GRPO训练 → 最终评估
```

## 模型评估

```python
# 07_model_evaluation.py
# 训练后在测试集上评估
# 使用准确率、格式合规率、工具调用成功率等指标
```

## 训练洞察

1. **SFT是基础**：先通过SFT让模型掌握Agent输出格式，再用GRPO优化策略
2. **奖励设计是关键**：稀疏奖励（答案正确性）+ 密集奖励（格式/工具使用）的组合更稳定
3. **GRPO的优势**：相比PPO省去critic网络，降低约50%显存占用
4. **LoRA的权衡**：r=16通常足够，更大的r不一定带来显著提升但增加成本
5. **数据质量决定上限**：SFT数据要多样化覆盖不同Agent场景，GRPO问题要有明确可验证答案
