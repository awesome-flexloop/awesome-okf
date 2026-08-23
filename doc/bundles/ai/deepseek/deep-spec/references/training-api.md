---
type: api-reference
scope: deep-spec
name: DeepSpec 训练 API 参考
version: "1.0.0"
source: deepspec/trainer/base_trainer.py, deepspec/trainer/dspark_trainer.py, deepspec/trainer/eagle3_trainer.py, deepspec/trainer/ckpt_manager.py, deepspec/utils/optim.py, train.py
description: DeepSpec 训练管线完整 API 参考，包括 Trainer 类、训练配置、BF16Optimizer、FSDP 配置与 Checkpoint 管理
---

# DeepSpec 训练 API 参考

DeepSpec 的训练系统以 `BaseTrainer` 为核心基类，DSpark 和 Eagle3 各自派生专用 Trainer。训练管线集成了 FSDP 分布式训练、BF16 混合精度优化器、CUDA 数据预取和原子 Checkpoint 管理。

---

## 一、训练入口

### 1.1 `train.py` 入口脚本

```bash
torchrun --nproc_per_node=<num_gpus> train.py --config <config_path> [--opts key.subkey=value ...]
```

**命令行参数：**

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--config` | str | ✅ | Python 配置文件路径 |
| `--opts` | list[str] | ❌ | 配置覆盖项，格式 `key.subkey=value`，可多次指定 |

**执行流程：**
1. `parse_args()`：通过 `load_config()` 加载 Python 配置文件，`parse_opts_to_config()` 解析命令行覆盖
2. `main(local_rank)`：设置随机种子 → 打印配置 → 实例化 `args.train.trainer_cls(local_rank, args)` → `trainer.train()` → `trainer.clean_up()`
3. `__main__`：调用 `torch.multiprocessing.spawn(main, nprocs=torch.cuda.device_count())`

---

## 二、BaseTrainer 基类

### 2.1 类定义

```python
class BaseTrainer:
    def __init__(self, local_rank: int, args: ConfigNode): ...
    def build_models(self) -> nn.Module: ...
    def _build_draft_model(self, draft_config) -> nn.Module: ...  # 抽象方法
    def run_batch(self, batch: dict) -> torch.Tensor: ...          # 抽象方法
    def train(self): ...
    def clean_up(self): ...
```

### 2.2 构造函数 `__init__(local_rank, args)`

初始化完整训练环境：

1. **分布式初始化**：调用 `init_dist(local_rank)` 初始化 NCCL 进程组
2. **Checkpoint 发现**：`discover_latest_checkpoint()` 查找 `step_latest` 符号链接
3. **Suspend 控制器**：初始化 `SuspendController` 用于 hfai 集群暂停信号处理
4. **模型构建**：调用 `build_models()` 加载目标模型和草稿模型
5. **torch.compile**（可选）：若 `train.torch_compile=True`，编译模型
6. **FSDP 包装**：按 `sharding_strategy` 包装模型
7. **数据集加载**：加载 `CacheDataset`，创建 `CacheCollator`
8. **训练调度计算**：
   - `gradient_accumulation_steps = global_batch_size // (local_batch_size × world_size)`
   - `samples_per_epoch = len(dataset)`
   - `steps_per_epoch = samples_per_epoch // (local_batch_size × gradient_accumulation_steps)`
   - `max_train_steps = num_train_epochs × steps_per_epoch`（或由配置指定）
9. **优化器初始化**：创建 `BF16Optimizer`
10. **训练状态恢复**：若存在 checkpoint，调用 `load_training_state()` 恢复

### 2.3 `build_models()` 方法

加载目标模型和草稿模型并初始化权重：

```python
def build_models(self):
    # 1. 加载 tokenizer 和 target_config
    tokenizer = AutoTokenizer.from_pretrained(target_model_name_or_path)
    target_config = AutoConfig.from_pretrained(target_model_name_or_path)
    
    # 2. 构建 draft 模型（由子类实现）
    draft_config = self._build_draft_config(target_config, args.model)
    draft_model = self._build_draft_model(draft_config)
    
    # 3. 从预训练目标模型获取 embed_tokens 和 lm_head（CPU, bf16, eval模式）
    target_model = AutoModelForCausalLM.from_pretrained(
        target_model_name_or_path, torch_dtype=torch.bfloat16, device_map="cpu"
    )
    target_model.eval()
    embed_tokens = target_model.get_input_embeddings()
    lm_head = target_model.get_output_embeddings()
    
    # 4. 初始化并冻结嵌入层和输出头
    draft_model.initialize_embeddings_and_head(embed_tokens, lm_head, freeze=True)
    del target_model
    return draft_model
```

