---
type: example
scope: deep-spec
name: DSpark 草稿模型训练示例
version: "1.0.0"
source: config/dspark/dspark_qwen3_8b.py, scripts/train/train.sh, train.py
description: 使用 DeepSpec 训练 DSpark 草稿模型的完整流程，包括数据准备、配置编写、训练启动与 Checkpoint 管理
---

# DSpark 草稿模型训练示例

本文档展示如何使用 DeepSpec 训练 DSpark 草稿模型，覆盖从数据准备到训练启动的完整流程。

---

## 一、环境准备

### 1.1 安装依赖

```bash
git clone https://github.com/deepseek-ai/DeepSpec.git
cd DeepSpec
pip install -r requirements.txt
```

主要依赖：
- PyTorch（推荐 ≥ 2.1，支持 FSDP 和 flex_attention）
- Transformers（HuggingFace）
- Triton（用于 FusedLogSoftmaxLoss）
- SGLang（用于数据准备阶段运行目标模型）

### 1.2 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|---|---|---|
| GPU | 8× GPU（BF16 支持） | 8× H800/A100 80GB |
| 显存 | ≥ 40GB/GPU（小模型） | ≥ 80GB/GPU |
| 系统内存 | ≥ 256GB | ≥ 512GB（用于数据缓存） |
| 存储 | ≥ 500GB SSD | ≥ 2TB NVMe（数据缓存） |
| 互联 | NVLink/PCIe 4.0 | NVLink（FSDP 多卡训练） |

---

## 二、数据准备

DSpark 训练需要预计算的目标模型隐状态缓存。

### 2.1 下载训练数据

```bash
# 使用内置脚本下载并切分训练数据
python scripts/data/download_and_split.py \
    --output_dir data/train \
    --split_ratio 0.995  # 99.5% 训练，0.5% 验证
```

### 2.2 准备目标隐状态缓存

```bash
# 1. 启动 SGLang 服务（加载目标模型）
bash scripts/data/launch_sglang_server.sh \
    --model_path Qwen/Qwen3-8B \
    --tp 8 \
    --port 30000

# 2. 生成隐状态缓存
python scripts/data/prepare_target_cache.py \
    --model_path Qwen/Qwen3-8B \
    --data_path data/train/train.jsonl \
    --output_cache_dir data/cache/qwen3_8b \
    --target_layer_ids 1,9,17,25,33 \
    --max_length 4096 \
    --chat_template qwen \
    --server_url http://localhost:30000
```

缓存目录结构：
```
data/cache/qwen3_8b/
├── samples.idx          # 索引文件（每条40字节）
├── shard_0000.bin       # 二进制数据 shard
├── shard_0001.bin
└── metadata.json        # 缓存元数据（layer_ids, hidden_size等）
```

---

## 三、编写训练配置

创建配置文件 `config/dspark/my_dspark_qwen3_8b.py`：

```python
from deepspec.trainer import Qwen3DSparkTrainer

project_name = "deepspec"
exp_name = "dspark_block7_qwen3_8b_my"
seed = 42

model = dict(
    # 目标模型配置
    target_model_name_or_path="Qwen/Qwen3-8B",
    
    # DSpark 架构配置
    block_size=7,                # 每个 block 推测 7 个 token
    num_draft_layers=5,          # 草稿模型 5 层 Transformer
    target_layer_ids=[1, 9, 17, 25, 33],  # 提取隐状态的目标层
    mask_token_id=151669,        # Qwen3 的 mask token ID
    num_anchors=512,             # 每样本采样 512 个锚点
    
    # Markov 头配置
    markov_rank=256,             # Markov 头低维嵌入维度
    markov_head_type="vanilla",  # 可选: "vanilla", "gated", "rnn"
    
    # 置信度头配置
    enable_confidence_head=True,
    confidence_head_with_markov=True,
    confidence_head_alpha=1.0,
    
    # 损失配置
    loss_decay_gamma=4.0,        # CE 损失指数衰减系数
    ce_loss_alpha=0.1,           # CE 损失权重
    l1_loss_alpha=0.9,           # L1 分布对齐损失权重
)

train = dict(
    trainer_cls=Qwen3DSparkTrainer,
    
    # 优化器配置
    lr=6e-4,
    warmup_ratio=0.04,
    weight_decay=0.0,
    
    # 训练配置
    precision="bf16",
    local_batch_size=1,          # 每 GPU batch size
    global_batch_size=512,       # 全局 batch size
    num_train_epochs=10,
    max_grad_norm=1.0,
    max_train_steps=None,        # 用 num_train_epochs 控制
    
    # 分布式配置
    sharding_strategy="no_shard",  # 小模型可用 no_shard；大模型用 full_shard
    torch_compile=True,           # 启用 torch.compile 加速
)

data = dict(
    target_cache_path="data/cache/qwen3_8b",
    chat_template="qwen",
    max_length=4096,
    num_workers=4,
)

logging = dict(
    logging_steps=10,            # 每 10 步打印日志
    checkpointing_steps=500,     # 每 500 步保存 checkpoint
)
```

