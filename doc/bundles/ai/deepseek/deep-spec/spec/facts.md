# DeepSpec 事实清单

## 项目入口与顶层结构

F-001: train.py 定义训练入口：`parse_args()` 解析 `--config`（必填）和 `--opts`（可选，`action="append"`），通过 `load_config()` + `parse_opts_to_config()` 加载配置；`main(local_rank)` 初始化种子、打印配置、实例化 `args.train.trainer_cls(local_rank, args)` 并调用 `trainer.train()` 和 `trainer.clean_up()`；`__main__` 块调用 `torch.multiprocessing.spawn(main, nprocs=torch.cuda.device_count())`。

F-002: eval.py 定义评估入口：`EVALUATORS` 字典映射模型架构名到评估器类（`"Qwen3DSparkModel"`→`Qwen3DSparkEvaluator`、`"Gemma4DSparkModel"`→`Gemma4DSparkEvaluator`、`"Qwen3Eagle3Model"`→`Qwen3Eagle3Evaluator`、`"Gemma4Eagle3Model"`→`Gemma4Eagle3Evaluator`、`"Eagle3DraftModel"`→`Qwen3Eagle3Evaluator`）；`TASKS` 列表包含9个评估数据集：`gsm8k`(500)、`math500`(500)、`aime25`(30)、`humaneval`(164)、`mbpp`(256)、`livecodebench`(500)、`mt-bench`(80)、`alpaca`(500)、`arena-hard-v2`(500)；CLI 参数包括 `--target_name_or_path`、`--draft_name_or_path`、`--max-new-tokens`(默认2048)、`--temperature`(默认1.0)、`--confidence-threshold`(默认0.0)、`--tensorboard-dir`、`--step`、`--seed`(默认980406)。

F-003: deepspec/__init__.py 中 `__all__` 为空列表。

## 配置系统

F-004: deepspec/utils/config.py 定义 `ConfigNode(dict)` 类：通过 `__getattr__`/`__setattr__` 支持属性访问字典键，`copy()` 返回新 `ConfigNode`。

F-005: deepspec/utils/config.py:25-34 定义 `to_config_node(value)` 函数：递归将 `dict` 转为 `ConfigNode`，`list`/`tuple` 递归处理元素。

F-006: deepspec/utils/config.py:37-46 定义 `config_to_plain_dict(value)` 函数：递归将 `ConfigNode` 转回普通 `dict`。

F-007: deepspec/utils/config.py:49-60 定义 `jsonable(value)` 函数：将 `Path` 转为 `str`，`ConfigNode`/`dict`/`list`/`tuple` 递归序列化。

F-008: deepspec/utils/config.py:63-77 定义 `CustomJSONEncoder(json.JSONEncoder)` 类：`default()` 方法处理 `FunctionType`（返回 `<function name>`）、`type`（返回 `<class 'name'>`）、`torch.dtype`（返回 `str`）、`Path`（返回 `str`）、`ConfigNode`（转为普通dict）、`Namespace`/`SimpleNamespace`（返回 `vars(obj)`）。

F-009: deepspec/utils/config.py:84-98 定义 `load_config(path)` 函数：使用 `importlib.util.spec_from_file_location` 动态加载 Python 配置文件，提取所有非 `__` 开头且非 `ModuleType` 的属性，返回 `ConfigNode`。

F-010: deepspec/utils/config.py:101-110 定义 `finalize_config(cfg)` 函数：若 cfg 包含可调用的 `finalize_cfg` 键，则调用 `finalize_cfg(cfg)` 并返回结果；否则直接返回 `to_config_node(cfg)`。

F-011: deepspec/utils/config.py:113-131 定义 `parse_opts_to_config(opts, cfg)` 函数：解析 `--opts key.subkey=value` 格式的命令行覆盖，使用 `yaml.safe_load` 解析标量值，支持点分路径嵌套设置，最后调用 `finalize_config()`。

F-012: 配置文件使用 Python 模块格式，顶层包含 `project_name`(str)、`exp_name`(str)、`seed`(int)、`model`(dict)、`train`(dict)、`logging`(dict)、`data`(dict) 以及可选的 `finalize_cfg(cfg)` 函数。`model` 字典包含 `target_model_name_or_path`、`block_size`/`ttt_length`、`num_draft_layers`/`draft_num_hidden_layers`、`target_layer_ids` 等模型超参数；`train` 字典包含 `trainer_cls`、`lr`、`warmup_ratio`、`weight_decay`、`precision`、`local_batch_size`、`global_batch_size`、`num_train_epochs`、`max_train_steps`、`max_grad_norm`、`sharding_strategy`、`torch_compile`；`logging` 字典包含 `logging_steps`、`checkpointing_steps`；`data` 字典包含 `target_cache_path`、`chat_template`、`max_length`、`num_workers`。

## 工具模块

F-013: deepspec/utils/__init__.py 定义 `seed_all(seed)` 函数：设置 `torch.manual_seed`、`random.seed`、`np.random.seed`、`torch.cuda.manual_seed_all`。

