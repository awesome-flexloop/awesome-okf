---
type: example
scope: deep-ep
name: 基础 MoE 通信示例
version: "2.1.0"
source: deep_ep/buffers/elastic.py, deep_ep/utils/envs.py
description: 使用 ElasticBuffer 进行 MoE dispatch/combine 的完整可运行 PyTorch 示例，包含分布式初始化、缓冲区创建、top-k 路由和前向传播
---

# 基础 MoE 通信示例

本示例演示如何使用 DeepEP 的 `ElasticBuffer` 完成一个 MoE 层的 dispatch → 专家计算 → combine 完整流程。

## 完整示例代码

```python
"""
DeepEP ElasticBuffer 基础 MoE 通信示例。

运行方式（需在多 GPU 环境中）：
    torchrun --nproc_per_node=8 basic_moe.py
"""

import torch
import torch.distributed as dist
import torch.nn as nn
import deep_ep


def init_distributed():
    """初始化 NCCL 分布式环境。"""
    dist.init_process_group(backend='nccl')
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    torch.cuda.set_device(rank)
    return rank, world_size


class SimpleExpert(nn.Module):
    """简单的专家 FFN 网络。"""
    def __init__(self, hidden: int):
        super().__init__()
        self.fc1 = nn.Linear(hidden, hidden * 4, bias=False)
        self.fc2 = nn.Linear(hidden * 4, hidden, bias=False)
        self.act = nn.SiLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.act(self.fc1(x)))


def moe_forward(
    buffer: deep_ep.ElasticBuffer,
    hidden_states: torch.Tensor,
    local_experts: nn.ModuleList,
    num_experts: int,
    top_k: int = 8,
    expert_alignment: int = 128,
) -> torch.Tensor:
    """
    MoE 前向传播：dispatch → 专家计算 → combine。

    Args:
        buffer: ElasticBuffer 实例
        hidden_states: 输入张量，形状 [num_tokens, hidden] (BF16)
        local_experts: 当前 GPU 上的本地专家列表
        num_experts: 全局专家总数
        top_k: 每个 token 选择的专家数
        expert_alignment: 专家 token 对齐粒度

    Returns:
        combined_output: 聚合后的输出，形状 [num_tokens, hidden] (BF16)
    """
    num_tokens = hidden_states.shape[0]
    rank = dist.get_rank()
    num_local_experts = len(local_experts)

    # ---- 步骤 1: 生成 Top-k 路由索引 ----
    # 实际应用中由 gating 网络/负载均衡器（如 LPLB）生成
    # 这里随机生成作为演示
    with torch.no_grad():
        # 每个 token 随机选择 top_k 个专家
        gate_logits = torch.randn(num_tokens, num_experts,
                                  device=hidden_states.device, dtype=torch.float32)
        topk_weights = torch.softmax(gate_logits, dim=-1)
        topk_idx = torch.topk(topk_weights, top_k, dim=-1).indices
        # 转为 deep_ep 的 topk_idx_t 类型
        topk_idx = topk_idx.to(deep_ep.topk_idx_t)

    # ---- 步骤 2: Dispatch（分发 token 到专家所在 GPU）----
    # 返回值: (recv_x, recv_topk_idx, recv_topk_weights, handle, event)
    recv_x, recv_topk_idx, recv_topk_weights, handle, event = buffer.dispatch(
        x=hidden_states,
        topk_idx=topk_idx,
        topk_weights=topk_weights,
        num_experts=num_experts,
        expert_alignment=expert_alignment,
    )

    # ---- 步骤 3: 等待 dispatch 完成 ----
    # 使用 with 语法自动等待事件完成
    with event:
        # recv_x 形状: [total_recv_tokens, hidden]
        # 按照每个专家的 token 偏移切分，分别送入对应专家
        expert_outputs = []
        tokens_offset = 0

        for expert_idx in range(num_local_experts):
            # 从 handle 获取该专家接收的 token 数
            global_expert_idx = rank * num_local_experts + expert_idx
            num_recv = handle.num_recv_tokens_per_expert_list[global_expert_idx]

            if num_recv > 0:
                # 取出该专家的 token
                expert_tokens = recv_x[tokens_offset:tokens_offset + num_recv]
                # 执行专家计算（BF16）
                expert_out = local_experts[expert_idx](expert_tokens)
                expert_outputs.append(expert_out)
            else:
                expert_outputs.append(
                    torch.empty(0, recv_x.shape[1], device=recv_x.device,
                                dtype=recv_x.dtype)
                )
            tokens_offset += num_recv

        # 拼接所有专家的输出
        expert_output = torch.cat(expert_outputs, dim=0)

    # ---- 步骤 4: Combine（聚合专家输出回源 GPU）----
    combined_x, _, combine_event = buffer.combine(
        x=expert_output,
        handle=handle,
        topk_weights=recv_topk_weights,
    )

    # 等待 combine 完成
    combine_event.current_stream_wait()

    return combined_x


def main():
    # 初始化分布式
    rank, world_size = init_distributed()

    # MoE 配置
    hidden = 4096
    num_experts = 64
    top_k = 8
    num_tokens = 1024  # 每个 rank 的 token 数
    num_local_experts = num_experts // world_size
    expert_alignment = 128

    # 创建输入数据（BF16）
    hidden_states = torch.randn(
        num_tokens, hidden, device='cuda', dtype=torch.bfloat16
    )

    # 创建本地专家
    local_experts = nn.ModuleList([
        SimpleExpert(hidden).to(device='cuda', dtype=torch.bfloat16)
        for _ in range(num_local_experts)
    ])

    # 计算推荐的缓冲区大小（可选，也可直接指定 num_max_tokens_per_rank 让构造函数自动计算）
    num_max_tokens = int(num_tokens * 1.5)  # 预留 50% 余量
    buffer_size = deep_ep.ElasticBuffer.get_buffer_size_hint(
        group=dist.group.WORLD,
        num_max_tokens_per_rank=num_max_tokens,
        hidden=hidden,
        num_topk=top_k,
        use_fp8_dispatch=False,
    )
    if rank == 0:
        print(f"Buffer size: {buffer_size / 1024**2:.1f} MB")

    # 创建 ElasticBuffer
    buffer = deep_ep.ElasticBuffer(
        group=dist.group.WORLD,
        num_bytes=buffer_size,
        num_max_tokens_per_rank=num_max_tokens,
        hidden=hidden,
        num_topk=top_k,
        use_fp8_dispatch=False,
        deterministic=False,
        allow_hybrid_mode=True,
        prefer_overlap_with_compute=True,
    )

    if rank == 0:
        print(f"Physical domain: {buffer.get_physical_domain_size()}")
        print(f"Logical domain: {buffer.get_logical_domain_size()}")
        print(f"Num scaleout ranks: {buffer.num_scaleout_ranks}")
        print(f"Num scaleup ranks: {buffer.num_scaleup_ranks}")

    # 执行 MoE 前向传播
    dist.barrier()
    output = moe_forward(
        buffer, hidden_states, local_experts,
        num_experts=num_experts, top_k=top_k,
        expert_alignment=expert_alignment,
    )

    if rank == 0:
        print(f"Input shape: {hidden_states.shape}")
        print(f"Output shape: {output.shape}")
        print("MoE forward pass completed successfully!")

    # 清理
    dist.barrier()
    dist.destroy_process_group()


if __name__ == '__main__':
    main()
```