### 3.1 配置调参建议

| 参数 | 小模型（4B） | 中模型（8B/14B） | 说明 |
|---|---|---|---|
| `num_draft_layers` | 3-5 | 5-7 | 更多层 → 更高接受率，但推理更慢 |
| `block_size` | 5-7 | 7 | 更大的 block → 每步推测更多，但接受率可能下降 |
| `markov_rank` | 128-256 | 256-512 | 更高的 rank → 更强 Markov 建模 |
| `markov_head_type` | vanilla | gated/rnn | 更复杂的头需要更多训练数据 |
| `lr` | 8e-4 | 3e-4~6e-4 | 模型越小学习率可以越高 |
| `global_batch_size` | 256-512 | 512-1024 | 大 batch 训练更稳定 |
| `sharding_strategy` | no_shard | shard_grad_op/full_shard | 根据显存选择 |

---

## 四、启动训练

### 4.1 单机多卡训练

```bash
# 8 卡训练
torchrun --nproc_per_node=8 train.py \
    --config config/dspark/my_dspark_qwen3_8b.py \
    2>&1 | tee train_log.txt
```

### 4.2 使用训练脚本

```bash
bash scripts/train/train.sh \
    --config config/dspark/my_dspark_qwen3_8b.py \
    --nnodes 1 \
    --nproc_per_node 8
```

### 4.3 多节点训练

```bash
# 在每个节点上运行（设置正确的 MASTER_ADDR 和 MASTER_PORT）
# Node 0:
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=0 \
    --master_addr=10.0.0.1 --master_port=29500 \
    train.py --config config/dspark/my_dspark_qwen3_8b.py

# Node 1:
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=1 \
    --master_addr=10.0.0.1 --master_port=29500 \
    train.py --config config/dspark/my_dspark_qwen3_8b.py
```

### 4.4 命令行覆盖配置

```bash
# 通过 --opts 覆盖任意配置项
torchrun --nproc_per_node=8 train.py \
    --config config/dspark/my_dspark_qwen3_8b.py \
    --opts train.lr=3e-4 \
    --opts model.block_size=5 \
    --opts train.max_train_steps=5000
```

---

## 五、训练监控

### 5.1 TensorBoard

```bash
tensorboard --logdir ~/tensorboard --port 6006
```

关键指标：
- `train/loss`：总训练损失
- `train/ce_loss`：CE 损失分量
- `train/l1_loss`：L1 分布对齐损失分量
- `train/confidence_loss`：置信度损失分量
- `train/lr`：当前学习率
- `train/grad_norm`：梯度范数
- `train/accuracy`：预测准确率
- `train/accept_rate`：模拟接受率

### 5.2 控制台输出

训练时每 `logging_steps` 步打印进度：
```
[step 100/10000] loss=2.345 ce_loss=0.234 l1_loss=2.111 lr=5.8e-4 grad_norm=0.876 time=0.45s/step
```

---

## 六、Checkpoint 管理

### 6.1 Checkpoint 结构

```
~/checkpoints/deepspec/dspark_block7_qwen3_8b_my/
├── step_latest -> step_1000       # 原子符号链接指向最新 checkpoint
├── step_500/                      # 第 500 步 checkpoint
│   ├── train_config.py            # 配置文件副本
│   ├── config.json                # HuggingFace 模型配置
│   ├── model.safetensors          # 模型权重（rank0 保存）
│   └── training_state.rank{0-7}.pt  # 各 rank 的训练状态
└── step_1000/                     # 第 1000 步 checkpoint
    └── ...
```

### 6.2 恢复训练

训练脚本会自动发现 `step_latest` 符号链接并恢复：

```bash
# 如果 checkpoint 目录存在，自动从最新 checkpoint 恢复
torchrun --nproc_per_node=8 train.py \
    --config config/dspark/my_dspark_qwen3_8b.py
```

