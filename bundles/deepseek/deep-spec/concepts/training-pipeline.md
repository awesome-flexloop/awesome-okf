---
type: concept
scope: deep-spec
name: DeepSpec 训练管线
version: "1.0.0"
source: deepspec/trainer/base_trainer.py, deepspec/trainer/ckpt_manager.py, deepspec/utils/optim.py, deepspec/data/cuda_prefetcher.py, deepspec/data/target_cache_dataset.py, deepspec/utils/distributed.py
description: DeepSpec 训练管线架构，包括 FSDP 分片策略、BF16Optimizer、CUDAPrefetcher、StatelessResumableDistributedSampler、目标隐状态缓存与原子 Checkpoint 管理
---

# DeepSpec 训练管线

DeepSpec 的训练管线是一个完整的分布式训练系统，集成了 FSDP 分片训练、BF16 混合精度优化、CUDA 数据预取、目标隐状态缓存、可恢复采样和原子 Checkpoint 管理，为 DSpark/Eagle3/DFlash 三种草稿模型提供统一的训练基础设施。

---

## 一、管线总体架构

```
数据准备（离线）
  │
  ├── 原始数据（JSONL 对话格式）
  ├── SGLang 服务运行目标模型
  ├── prepare_target_cache.py → 目标隐状态缓存（mmap二进制）
  │
  ▼
训练阶段
  │
  ├── ConfigNode 配置系统（Python 模块 + --opts 覆盖）
  │
  ├── 分布式初始化（NCCL, init_process_group）
  │
  ├── 模型构建
  │     ├── 加载目标模型（CPU, BF16, eval模式）→ 提取 embed_tokens, lm_head
  │     ├── 构建 draft 模型（随机初始化）
  │     ├── initialize_embeddings_and_head() → 拷贝并冻结
  │     ├── 可选 torch.compile
  │     └── FSDP 包装
  │
  ├── 数据加载
  │     ├── CacheDataset（mmap 读取隐状态缓存）
  │     ├── StatelessResumableDistributedSampler（可恢复流式采样）
  │     ├── CacheCollator（padding + attention_mask）
  │     └── CUDAPrefetcher（CUDA stream 预取）
  │
  ├── 优化器
  │     └── BF16Optimizer（FP32 master weight + AdamW + CosineWarmupScheduler）
  │
  ├── 训练循环
  │     ├── 梯度累积（global_batch_size / local_batch_size / world_size）
  │     ├── FSDP.clip_grad_norm_ 梯度裁剪
  │     ├── optimizer.step()（FP32更新 → 拷贝回BF16）
  │     ├── 指标收集与 TensorBoard 日志
  │     ├── 原子 Checkpoint 保存
  │     └── SuspendController 暂停信号处理
  │
  └── 训练完成 → clean_up()
```

---

## 二、配置系统

### 2.1 Python 模块配置

DeepSpec 使用 Python 文件作为配置格式，通过 `importlib` 动态加载：

```python
# config/dspark/dspark_qwen3_8b.py 示例
project_name = "deepspec"
exp_name = "dspark_block7_qwen3_8b"
seed = 42

model = dict(
    target_model_name_or_path="Qwen/Qwen3-8B",
    block_size=7,
    num_draft_layers=5,
    target_layer_ids=[1, 9, 17, 25, 33],
    mask_token_id=151669,
    num_anchors=512,
    markov_rank=256,
    markov_head_type="vanilla",
    confidence_head_alpha=1.0,
    loss_decay_gamma=4.0,
    ce_loss_alpha=0.1,
    l1_loss_alpha=0.9,
)

train = dict(
    trainer_cls=Qwen3DSparkTrainer,
    lr=6e-4,
    warmup_ratio=0.04,
    weight_decay=0.0,
    precision="bf16",
    local_batch_size=1,
    global_batch_size=512,
    num_train_epochs=10,
    max_grad_norm=1.0,
    sharding_strategy="no_shard",
    torch_compile=True,
)

data = dict(
    target_cache_path="path/to/cache",
    chat_template="qwen",
    max_length=4096,
    num_workers=4,
)

logging = dict(
    logging_steps=10,
    checkpointing_steps=500,
)

def finalize_cfg(cfg):
    """可选：配置后处理钩子"""
    return cfg
```

### 2.2 ConfigNode

