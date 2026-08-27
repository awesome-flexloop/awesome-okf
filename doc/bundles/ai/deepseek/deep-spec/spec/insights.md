---
type: spec-insights
scope: deep-spec
source: deep-spec-spec-facts
---

# DeepSpec 核心洞察

## 一、框架定位

DeepSpec 是 DeepSeek 开源的**投机解码（Speculative Decoding）草稿模型训练框架**，支持训练三种草稿模型架构：
- **DSpark**：块级锚点采样（Block-level Anchor Sampling）+ 噪声嵌入（Noise Embedding）+ Markov 头的投机解码模型
- **Eagle3**：基于 EAGLE-3 风格的 5 层目标隐状态拼接 + 单层草稿层 + TTT（Test-Time Training）自回归草稿模型
- **DFlash**：DSpark 的纯 CE 损失变体（`markov_rank=0`，无 Markov 头、无置信度头），通过配置复用 DSpark 训练器

DeepSpec 原生支持 **Qwen3** 和 **Gemma4** 两大模型系列，训练管线采用 FSDP 分片 + BF16 主权重优化器 + CUDA 预取器，评估管线提供通用的回调式投机解码验证框架，覆盖 9 个标准评测任务。

## 二、三种草稿模型架构对比

| 特性 | DSpark | Eagle3 | DFlash |
|---|---|---|---|
| 核心思想 | 块级锚点 + 噪声嵌入 + Markov 头 | 5层目标隐状态拼接 + TTT 自回归 | 纯 CE 训练的 DSpark 简化版 |
| 草稿层数 | 可配置（典型 5 层） | 固定 1 层（draft_num_hidden_layers=1） | 同 DSpark |
| 关键组件 | Markov 头（vanilla/gated/rnn）、置信度头 | fc 投影层、TTT BlockMask、FusedLogSoftmaxLoss | 无 Markov 头、无置信度头 |
| 损失函数 | CE + L1（分布对齐）+ 置信度 BCE | TTT 多步 soft CE（指数衰减加权） | 纯 CE |
| 训练数据 | 目标模型隐状态缓存（target_hidden_states） | 目标模型隐状态缓存 + target_logits | 同 DSpark |
| 推测长度 | block_size（典型 7） | ttt_length（典型 7） | block_size（典型 7） |

## 三、DSpark 架构关键洞察

### 3.1 块级锚点采样

DSpark 不采用逐 token 自回归草稿生成，而是以 **block** 为单位进行训练：
1. 从序列中采样 `num_anchors` 个锚点位置（满足前后 token 均有 loss mask 的位置）
2. 每个锚点位置后接 `block_size` 个 token 作为一个 block
3. 构造噪声嵌入：block 起始位置使用锚点 token 的 embedding，其余位置填充 mask_token_id 的 embedding
4. 模型一次性预测整个 block 的 logits，再通过 Markov 头进行自回归修正

这种设计使得训练可以高度并行化——多个 block 的前向计算可以同时进行，而不需要像逐 token 方式那样串行。

### 3.2 Markov 头三变

Markov 头利用前一 token 的低秩嵌入来修正当前位置的 logits，有三种实现：

| 类型 | 核心机制 | 参数量 | 适用场景 |
|---|---|---|---|
| `vanilla` | `markov_w1`(Embedding) + `markov_w2`(Linear)，将前一token嵌入投影为 vocab 维偏置 | `V × r + r × V` | 基线 |
| `gated` | 在 vanilla 基础上增加 gate_proj，通过 sigmoid 门控融合隐状态和前一token嵌入 | 额外 `(h+r) × r` | 需要隐状态调制 |
| `rnn` | GRU 风格循环，joint_proj 融合前一嵌入、当前隐状态、RNN 状态，逐步更新 | 额外 `(2r+h) × 3r` | 长距离依赖建模 |

其中 `r = markov_rank`，当 `markov_rank=0` 时不构建 Markov 头（即 DFlash 模式）。

### 3.3 多任务损失

DSpark 的损失由三部分组成（可通过 alpha 系数调节权重）：
1. **CE Loss**：标准交叉熵，可选指数衰减权重 `exp(-pos/gamma)`（靠近锚点的 token 权重更高）
2. **L1 Loss**：draft 概率分布与 target 概率分布的 L1 距离（需要 aligned_target_logits），用于分布对齐
3. **Confidence BCE Loss**：置信度头预测每个 token 的接受概率，用于推理时的早停

## 四、Eagle3 架构关键洞察

### 4.1 5层目标隐状态拼接

Eagle3 从目标模型的 **恰好 5 个** decoder 层（`target_layer_ids`）提取 hidden states，在特征维度拼接后通过 `fc` 投影层映射到草稿模型的 hidden_size。与 DSpark 不同，Eagle3 **不支持 -1（embedding 层）** 作为目标层。

### 4.2 TTT（Test-Time Training）自回归

Eagle3 的训练采用 TTT 范式：
1. 将草稿模型输入维度扩展为 `hidden_size × 2`（拼接 token embedding 和目标隐状态）
2. 在一个 block 内执行 `ttt_length` 步自回归：每步用 draft 模型预测下一个 token 的 logits，然后将该 token 的 embedding 作为下一步输入
3. 使用 **KV cache 复用**加速多步推理
4. 创建专用的 **BlockMask** 注意力掩码：causal 部分可见前文，suffix 部分每 TTT 步可见对应位置的 draft token

