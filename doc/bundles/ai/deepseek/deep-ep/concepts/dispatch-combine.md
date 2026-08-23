---
type: concept
scope: deep-ep
name: Dispatch/Combine 流程
version: "2.1.0"
source: deep_ep/buffers/elastic.py, csrc/kernels/elastic/dispatch.hpp, csrc/kernels/elastic/combine.hpp
description: MoE dispatch 和 combine 的数据流动模型、内核执行流程、EPHandle 路由元数据结构，以及缓存/展开/确定性等高级模式
---

# Dispatch/Combine 流程

Dispatch 和 Combine 是 DeepEP 最核心的两个操作，分别对应 MoE 前向传播中 token 分发到专家和专家输出聚合回源的两次 all-to-all 通信。理解这两个操作的数据流动模型是正确使用 DeepEP 的基础。

## 为什么需要专门的 EP 通信

在标准数据并行或张量并行中，all-reduce、all-gather 等集合通信具有**均匀的数据分布**——每个 rank 发送和接收的数据量相同。但 MoE 的 EP 通信不同：

- **非均匀分布**：每个 token 只路由到 top-k 个专家，不同 rank 发送给不同对等端的数据量差异很大
- **动态路由**：每个批次的路由决策（top-k 专家索引）不同，通信模式随输入变化
- **有状态**：combine 需要精确逆转化 dispatch 的路由，需要保存路由元数据
- **双向语义**：dispatch 是 token → 专家的散射，combine 是专家输出 → 源 GPU 的加权聚合

NCCL 的 `all_to_all_single` 无法高效处理这种非均匀、动态、有状态的通信模式，因此 DeepEP 实现了专门的 EP 通信内核。

## Dispatch 流程

Dispatch 将输入 token 路由到持有对应专家的 GPU。以 V2 ElasticBuffer 为例，执行流程如下：

### 阶段 1：布局计算（Layout Calculation）

Dispatch 内核首先根据 `topk_idx` 计算通信布局：

1. **统计每个 rank/专家的 token 数**：扫描 `topk_idx`（形状 `[num_tokens, num_topk]`），统计每个目标 rank 和每个专家将接收多少 token
2. **前缀和计算**：计算 `psum_num_recv_tokens_per_scaleup_rank`（每个 scaleup rank 去重接收 token 数的前缀和）和 `psum_num_recv_tokens_per_expert`（每个本地专家对齐后接收 token 数的前缀和）
3. **目标缓冲区槽位分配**：为每个要发送的 token 计算在目标 rank 缓冲区中的写入位置（`dst_buffer_slot_idx`）

这些信息被封装在返回的 `EPHandle` 中，供 combine 和后续缓存 dispatch 使用。

### 阶段 2：数据推送（Data Push）

JIT 编译的 dispatch 内核在通信流上执行：

- 每个 SM 作为独立"信道"（channel），通过 NCCL 对称内存的 put 操作将 token 数据（`x` 和可选的 `topk_weights`/缩放因子）直接写入目标 rank 的对称缓冲区
- 混合模式下，节点内通过 NVLink 直接写入，节点间通过 RDMA 写入；`channel_linked_list` 维护信道链表实现流水线传输
- Dispatch 内核使用 1024 线程/block

### 阶段 3：Copy Epilogue

Dispatch 内核将数据写入中间缓冲区后，`DispatchCopyEpilogueRuntime` 内核执行收尾：
- 将数据从中间缓冲区拷贝到最终的 `recv_x` 张量
- 填充 `recv_src_metadata`（源 token 索引和槽位元数据）
- 非 CPU 同步模式下，此时接收张量可能尚未完全填充

### 阶段 4：确定性排序（可选）

当 `deterministic=True` 时，dispatch 完成后通过 `EPHandle.deterministic_sort()` 对接收到的 token 按源 token 全局索引排序，保证相同输入产生相同的接收顺序。

### Dispatch 输入输出

**输入：**
- `x`：`[num_tokens, hidden]`（BF16）或 `(fp8_data, scales)` 元组
- `topk_idx`：`[num_tokens, num_topk]`（`deep_ep.topk_idx_t`，即 int64），值为专家索引，`-1` 表示填充
- `topk_weights`（可选）：`[num_tokens, num_topk]`（float32），gating 权重