F-014: deepspec/utils/__init__.py:26-50 定义 `get_git_sha(detail_info=False)` 函数：调用 `git rev-parse --short HEAD` 获取短 commit SHA；`detail_info=True` 时额外返回 `git status` 和 `git log -n 1` 输出。定义 `get_git_diff(rev="HEAD")` 函数：调用 `git diff rev`。

F-015: deepspec/utils/distributed.py:11-31 定义 `init_dist(local_rank: int, timeout_minutes: int = 60)` 函数：从环境变量读取 `RANK`/`WORLD_SIZE`/`MASTER_ADDR`/`MASTER_PORT`，计算全局 rank = `node_rank * local_world_size + local_rank`，调用 `dist.init_process_group(backend="nccl", ...)`，返回 `(device, rank, world_size)` 元组。

F-016: deepspec/utils/distributed.py:34-51 定义分布式工具函数：`is_global_main_process()` 返回 `dist.get_rank() == 0`；`is_local_main_process()` 返回 `torch.cuda.current_device() == 0`；`print_on_global_main(*args, **kwargs)` 仅全局主进程打印并添加时间戳前缀；`print_on_local_main(*args, **kwargs)` 仅本地主进程打印。

F-017: deepspec/utils/distributed.py:54-61 定义 `main_process_first()` 上下文管理器：rank 0 先执行再 `dist.barrier()`，其他 rank 先 barrier 再执行。

F-018: deepspec/utils/distributed.py:63-141 定义 `StatelessResumableDistributedSampler(Sampler)` 类：构造参数 `(dataset, num_replicas, rank, total_size, seed=42, start_global_offset_samples=0, num_samples=None)`；支持跨 epoch 边界流式采样，每 epoch 使用 `seed + epoch_idx` 的 `torch.randperm` 确定性打乱；`__len__()` 返回当前 rank 在当前偏移后的剩余样本数或指定 `num_samples`；`_iter_stream()` 为无限生成器，自动跨 epoch 生成新排列。

F-019: deepspec/utils/io.py:5-15 定义 `ensure_dir(path)` 调用 `os.makedirs(path, exist_ok=True)`；定义 `safe_symlink(src, dst)` 通过临时文件+`os.replace` 原子更新符号链接。

F-020: deepspec/utils/metrics.py:91-138 定义 `add_metric(name, value, *, den=None, reduction="dp_sum", tag="train")` 函数：支持 ratio 类型（传入 `den` 时记录分子分母）和 scalar 类型；reduction 模式匹配正则 `^(dp_)?(mean|sum|max|min|last)$`；所有 tensor 值在 API 边界 detach，ratio 类型强制使用 `dp_sum` reduction。

F-021: deepspec/utils/metrics.py:141-166 定义 `flush() -> dict[str, float]` 函数：先调用 `_assert_schema_consistent()` 跨 rank 校验 metric schema 一致；ratio 类型 metric 计算 `sum(num)/sum(den)` 并 all_reduce；scalar 类型先本地 reduce 再分布式 reduce（dp_ 前缀触发 all_reduce）；最后调用 `reset()` 清空缓存。

F-022: deepspec/utils/optim.py:6-80 定义学习率调度器：`TwoStageScheduler(_LRScheduler)` 支持 warmup 后接任意调度器；`WarmupScheduler(TwoStageScheduler)` 线性 warmup `warmup_epochs` 步后切换到 after_scheduler；`CosineAnnealingWarmupLR(WarmupScheduler)` 组合 warmup + cosine annealing，构造参数 `(optimizer, total_steps, warmup_steps=0, eta_min=0.0, last_epoch=-1)`。

F-023: deepspec/utils/optim.py:82-142 定义 `BF16Optimizer` 类：构造参数 `(model, lr, total_steps, warmup_ratio, weight_decay=0.0)`；内部维护 fp32 master 参数副本，使用 `torch.optim.AdamW` 优化 fp32 参数；`step()` 将模型梯度转 fp32 写入 master 参数 grad、执行优化器 step 和 scheduler step、再将 master 参数拷贝回模型；`state_dict()`/`load_state_dict()` 序列化/恢复优化器、调度器和 fp32 master 参数；`get_learning_rate()` 返回当前学习率。

F-024: deepspec/utils/sampling.py:6-27 定义采样工具函数：`logits_to_probs(logits, temperature)` 温度为0时返回 one-hot argmax，否则返回 softmax；`sample_from_probs(probs)` 对 3D probs 调用 `torch.multinomial`；`sample_tokens(logits, temperature=0.0)` 温度为0时 argmax，否则 softmax + multinomial。

F-025: deepspec/utils/sampling.py:30-44 定义 `gather_token_probs(probs, token_ids)` 沿最后一维 gather；定义 `sample_residual(target_probs, draft_probs)` 计算残差分布 `max(0, target - draft)` 归一化后采样。

