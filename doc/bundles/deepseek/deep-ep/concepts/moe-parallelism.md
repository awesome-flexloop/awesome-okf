---
type: concept
scope: deep-ep
name: MoE 专家并行
version: "2.1.0"
source: deep_ep/buffers/elastic.py, deep_ep/buffers/legacy.py
description: MoE 模型中专家并行（EP）的核心概念、top-k 路由机制、token dispatch/combine 语义、EP 与其他并行策略的组合方式
---

# MoE 专家并行

专家并行（Expert Parallelism, EP）是 MoE（Mixture of Experts）模型特有的并行策略，DeepEP 为其提供高性能通信原语。理解 EP 的基本概念是正确使用 DeepEP 的前提。

## MoE 模型基础

### 什么是 MoE

MoE 模型将前馈网络（FFN）层替换为多个"专家"子网络，每个 token 只激活其中少数几个专家（通常 top-1 到 top-8）。这使得模型参数量可以大幅增加而计算量仅按激活专家数线性增长。

MoE 层的前向传播包含三个步骤：

1. **路由（Routing）**：通过 gating 网络计算每个 token 对每个专家的亲和度分数，选择 top-k 个专家
2. **Dispatch → 专家计算 → Combine**：DeepEP 负责其中的通信部分
3. **输出加权**：将各专家的输出按 gating 权重加权求和

### Top-k 路由

每个 token 被路由到 k 个专家。在 DeepEP 中：

- `topk_idx`：形状 `[num_tokens, num_topk]`，类型 `deep_ep.topk_idx_t`（默认 int64），存储每个 token 选中的专家索引，`-1` 表示无选择（填充位）
- `topk_weights`：形状 `[num_tokens, num_topk]`，类型 `float32`，存储对应专家的 gating 权重

路由决策通常由 [LPLB](/deepseek/lplb)（负载均衡器）生成，以确保专家间的负载均衡。

## 专家并行策略

当专家数量超过单个 GPU 的显存容量时，需要将专家分布到多个 GPU 上，这就是专家并行。

### 专家分布

假设 8 个 GPU，64 个专家：
- 每个 GPU 持有 8 个专家（`num_local_experts = num_experts / num_ranks = 8`）
- 每个 token 可能需要发送到持有其 top-k 专家的任何 GPU
- 这就产生了 all-to-all 通信需求

### EP 通信模式

```
GPU0 (专家0-7)    GPU1 (专家8-15)   ...  GPU7 (专家56-63)
    │                 │                     │
    │  token(→专家8)   │ ←───────────────────│ token 路由决定发送到哪个 GPU
    │────────────────▶│                     │
    │                 │                     │
    │  专家计算        │  专家计算             │  各 GPU 并行计算本地专家
    │                 │                     │
    │◀────────────────│  result(→源GPU)      │ combine 聚合回源
    │                 │                     │
```

### Dispatch 语义

Dispatch 是一个**个性化 all-to-all**（personalized all-to-all）操作：
- 不同于标准 all-to-all（每个 rank 向每个对等端发送相同量的数据）
- 每个 rank 向不同对等端发送不同数量的 token，取决于路由决策
- 发送数据量 = 目标 rank 持有的专家被选中的次数 × hidden_size × dtype_size

DeepEP 的 JIT 内核在运行时计算布局并执行非均匀的 put 操作，将 token 数据直接写入目标 rank 的对称内存。

### Combine 语义

Combine 是 dispatch 的逆操作，但包含加权规约：
- 每个专家计算完输出后，将结果发送回 token 的源 GPU
- 源 GPU 将来自不同专家的结果按 `topk_weights` 加权求和
- 这是一个 **all-to-all + reduce** 操作

V2 的 combine 支持 `allow_multiple_reduction` 控制：
- `True`（默认）：在传输过程中做部分规约，减少传输数据量，可能损失微小精度
- `False`：仅在源 GPU 做一次规约，精度最高但传输量更大

## EP 与其他并行策略的组合

在大规模 MoE 模型训练中（如 DeepSeek-V3），EP 通常与其他并行策略组合使用：

### EP + TP（张量并行）

张量并行将单个专家的计算分布到多个 GPU 上：
- EP 维度：分布专家
- TP 维度：分布单个专家内的矩阵计算
- DeepEP 的 `group` 参数可以是 EP 子组（TP 组内的 rank 持有相同专家）

### EP + PP（流水线并行）