**输出（五元组）：**
- `recv_x`：接收的 token 数据，形状为总接收 token 数 × hidden
- `recv_topk_idx`：接收的 top-k 索引（非 expand 模式）
- `recv_topk_weights`：接收的 top-k 权重
- `handle`：[EPHandle](/ai/deepseek/deep-ep/references/buffer-elastic#ephandle-类)，路由元数据句柄
- `event`：[EventOverlap](/ai/deepseek/deep-ep/references/events)，事件句柄用于同步

## Combine 流程

Combine 是 dispatch 的逆操作：将每个专家的输出按 top-k 权重加权聚合回 token 源 GPU。

### 阶段 1：数据推送（Combine Push）

`CombineRuntime` 内核（1024 线程/block）在通信流上执行：
- 将每个专家的输出 token 推送到源 rank 的对称内存缓冲区
- 根据 EPHandle 中的路由元数据确定每个 token 的目标位置
- 支持 FP8/BF16 数据类型

### 阶段 2：Reduce Epilogue

`CombineReduceEpilogueRuntime` 内核在源 rank 上执行：
- 对同一源 token 的多个专家输出执行加权规约加法（按 `topk_weights` 加权）
- `allow_multiple_reduction=True`（默认）：在传输过程中做部分规约，减少数据量但可能损失精度
- `allow_multiple_reduction=False`：仅在 epilogue 做一次规约，精度最高但传输量更大
- 支持 `bias` 参数：在最终输出上添加偏置

### Combine 输入输出

**输入：**
- `x`：专家计算后的输出，`[num_recv_tokens, hidden]`（BF16）
- `handle`：dispatch 返回的 EPHandle（必须）
- `topk_weights`：非 expand 模式 `[num_recv_tokens, num_topk]`，expand 模式 `[num_recv_tokens]`
- `bias`（可选）：单 tensor 或双 tensor 元组，添加到最终输出

**输出（三元组）：**
- `combined_x`：聚合后的输出，`[num_tokens, hidden]`（BF16）
- `combined_topk_weights`：聚合后的权重（通常为 None）
- `event`：EventOverlap 事件句柄

## EPHandle：路由元数据的核心

`EPHandle` 是理解 dispatch/combine 的关键数据结构，它封装了将 combine 输出正确路由回源所需的全部元数据：

| 字段 | 作用 |
|------|------|
| `topk_idx` | 克隆的 top-k 索引，用于 combine 时确定每个 token 的目标 rank |
| `psum_num_recv_tokens_per_scaleup_rank` | 前缀和数组，确定每个 scaleup rank 的数据在接收缓冲区中的偏移 |
| `psum_num_recv_tokens_per_expert` | 前缀和数组，确定每个专家的数据偏移 |
| `recv_src_metadata` | 源 token 索引和缓冲区槽位索引，combine 时用于逆路由 |
| `dst_buffer_slot_idx` | dispatch 时目标缓冲区槽位索引 |
| `channel_linked_list` | 混合模式下的信道链表 |

EPHandle 的生命周期跨越 dispatch → 专家计算 → combine，是连接两个通信阶段的桥梁。

## 高级模式

### 缓存 Dispatch（Cached Dispatch）

当多次 dispatch 的路由模式相同时（如推理中相同的 MoE 配置），可以复用 EPHandle 跳过布局重计算：

```python
# 首次 dispatch：计算布局
recv_x, _, _, handle, event = buffer.dispatch(x, topk_idx=topk_idx, ...)
# 后续 dispatch：复用 handle，topk_idx 必须为 None
recv_x2, _, _, handle2, event2 = buffer.dispatch(x2, handle=handle, ...)
```

缓存模式下 `do_cpu_sync` 自动设为 `False`，避免 CPU 同步开销。适用于推理场景中固定 batch size 和固定专家数的情况。

### Expand 模式

默认模式下，每个 token 分配一个接收槽位（无论 top-k 多少）。Expand 模式（`do_expand=True`）为每个 top-k 专家分配独立槽位：
- 接收张量按专家分组，可能有 padding（`expert_alignment` 对齐）
- `num_unaligned_recv_tokens_per_expert` 记录每个专家未对齐的实际 token 数
- Combine 时 `topk_weights` 为一维张量（每个展开槽位一个权重）
- 适用于需要逐专家独立处理的场景

### 确定性模式（Deterministic）

`deterministic=True` 时：
- Dispatch 后自动注册 `deterministic_sort` 回调
- 等待通信完成后，按源 token 全局索引对接收到的 token 排序
- 非 expand 模式：排序所有接收数据和元数据
- Expand 模式：按专家分组排序，更新槽位指针
- 保证相同输入始终产生相同的输出顺序，用于可复现训练

### 流控制参数

- `async_with_compute_stream=True`：通信在通信流上异步执行，不插入计算流等待；用户需通过事件手动同步
- `allocate_on_comm_stream=True`：在通信流上分配临时张量（默认在计算流上分配）
- `previous_event`：等待前序通信事件完成后再开始，避免多个通信竞争网络
- `previous_event_before_epilogue`：在 epilogue 阶段前等待前序事件

## FP8 支持

DeepEP 支持 FP8 dispatch 以减少通信带宽：
- 输入 `x` 为 `(fp8_tensor, scales)` 元组
- `use_fp8_dispatch=True` 时缓冲区按 FP8 大小计算
- `use_tma_aligned_col_major_sf=True` 时缩放因子使用 TMA 对齐的列优先布局（Hopper+ 架构）
- 提供 `per_token_cast_to_fp8()` 和 `per_token_cast_back()` 工具函数进行 BF16↔FP8 转换

## 与 DualPipe 的流水线集成

在 EP+PP 混合并行中（如 [DualPipe](/ai/deepseek/dual-pipe)），ElasticBuffer 的 PP send/recv API 提供了与 dispatch/combine 共享同一对称内存缓冲区的流水线通信能力，避免额外的内存分配和拷贝。详见 [ElasticBuffer API](/ai/deepseek/deep-ep/references/buffer-elastic#流水线并行pp)。

## 相关参考

- [ElasticBuffer API](/ai/deepseek/deep-ep/references/buffer-elastic) — dispatch/combine 完整参数说明
- [EPHandle 类](/ai/deepseek/deep-ep/references/buffer-elastic#ephandle-类) — 路由元数据详细字段
- [事件系统](/ai/deepseek/deep-ep/references/events) — EventOverlap 同步机制
- [基础 MoE 示例](/ai/deepseek/deep-ep/examples/basic-moe) — 可运行的 dispatch/combine 代码
- [计算-通信重叠示例](/ai/deepseek/deep-ep/examples/event-overlap) — EventOverlap 使用示例