F-026: deepspec/utils/training_logger.py:16-56 定义训练日志模块：`init(logging_steps, tensorboard_dir=None)` 初始化 SummaryWriter；`start_session(global_step)` 重置 metrics 并记录会话起始时间步；`on_optimizer_step(global_step, next_micro_step, ...)` 记录 lr/grad_norm，每 `logging_steps` 步 flush metrics 并写入 tensorboard/打印进度。

F-027: deepspec/utils/hfai_suspend.py:18-71 定义 `SuspendController` 类：通过后台线程监控 hfai 暂停信号；`monitoring()` 上下文管理器启动/停止监控线程；`requested()` 通过 NCCL broadcast 从 rank 0 广播暂停标志到所有 rank；`go_suspend()` 调用 `hfai.client.go_suspend()`。

F-028: deepspec/utils/constant/public.py:1-15 定义公共常量：`CACHE_DIR = "~/.cache/deepspec"`；模型路径常量 `QWEN_3_4B = "Qwen/Qwen3-4B"`、`QWEN_3_8B = "Qwen/Qwen3-8B"`、`QWEN_3_14B = "Qwen/Qwen3-14B"`、`GEMMA_4_12B = "google/gemma-4-12B-it"`；`BASE_TB_DIR = "~/tensorboard"`、`BASE_CKPT_DIR = "~/checkpoints"`；`auto_eval_command = None`。

## 数据加载与缓存

F-029: deepspec/data/__init__.py 导出 `CacheCollator`、`CacheDataset`、`ConversationCollator`、`TEMPLATE_REGISTRY`、`validate_train_cache`。

F-030: deepspec/data/parser.py 定义 `ChatTemplate` 类、`TemplateRegistry`（即 `TEMPLATE_REGISTRY`）、`GeneralParser` 类，以及 `render_chat_messages`、`encode_chat_messages` 等函数；`encode_chat_messages(tokenizer, messages, add_generation_prompt=True, enable_thinking=False)` 将对话消息编码为 input_ids。

F-031: deepspec/data/jsonl_dataset.py 实现 `JsonLineDataset` 类：使用 mmap 高效读取 JSONL 文件。

F-032: deepspec/data/cuda_prefetcher.py 实现 `CUDAPrefetcher` 类：通过 CUDA stream 重叠数据加载和主机到设备传输。

F-033: deepspec/data/target_cache_dataset.py:20-26 定义目标缓存格式常量：`TARGET_CACHE_VERSION = 2`；`INDEX_RECORD_STRUCT = struct.Struct("<QIIQQQQQ")`（对应 sample_id:Q, shard_id:I, seq_len:I, input_ids_offset:Q, attention_mask_offset:Q, loss_mask_offset:Q, target_hidden_states_offset:Q, target_last_hidden_states_offset:Q）；`INDEX_RECORD_SIZE = 40` 字节；hidden states 使用 bfloat16，tokens 使用 int32，masks 使用 uint8。

F-034: deepspec/data/target_cache_dataset.py:615-798 定义 `CacheDataset(torch.utils.data.Dataset)` 类：构造参数 `(cache_dir: str, max_open_shards: int = 4)`；通过 mmap 读取 `samples.idx` 索引文件和二进制 shard 文件；使用 LRU 策略（OrderedDict）管理最多 `max_open_shards` 个打开的 shard mmap；`__getitem__(index)` 返回字典包含 `"input_ids"`(int32, [seq_len])、`"loss_mask"`(uint8, [seq_len])、`"target_hidden_states"`(bfloat16, [seq_len, num_layers*hidden_size])、`"target_last_hidden_states"`(bfloat16, [seq_len, hidden_size])。

F-035: deepspec/data/target_cache_dataset.py:824-856 定义 `ConversationCollator` 类：构造参数 `(tokenizer, chat_template, max_length, min_loss_tokens)`；`__call__(features)` 调用 `preprocess_record` 处理原始对话数据，过滤 loss token 数少于 `min_loss_tokens` 的样本，pad 到同一长度返回 batch。

F-036: deepspec/data/target_cache_dataset.py:859-870 定义 `CacheCollator` 类：`__call__(features)` 将 `input_ids`、`loss_mask` pad 到同一长度，构造 `attention_mask`（有效位置为1），pad `target_hidden_states` 和 `target_last_hidden_states` 到同一长度。

F-037: deepspec/data/target_cache_dataset.py:203-218 定义 `validate_train_cache(*, train_dataset, draft_model, target_model_name_or_path)` 函数：校验缓存的 `target_layer_ids` 与 draft model 配置一致、`hidden_size` 匹配、`target_model_name_or_path` 匹配。

## DSpark 模型实现

F-038: deepspec/modeling/__init__.py 导出 `DSparkForwardOutput`、`Gemma4Eagle3Model`、`Gemma4DSparkModel`、`Qwen3Eagle3Model`、`Qwen3DSparkModel`。