### 2.4 `train()` 方法

主训练循环：

```python
def train(self):
    model.train()
    dataloader = self._build_resumable_dataloader(next_micro_step)
    prefetcher = CUDAPrefetcher(dataloader, device)
    data_iter = iter(prefetcher)
    
    for global_step in range(next_micro_step // grad_accum_steps, max_train_steps):
        for micro_step in range(grad_accum_steps):
            is_sync_step = (micro_step == grad_accum_steps - 1)
            context = model.no_sync() if not is_sync_step else nullcontext()
            
            with context:
                batch = next(data_iter)
                loss = self.run_batch(batch)
                (loss / grad_accum_steps).backward()
            
            if is_sync_step:
                FSDP.clip_grad_norm_(model, max_grad_norm)
                optimizer.step()
                training_logger.on_optimizer_step(global_step, ...)
                
                if global_step % checkpointing_steps == 0:
                    self._save_checkpoint(global_step)
                
                if suspend_controller.requested():
                    suspend_controller.go_suspend()
```

### 2.5 精度与分片策略

```python
_PRECISION_DTYPES = {
    "bf16": torch.bfloat16,
    "fp16": torch.float16,
    "fp32": torch.float32,
}

_SHARDING_STRATEGIES = {
    "full_shard": ShardingStrategy.FULL_SHARD,        # ZeRO Stage 3
    "shard_grad_op": ShardingStrategy.SHARD_GRAD_OP,   # ZeRO Stage 2
    "no_shard": ShardingStrategy.NO_SHARD,             # DDP
    "hybrid_shard": ShardingStrategy.HYBRID_SHARD,     # 节点内 FULL_SHARD + 节点间 DDP
    "hybrid_shard_zero2": ShardingStrategy._HYBRID_SHARD_ZERO2,  # 节点内 SHARD_GRAD_OP + 节点间 DDP
}
```

---

## 三、DSpark 训练器

### 3.1 `Qwen3DSparkTrainer`

```python
class Qwen3DSparkTrainer(BaseTrainer):
    data_collator_cls = CacheCollator
    
    def _build_draft_model(self, draft_config):
        return Qwen3DSparkModel(draft_config)
    
    def _build_draft_config(self, target_config, model_args):
        return build_qwen3_draft_config(target_config, model_args)
    
    def run_batch(self, batch):
        outputs = self.model(
            input_ids=batch["input_ids"],
            target_hidden_states=batch["target_hidden_states"],
            loss_mask=batch["loss_mask"],
            target_last_hidden_states=batch.get("target_last_hidden_states"),
        )
        loss = compute_dspark_loss(
            outputs=outputs,
            loss_decay_gamma=self.args.model.loss_decay_gamma,
            ce_loss_alpha=self.args.model.ce_loss_alpha,
            l1_loss_alpha=self.args.model.l1_loss_alpha,
            confidence_head_alpha=self.args.model.confidence_head_alpha,
        )
        return loss
```

### 3.2 `Gemma4DSparkTrainer`

```python
class Gemma4DSparkTrainer(Qwen3DSparkTrainer):
    def _build_draft_model(self, draft_config):
        return Gemma4DSparkModel(draft_config)
    
    def _build_draft_config(self, target_config, model_args):
        return build_gemma4_draft_config(target_config, model_args)
```

---

## 四、Eagle3 训练器

### 4.1 `Qwen3Eagle3Trainer`

```python
class Qwen3Eagle3Trainer(BaseTrainer):
    data_collator_cls = CacheCollator
    
    def build_models(self):
        # 与基类类似，但 draft head/norm 不继承目标模型
        ...
    
    def _build_draft_model(self, draft_config):
        return Qwen3Eagle3Model(draft_config)
    
    def _build_draft_config(self, target_config, model_args):
        return build_qwen3_eagle3_config(target_config, model_args)
    
    def run_batch(self, batch):
        loss = compute_eagle3_loss(
            model=self.model,
            batch=batch,
            ttt_length=self.args.model.ttt_length,
            step_loss_decay=self.args.model.step_loss_decay,
        )
        return loss
```

