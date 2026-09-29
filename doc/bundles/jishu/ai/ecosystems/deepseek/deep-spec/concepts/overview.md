---
type: concept
scope: deep-spec
name: DeepSpec 概述
version: "1.0.0"
source: README.md, train.py, eval.py, deepspec/__init__.py, config/
description: DeepSpec 投机解码草稿模型训练框架整体架构、支持模型、训练与评估管线、包结构与快速开始
---

# DeepSpec 概述

DeepSpec 是 DeepSeek 开源的**投机解码（Speculative Decoding）草稿模型训练框架**，专为训练高性能草稿模型（Draft Model）而设计。框架支持 DSpark、Eagle3 和 DFlash 三种草稿模型架构，原生兼容 Qwen3 和 Gemma4 两大模型系列，提供完整的分布式训练、Checkpoint 管理和多任务评估管线。

---

## 一、核心定位

投机解码是加速大语言模型推理的关键技术：用一个小的草稿模型快速生成候选 token，再用大模型并行验证，从而在不损失生成质量的前提下减少大模型的串行前向调用次数。DeepSpec 的核心目标是**训练高质量的草稿模型**，使得草稿生成的 token 具有高接受率，最大化推理加速比。

DeepSpec 的核心特性：

1. **多架构支持**：DSpark（块级锚点采样 + Markov 头）、Eagle3（TTT 自回归）、DFlash（纯 CE 简化版）三种草稿模型架构
2. **双模型系列**：原生支持 Qwen3（4B/8B/14B）和 Gemma4（12B）模型系列
3. **高效训练管线**：FSDP 分布式训练 + BF16 混合精度优化器 + CUDA 数据预取 + 原子 Checkpoint
4. **目标隐状态缓存**：预计算并缓存目标模型 hidden states，训练时无需前向目标模型，大幅节省显存和计算
5. **Triton 融合损失**：FusedLogSoftmaxLoss 通过 Triton 融合 log_softmax + 交叉熵，提升训练效率
6. **完整评估框架**：通用回调式投机解码验证框架，覆盖 9 个标准评测任务，支持置信度校准分析

---

## 二、三种草稿模型

| 模型 | 核心方法 | 草稿层数 | 推测长度 | 关键特性 |
|---|---|---|---|---|
| **DSpark** | 块级锚点采样 + 噪声嵌入 + Markov 头 | 可配置（典型5层） | block_size（典型7） | 多任务损失（CE+L1+置信度），三种 Markov 头变 |
| **Eagle3** | 5层目标隐状态拼接 + 单层draft + TTT | 固定1层 | ttt_length（典型7） | TTT自回归训练，FusedLogSoftmaxLoss，KV cache复用 |
| **DFlash** | 纯CE训练的DSpark简化版 | 同DSpark | block_size（典型7） | markov_rank=0，无Markov头，无置信度头，配置即变体 |

### 2.1 DSpark 方法概要

DSpark 采用**块级并行预测**策略：
- 从序列中采样锚点位置，以 block（如7个token）为单位并行预测
- 使用噪声嵌入：block 起始位置为真实 token，其余位置填充 mask token
- Transformer backbone 一次性输出整个 block 的 base logits
- Markov 头利用前一 token 的低维嵌入自回归修正 logits
- 支持置信度头预测每个 token 的接受概率

### 2.2 Eagle3 方法概要

Eagle3 基于 EAGLE-3 风格设计：
- 从目标模型的恰好5层提取 hidden states，拼接后投影
- 草稿模型仅1层 Transformer，输入维度为 hidden_size × 2（token embedding + 目标隐状态）
- 训练时使用 TTT（Test-Time Training）范式：在 block 内自回归多步预测
- 每步损失按 `step_loss_decay^step` 指数衰减
- 使用 Triton 融合的 soft 交叉熵损失

---

## 三、训练管线架构

```
目标模型（冻结，BF16）
    │
    ▼ 预计算隐状态缓存
target_cache/（mmap二进制格式）
    │
    ▼ CacheDataset + CUDAPrefetcher
FSDP 包装的 Draft 模型（BF16 计算 + FP32 master weight）
    │
    ├── DSpark: compute_dspark_loss(CE + L1 + Confidence BCE)
    └── Eagle3: compute_eagle3_loss(TTT 多步 soft CE + FusedLogSoftmaxLoss)
    │
    ▼ BF16Optimizer (AdamW + CosineWarmupScheduler)
    │
    ▼ 原子 Checkpoint（HuggingFace 格式 + 训练状态）
```