F-039: deepspec/modeling/dspark/common.py:11-40 定义 `DSparkForwardOutput` 数据类：字段包括 `draft_logits`([B, num_anchors, block_size, V])、`target_ids`([B, num_anchors, block_size])、`eval_mask`([B, num_anchors, block_size])、`block_keep_mask`([B, num_anchors])、`confidence_pred`(Optional[B, num_anchors, block_size])、`aligned_target_logits`(Optional[B, num_anchors, block_size, V])。

F-040: deepspec/modeling/dspark/common.py:43-49 定义 `AcceptRatePredictor(nn.Module)` 类：构造参数 `input_dim: int`；包含单个 `nn.Linear(input_dim, 1)` 投影层；`forward(features)` 返回 `self.proj(features).squeeze(-1)`。

F-041: deepspec/modeling/dspark/common.py:52-75 定义 `extract_context_feature(hidden_states, layer_ids)` 函数：从 hidden_states 元组中按 `layer_ids` 选择指定层（-1 表示 embedding 输出即 index 0，其他 layer_id 使用 index+1），在最后一维拼接；定义 `validate_target_layer_ids(layer_ids, num_target_layers)` 函数：校验 layer_ids 非空、严格递增、在 {-1} ∪ [0, num_target_layers-1] 范围内。

F-042: deepspec/modeling/dspark/common.py:123-169 定义 `sample_anchor_positions(*, seq_len, loss_mask, num_anchors, device)` 函数：从满足 `loss_mask[i] > 0.5 & loss_mask[i+1] > 0.5` 的有效锚点位置中随机采样 `num_anchors` 个，返回 `(anchor_positions, block_keep_mask)` 元组，形状分别为 [B, num_anchors] 和 [B, num_anchors]。

F-043: deepspec/modeling/dspark/common.py:264-294 定义 `create_noise_embed(embed_tokens, input_ids, anchor_positions, block_keep_mask, *, mask_token_id, block_size)` 函数：构造形状 [B, num_anchors*block_size] 的 noise_ids（初始填充 mask_token_id，每个 block 起始位置替换为 anchor token），通过 `embed_tokens` 得到噪声嵌入。

F-044: deepspec/modeling/dspark/markov_head.py:8-53 定义 `VanillaMarkov(nn.Module)` 类：构造参数 `(vocab_size, markov_rank)`；包含 `markov_w1 = nn.Embedding(vocab_size, markov_rank)` 和 `markov_w2 = nn.Linear(markov_rank, vocab_size, bias=False)`；`get_prev_embeddings(token_ids)` 返回前一token的低维嵌入；`apply_step_logits(logits, token_ids, hidden_states)` 将 markov 偏置加到 logits 上；`apply_block_logits(base_logits, token_ids, hidden_states)` 对 block 内所有位置应用 markov 偏置；`sample_block_tokens(base_logits, first_prev_token_ids, hidden_states, temperature)` 自回归采样 block 内 token。

F-045: deepspec/modeling/dspark/markov_head.py:93-122 定义 `GatedMarkovHead(VanillaMarkov)` 类：额外包含 `gate_proj = nn.Linear(hidden_size + markov_rank, markov_rank)`；`compute_gate(token_ids, hidden_states)` 通过 sigmoid 门控融合前一token嵌入和隐状态；`compute_step_bias` 使用门控后的嵌入投影偏置。

F-046: deepspec/modeling/dspark/markov_head.py:125-284 定义 `RNNHead(VanillaMarkov)` 类：包含 `joint_proj = nn.Linear(2*markov_rank + hidden_size, 3*markov_rank)` 实现 GRU 风格循环；`_rnn_step(state, prev_embeddings, hidden_states)` 执行单步 RNN 更新，返回 `(new_state, bias)`；`apply_block_logits` 在 block 内展开 RNN 逐步应用偏置（teacher forcing）；`sample_block_tokens` 自回归采样时维护 RNN 状态。

F-047: deepspec/modeling/dspark/markov_head.py:287-311 定义 `build_markov_head(config) -> nn.Module | None` 函数：`markov_rank == 0` 时返回 None；`markov_head_type == "vanilla"` 返回 `VanillaMarkov`；`"gated"` 返回 `GatedMarkovHead`；`"rnn"` 返回 `RNNHead`。

F-048: deepspec/modeling/dspark/qwen3/config.py 定义 `build_draft_config(target_config, model_args)` 函数：深度拷贝 target_config，设置 `architectures=["Qwen3DSparkModel"]`、`num_hidden_layers=num_draft_layers`、`layer_types=["full_attention"]*num_draft_layers`、`block_size`、`mask_token_id`、`target_layer_ids`、`num_anchors`、`enable_confidence_head`、`markov_rank`、`markov_head_type`、`confidence_head_with_markov` 等字段；attention 实现设为 `"flex_attention"`。