## 代码说明

### 分布式初始化

使用 `torch.distributed.init_process_group('nccl')` 初始化 NCCL 分布式环境。DeepEP 需要一个 `dist.ProcessGroup` 来定义通信域。

### ElasticBuffer 创建

创建缓冲区有两种方式：
1. **自动计算大小**：传入 `num_max_tokens_per_rank`、`hidden`、`num_topk`，构造函数内部调用 `_C.calculate_elastic_buffer_size()` 自动计算
2. **手动指定大小**：先通过 `get_buffer_size_hint()` 计算推荐值，再传入 `num_bytes`

建议预留一定余量（如 ×1.5）以应对负载波动。

### Dispatch

`dispatch()` 将 token 路由到持有对应专家的 GPU。关键参数：
- `x`：BF16 输入张量 `[num_tokens, hidden]`
- `topk_idx`：top-k 专家索引 `[num_tokens, top_k]`，类型为 `deep_ep.topk_idx_t`
- `topk_weights`：gating 权重 `[num_tokens, top_k]`，float32
- `num_experts`：全局专家总数
- `expert_alignment`：专家 token 对齐粒度，建议设为 128 的倍数以兼容 [DeepGEMM](/deepseek/deep-gemm) 分组 GEMM

### 专家计算

`EPHandle.num_recv_tokens_per_expert_list` 是一个 Python list，包含所有专家（包括非本地专家）接收的 token 数。本地专家的 token 数据在 `recv_x` 中连续排列，通过前缀和偏移切分。

### Combine

`combine()` 将各专家的输出加权聚合回源 GPU。必须传入 dispatch 返回的 `handle` 以逆转化路由。

### 事件同步

`EventOverlap` 支持上下文管理器（`with event:`），退出时自动等待通信完成。这是实现计算-通信重叠的基础，详见 [事件重叠示例](event-overlap.md)。

## 相关参考

- [ElasticBuffer API](/deepseek/deep-ep/references/buffer-elastic)
- [Dispatch/Combine 流程](/deepseek/deep-ep/concepts/dispatch-combine)
- [MoE 专家并行](/deepseek/deep-ep/concepts/moe-parallelism)
- [计算-通信重叠示例](event-overlap.md)
- [ElasticBuffer 使用示例](elastic-buffer.md)