```python
class ConfigNode(dict):
    """支持属性访问的字典"""
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, value):
        self[key] = value
    def copy(self):
        return ConfigNode(super().copy())
```

### 2.3 命令行覆盖

```bash
# --opts 支持点分路径覆盖，yaml.safe_load 解析值
python train.py --config config.py --opts train.lr=1e-3 --opts model.block_size=5
```

---

## 三、分布式训练

### 3.1 初始化

```python
def init_dist(local_rank, timeout_minutes=60):
    # 从环境变量读取
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    master_addr = os.environ["MASTER_ADDR"]
    master_port = os.environ["MASTER_PORT"]
    
    # 计算全局 rank（多节点）
    node_rank = rank // torch.cuda.device_count()
    local_world_size = torch.cuda.device_count()
    global_rank = node_rank * local_world_size + local_rank
    
    dist.init_process_group(
        backend="nccl",
        rank=global_rank,
        world_size=world_size,
        timeout=timedelta(minutes=timeout_minutes),
    )
    torch.cuda.set_device(local_rank)
    device = torch.device("cuda", local_rank)
    return device, global_rank, world_size
```

### 3.2 FSDP 分片策略

```python
_SHARDING_STRATEGIES = {
    "full_shard": ShardingStrategy.FULL_SHARD,          # ZeRO Stage 3：参数、梯度、优化器状态全分片
    "shard_grad_op": ShardingStrategy.SHARD_GRAD_OP,    # ZeRO Stage 2：梯度和优化器状态分片
    "no_shard": ShardingStrategy.NO_SHARD,              # DDP：仅数据并行
    "hybrid_shard": ShardingStrategy.HYBRID_SHARD,      # 节点内 FULL_SHARD + 节点间 DDP
    "hybrid_shard_zero2": ShardingStrategy._HYBRID_SHARD_ZERO2,  # 节点内 SHARD_GRAD_OP + 节点间 DDP
}
```

| 策略 | 适用场景 | 显存节省 | 通信开销 |
|---|---|---|---|
| `no_shard` | 单节点/小模型 | 无 | 最低（仅梯度 all-reduce） |
| `shard_grad_op` | ZeRO-2 | 中等 | 梯度 reduce-scatter + all-gather |
| `full_shard` | ZeRO-3，大模型 | 最大 | 参数 all-gather 前向/反向 |
| `hybrid_shard` | 多节点大模型 | 大 | 节点内高带宽，节点间低 |

### 3.3 FSDP 包装

```python
model = FSDP(
    model,
    sharding_strategy=_SHARDING_STRATEGIES[sharding_strategy],
    mixed_precision=MixedPrecision(
        param_dtype=precision_dtype,  # torch.bfloat16
        reduce_dtype=precision_dtype,
        buffer_dtype=precision_dtype,
    ),
    device_id=device,
    use_orig_params=True,
)
```

---

## 四、BF16Optimizer（混合精度优化器）

### 4.1 设计原理

BF16Optimizer 是 DeepSpec 自定义的混合精度优化器，核心思想是：
- **模型参数**：BF16 格式存储和计算（节省显存，利用 BF16 张量核心）
- **主权重副本**：FP32 格式，用于优化器更新（保证更新精度）
- **梯度**：BF16 反向 → 转 FP32 → 更新 FP32 master → 拷贝回 BF16 模型

```
模型前向/反向: BF16 参数 → BF16 梯度
    │
    ▼
optimizer.step():
    1. grad_fp32 = model.grad.to(fp32)
    2. optimizer_fp32.step()  # AdamW 更新 FP32 master weight
    3. scheduler.step()       # 学习率调度
    4. model.param.copy_(master_param_fp32.to(bf16))
```

### 4.2 实现