F-049: deepspec/modeling/dspark/qwen3/modeling.py 定义 `Qwen3DSparkModel`（继承 Qwen3PreTrainedModel）、`Qwen3DSparkAttention`、`Qwen3DSparkDecoderLayer`；模型结构包含 `embed_tokens`、`fc`(投影拼接的多层 target hidden)、`layers`(ModuleList of Qwen3DSparkDecoderLayer)、`norm`、`rotary_emb`、`lm_head`、`markov_head`、可选的 `confidence_head`(AcceptRatePredictor)。

F-050: deepspec/modeling/dspark/gemma4/config.py:52-102 定义 `build_draft_config(target_config, model_args)` 函数：从 Gemma4 统一模型中提取 text_config，校验必需字段后设置 draft config，字段与 Qwen3 版本一致，额外处理 `num_global_key_value_heads`、`global_head_dim`、`attention_k_eq_v`、`enable_moe_block` 等 Gemma4 特有属性。

F-051: deepspec/modeling/dspark/gemma4/modeling.py:241-597 定义 `Gemma4DSparkModel(Gemma4PreTrainedModel)` 类：`forward(input_ids, target_hidden_states, loss_mask, target_last_hidden_states=None) -> DSparkForwardOutput` 执行完整前向传播：采样锚点位置 → 构造 noise embedding → 构造 position_ids 和 attention mask → `_forward_backbone` → reshape 输出 → gather target_ids → 计算 eval_mask → 通过 markov_head 修正 logits → 计算 confidence prediction → 返回 DSparkForwardOutput。

F-052: deepspec/modeling/dspark/loss.py:255-329 定义 `compute_dspark_loss(*, outputs, loss_decay_gamma, ce_loss_alpha, l1_loss_alpha, confidence_head_alpha)` 函数：计算 CE loss（交叉熵，可选指数衰减权重 `exp(-pos/gamma)`）、L1 loss（draft_probs 与 target_probs 的 L1 距离，需要 `aligned_target_logits`）、confidence BCE loss；通过 all_reduce 同步分母；返回 `(ce_loss_alpha*ce + l1_loss_alpha*l1 + confidence_alpha*conf) * world_size` 作为反向传播损失。

## Eagle3 模型实现

F-053: deepspec/modeling/eagle3/common.py:13-17 定义 `Eagle3ForwardOutput` 数据类：字段 `hidden_states`(torch.Tensor)、`draft_logits`(torch.Tensor)、`target_logits`(Optional[torch.Tensor]=None)。

F-054: deepspec/modeling/eagle3/common.py:20-41 定义 `validate_eagle3_target_layer_ids(layer_ids, num_target_layers)` 函数：要求恰好5个目标层，严格递增，在 [0, num_target_layers-1] 范围内；定义 `extract_eagle3_context_feature(hidden_states, layer_ids)` 从指定 decoder 层输出拼接（不支持 -1 embedding）。

F-055: deepspec/modeling/eagle3/common.py:103-139 定义 `create_eagle3_attention_mask(*, attention_mask, q_len, kv_len, lck, device)` 函数：创建 Eagle3 TTT 专用 BlockMask，causal 部分可见前文，suffix 部分每 TTT 步可见对应位置的 draft token；q_len ≤ 128 时使用 eager create_block_mask，否则使用编译版本。

F-056: deepspec/modeling/eagle3/qwen3/config.py:9-39 定义 `build_draft_config(*, target_config, model_args)` 函数：深度拷贝 target_config，设置 `architectures=["Qwen3Eagle3Model"]`、`num_target_layers`、`num_hidden_layers=draft_num_hidden_layers`、`layer_types=["full_attention"]*draft_num_hidden_layers`、`target_layer_ids`、`ttt_length`、`step_loss_decay`、`tie_word_embeddings=False`、`_attn_implementation="flex_attention"`。

F-057: deepspec/modeling/eagle3/qwen3/modeling.py:204-407 定义 `Qwen3Eagle3Model(Qwen3PreTrainedModel)` 类：必需配置字段 `target_layer_ids`、`ttt_length`、`step_loss_decay`；包含 `embed_tokens`、`fc`(投影5层拼接 hidden)、`layers`(Qwen3Eagle3DecoderLayer)、`norm`、`rotary_emb`、`lm_head`；`initialize_embeddings_and_head(embed_tokens, lm_head, freeze=True)` 从目标模型拷贝嵌入和lm_head权重；`forward(hidden_states, input_ids, ..., return_logits=False, rope_cache_step_offset=False, target_logits_only=False)` 支持目标logits快速计算、hidden_states投影、TTT自回归推理，return_logits时返回Eagle3ForwardOutput。

F-058: deepspec/modeling/eagle3/qwen3/modeling.py:41-153 定义 `Qwen3Eagle3Attention(nn.Module)` 类：输入维度为 `hidden_size*2`（拼接 input_embeds 和 hidden_states）；q/k/v 投影输入维度均为 `hidden_size*2`；支持 flex_attention（q_len ≤ 128 用原生，否则编译）和 SDPA/eager 后端；使用 Qwen3RMSNorm 对 q/k 归一化。