### 4.2 `Gemma4Eagle3Trainer`

```python
class Gemma4Eagle3Trainer(Qwen3Eagle3Trainer):
    def _build_draft_model(self, draft_config):
        return Gemma4Eagle3Model(draft_config)
    
    def _build_draft_config(self, target_config, model_args):
        return build_gemma4_eagle3_config(target_config, model_args)
```

---

## 五、BF16Optimizer

```python
class BF16Optimizer:
    def __init__(
        self,
        model: nn.Module,
        lr: float,
        total_steps: int,
        warmup_ratio: float,
        weight_decay: float = 0.0,
    ):
        """
        BF16 混合精度优化器：
        - 内部维护 FP32 master 参数副本
        - 使用 AdamW 优化 FP32 参数
        - step() 时将梯度转 FP32 → 更新 master → 拷贝回 BF16 模型
        """
        ...
    
    def step(self):
        """执行一步优化：梯度转FP32 → optimizer.step → scheduler.step → 参数拷贝回模型"""
        ...
    
    def zero_grad(self):
        """清零模型梯度"""
        ...
    
    def state_dict(self) -> dict:
        """序列化优化器、调度器和 FP32 master 参数"""
        ...
    
    def load_state_dict(self, state_dict: dict):
        """恢复优化器、调度器和 FP32 master 参数"""
        ...
    
    def get_learning_rate(self) -> float:
        """返回当前学习率"""
        ...
```

### 学习率调度器

```python
class CosineAnnealingWarmupLR(WarmupScheduler):
    def __init__(
        self,
        optimizer,
        total_steps: int,
        warmup_steps: int = 0,
        eta_min: float = 0.0,
        last_epoch: int = -1,
    ):
        """线性 warmup + Cosine Annealing 调度器"""
        ...
```

---

## 六、Checkpoint 管理

### 6.1 `discover_latest_checkpoint`

```python
def discover_latest_checkpoint(checkpoint_dir: str) -> str | None:
    """检查 checkpoint_dir/step_latest 符号链接/目录，存在则返回真实路径"""
    ...
```

### 6.2 `TrainingResumeState`

```python
@dataclass(frozen=True)
class TrainingResumeState:
    next_micro_step: int  # 训练进度的唯一真相来源
```

### 6.3 `save_checkpoint`

```python
def save_checkpoint(
    *,
    model,                          # FSDP 包装的模型
    draft_model,                    # 原始 draft 模型（用于 save_pretrained）
    optimizer: BF16Optimizer,
    checkpoint_dir_root: str,
    train_config: ConfigNode,
    next_micro_step: int,
    gradient_accumulation_steps: int,
    global_rank: int,
    world_size: int,
    local_batch_size: int,
) -> str:
    """
    保存 checkpoint 流程：
    1. 创建 step_{global_step} 目录
    2. 保存 train_config.py 配置副本
    3. FSDP FULL_STATE_DICT 聚合模型权重（rank0_only, offload_to_cpu）
    4. rank0 使用 draft_model.save_pretrained 保存 HuggingFace 格式
    5. 每个 rank 保存各自的 training_state（optimizer state、RNG 状态、next_micro_step 等）
    6. 原子更新 step_latest 符号链接
    """
    ...
```

### 6.4 `load_resume_draft_model`

```python
def load_resume_draft_model(
    *,
    resume_checkpoint_dir: str,
    draft_model: nn.Module,
    device: torch.device,
    precision_dtype: torch.dtype,
    global_rank: int,
) -> nn.Module:
    """从 checkpoint 加载 draft 模型权重，设置 embedding/head 不可训练"""
    ...
```

### 6.5 `load_training_state`

```python
def load_training_state(
    *,
    resume_checkpoint_dir: str,
    optimizer: BF16Optimizer,
    global_rank: int,
    world_size: int,
    local_batch_size: int,
    gradient_accumulation_steps: int,
    micro_batches_per_epoch: int,
) -> TrainingResumeState:
    """
    加载训练状态：
    1. 加载 training_state.rank{rank}.pt
    2. 恢复 optimizer state
    3. 校验 rank/world_size/local_batch_size 一致性
    4. 恢复 torch/cuda/numpy/python RNG 状态
    5. 返回 TrainingResumeState(next_micro_step)
    """
    ...
```