流水线并行将模型按层分布到多个 GPU 上：
- 使用 [DualPipe](/deepseek/dual-pipe) 实现双向流水线
- ElasticBuffer 的 `pp_send()`/`pp_recv()` 提供 PP 通信原语
- PP 和 EP 共享同一 ElasticBuffer 实例，减少内存开销

### EP + DP（数据并行）

数据并行将数据分片到不同 GPU 组：
- 每个 DP 组内有独立的 EP 通信
- EP group 通常就是 DP group 内部的通信组

### 混合并行配置示例

DeepSeek-V3 使用 8-way EP + 流水线并行的组合：
- EP world size = 8（每个 token 可以路由到 8 个节点中的专家）
- PP 使用 DualPipe 双向调度
- DeepEP ElasticBuffer 在同一缓冲区上支持 EP dispatch/combine 和 PP send/recv

## 容量因子与负载均衡

### Capacity Factor

由于路由是动态的，某个 GPU 可能在某些批次接收过多 token。实践中使用**容量因子**（capacity factor）来限制每个专家接收的最大 token 数：

```
max_tokens_per_expert = (num_tokens / num_experts) * capacity_factor * top_k
```

- `capacity_factor > 1.0`：为负载不均衡预留缓冲区
- `capacity_factor = 1.0`：严格平均分配，溢出 token 可能被丢弃或使用辅助专家
- DeepEP 通过 `num_max_tokens_per_rank` 参数设置每个 rank 接收的最大 token 数

### 专家对齐（Expert Alignment）

`expert_alignment` 参数控制每个专家接收 token 数的对齐粒度：
- 默认 1：不对齐
- 设置为 2 的幂（如 128/256）：每个专家接收的 token 数向上对齐到该值
- 对齐后便于使用 [DeepGEMM](/deepseek/deep-gemm) 等分组 GEMM 内核（需要规整的形状）

## V2 增强的 EP 特性

### 缓存 Dispatch

当路由模式固定时（如推理中相同 batch size），可以缓存 EPHandle 复用布局信息：

```python
# 首次：计算布局 + 传输
recv_x, _, _, handle, event = buffer.dispatch(x, topk_idx=topk_idx, ...)
# 后续：仅传输，跳过布局计算
recv_x2, _, _, handle2, event2 = buffer.dispatch(x2, handle=handle, ...)
```

这在推理部署中显著减少延迟。

### Expand 模式

默认模式下，每个 token 在接收缓冲区中只占一个槽位（top-k 个专家的输出在 combine 时规约到一起）。Expand 模式（`do_expand=True`）为每个 top-k 槽位分配独立空间：
- 接收张量按专家分组，形状为 `[num_expanded_tokens, hidden]`
- 每个专家的 token 连续存储，便于独立处理
- 适用于需要专家级别的特殊处理（如专家 dropout、专家级别的量化）

### 确定性路由

`deterministic=True` 保证相同输入产生相同的接收顺序：
- 对接收到的 token 按源 token 全局索引排序
- 非 expand 和 expand 模式有不同的排序策略
- 用于需要精确复现的训练场景（如调试、对比实验）

### FP8 通信

使用 FP8 精度 dispatch 可以将通信带宽需求减半：
- `use_fp8_dispatch=True` 自动量化/反量化
- 提供 `per_token_cast_to_fp8()`/`per_token_cast_back()` 工具函数
- 需要 SM90（Hopper）或更新架构

## Engram：条件内存扩展

DeepSeek-V4/R1 引入的 Engram 机制利用 EP 通信基础设施实现远程 KV 缓存：
- `engram_write()` 将非活跃专家的 KV 缓存写入 CPU 内存
- `engram_fetch()` 通过 RDMA 从远程 CPU 内存拉取需要的 KV 条目
- 这本质上是 EP 通信的扩展应用，复用了 ElasticBuffer 的 RDMA 能力

详见 [ElasticBuffer API](/deepseek/deep-ep/references/buffer-elastic#engram远程-kv-缓存)。

## 相关参考

- [Dispatch/Combine 流程](dispatch-combine.md)
- [低延迟模式](low-latency-mode.md)
- [基础 MoE 示例](/deepseek/deep-ep/examples/basic-moe)
- [ElasticBuffer API](/deepseek/deep-ep/references/buffer-elastic)
- [LPLB](/deepseek/lplb) — 专家负载均衡器
- [DeepGEMM](/deepseek/deep-gemm) — MoE 分组 GEMM 内核
- [DualPipe](/deepseek/dual-pipe) — 与 EP 组合的流水线并行