F-059: deepspec/modeling/eagle3/gemma4/config.py:52-88 定义 Gemma4 版本的 `build_draft_config(*, target_config, model_args)`：从 Gemma4 统一模型提取 text_config，校验25个必需字段后设置 draft config，额外包含 `target_model_type`、`target_text_model_type`、`num_global_key_value_heads`、`global_head_dim` 等字段。

F-060: deepspec/modeling/eagle3/gemma4/modeling.py:260-488 定义 `Gemma4Eagle3Model(Gemma4PreTrainedModel)` 类：使用 `Gemma4TextScaledWordEmbedding`（embed_scale=sqrt(hidden_size)）、`Gemma4TextRotaryEmbedding`、`Gemma4RMSNorm`；支持 `final_logit_softcapping`（通过 `_softcap_logits` 应用 tanh 缩放）；DecoderLayer 包含 `pre_feedforward_layernorm`/`post_feedforward_layernorm` 和可学习的 `layer_scalar`；`v_proj` 在 `attention_k_eq_v=True` 时为 None（v=k）。

F-061: deepspec/modeling/eagle3/loss.py:282-351 定义 `FusedLogSoftmaxLoss(torch.autograd.Function)` 类：Triton 融合的 soft 交叉熵损失，forward 计算 `-sum(target_p * log_softmax(logits)) / normalizer`，backward 原地写入梯度到 logits 存储；BLOCK_SIZE 根据 vocab 大小动态选择（最大131072），num_warps 根据 BLOCK_SIZE 调整。

F-062: deepspec/modeling/eagle3/loss.py:354-452 定义 `compute_eagle3_loss(*, model, batch, ttt_length, step_loss_decay) -> torch.Tensor` 函数：TTT 自回归训练循环，每步调用 model forward 得到 draft_logits，使用 FusedLogSoftmaxLoss 计算与 target_probs 的 soft CE loss，按 `step_loss_decay^step_idx` 指数衰减加权求和；支持 KV cache 复用；记录每步 accuracy/accept_rate/valid_tokens 和前缀 tau_greedy/tau_probabilistic 指标。

## 训练管线

F-063: deepspec/trainer/__init__.py 导出 `BaseTrainer`、`Gemma4Eagle3Trainer`、`Gemma4DSparkTrainer`、`Qwen3Eagle3Trainer`、`Qwen3DSparkTrainer`。

F-064: deepspec/trainer/base_trainer.py:34-47 定义精度和分片策略映射：`_PRECISION_DTYPES = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}`；`_SHARDING_STRATEGIES` 映射 `"full_shard"`/`"shard_grad_op"`/`"no_shard"`/`"hybrid_shard"`/`"hybrid_shard_zero2"` 到 FSDP ShardingStrategy 枚举值。

F-065: deepspec/trainer/base_trainer.py:155-234 定义 `BaseTrainer` 类：`__init__(self, local_rank, args)` 初始化分布式环境、发现最新 checkpoint、初始化 suspend_controller、构建模型（支持从 checkpoint 恢复）、可选 torch.compile、FSDP 包装、加载 CacheDataset、计算训练调度（gradient_accumulation_steps、samples_per_epoch、steps_per_epoch、max_train_steps）、初始化 BF16Optimizer、恢复训练状态。

F-066: deepspec/trainer/base_trainer.py:251-282 定义 `BaseTrainer.build_models(self)` 方法：加载 tokenizer 和 target_config，调用 `_build_draft_model` 构建 draft 模型，从预训练目标模型（CPU上，bf16，eval模式）获取 embed_tokens 和 lm_head，调用 `draft_model.initialize_embeddings_and_head(embed_tokens, lm_head, freeze=True)` 初始化并冻结嵌入层和输出头。

F-067: deepspec/trainer/base_trainer.py:355-407 定义 `BaseTrainer.train(self)` 方法：设置模型为 train 模式；构建可恢复 DataLoader（从 next_micro_step 偏移开始）；使用 CUDAPrefetcher 预取数据；梯度累积循环中，非同步步使用 `model.no_sync()`，同步步执行梯度裁剪（`FSDP.clip_grad_norm_(model, max_grad_norm)`）、optimizer.step()、记录日志；每 `checkpointing_steps` 步保存 checkpoint 并触发自动评估；检查 suspend 信号处理暂停。

F-068: deepspec/trainer/dspark_trainer.py:14-48 定义 `Qwen3DSparkTrainer(BaseTrainer)`：`data_collator_cls = CacheCollator`；`_build_draft_model` 调用 `build_qwen3_draft_config` + `Qwen3DSparkModel(draft_config)`；`run_batch(batch)` 调用 model forward 传入 input_ids/target_hidden_states/loss_mask/target_last_hidden_states，然后 `compute_dspark_loss` 计算损失。`Gemma4DSparkTrainer(Qwen3DSparkTrainer)` 仅重写 `_build_draft_model` 使用 Gemma4 版本。