### 4.3 FusedLogSoftmaxLoss

Eagle3 使用 Triton 融合的 `FusedLogSoftmaxLoss`（自定义 `torch.autograd.Function`）：
- Forward 计算 `-sum(target_p * log_softmax(logits)) / normalizer`（soft 交叉熵，target 可以是软标签）
- Backward 原地写入梯度到 logits 存储，减少内存占用
- BLOCK_SIZE 根据 vocab 大小动态选择（最大 131072），num_warps 自动调整
- 损失按 `step_loss_decay^step_idx` 指数衰减加权，越靠后的 TTT 步权重越低

## 五、训练管线关键设计

### 5.1 目标隐状态缓存

训练的核心数据前提是预先计算并缓存目标模型的 hidden states：
- 缓存格式版本：`TARGET_CACHE_VERSION = 2`
- 每个样本包含：`input_ids`(int32)、`loss_mask`(uint8)、`target_hidden_states`(bfloat16, [seq_len, num_layers*hidden_size])、`target_last_hidden_states`(bfloat16, [seq_len, hidden_size])
- 使用 mmap 读取二进制 shard 文件，LRU 策略管理最多 `max_open_shards` 个打开的 mmap
- 索引记录每条 40 字节（struct: `QIIQQQQQ`）

### 5.2 FSDP + BF16Optimizer

- **精度**：模型使用 BF16 计算，但 BF16Optimizer 内部维护 FP32 master 参数副本
- **优化器**：AdamW（FP32 master weight），梯度转 FP32 更新 master，再拷贝回 BF16 模型
- **FSDP 分片策略**：支持 `full_shard`、`shard_grad_op`、`no_shard`、`hybrid_shard`、`hybrid_shard_zero2`
- **梯度累积**：根据 global_batch_size / (local_batch_size × world_size) 自动计算 gradient_accumulation_steps
- **梯度裁剪**：使用 `FSDP.clip_grad_norm_` 进行梯度裁剪

### 5.3 CUDAPrefetcher 与可恢复采样

- **CUDAPrefetcher**：通过 CUDA stream 重叠数据加载和主机到设备传输
- **StatelessResumableDistributedSampler**：跨 epoch 边界的确定性流式采样，支持从 `start_global_offset_samples` 恢复，每 epoch 使用 `seed + epoch_idx` 的 `torch.randperm` 打乱
- **原子 Checkpoint**：通过临时符号链接 + `os.replace` 原子更新 `step_latest`，支持训练中断恢复（含 optimizer state、RNG 状态）

## 六、评估管线关键设计

### 6.1 通用投机解码框架

`generate_decoding_sample` 是一个通用的投机解码循环，通过回调接口实现不同草稿模型的提议和验证：
- `init_context(initial_output, output_ids, position_ids, num_input_tokens)`：初始化算法状态
- `propose(context, output_ids, position_ids, start, stop_token_ids)`：生成 `DraftProposal`
- `update(context, verification)`：根据验证结果更新状态
- `post_verify(proposal, verification)`：可选诊断钩子

### 6.2 拒绝采样验证

`verify_draft_tokens` 实现标准投机解码验证：
1. 用目标模型前向计算 target_probs
2. 逐 token 执行拒绝采样：`accept_prob = min(1, target_prob / draft_prob)`
3. 被拒绝位置从残差分布 `max(0, target - draft)` 归一化后采样补全
4. 处理 stop token 截断

### 6.3 置信度校准

DSpark 评估器支持 `ConfidenceHeadRecorder`：
- 收集置信度预测与实际接受/拒绝的对应关系
- 当 `confidence_threshold > 0` 时，基于置信度头提前截断草稿
- `confidence_threshold = 0` 时收集校准指标

### 6.4 评测任务

9 个标准评测任务覆盖数学推理、代码生成、对话能力：
- **数学**：gsm8k(500)、math500(500)、aime25(30)
- **代码**：humaneval(164)、mbpp(256)、livecodebench(500)
- **对话**：mt-bench(80)、alpaca(500)、arena-hard-v2(500)

## 七、配置系统设计

- 配置文件使用 **Python 模块格式**，通过 `importlib` 动态加载
- 支持 `--opts key.subkey=value` 命令行覆盖（yaml.safe_load 解析值）
- 可选 `finalize_cfg(cfg)` 钩子函数进行配置后处理
- 三种模型架构各自独立的配置模板（dspark/、eagle3/、dflash/），覆盖 Qwen3-4B/8B/14B 和 Gemma4-12B

## 八、与 FlashMLA 的关系

DeepSpec 训练的草稿模型在推理时需要与目标模型配合进行投机解码，其中目标模型的注意力计算可以利用 [FlashMLA](../../flash-mla/index.md) 进行 MLA 解码加速。FlashMLA 为 Hopper/Blackwell GPU 提供高效的 MLA 注意力核函数，DeepSpec 训练出的草稿模型减少目标模型前向调用次数，二者在推理 pipeline 中协同工作——草稿模型负责快速生成候选 token，FlashMLA 加速目标模型的验证前向。
