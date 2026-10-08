---
type: concept
title: "参数高效微调与人类对齐"
bundle: "/datawhale/base-llm"
description: "PEFT 技术谱系（Adapter/Prefix/Prompt Tuning）、LoRA 低秩分解原理与实践、QLoRA 4-bit 量化微调、RLHF 三阶段对齐流程、DPO 直接偏好优化、LLaMA-Factory 实战。"
sources:
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/01_PEFT.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/02_lora.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/03_peft_lora.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/04_qwen2.5_qlora.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter12/01_RLHF.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter12/02_llama_factory.md
related:
  - /datawhale/base-llm/concepts/pretrained-models
  - /datawhale/base-llm/concepts/llm-architecture
  - /datawhale/base-llm/concepts/inference-deployment
---

# 参数高效微调与人类对齐

## 核心理解

全量微调大模型需要更新所有参数并为每个任务存储完整模型副本，成本极高。参数高效微调（PEFT）通过只训练少量参数解决成本问题；人类对齐（RLHF/DPO）则解决模型输出"符合人类偏好"的问题。两者共同构成了大模型从预训练基座走向实际应用的关键环节。教程通过 LoRA 理论推导、peft 库实战、Qwen2.5 QLoRA 私有数据微调、LLaMA-Factory DPO 对齐，形成完整的知识闭环。

## PEFT 技术谱系

### 为什么需要 PEFT

- 全量微调 7B 模型需 ~14GB 显存（FP16）+ 优化器状态等，总计可达 80GB+。
- 每个下游任务存储一份完整模型副本，存储和切换成本高。
- PEFT 只需训练和存储 0.1% 以下的参数，显存可降至单卡。

### 主要 PEFT 方法

| 方法 | 思路 | 优点 | 缺点 |
|------|------|------|------|
| **Adapter Tuning** | 在 Transformer 层间插入小型瓶颈网络 | 模块化 | 引入推理延迟（串行） |
| **Prefix Tuning** | 在输入端添加可学习的虚拟 token 前缀 | 不修改模型 | 占用序列长度 |
| **Prompt Tuning** | Prefix Tuning 的简化，仅在输入层加软提示 | 极简 | 小模型效果差 |
| **P-Tuning v2** | 每层都加可学习前缀 | 深层优化 | 实现较复杂 |
| **LoRA** | 低秩分解权重更新矩阵 | 参数少/零延迟 | 需选择目标模块 |

## LoRA（Low-Rank Adaptation）

### 核心假设

大语言模型是**过参数化**的，微调时权重更新矩阵 ΔW 具有很低的"内在秩"（Intrinsic Rank）。这意味着 ΔW 虽然维度高，但有效信息可被远小于其规模的低秩矩阵表示。

### 低秩分解

用两个小矩阵 A 和 B 的乘积近似 ΔW：

$$\Delta W = B \cdot A, \quad h = W_0 x + \frac{\alpha}{r} BAx$$

- $W_0 \in \mathbb{R}^{d \times k}$（冻结的预训练权重）
- $B \in \mathbb{R}^{d \times r}$，$A \in \mathbb{R}^{r \times k}$
- 秩 $r \ll \min(d, k)$，通常取 8/16/32/64
- 参数量从 $d \times k$ 降至 $d \times r + r \times k$

### 初始化与缩放

- **A 矩阵**：高斯随机初始化（$A \sim \mathcal{N}(0, \sigma^2)$）。
- **B 矩阵**：零初始化（$B = 0$），确保训练开始时旁路输出为零，从预训练状态出发。
- **缩放因子 α**：前向计算乘以 $\alpha/r$，调整 r 时无需重新调学习率。

### 核心优势

1. **参数效率极高**：checkpoint 可缩小 10,000 倍（350GB→35MB），节省 2/3 显存，训练提速约 25%。
2. **零额外推理延迟**：训练后可将 BA 合并回 W₀（$W' = W_0 + \frac{\alpha}{r}BA$），推理结构与原模型完全一致。
3. **效果媲美全量微调**：直接作用于权重矩阵，比 Prompt Tuning 更深入影响模型行为。
4. **不占用输入长度**：不添加 virtual token。
5. **可组合性**：LoRA 可与 Prefix Tuning 等正交组合。

### 实践要点