```python
class BF16Optimizer:
    def __init__(self, model, lr, total_steps, warmup_ratio, weight_decay=0.0):
        # 创建 FP32 master 参数副本
        self.master_params = [p.detach().float().clone() for p in model.parameters()]
        for p in self.master_params:
            p.requires_grad_(True)
        
        # 使用 FP32 参数创建 AdamW 优化器
        self.optimizer = torch.optim.AdamW(
            self.master_params, lr=lr, weight_decay=weight_decay,
            betas=(0.9, 0.95), eps=1e-8,
        )
        
        # Cosine Warmup 调度器
        warmup_steps = int(total_steps * warmup_ratio)
        self.scheduler = CosineAnnealingWarmupLR(
            self.optimizer, total_steps, warmup_steps, eta_min=0.1 * lr,
        )
    
    def step(self):
        # 1. 将 BF16 梯度转 FP32 写入 master 参数的 grad
        for model_p, master_p in zip(model.parameters(), self.master_params):
            if model_p.grad is not None:
                master_p.grad = model_p.grad.to(torch.float32)
        
        # 2. 优化器更新（FP32）
        self.optimizer.step()
        self.scheduler.step()
        
        # 3. 将更新后的 FP32 参数拷贝回 BF16 模型
        for model_p, master_p in zip(model.parameters(), self.master_params):
            model_p.data.copy_(master_p.data.to(torch.bfloat16))
        
        self.optimizer.zero_grad()
    
    def state_dict(self):
        """序列化 optimizer state、scheduler state 和 FP32 master params"""
        return {
            "optimizer": self.optimizer.state_dict(),
            "scheduler": self.scheduler.state_dict(),
            "master_params": [p.data.clone() for p in self.master_params],
        }
    
    def load_state_dict(self, state_dict):
        """恢复 optimizer state、scheduler state 和 FP32 master params"""
        ...
```

### 4.3 学习率调度

```python
class CosineAnnealingWarmupLR(WarmupScheduler):
    """线性 warmup + Cosine Annealing"""
    def __init__(self, optimizer, total_steps, warmup_steps=0, eta_min=0.0):
        # warmup 阶段：lr 从 0 线性增长到 lr_max
        # cosine 阶段：lr 从 lr_max 余弦衰减到 eta_min
        ...
```

---

## 五、数据加载系统

### 5.1 目标隐状态缓存

训练的核心数据前提是**预计算目标模型的 hidden states**：

```
缓存格式（version 2）:
├── samples.idx          # 索引文件（每条记录40字节）
│   └── 每条记录: sample_id(Q) + shard_id(I) + seq_len(I)
│                 + input_ids_offset(Q) + attention_mask_offset(Q)
│                 + loss_mask_offset(Q) + target_hidden_states_offset(Q)
│                 + target_last_hidden_states_offset(Q)
├── shard_0000.bin       # 二进制 shard 文件
├── shard_0001.bin
└── ...

每条样本数据:
├── input_ids:           int32, [seq_len]
├── attention_mask:      uint8, [seq_len]
├── loss_mask:           uint8, [seq_len]（标记需要计算loss的位置）
├── target_hidden_states: bfloat16, [seq_len, num_layers*hidden_size]
└── target_last_hidden_states: bfloat16, [seq_len, hidden_size]
```

缓存通过 `scripts/data/prepare_target_cache.py` 离线生成，使用 SGLang 服务运行目标模型来计算 hidden states。

### 5.2 CacheDataset

```python
class CacheDataset(torch.utils.data.Dataset):
    def __init__(self, cache_dir, max_open_shards=4):
        # mmap 读取 samples.idx 索引文件
        self.index_mmap = np.mmap(cache_dir / "samples.idx", ...)
        
        # LRU 管理最多 max_open_shards 个 shard mmap
        self.open_shards = OrderedDict()  # LRU cache
    
    def __getitem__(self, index):
        # 1. 解析索引记录
        # 2. 获取或打开对应 shard 的 mmap（LRU）
        # 3. 从 mmap 读取数据并转为 tensor
        return {
            "input_ids": torch.Tensor(int32),
            "loss_mask": torch.Tensor(uint8),
            "target_hidden_states": torch.Tensor(bfloat16),
            "target_last_hidden_states": torch.Tensor(bfloat16),
        }
```

- 使用 mmap 避免将整个数据集加载到内存
- LRU 策略管理打开的 shard 文件句柄，避免打开过多文件
- 数据以 BF16/int32/uint8 紧凑存储，最大化 IO 效率

### 5.3 CacheCollator

```python
class CacheCollator:
    def __call__(self, features):
        # 1. 将 input_ids, loss_mask pad 到同一长度
        # 2. 构造 attention_mask（有效位置为1，pad位置为0）
        # 3. pad target_hidden_states 和 target_last_hidden_states
        return batch_dict
```

### 5.4 CUDAPrefetcher

