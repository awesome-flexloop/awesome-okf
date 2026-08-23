---
type: example
scope: deep-gemm
name: MegaMoE 前向计算示例
version: "2.6.1"
source: tests/test_mega_moe.py, deep_gemm/mega/__init__.py
description: 使用 DeepGEMM MegaMoE 进行 MoE 前向计算的完整示例，仅支持 SM100 Blackwell
---

# MegaMoE 前向计算示例

本文档展示如何使用 DeepGEMM 的 MegaMoE API 进行高性能 MoE（Mixture of Experts）前向计算。MegaMoE 利用对称内存实现融合的 dispatch-compute-combine 流程，仅支持 SM100（Blackwell）GPU。

> **注意**：MegaMoE 仅在 Blackwell（SM100）GPU 上可用。如需在 Hopper 上运行 MoE，请使用分组 GEMM 方案（参见 [/deepseek/deep-gemm/examples/basic-gemm#分组GEMM示例](/ai/deepseek/deep-gemm/examples/basic-gemm) 中的 M-grouped GEMM）。

---

## 一、M-Grouped GEMM 实现 MoE（Hopper/Blackwell 通用）

在不使用 MegaMoE 融合核时，可以通过 M-grouped GEMM 实现 MoE 前向：

### 1.1 连续布局 M-Grouped GEMM

```python
import torch
import deep_gemm

assert torch.cuda.get_device_capability()[0] >= 9

# MoE 配置
num_experts = 8
num_tokens = 4096
hidden = 4096
intermediate = 1408  # SwiGLU 中间维度（gate+up 前）
topk = 2
num_local_experts = num_experts  # 单 rank 示例

# 创建权重（BF16 示例）
# Gate+Up 投影权重: [num_experts, 2*intermediate, hidden]
w1_bf16 = torch.randn(num_experts, 2 * intermediate, hidden,
                      device='cuda', dtype=torch.bfloat16)
# Down 投影权重: [num_experts, hidden, intermediate]
w2_bf16 = torch.randn(num_experts, hidden, intermediate,
                      device='cuda', dtype=torch.bfloat16)

# 输入 token
x = torch.randn(num_tokens, hidden, device='cuda', dtype=torch.bfloat16)

# 模拟 router 输出（简化：随机分配 token 到 expert）
# 实际应用中由 router 网络 + top-k 选择产生
topk_indices = torch.randint(0, num_experts, (num_tokens, topk),
                              device='cuda', dtype=torch.int64)
topk_weights = torch.randn(num_tokens, topk, device='cuda', dtype=torch.float32)
topk_weights = torch.softmax(topk_weights, dim=-1).to(torch.bfloat16)

# Dispatch: 将 token 按 expert 排序，生成 grouped_layout
# 简化实现：实际需要根据 topk_indices 重排 token
expert_ids = topk_indices[:, 0]  # 简化：仅取 top-1 用于演示
sorted_indices = torch.argsort(expert_ids)
x_sorted = x[sorted_indices]
grouped_layout = expert_ids[sorted_indices].to(torch.int32).contiguous()

# 统计每个 expert 的 token 数
tokens_per_expert = torch.bincount(expert_ids, minlength=num_experts).tolist()

# L1 GEMM: [num_tokens, hidden] @ [num_experts, 2*intermediate, hidden]^T
# 输出形状: [num_tokens, 2*intermediate]
l1_out = torch.empty(num_tokens, 2 * intermediate,
                     device='cuda', dtype=torch.bfloat16)
deep_gemm.m_grouped_bf16_gemm_nt_contiguous(
    x_sorted, w1_bf16, l1_out, grouped_layout
)

# SwiGLU 激活: out = gate * silu(up)
gate = l1_out[:, :intermediate]
up = l1_out[:, intermediate:]
l1_act = torch.nn.functional.silu(gate) * up

# L2 GEMM: [num_tokens, intermediate] @ [num_experts, hidden, intermediate]^T
l2_out = torch.empty(num_tokens, hidden,
                     device='cuda', dtype=torch.bfloat16)
deep_gemm.m_grouped_bf16_gemm_nt_contiguous(
    l1_act, w2_bf16, l2_out, grouped_layout
)

# Combine: 按 topk_weights 加权求和（逆 permute）
output = torch.zeros(num_tokens, hidden, device='cuda', dtype=torch.bfloat16)
output[sorted_indices] = l2_out * topk_weights[sorted_indices, :1].to(torch.bfloat16)

print(f"MoE 前向输出形状: {output.shape}")
```

### 1.2 FP8 分组 GEMM

```python
from deep_gemm import per_block_cast_to_fp8

# FP8 量化权重
w1_fp8, w1_sf = per_block_cast_to_fp8(w1_bf16.float(), use_ue8m0=False)
w2_fp8, w2_sf = per_block_cast_to_fp8(w2_bf16.float(), use_ue8m0=False)

# FP8 量化输入
x_fp8, x_sf = per_block_cast_to_fp8(x_sorted.float(), use_ue8m0=False)

# FP8 L1 GEMM
l1_out_fp8 = torch.empty(num_tokens, 2 * intermediate,
                         device='cuda', dtype=torch.bfloat16)
deep_gemm.m_grouped_fp8_gemm_nt_contiguous(
    (x_fp8, x_sf), (w1_fp8, w1_sf), l1_out_fp8, grouped_layout
)

# SwiGLU (在 BF16 上执行)
gate = l1_out_fp8[:, :intermediate]
up = l1_out_fp8[:, intermediate:]
l1_act_bf16 = torch.nn.functional.silu(gate) * up

# 量化激活到 FP8
l1_act_fp8, l1_act_sf = per_block_cast_to_fp8(l1_act_bf16.float(), use_ue8m0=False)

# FP8 L2 GEMM
l2_out_fp8 = torch.empty(num_tokens, hidden,
                         device='cuda', dtype=torch.bfloat16)
deep_gemm.m_grouped_fp8_gemm_nt_contiguous(
    (l1_act_fp8, l1_act_sf), (w2_fp8, w2_sf), l2_out_fp8, grouped_layout
)
```

---

## 二、MegaMoE 融合核（SM100 Blackwell 专用）

MegaMoE 融合核使用对称内存实现零拷贝通信，需要分布式环境。以下示例展示单 rank 调试和多 rank 完整用法。

### 2.1 单 Rank 调试模式

```python
import torch
import deep_gemm

assert torch.cuda.get_device_capability() == (10, 0), "MegaMoE requires SM100 (Blackwell)"

# MoE 配置
num_ranks = 1
num_experts = 4
hidden = 4096
intermediate_hidden = 1408
num_topk = 4
num_tokens = 1024
num_max_tokens_per_rank = 1536  # 会自动对齐到 384
num_shared_experts = 1  # 可选共享专家（设为 0 则不使用）

# 创建 FP4 路由专家权重（packed as Int8）
# L1: (num_experts, 2*intermediate, hidden) for FP4 (physical: k/2 due to packing)
# 注意：FP4 权重实际物理最后一维为 hidden/2（每 byte 存 2 个 FP4），但 DeepGEMM 通过 dtype 推断
l1_weights = torch.randint(-128, 127, (num_experts, 2 * intermediate_hidden, hidden),
                           device='cuda', dtype=torch.int8)
l2_weights = torch.randint(-128, 127, (num_experts, hidden, intermediate_hidden),
                           device='cuda', dtype=torch.int8)

# FP4 权重缩放因子 (Int32 UE8M0 packed)
# 形状: (num_experts, ceil(2*inter/1), ceil(hidden/(32*4)))  for gran_mn=1, gran_k=32
from deep_gemm.utils.math import ceil_div
l1_sf = torch.ones(num_experts, ceil_div(2 * intermediate_hidden, 1), ceil_div(hidden, 32 * 4),
                   device='cuda', dtype=torch.int32)
l2_sf = torch.ones(num_experts, ceil_div(hidden, 1), ceil_div(intermediate_hidden, 32 * 4),
                   device='cuda', dtype=torch.int32)

# FP8 共享专家权重（可选）
shared_l1_w = torch.randn(2 * intermediate_hidden * num_shared_experts, hidden,
                          device='cuda', dtype=torch.float8_e4m3fn)
shared_l2_w = torch.randn(hidden, intermediate_hidden * num_shared_experts,
                          device='cuda', dtype=torch.float8_e4m3fn)
shared_l1_sf = torch.ones(ceil_div(2 * intermediate_hidden * num_shared_experts, 1),
                          ceil_div(hidden, 32 * 4), device='cuda', dtype=torch.int32)
shared_l2_sf = torch.ones(ceil_div(hidden, 1), ceil_div(intermediate_hidden * num_shared_experts, 32 * 4),
                          device='cuda', dtype=torch.int32)

# 权重变换（interleave + SF transpose）
l1_weights_t, l2_weights_t = deep_gemm.transform_weights_for_mega_moe(
    (l1_weights, l1_sf), (l2_weights, l2_sf)
)
shared_l1_t, shared_l2_t = deep_gemm.transform_weights_for_mega_moe(
    (shared_l1_w, shared_l1_sf), (shared_l2_w, shared_l2_sf)
)

# 创建 SymmBuffer（单 rank 模式，无需分布式组）
# 单 rank 使用 SimpleNamespace 模拟 group
class SimpleGroup:
    def __init__(self):
        self.rank_ = 0
        self.size_ = 1
    def rank(self): return self.rank_
    def size(self): return self.size_
    def barrier(self): pass

# 注意：实际使用时需要 torch.distributed ProcessGroup
# group = dist.new_group(ranks=list(range(world_size)))

from types import SimpleNamespace
import torch.distributed as dist

# 对于单 rank 调试，可以直接用 None 创建（SymmBuffer 内部处理单 rank 情况）
# 这里展示多 rank 标准用法的参数准备
sym_buffer = deep_gemm.get_symm_buffer_for_mega_moe(
    group=None,  # 单 rank 传 None；多 rank 传 ProcessGroup
    num_experts=num_experts,
    num_max_tokens_per_rank=num_max_tokens_per_rank,
    num_topk=num_topk,
    hidden=hidden,
    intermediate_hidden=intermediate_hidden,
    num_shared_experts=num_shared_experts,
    mma_type='fp8xfp4',
)

# 准备输入数据
x = torch.randn(num_tokens, hidden, device='cuda', dtype=torch.float8_e4m3fn)
# 将 x 拷贝到 sym_buffer.x
sym_buffer.x[:num_tokens].copy_(x)

# 模拟 top-k 路由（实际应用中由 router 产生）
sym_buffer.topk_idx[:num_tokens] = torch.randint(
    0, num_experts, (num_tokens, num_topk), device='cuda', dtype=torch.int64
)
sym_buffer.topk_weights[:num_tokens] = torch.softmax(
    torch.randn(num_tokens, num_topk, device='cuda'), dim=-1
)

# 输出张量
y = torch.empty(num_tokens, hidden, device='cuda', dtype=torch.bfloat16)

# 执行 MegaMoE 前向
deep_gemm.fp8_fp4_mega_moe(
    y,
    l1_weights_t, l2_weights_t,           # (weights, sf) tuples after transform
    sym_buffer,
    shared_l1_weights=shared_l1_t,
    shared_l2_weights=shared_l2_t,
    cumulative_local_expert_recv_stats=None,
    recipe=(1, 1, 32),
    activation='swiglu',
    activation_clamp=None,
    fast_math=True,
)

print(f"MegaMoE 输出形状: {y.shape}")

# 清理
sym_buffer.destroy()
```

### 2.2 多 Rank 分布式用法

```python
"""
MegaMoE 多 rank 完整示例（需通过 torchrun 启动）:
torchrun --nproc_per_node=8 mega_moe_demo.py
"""
import torch
import torch.distributed as dist
import deep_gemm
from deep_gemm.utils import init_dist

def main():
    # 初始化分布式
    rank, world_size, group = init_dist(
        local_rank=0,  # 实际应从启动参数获取
        num_local_ranks=8
    )

    # 配置
    num_experts = 64           # 总专家数
    num_ranks = world_size     # EP 并行度
    num_experts_per_rank = num_experts // num_ranks
    hidden = 7168
    intermediate_hidden = 2048
    num_topk = 8
    num_tokens_per_rank = 8192
    num_max_tokens_per_rank = 10240  # 每 rank 最大 token 容量
    num_shared_experts = 2

    # 创建本地专家权重（每个 rank 持有 num_experts_per_rank 个专家）
    # ...（权重创建和量化过程同单 rank 示例，但使用 num_experts_per_rank）
    l1_weights = torch.randint(-128, 127,
        (num_experts_per_rank, 2 * intermediate_hidden, hidden),
        device='cuda', dtype=torch.int8)
    # ... SF 同理，使用 num_experts_per_rank

    # 权重变换
    l1_t, l2_t = deep_gemm.transform_weights_for_mega_moe(
        (l1_weights, l1_sf), (l2_weights, l2_sf))

    # 创建对称缓冲区（多 rank 模式，内部使用 symm_mem）
    sym_buffer = deep_gemm.get_symm_buffer_for_mega_moe(
        group=group,
        num_experts=num_experts,  # 总专家数（跨所有 rank）
        num_max_tokens_per_rank=num_max_tokens_per_rank,
        num_topk=num_topk,
        hidden=hidden,
        intermediate_hidden=intermediate_hidden,
        num_shared_experts=num_shared_experts,
        mma_type='fp8xfp4',
    )

    # 准备输入：将本地 token 拷贝到 sym_buffer.x
    # x_local shape: (num_tokens_this_rank, hidden)
    sym_buffer.x[:num_tokens_per_rank].copy_(x_local)
    sym_buffer.topk_idx[:num_tokens_per_rank] = topk_idx_local
    sym_buffer.topk_weights[:num_tokens_per_rank] = topk_weights_local

    # 确保所有 rank 数据就绪
    group.barrier()
    torch.cuda.synchronize()

    # 执行 MegaMoE（所有 rank 同时调用）
    y = torch.empty(num_tokens_per_rank, hidden, device='cuda', dtype=torch.bfloat16)
    deep_gemm.fp8_fp4_mega_moe(
        y, l1_t, l2_t, sym_buffer,
        shared_l1_weights=shared_l1_t,
        shared_l2_weights=shared_l2_t,
        recipe=(1, 1, 32),
        activation='swiglu',
        fast_math=True,
    )

    # y 包含本 rank token 的最终输出（已 combine）
    print(f"Rank {rank}: output shape {y.shape}")

    # 清理
    sym_buffer.destroy()
    dist.destroy_process_group()

if __name__ == '__main__':
    main()
```

---

## 三、BF16 MegaMoE

```python
# BF16 模式不需要 SF，权重为 BF16 tensor
l1_bf16 = torch.randn(num_experts_per_rank, 2 * intermediate, hidden,
                      device='cuda', dtype=torch.bfloat16)
l2_bf16 = torch.randn(num_experts_per_rank, hidden, intermediate,
                      device='cuda', dtype=torch.bfloat16)

# 权重变换（仅 interleave）
l1_t, l2_t = deep_gemm.transform_weights_for_mega_moe(l1_bf16, l2_bf16)

# 创建 buffer 时指定 mma_type
sym_buffer = deep_gemm.get_symm_buffer_for_mega_moe(
    group, num_experts, num_max_tokens_per_rank, num_topk,
    hidden, intermediate, mma_type='bf16xbf16'
)

# BF16 前向
deep_gemm.bf16_mega_moe(
    y, l1_t, l2_t, sym_buffer,
    activation='swiglu', fast_math=True
)
```

---

## 四、关键注意事项

1. **架构限制**：MegaMoE 仅支持 SM100（Blackwell），在 Hopper 上调用会触发 `DG_HOST_UNREACHABLE`
2. **SwiGLU 硬编码**：激活函数固定为 SwiGLU，L1 权重形状必须包含 gate+up（`intermediate_hidden * 2`）
3. **权重交错**：调用核函数前必须使用 `transform_weights_for_mega_moe` 预处理权重，将 gate/up 交错排列
4. **SF 布局**：UE8M0 packed SF 必须为 MN-major（stride(-2)==1）、TMA 对齐、dtype=Int32
5. **Token 对齐**：`num_max_tokens_per_rank` 会被自动对齐到 384（`get_token_alignment_for_mega_moe()` 返回值）
6. **维度对齐**：hidden 和 intermediate_hidden 必须是 128 的倍数
7. **对称内存依赖**：多 rank 模式需要 PyTorch 编译时启用 symmetric_memory 支持
8. **Buffer 复用**：每次调用 MegaMoE 前必须重新填充 `sym_buffer.x`、`topk_idx`、`topk_weights`；调试模式（`DG_COMM_KERNEL_DEBUG=1`）下 buffer 会被清零
9. **Expert 分布**：`num_experts` 必须能被 `num_ranks`（group size）整除
10. **累积统计**：可选的 `cumulative_local_expert_recv_stats` 为 Int32 张量，长度 `num_experts_per_rank`，可用于负载均衡监控

---

## 五、与 DeepEP 的协同

对于非融合 MoE 方案，可以结合 [/deepseek/deep-ep/](/ai/deepseek/deep-ep/) 进行专家并行通信：

```
DeepEP (通信) + DeepGEMM M-grouped GEMM (计算):
1. DeepEP: dispatch (all-to-all 发送 token 到 expert 所在 rank)
2. DeepGEMM: m_grouped_gemm_nt_contiguous (L1 + SwiGLU + L2)
3. DeepEP: combine (all-to-all 发送结果回源 rank)
```

MegaMoE 将上述三步融合为单内核，通过对称环形缓冲区在核函数内部完成通信。

---

## 六、相关链接

- [/deepseek/deep-gemm/concepts/moe-operations](/ai/deepseek/deep-gemm/concepts/moe-operations) — MegaMoE 设计原理
- [/deepseek/deep-gemm/concepts/grouped-gemm](/ai/deepseek/deep-gemm/concepts/grouped-gemm) — 分组 GEMM 概念
- [/deepseek/deep-gemm/references/mega-moe](/ai/deepseek/deep-gemm/references/mega-moe) — MegaMoE API 参考
- [/deepseek/deep-ep/](/ai/deepseek/deep-ep/) — DeepEP 专家并行通信库