关键组件：
- **FSDP 分片**：支持 full_shard/shard_grad_op/no_shard/hybrid_shard 等策略
- **BF16Optimizer**：内部维护 FP32 master 参数副本，确保优化精度
- **CUDAPrefetcher**：通过 CUDA stream 重叠数据加载和 H2D 传输
- **StatelessResumableDistributedSampler**：支持确定性恢复的流式采样器
- **原子 Checkpoint**：临时符号链接 + os.replace 保证一致性，支持训练中断恢复

---

## 四、评估管线架构

```
输入 Prompt → Tokenize → generate_decoding_sample 循环
    │
    ├── init_context: 初始化 KV cache 和模型状态
    ├── propose: Draft 模型生成候选 token 块
    │     ├── DSpark: forward_dspark_draft_block + 自回归采样
    │     └── Eagle3: TTT 步循环自回归采样
    ├── verify: 目标模型验证（拒绝采样）
    │     └── target_probs vs draft_probs → 接受/拒绝 + 残差采样
    ├── post_verify: 收集诊断指标（置信度校准）
    └── update: 更新 KV cache 和隐状态
    │
    ▼ 统计指标（接受率、验证率、逐位置接受率）
```

9 个评测任务覆盖三大类能力：
- **数学推理**：GSM8K、MATH-500、AIME25
- **代码生成**：HumanEval、MBPP、LiveCodeBench
- **对话能力**：MT-Bench、Alpaca、Arena-Hard v2

---

## 五、Python 包结构

```
deepspec/
├── __init__.py                    # 包入口（__all__ 为空）
├── trainer/                       # 训练模块
│   ├── __init__.py                # 导出 BaseTrainer + 4个具体Trainer
│   ├── base_trainer.py            # BaseTrainer 基类（训练循环、FSDP、优化器）
│   ├── dspark_trainer.py          # DSpark 训练器（Qwen3/Gemma4）
│   ├── eagle3_trainer.py          # Eagle3 训练器（Qwen3/Gemma4）
│   └── ckpt_manager.py            # Checkpoint 保存/加载/发现
├── modeling/                      # 模型模块
│   ├── __init__.py                # 导出4个模型类 + DSparkForwardOutput
│   ├── dspark/                    # DSpark 模型
│   │   ├── common.py              # DSparkForwardOutput, AcceptRatePredictor, anchor采样, 噪声嵌入
│   │   ├── markov_head.py         # Markov 头（Vanilla/Gated/RNN + build_markov_head）
│   │   ├── loss.py                # compute_dspark_loss
│   │   ├── qwen3/                 # Qwen3 DSpark 实现
│   │   │   ├── config.py          # build_qwen3_draft_config
│   │   │   └── modeling.py        # Qwen3DSparkModel, Attention, DecoderLayer
│   │   └── gemma4/                # Gemma4 DSpark 实现
│   │       ├── config.py          # build_gemma4_draft_config
│   │       └── modeling.py        # Gemma4DSparkModel
│   └── eagle3/                    # Eagle3 模型
│       ├── common.py              # Eagle3ForwardOutput, BlockMask创建, 特征提取
│       ├── loss.py                # FusedLogSoftmaxLoss, compute_eagle3_loss
│       ├── qwen3/                 # Qwen3 Eagle3 实现
│       │   ├── config.py          # build_qwen3_eagle3_config
│       │   └── modeling.py        # Qwen3Eagle3Model, Attention, DecoderLayer
│       └── gemma4/                # Gemma4 Eagle3 实现
│           ├── config.py          # build_gemma4_eagle3_config
│           └── modeling.py        # Gemma4Eagle3Model
├── eval/                          # 评估模块
│   ├── __init__.py                # 导出 BaseEvaluator + 4个Evaluator + 数据类
│   ├── base_evaluator.py          # BaseEvaluator, generate_decoding_sample, verify_draft_tokens
│   ├── dspark/                    # DSpark 评估
│   │   ├── evaluator.py           # Qwen3/Gemma4 DSpark 评估器
│   │   └── draft_ops.py           # DSpark draft 前向和提议构建
│   └── eagle3/                    # Eagle3 评估
│       └── evaluator.py           # Qwen3/Gemma4 Eagle3 评估器
├── data/                          # 数据模块
│   ├── __init__.py                # 导出 CacheDataset, CacheCollator 等
│   ├── target_cache_dataset.py    # CacheDataset, CacheCollator, ConversationCollator
│   ├── cuda_prefetcher.py         # CUDAPrefetcher（CUDA stream 预取）
│   ├── jsonl_dataset.py           # JsonLineDataset（mmap 读取 JSONL）
│   └── parser.py                  # ChatTemplate, TemplateRegistry, 消息编码
└── utils/                         # 工具模块
    ├── __init__.py                # seed_all, get_git_sha, get_git_diff
    ├── config.py                  # ConfigNode, load_config, parse_opts_to_config
    ├── distributed.py             # init_dist, StatelessResumableDistributedSampler
    ├── optim.py                   # BF16Optimizer, CosineAnnealingWarmupLR
    ├── io.py                      # ensure_dir, safe_symlink
    ├── metrics.py                 # add_metric, flush（分布式指标收集）
    ├── sampling.py                # logits_to_probs, sample_tokens, sample_residual
    ├── training_logger.py         # 训练日志（TensorBoard、进度打印）
    ├── hfai_suspend.py            # hfai 集群暂停信号处理
    └── constant/
        └── public.py              # 公共常量（模型路径、缓存目录等）
```