```python
class CUDAPrefetcher:
    """通过 CUDA stream 重叠数据加载和主机到设备传输"""
    def __init__(self, dataloader, device):
        self.dataloader = dataloader
        self.device = device
        self.stream = torch.cuda.Stream()
        self.preload()
    
    def preload(self):
        try:
            self.next_batch = next(self.iter)
        except StopIteration:
            self.next_batch = None
            return
        # 在非默认 stream 上将数据异步传输到 GPU
        with torch.cuda.stream(self.stream):
            self.next_batch = {
                k: v.to(self.device, non_blocking=True)
                for k, v in self.next_batch.items()
            }
    
    def __next__(self):
        # 等待预取 stream 完成
        torch.cuda.current_stream().wait_stream(self.stream)
        batch = self.next_batch
        self.preload()  # 异步预取下一批
        return batch
```

通过双缓冲机制，当 GPU 计算当前 batch 时，CPU 已经在后台加载下一批数据并通过 PCIe 传输到 GPU，隐藏 IO 和数据传输延迟。

### 5.5 StatelessResumableDistributedSampler

```python
class StatelessResumableDistributedSampler(Sampler):
    """
    无状态可恢复分布式采样器：
    - 支持跨 epoch 边界的流式采样（不重置到开头）
    - 每 epoch 使用 seed + epoch_idx 的确定性打乱
    - 可从 start_global_offset_samples 恢复
    """
    def __init__(self, dataset, num_replicas, rank, total_size,
                 seed=42, start_global_offset_samples=0, num_samples=None):
        ...
    
    def _iter_stream(self):
        """无限生成器，自动跨 epoch 生成新排列"""
        epoch = 0
        while True:
            # 每 epoch 用 seed + epoch 生成确定性 permutation
            g = torch.Generator()
            g.manual_seed(self.seed + epoch)
            perm = torch.randperm(self.total_size, generator=g)
            
            # 按 rank 切片
            indices = perm[self.rank::self.num_replicas]
            
            for idx in indices:
                yield idx.item()
            epoch += 1
```

关键特性：
- **无状态**：不需要保存/恢复采样器状态，只需记录 `next_micro_step` 即可恢复
- **确定性**：给定 seed 和 epoch，perm 完全确定
- **流式**：跨 epoch 连续采样，不会在 epoch 边界重置
- **可恢复**：从 `start_global_offset_samples` 跳过已处理的样本

---

## 六、训练循环

### 6.1 调度计算

```python
# 梯度累积步数
gradient_accumulation_steps = global_batch_size // (local_batch_size * world_size)

# 每 epoch 样本数（分布式聚合后）
samples_per_epoch = len(dataset) // (local_batch_size * world_size)

# 每 epoch 的 optimizer 步数
steps_per_epoch = samples_per_epoch // gradient_accumulation_steps

# 最大训练步数
if max_train_steps is None:
    max_train_steps = num_train_epochs * steps_per_epoch
```

### 6.2 主循环

```python
def train(self):
    model.train()
    dataloader = self._build_resumable_dataloader(next_micro_step)
    prefetcher = CUDAPrefetcher(dataloader, device)
    data_iter = iter(prefetcher)
    
    for micro_step in range(next_micro_step, max_train_steps * gradient_accumulation_steps):
        is_sync_step = (micro_step + 1) % gradient_accumulation_steps == 0
        
        # 非同步步使用 no_sync() 避免梯度 all-reduce
        context = model.no_sync() if not is_sync_step else nullcontext()
        
        with context:
            batch = next(data_iter)
            loss = self.run_batch(batch)  # 模型前向 + loss计算
            (loss / gradient_accumulation_steps).backward()
        
        if is_sync_step:
            # 梯度裁剪
            FSDP.clip_grad_norm_(model, max_grad_norm)
            
            # 优化器步骤（FP32更新 → 拷贝回BF16）
            optimizer.step()
            optimizer.zero_grad()
            
            global_step = micro_step // gradient_accumulation_steps
            
            # 日志记录
            if global_step % logging_steps == 0:
                training_logger.on_optimizer_step(global_step, ...)
            
            # Checkpoint 保存
            if global_step % checkpointing_steps == 0:
                self._save_checkpoint(global_step)
                if auto_eval_command:
                    subprocess.Popen(auto_eval_command, ...)
            
            # 暂停信号处理（hfai集群）
            if suspend_controller.requested():
                self._save_checkpoint(global_step)
                suspend_controller.go_suspend()
```

---

## 七、Checkpoint 管理