恢复内容包括：
- 模型权重
- 优化器状态（包括 FP32 master weights）
- 学习率调度器状态
- 所有 RNG 状态（torch/cuda/numpy/python）
- 训练进度（next_micro_step）

### 6.3 从指定 Checkpoint 评估

```bash
torchrun --nproc_per_node=8 eval.py \
    --target_name_or_path Qwen/Qwen3-8B \
    --draft_name_or_path ~/checkpoints/.../step_1000 \
    --max-new-tokens 2048 \
    --temperature 0.0
```

---

## 七、训练 DFlash（纯 CE 变体）

DFlash 通过配置实现，无需单独代码。创建配置文件 `config/dflash/my_dflash_qwen3_8b.py`：

```python
from deepspec.trainer import Qwen3DSparkTrainer

project_name = "deepspec"
exp_name = "dflash_qwen3_8b"
seed = 42

model = dict(
    target_model_name_or_path="Qwen/Qwen3-8B",
    block_size=7,
    num_draft_layers=5,
    target_layer_ids=[1, 9, 17, 25, 33],
    mask_token_id=151669,
    num_anchors=512,
    markov_rank=0,                # 关键：禁用 Markov 头
    markov_head_type="vanilla",   # 不使用，但需要设置
    enable_confidence_head=False,
    confidence_head_alpha=0.0,    # 关键：禁用置信度损失
    loss_decay_gamma=0.0,         # 无衰减（或设为正值）
    ce_loss_alpha=1.0,            # 纯 CE
    l1_loss_alpha=0.0,            # 无 L1 损失
)

train = dict(
    trainer_cls=Qwen3DSparkTrainer,  # 复用 DSpark 训练器
    # ... 其余训练配置与 DSpark 相同
)
```

---

## 八、训练 Eagle3 模型

```python
from deepspec.trainer import Qwen3Eagle3Trainer

model = dict(
    target_model_name_or_path="Qwen/Qwen3-8B",
    target_layer_ids=[1, 9, 17, 25, 33],  # Eagle3 要求恰好5层
    ttt_length=7,                 # TTT 自回归步数
    draft_num_hidden_layers=1,    # Eagle3 固定1层
    step_loss_decay=0.8,          # TTT 步损失衰减
)

train = dict(
    trainer_cls=Qwen3Eagle3Trainer,  # 使用 Eagle3 训练器
    torch_compile=False,             # Eagle3 首次运行可能不建议 compile
    # ... 其余训练配置类似
)
```

---

## 九、Gemma4 模型训练

```python
from deepspec.trainer import Gemma4DSparkTrainer

model = dict(
    target_model_name_or_path="google/gemma-4-12b-it",
    block_size=7,
    num_draft_layers=5,
    target_layer_ids=[1, 9, 17, 25, 33, 41][:5],  # 根据实际层数调整
    # Gemma4 特有配置会自动处理
)

train = dict(
    trainer_cls=Gemma4DSparkTrainer,
    # ...
)
```

---

## 十、常见问题

### Q1: CUDA OOM 怎么办？
- 减小 `local_batch_size`（如改为 1）
- 使用 `sharding_strategy="full_shard"`（ZeRO-3）
- 减小 `num_anchors`（如改为 256）
- 启用 gradient checkpointing（如果代码支持）

### Q2: 训练损失不收敛？
- 检查 `target_layer_ids` 是否正确（层数从 0 开始）
- 确认隐状态缓存的版本与模型匹配（运行 `validate_train_cache`）
- 降低学习率或增加 warmup 步数
- 检查数据缓存的 `hidden_size` 是否与模型配置一致

### Q3: 接受率低怎么办？
- 增加草稿模型层数（`num_draft_layers`）
- 调整损失权重（增加 `l1_loss_alpha` 比例）
- 使用 `gated` 或 `rnn` Markov 头
- 增加训练数据量或训练步数

---

## 十一、相关链接

- [/deepseek/deep-spec/concepts/dspark-model](/deepseek/deep-spec/concepts/dspark-model) — DSpark 架构详解
- [/deepseek/deep-spec/concepts/training-pipeline](/deepseek/deep-spec/concepts/training-pipeline) — 训练管线详解
- [/deepseek/deep-spec/references/training-api](/deepseek/deep-spec/references/training-api) — 训练 API 完整参考
- [/deepseek/deep-spec/examples/evaluation](/deepseek/deep-spec/examples/evaluation) — 模型评估示例