---

## 六、配置文件结构

```
config/
├── dspark/                        # DSpark 配置
│   ├── dspark_qwen3_4b.py
│   ├── dspark_qwen3_8b.py         # 典型：block_size=7, num_draft_layers=5, markov_rank=256
│   ├── dspark_qwen3_14b.py
│   └── dspark_gemma4_12b.py
├── eagle3/                        # Eagle3 配置
│   ├── eagle3_qwen3_4b.py
│   ├── eagle3_qwen3_8b.py         # 典型：ttt_length=7, draft_num_hidden_layers=1
│   ├── eagle3_qwen3_14b.py
│   └── eagle3_gemma4_12b.py
└── dflash/                        # DFlash 配置（复用 DSpark trainer）
    ├── dflash_qwen3_4b.py
    ├── dflash_qwen3_8b.py
    ├── dflash_qwen3_14b.py
    └── dflash_gemma4_12b.py
```

---

## 七、快速开始

### 7.1 数据准备

```bash
# 1. 下载并预处理训练数据
python scripts/data/download_and_split.py

# 2. 启动 SGLang 服务生成目标模型隐状态缓存
bash scripts/data/launch_sglang_server.sh
python scripts/data/prepare_target_cache.py
```

### 7.2 训练 DSpark

```bash
bash scripts/train/train.sh --config config/dspark/dspark_qwen3_8b.py
# 或直接使用 torchrun
torchrun --nproc_per_node=8 train.py --config config/dspark/dspark_qwen3_8b.py
```

### 7.3 评估

```bash
bash scripts/eval/eval.sh \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path <checkpoint_path>
```

---

## 八、典型配置示例（DSpark Qwen3-8B）

| 参数 | 值 | 说明 |
|---|---|---|
| block_size | 7 | 每块推测 7 个 token |
| num_draft_layers | 5 | 草稿模型 5 层 |
| target_layer_ids | [1,9,17,25,33] | 从 Qwen3-8B 的第1/9/17/25/33层提取隐状态 |
| markov_rank | 256 | Markov 头低维嵌入维度 |
| markov_head_type | vanilla | 基础 Markov 头 |
| num_anchors | 512 | 每样本采样 512 个锚点 |
| lr | 6e-4 | 学习率 |
| global_batch_size | 512 | 全局 batch size |
| precision | bf16 | BF16 混合精度 |
| loss_decay_gamma | 4.0 | CE 损失指数衰减系数 |
| ce_loss_alpha / l1_loss_alpha | 0.1 / 0.9 | CE 和 L1 损失权重 |

---

## 九、相关链接

### 核心概念
- /deepseek/deep-spec/concepts/speculative-decoding-training — 投机解码训练方法论
- /deepseek/deep-spec/concepts/dspark-model — DSpark 架构详解
- /deepseek/deep-spec/concepts/eagle3-model — Eagle3 架构详解
- /deepseek/deep-spec/concepts/training-pipeline — 训练管线详解

### API 参考
- /deepseek/deep-spec/references/training-api — 训练 API 参考
- /deepseek/deep-spec/references/model-api — 模型 API 参考
- /deepseek/deep-spec/references/eval-api — 评估 API 参考

### 代码示例
- /deepseek/deep-spec/examples/training-dspark — DSpark 训练示例
- /deepseek/deep-spec/examples/evaluation — 评估使用示例

### 相关项目
- [/deepseek/flash-mla/](../../flash-mla/index.md) — FlashMLA 高效 MLA 注意力解码核函数，可用于加速目标模型的验证前向
