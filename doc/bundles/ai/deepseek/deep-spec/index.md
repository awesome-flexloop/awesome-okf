---
type: bundle
okf_version: "0.2"
scope: deep-spec
name: DeepSpec Wiki
version: "1.0.0"
source: https://github.com/deepseek-ai/DeepSpec
description: DeepSpec - DeepSeek 投机解码草稿模型训练框架文档，支持 DSpark/Eagle3/DFlash 三种草稿模型架构，Qwen3/Gemma4 模型系列
---

# DeepSpec

**DeepSpec** 是 DeepSeek 开源的**投机解码（Speculative Decoding）草稿模型训练框架**，用于训练高性能的小模型（Draft Model），使其能够快速生成候选 token 供大模型（Target Model）并行验证，从而在不损失生成质量的前提下大幅加速 LLM 推理。

- **版本**：1.0.0
- **开源仓库**：[deepseek-ai/DeepSpec](https://github.com/deepseek-ai/DeepSpec)
- **支持模型系列**：Qwen3（4B/8B/14B）、Gemma4（12B）
- **草稿模型架构**：DSpark、Eagle3、DFlash
- **训练精度**：BF16 混合精度（FP32 master weight）
- **分布式策略**：FSDP（支持 ZeRO-2/3、Hybrid Shard）

---

## 核心能力

| 能力 | 说明 |
|---|---|
| **DSpark 训练** | 块级锚点采样 + 噪声嵌入 + Markov 头（vanilla/gated/rnn），多任务损失（CE+L1+置信度BCE） |
| **Eagle3 训练** | 5层目标隐状态拼接 + 单层 draft + TTT 自回归训练，Triton 融合 FusedLogSoftmaxLoss |
| **DFlash 训练** | DSpark 简化变体，markov_rank=0 纯 CE 损失，配置即变体 |
| **目标隐状态缓存** | 预计算目标模型 hidden states（mmap 格式），训练时无需前向目标模型 |
| **FSDP 分布式** | full_shard/shard_grad_op/no_shard/hybrid_shard 多种分片策略 |
| **BF16Optimizer** | FP32 master weight 副本，AdamW 精确优化 |
| **CUDAPrefetcher** | CUDA stream 重叠数据加载和 H2D 传输 |
| **原子 Checkpoint** | 临时符号链接 + os.replace 保证一致性，支持断点续训 |
| **通用评估框架** | 回调式投机解码验证（propose/verify/update），支持9个标准评测任务 |
| **置信度校准** | DSpark 置信度头训练与推理时早停，收集 ECE 校准指标 |

---

## 三种草稿模型

| 模型 | 核心方法 | 草稿层数 | 推测长度 | 关键特性 |
|---|---|---|---|---|
| **DSpark** | 块级锚点采样 + 噪声嵌入 + Markov 头 | 可配置（典型5层） | block_size（典型7） | 三种Markov头变体，CE+L1+置信度多任务损失 |
| **Eagle3** | 5层隐状态拼接 + 单层draft + TTT自回归 | 固定1层 | ttt_length（典型7） | TTT训练，FusedLogSoftmaxLoss，KV cache复用 |
| **DFlash** | 纯CE训练的DSpark简化版 | 同DSpark | block_size（典型7） | markov_rank=0，无Markov头/置信度头，配置即变体 |

---

## 文档导航

### 📘 核心概念 [concepts/](/ai/deepseek/deep-spec/concepts/)

| 文档 | 内容 |
|---|---|
| [概述](/ai/deepseek/deep-spec/concepts/overview) | DeepSpec 整体架构、三种草稿模型对比、训练与评估管线概览、包结构、快速开始 |
| [投机解码训练方法论](/ai/deepseek/deep-spec/concepts/speculative-decoding-training) | 投机解码基本原理、拒绝采样验证机制、草稿模型训练范式、置信度校准 |
| [DSpark 模型架构](/ai/deepseek/deep-spec/concepts/dspark-model) | 块级锚点采样、噪声嵌入、Markov头三种变体（vanilla/gated/rnn）、多任务损失设计、DFlash变体 |
| [Eagle3 模型架构](/ai/deepseek/deep-spec/concepts/eagle3-model) | 5层目标隐状态拼接、双维度注意力、TTT自回归训练、FusedLogSoftmaxLoss Triton融合损失 |
| [训练管线](/ai/deepseek/deep-spec/concepts/training-pipeline) | FSDP分片策略、BF16Optimizer、CUDAPrefetcher、目标隐状态缓存、可恢复采样器、原子Checkpoint |

### 📗 API 参考 [references/](/ai/deepseek/deep-spec/references/)

| 文档 | 内容 |
|---|---|
| [训练 API](/ai/deepseek/deep-spec/references/training-api) | BaseTrainer、DSparkTrainer、Eagle3Trainer、BF16Optimizer、FSDP配置、Checkpoint管理、配置系统 |
| [模型 API](/ai/deepseek/deep-spec/references/model-api) | Qwen3/Gemma4 DSpark/Eagle3模型类、Markov头（Vanilla/Gated/RNN）、FusedLogSoftmaxLoss、损失函数、配置构建 |
| [评估 API](/ai/deepseek/deep-spec/references/eval-api) | BaseEvaluator、DSpark/Eagle3评估器、verify_draft_tokens、generate_decoding_sample回调框架、DraftProposal/VerificationResult |

### 📙 代码示例 [examples/](/ai/deepseek/deep-spec/examples/)

| 示例 | 内容 |
|---|---|
| [DSpark 训练](/ai/deepseek/deep-spec/examples/training-dspark) | DSpark 草稿模型训练完整流程，包括数据准备、配置编写、训练启动、DFlash/Eagle3/Gemma4变体 |
| [投机解码评估](/ai/deepseek/deep-spec/examples/evaluation) | 模型评估方法，9个评测任务、指标解读、置信度校准与早停、Python API调用 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/deepseek-ai/DeepSpec.git
cd DeepSpec
pip install -r requirements.txt
```

### 数据准备

```bash
# 1. 下载训练数据
python scripts/data/download_and_split.py

# 2. 启动 SGLang 服务计算目标隐状态缓存
bash scripts/data/launch_sglang_server.sh --model_path Qwen/Qwen3-8B
python scripts/data/prepare_target_cache.py \
    --model_path Qwen/Qwen3-8B \
    --data_path data/train/train.jsonl \
    --output_cache_dir data/cache/qwen3_8b \
    --target_layer_ids 1,9,17,25,33
```

### 训练 DSpark

```bash
# 8 GPU 训练 DSpark Qwen3-8B
torchrun --nproc_per_node=8 train.py \
    --config config/dspark/dspark_qwen3_8b.py
```

### 评估

```bash
# 8 GPU 评估（贪婪解码）
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path <checkpoint_path> \
    --temperature 0.0
```

---

## 包结构

```
DeepSpec/
├── train.py                          # 训练入口
├── eval.py                           # 评估入口
├── config/                           # 配置文件
│   ├── dspark/                       # DSpark 配置（Qwen3-4B/8B/14B, Gemma4-12B）
│   ├── eagle3/                       # Eagle3 配置
│   └── dflash/                       # DFlash 配置
├── deepspec/
│   ├── trainer/                      # 训练模块
│   │   ├── base_trainer.py           # BaseTrainer 基类
│   │   ├── dspark_trainer.py         # DSpark 训练器
│   │   ├── eagle3_trainer.py         # Eagle3 训练器
│   │   └── ckpt_manager.py           # Checkpoint 管理
│   ├── modeling/                     # 模型模块
│   │   ├── dspark/                   # DSpark 模型（Qwen3/Gemma4 + Markov头 + 损失）
│   │   └── eagle3/                   # Eagle3 模型（Qwen3/Gemma4 + FusedLoss）
│   ├── eval/                         # 评估模块
│   │   ├── base_evaluator.py         # 通用投机解码框架
│   │   ├── dspark/                   # DSpark 评估器
│   │   └── eagle3/                   # Eagle3 评估器
│   ├── data/                         # 数据模块
│   │   ├── target_cache_dataset.py   # CacheDataset + Collator
│   │   ├── cuda_prefetcher.py        # CUDA 预取器
│   │   └── parser.py                 # 对话模板与解析
│   └── utils/                        # 工具模块
│       ├── optim.py                  # BF16Optimizer + LR Scheduler
│       ├── config.py                 # ConfigNode 配置系统
│       ├── distributed.py            # 分布式初始化 + 可恢复采样器
│       ├── metrics.py                # 分布式指标收集
│       └── sampling.py               # 采样工具函数
├── scripts/                          # 训练/评估/数据准备脚本
└── eval_datasets/                    # 评估数据集
```

---

## 相关项目

| 项目 | 关系 |
|---|---|
| [FlashMLA](/ai/deepseek/flash-mla/) | DeepSeek 高效 MLA 注意力解码核函数库，可加速目标模型在推理验证阶段的注意力计算，与 DeepSpec 训练的草稿模型协同工作——草稿模型减少目标模型前向次数，FlashMLA 加速每次前向 |
| [DeepGEMM](/ai/deepseek/deep-gemm/) | DeepSeek 高性能 JIT GEMM 核函数库，为 LLM 训练/推理提供矩阵乘法能力 |
| [DeepEP](/ai/deepseek/deep-ep/) | DeepSeek 专家并行通信库，提供 all-to-all 通信原语 |
| [DualPipe](/ai/deepseek/dual-pipe/) | DeepSeek 双向流水线并行调度算法 |