- **目标模块选择**：LoRA 论文实验表明，同时适配 W_q 和 W_v 效果较好；现代实践中通常适配所有线性层（q/k/v/o/gate/up/down）。
- **秩 r 选择**：r 越大表达能力越强但参数越多；需在任务复杂度和参数效率间权衡。
- **多任务服务**：不同 LoRA 适配器可热插拔，共享基座模型。

## QLoRA（Quantized LoRA）

QLoRA 将 LoRA 与 4-bit 量化结合，实现单卡微调大模型：

- **4-bit NormalFloat（NF4）**：针对正态分布权重优化的量化数据类型。
- **双重量化（Double Quantization）**：对量化常数本身再量化，进一步节省显存。
- **分页优化器（Paged Optimizers）**：利用 CPU 内存处理显存峰值，防止 OOM。
- 效果：4-bit 量化基座 + LoRA 适配器，在单张 48GB 卡上微调 65B 模型，性能媲美全量微调。

### Qwen2.5 私有数据微调实战

`code/C11/04_qwen2.5_qlora.ipynb` 演示完整流程：
1. 私有数据集构建（`04_dataset_gen.ipynb`，blackwukong 数据集）。
2. 4-bit 量化加载 Qwen2.5 基座模型。
3. 配置 LoRA（目标模块、秩、alpha）。
4. SFT 训练与推理测试。

## RLHF（Reinforcement Learning from Human Feedback）

### 三阶段流程

```
预训练模型
    ↓
阶段1: SFT（Supervised Fine-Tuning，监督微调）
    ├── 用高质量指令-回答对微调基座模型
    └── 让模型学会遵循指令格式
    ↓
阶段2: RM（Reward Model，奖励模型训练）
    ├── 对同一 prompt 采样多个回答
    ├── 人类标注员排序回答质量
    └── 训练奖励模型输出标量奖励分数
    ↓
阶段3: PPO（Proximal Policy Optimization）
    ├── SFT 模型作为策略（Policy）生成回答
    ├── RM 对回答打分作为奖励
    ├── PPO 优化策略最大化奖励
    └── KL 散度约束防止偏离 SFT 模型太远
```

### PPO 的关键组件

- **Policy 模型**：待优化的语言模型（初始为 SFT 模型）。
- **Reference 模型**：冻结的 SFT 模型，用于计算 KL 惩罚。
- **Reward 模型**：提供奖励信号。
- **Value 模型**：估计状态价值，降低策略梯度方差。
- **KL 惩罚**：$R(x,y) = R_{RM}(x,y) - \beta \log(\pi_\theta(y|x)/\pi_{ref}(y|x))$，防止模型为追求高分而退化。

### RLHF 的挑战

- 流程复杂，需维护 4 个模型（Policy/Ref/RM/Value）。
- 超参数敏感，训练不稳定。
- 人类标注成本高。

## DPO（Direct Preference Optimization）

DPO 是 RLHF 的简化方案，通过数学变换**绕过显式奖励模型和 PPO**：

- 直接在偏好数据（chosen/rejected 对）上优化策略模型。
- 损失函数隐式包含奖励模型和 KL 约束。
- 只需一个模型、一个阶段，训练更简单稳定。
- LLaMA-Factory 等框架支持 DPO 训练。

## LLaMA-Factory 实战

LLaMA-Factory 是一站式大模型微调框架，支持：
- 多种微调方法：LoRA/QLoRA/全量微调。
- 多种对齐方法：SFT/DPO/PPO/ORPO。
- 数百种模型架构（LLaMA/Qwen/ChatGLM 等）。
- Web UI 界面，零代码微调。
- 数据集格式化和评估集成。

`code/C12/02_llama_factory.md` 演示了基于 LLaMA-Factory 的 DPO 对齐实战。

## 代码示例

| 文件 | 内容 |
|------|------|
| `code/C11/03_peft_pythia-2.8b.ipynb` | peft 库 LoRA 微调 Pythia-2.8b |
| `code/C11/04_dataset_gen.ipynb` | 私有数据集生成 |
| `code/C11/04_qwen2.5_qlora.ipynb` | Qwen2.5 QLoRA 微调实战 |
| `code/C11/04_qwen2.5_test.ipynb` | 微调后模型测试 |

## 延伸阅读

- 前置：[大模型架构深入](llm-architecture.md)
- 部署：[量化推理与服务部署](inference-deployment.md)——量化是 QLoRA 和推理部署的共同技术
- 示例代码：[C11 LoRA 微调代码](../examples/index.md#c11-参数高效微调)