---

## 七、训练配置结构

配置文件为 Python 模块，顶层字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `project_name` | str | 项目名称 |
| `exp_name` | str | 实验名称 |
| `seed` | int | 随机种子 |
| `model` | dict | 模型超参数 |
| `train` | dict | 训练超参数 |
| `logging` | dict | 日志配置 |
| `data` | dict | 数据配置 |
| `finalize_cfg(cfg)` | callable | 可选配置后处理钩子 |

### model 字段

| 参数 | DSpark | Eagle3 | DFlash | 说明 |
|---|---|---|---|---|
| `target_model_name_or_path` | ✅ | ✅ | ✅ | 目标模型路径 |
| `block_size` | ✅ | ❌ | ✅ | 每块推测 token 数 |
| `num_draft_layers` | ✅ | ❌ | ✅ | 草稿模型层数 |
| `draft_num_hidden_layers` | ❌ | ✅ | ❌ | Eagle3 草稿层数（固定1） |
| `target_layer_ids` | ✅ | ✅(5层) | ✅ | 提取隐状态的目标层 |
| `ttt_length` | ❌ | ✅ | ❌ | TTT 自回归步数 |
| `num_anchors` | ✅ | ❌ | ✅ | 每样本锚点数 |
| `mask_token_id` | ✅ | ❌ | ✅ | 噪声嵌入 mask token ID |
| `markov_rank` | ✅ | ❌ | 0 | Markov 头秩（0=禁用） |
| `markov_head_type` | ✅ | ❌ | ❌ | Markov 头类型（vanilla/gated/rnn） |
| `enable_confidence_head` | ✅ | ❌ | False | 是否启用置信度头 |
| `confidence_head_with_markov` | ✅ | ❌ | ❌ | 置信度头是否使用 Markov 特征 |
| `confidence_head_alpha` | ✅ | ❌ | 0.0 | 置信度损失权重 |
| `loss_decay_gamma` | ✅ | ❌ | ✅ | CE 损失衰减系数 |
| `ce_loss_alpha` | ✅ | ❌ | 1.0 | CE 损失权重 |
| `l1_loss_alpha` | ✅ | ❌ | 0.0 | L1 分布对齐损失权重 |
| `step_loss_decay` | ❌ | ✅ | ❌ | TTT 步损失衰减系数 |

### train 字段

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `trainer_cls` | type | — | 训练器类（如 Qwen3DSparkTrainer） |
| `lr` | float | — | 学习率 |
| `warmup_ratio` | float | — | Warmup 比例 |
| `weight_decay` | float | 0.0 | 权重衰减 |
| `precision` | str | "bf16" | 精度（bf16/fp16/fp32） |
| `local_batch_size` | int | — | 每 GPU batch size |
| `global_batch_size` | int | — | 全局 batch size |
| `num_train_epochs` | int | — | 训练 epoch 数 |
| `max_train_steps` | int | None | 最大训练步数（覆盖 epoch 设置） |
| `max_grad_norm` | float | 1.0 | 梯度裁剪阈值 |
| `sharding_strategy` | str | "no_shard" | FSDP 分片策略 |
| `torch_compile` | bool | False | 是否使用 torch.compile |

---

## 八、相关链接

- [/deepseek/deep-spec/concepts/training-pipeline](/ai/deepseek/deep-spec/concepts/training-pipeline) — 训练管线架构详解
- [/deepseek/deep-spec/concepts/dspark-model](/ai/deepseek/deep-spec/concepts/dspark-model) — DSpark 模型架构
- [/deepseek/deep-spec/concepts/eagle3-model](/ai/deepseek/deep-spec/concepts/eagle3-model) — Eagle3 模型架构
- [/deepseek/deep-spec/examples/training-dspark](/ai/deepseek/deep-spec/examples/training-dspark) — DSpark 训练示例
- [/deepseek/deep-spec/references/model-api](/ai/deepseek/deep-spec/references/model-api) — 模型 API 参考