### 7.1 原子保存

```python
def save_checkpoint(*, model, draft_model, optimizer, checkpoint_dir_root,
                    train_config, next_micro_step, ...):
    global_step = next_micro_step // gradient_accumulation_steps
    ckpt_dir = checkpoint_dir_root / f"step_{global_step}"
    
    # 1. 创建 step_{global_step} 目录
    ensure_dir(ckpt_dir)
    
    # 2. 保存配置副本
    shutil.copy2(config_path, ckpt_dir / "train_config.py")
    
    # 3. FSDP 聚合模型权重（rank0_only, offload_to_cpu）
    if global_rank == 0:
        full_state_dict = model.state_dict()  # FSDP FULL_STATE_DICT
        draft_model.save_pretrained(ckpt_dir, state_dict=full_state_dict)
    
    # 4. 每个 rank 保存各自的训练状态
    training_state = {
        "optimizer": optimizer.state_dict(),
        "next_micro_step": next_micro_step,
        "world_size": world_size,
        "local_batch_size": local_batch_size,
        "rng_states": {
            "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state(),
            "numpy": np.random.get_state(),
            "python": random.getstate(),
        },
    }
    torch.save(training_state, ckpt_dir / f"training_state.rank{global_rank}.pt")
    
    dist.barrier()
    
    # 5. 原子更新 step_latest 符号链接
    if global_rank == 0:
        safe_symlink(ckpt_dir, checkpoint_dir_root / "step_latest")
    
    return str(ckpt_dir)
```

### 7.2 安全符号链接

```python
def safe_symlink(src, dst):
    """通过临时文件+os.replace原子更新符号链接"""
    tmp = dst.parent / f".tmp_{uuid.uuid4().hex}"
    os.symlink(src, tmp)
    os.replace(tmp, dst)  # 原子操作
```

使用原子符号链接确保 Checkpoint 发现不会读取到不完整的状态。

### 7.3 恢复流程

```python
def discover_latest_checkpoint(checkpoint_dir):
    """通过 step_latest 符号链接发现最新 checkpoint"""
    latest = checkpoint_dir / "step_latest"
    if latest.exists() or latest.is_symlink():
        return os.path.realpath(latest)
    return None

# 恢复步骤：
# 1. 加载模型权重：draft_model.from_pretrained(resume_ckpt, dtype=bf16)
# 2. FSDP 包装
# 3. 加载训练状态：torch.load(training_state.rank{rank}.pt)
#    - 恢复 optimizer state
#    - 校验 world_size 和 local_batch_size 一致性
#    - 恢复所有 RNG 状态
#    - 获取 next_micro_step
# 4. 构建从 next_micro_step 偏移的 DataLoader
```

### 7.4 TrainingResumeState

```python
@dataclass(frozen=True)
class TrainingResumeState:
    next_micro_step: int  # 训练进度的唯一真相来源
```

训练进度完全由 `next_micro_step` 决定。采样器、学习率调度器、数据加载器都可以从这个值确定性地重建。

---

## 八、指标收集与日志

```python
# 训练中记录指标
add_metric("loss", loss.item(), reduction="dp_mean")
add_metric("lr", optimizer.get_learning_rate(), reduction="last")
add_metric("grad_norm", grad_norm, reduction="dp_mean")
add_metric("accuracy", correct, den=total, reduction="dp_sum")  # ratio 类型

# 每 logging_steps 步 flush
metrics = flush()
# - ratio 类型: sum(num)/sum(den) 后 all_reduce
# - scalar 类型: 本地 reduce 后分布式 reduce（dp_ 前缀触发 all_reduce）
# 结果写入 TensorBoard 和打印
```

---

## 九、相关链接

- [/deepseek/deep-spec/concepts/overview](/deepseek/deep-spec/concepts/overview) — DeepSpec 整体概述
- [/deepseek/deep-spec/concepts/dspark-model](/deepseek/deep-spec/concepts/dspark-model) — DSpark 模型架构
- [/deepseek/deep-spec/concepts/eagle3-model](/deepseek/deep-spec/concepts/eagle3-model) — Eagle3 模型架构
- [/deepseek/deep-spec/references/training-api](/deepseek/deep-spec/references/training-api) — 训练 API 完整参考
- [/deepseek/deep-spec/examples/training-dspark](/deepseek/deep-spec/examples/training-dspark) — DSpark 训练示例