F-069: deepspec/trainer/eagle3_trainer.py:16-76 定义 `Qwen3Eagle3Trainer(BaseTrainer)`：重写 `build_models`（与基类逻辑相同但注释说明 draft head/norm 不继承目标模型）；`_build_draft_model` 使用 `build_qwen3_eagle3_config` + `Qwen3Eagle3Model`；`run_batch(batch)` 调用 `compute_eagle3_loss(model, batch, ttt_length, step_loss_decay)`。`Gemma4Eagle3Trainer(Qwen3Eagle3Trainer)` 仅重写 `_build_draft_model` 使用 Gemma4 版本。

## 评估管线

F-070: deepspec/eval/__init__.py 导出 `BaseEvaluator`、`DraftProposal`、`Gemma4Eagle3Evaluator`、`Gemma4DSparkEvaluator`、`Qwen3Eagle3Evaluator`、`Qwen3DSparkEvaluator`、`VerificationResult`。

F-071: deepspec/eval/base_evaluator.py:167-183 定义 `DraftProposal` 数据类：字段 `draft_token_count: int`、`verify_input_ids: torch.Tensor`、`draft_probs: torch.Tensor | None`；定义 `VerificationResult` 数据类：字段 `target_output`、`target_probs: torch.Tensor`、`accept_prefix_mask: torch.Tensor | None`、`accepted_draft_tokens: int`、`next_token: torch.Tensor`、`effective_proposal_length: int`、`terminated_by_stop_token: bool = False`、`committed_tokens: torch.Tensor | None = None`。

F-072: deepspec/eval/base_evaluator.py:186-304 定义 `verify_draft_tokens(*, target_model, proposal, position_ids, start, past_key_values_target, temperature, max_proposal_tokens, current_token_ids=None, stop_token_ids=None) -> VerificationResult` 函数：执行投机解码验证，用目标模型前向计算 target_probs，通过拒绝采样（`accept_prob = min(1, target_prob/draft_prob)`）确定接受前缀，被拒绝位置从残差分布采样补全 token，处理 stop token 截断。

F-073: deepspec/eval/base_evaluator.py:307-441 定义 `generate_decoding_sample(*, target_model, input_ids, max_new_tokens, max_proposal_tokens, temperature, stop_token_ids, init_context, propose, update, post_verify=None) -> SimpleNamespace` 函数：通用投机解码循环，回调接口 `init_context(initial_output, output_ids, position_ids, num_input_tokens)` 初始化算法状态、`propose(context, output_ids, position_ids, start, stop_token_ids)` 生成 DraftProposal、`update(context, verification)` 更新状态、`post_verify(proposal, verification)` 可选诊断钩子；返回包含 output_ids、acceptance_lengths、proposal_lengths、accepted_draft_lengths、verify_count 的命名空间。

F-074: deepspec/eval/base_evaluator.py:444-728 定义 `BaseEvaluator` 类：`__init__(local_rank, args)` 初始化分布式和模型；`max_proposal_tokens` 属性（抽象）；`build_models()`（抽象）；`generate_one_sample(input_ids, stop_token_ids)`（抽象）；`run_dataset(dataset_name, max_samples)` 加载数据集、编码输入、调用 generate_one_sample；`allreduce_response_metrics(responses)` 跨 rank 汇总 acceptance_length_sum、proposal_length_sum、逐位置接受率；`evaluate()` 遍历所有任务执行评估；`build_metrics_row` 计算 draft_tokens_per_proposal、acceptance_length、verify_rate、逐位置 accept_rate。

F-075: deepspec/eval/dspark/evaluator.py:32-221 定义 `Qwen3DSparkEvaluator(BaseEvaluator)`：`EVAL_ATTN_IMPLEMENTATION = "sdpa"`；`max_proposal_tokens = block_size`；`build_models()` 加载 bfloat16 的目标模型和 draft 模型（均使用 sdpa 注意力），校验 target_layer_ids 不含最后一层；`_init_context` 初始化 draft DynamicCache 和 target_hidden_states；`_propose` 调用 `forward_dspark_draft_block` 和 `build_dspark_proposal` 生成提议；`_update` 裁剪并更新 target_hidden_states；支持 `ConfidenceHeadRecorder` 收集置信度校准指标。`Gemma4DSparkEvaluator(Qwen3DSparkEvaluator)` 仅修改 `draft_model_cls = Gemma4DSparkModel`。

F-076: deepspec/eval/dspark/draft_ops.py:17-152 定义 `DSparkDraftProposal(DraftProposal)` 数据类（增加 `confidence_logits` 字段）；定义 `forward_dspark_draft_block(model, draft_input_ids, position_ids, past_key_values_draft, target_hidden_states, start, block_size)` 执行单块 draft 前向；定义 `build_dspark_proposal(model, draft_input_ids, block_hidden, block_size, temperature, confidence_threshold)` 自回归采样 draft tokens，可选基于 confidence head 提前截断（`_confident_prefix_length` 找到第一个低于阈值的位置）。

F-077: deepspec/eval/eagle3/evaluator.py:22-193 定义 `Qwen3Eagle3Evaluator(BaseEvaluator)`：`EVAL_ATTN_IMPLEMENTATION = "sdpa"`；构造时断言 `draft_num_hidden_layers == 1`；`max_proposal_tokens = ttt_length`；`_init_context` 使用 shifted prompt ids 预填充 draft KV cache；`_propose` 循环 TTT 步自回归采样 draft tokens 构建 DraftProposal；`_update` 裁剪 draft cache 并 extend 已验证 token 的 KV；`Gemma4Eagle3Evaluator(Qwen3Eagle3Evaluator)` 修改 `draft_model_cls = Gemma4Eagle3Model`。

## Checkpoint 管理

F-078: deepspec/trainer/ckpt_manager.py:25-29 定义 `discover_latest_checkpoint(checkpoint_dir)` 函数：检查 `checkpoint_dir/step_latest` 符号链接/目录，存在则返回真实路径，否则返回 None。

F-079: deepspec/trainer/ckpt_manager.py:56-61 定义 `TrainingResumeState` 冻结数据类：唯一字段 `next_micro_step: int`（训练进度的唯一真相来源）。

F-080: deepspec/trainer/ckpt_manager.py:64-81 定义 `load_resume_draft_model(*, resume_checkpoint_dir, draft_model, device, precision_dtype, global_rank)` 函数：使用 `type(draft_model).from_pretrained(resume_checkpoint_dir, dtype=precision_dtype, attn_implementation=...)` 加载模型权重，移到设备后设置 `set_embedding_head_trainable(False)`。

F-081: deepspec/trainer/ckpt_manager.py:84-133 定义 `load_training_state(*, resume_checkpoint_dir, optimizer, global_rank, world_size, local_batch_size, gradient_accumulation_steps, micro_batches_per_epoch) -> TrainingResumeState` 函数：加载 `training_state.rank{rank}.pt`，恢复 optimizer state、校验 rank/world_size/local_batch_size 一致性、恢复 torch/cuda/numpy/python RNG 状态。

F-082: deepspec/trainer/ckpt_manager.py:136-185 定义 `save_checkpoint(*, model, draft_model, optimizer, checkpoint_dir_root, train_config, next_micro_step, gradient_accumulation_steps, global_rank, world_size, local_batch_size) -> str` 函数：创建 `step_{global_step}` 目录，保存 train_config.py，通过 FSDP FULL_STATE_DICT 聚合模型权重（rank0_only, offload_to_cpu），rank0 使用 `draft_model.save_pretrained` 保存 HuggingFace 格式，每个 rank 保存各自的 training_state（含 optimizer state、RNG 状态、next_micro_step、world_size 等），最后原子更新 `step_latest` 符号链接。

## DFlash 配置

F-083: config/dflash/ 目录仅包含配置文件（dflash_qwen3_4b.py、dflash_qwen3_8b.py、dflash_qwen3_14b.py、dflash_gemma4_12b.py），无独立 modeling/eval/trainer 实现；DFlash 配置复用 `Qwen3DSparkTrainer`，设置 `markov_rank=0`、`confidence_head_alpha=0.0`、`ce_loss_alpha=1.0`、`l1_loss_alpha=0.0`（即纯 CE 损失、无 Markov 头、无 confidence 头的 DSpark 变体）。

## 配置文件实例

F-084: config/dspark/dspark_qwen3_8b.py 示例配置：`project_name="deepspec"`、`exp_name="dspark_block7_qwen3_8b"`、`seed=42`；model 参数 `block_size=7`、`num_draft_layers=5`、`target_layer_ids=[1,9,17,25,33]`、`mask_token_id=151669`、`num_anchors=512`、`markov_rank=256`、`markov_head_type='vanilla'`、`confidence_head_alpha=1.0`、`confidence_head_with_markov=True`、`loss_decay_gamma=4.0`、`ce_loss_alpha=0.1`、`l1_loss_alpha=0.9`；训练参数 `lr=6e-4`、`warmup_ratio=0.04`、`precision="bf16"`、`local_batch_size=1`、`global_batch_size=512`、`num_train_epochs=10`、`max_grad_norm=1.0`、`sharding_strategy="no_shard"`、`torch_compile=True`；数据参数 `chat_template="qwen"`、`max_length=4096`、`num_workers=4`。

F-085: config/eagle3/eagle3_qwen3_8b.py 示例配置：`exp_name="eagle3_ttt7_qwen3_8b"`、`seed=0`；model 参数 `target_layer_ids=[1,9,17,25,33]`、`ttt_length=7`、`step_loss_decay=0.8`、`draft_num_hidden_layers=1`；训练参数 `torch_compile=False`，其余与 dspark 类似。
