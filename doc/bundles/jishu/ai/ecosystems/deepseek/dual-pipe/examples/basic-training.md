---
type: example
scope: dual-pipe
name: DualPipe 基础训练示例
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/examples/example_dualpipe.py
description: 使用 DualPipe 进行双向流水线并行训练的完整示例，包含自定义模块、零气泡优化和训练循环
---

# DualPipe 基础训练示例

本示例演示如何使用 DualPipe 在多个 GPU 上进行双向流水线并行训练。

## 前置条件

- 至少 2 个 GPU（DualPipe 要求偶数个 GPU）
- PyTorch 分布式环境已初始化（NCCL backend）
- 模型按层切分为 pp_size 个 stage

## 完整代码

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributed as dist
from dualpipe import DualPipe, set_p2p_tensor_shapes, set_p2p_tensor_dtype, WeightGradStore


# ========== 1. 自定义 autograd Function（支持零气泡优化）==========

class LinearFunc(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input, weight):
        ctx.save_for_backward(input, weight)
        return input @ weight.t()

    @staticmethod
    def backward(ctx, grad_output):
        input, weight = ctx.saved_tensors
        grad_input = grad_output @ weight
        
        if WeightGradStore.enabled:
            # 零气泡模式：将 dW 计算延迟到通信阶段
            WeightGradStore.put(lambda: torch.matmul(grad_output.t(), input, out=weight.grad))
            return grad_input, None
        else:
            return grad_input, grad_output.t() @ input


class MyLinear(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None

    def forward(self, x):
        out = LinearFunc.apply(x, self.weight)
        return out + self.bias if self.bias is not None else out


# ========== 2. Pipeline Stage 模块 ==========

class PipelineStage(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.linear1 = MyLinear(hidden_size, hidden_size, bias=False)
        self.act = nn.GELU()
        self.linear2 = MyLinear(hidden_size, hidden_size, bias=False)

    def forward(self, x):
        x = self.linear1(x)
        x = self.act(x)
        x = self.linear2(x)
        return x

    @classmethod
    def overlapped_forward_backward(cls, module0, phase0, inputs0, 
                                     module1, phase1, inputs1):
        """自定义前后向重叠策略"""
        # Phase 0 前向
        x0 = module0.linear1(inputs0[0])
        x0_act = module0.act(x0)
        x0_out = module0.linear2(x0_act)
        
        # Phase 1 前向
        x1 = module1.linear1(inputs1[0])
        x1_act = module1.act(x1)
        x1_out = module1.linear2(x1_act)
        
        outputs0 = (x0_out,)
        outputs1 = (x1_out,)
        
        # 执行反向（与前向重叠）
        from dualpipe.utils import run_backward
        if outputs0[0].grad_fn is not None:
            run_backward(outputs0, [torch.ones_like(o) for o in outputs0 if o.requires_grad])
        if outputs1[0].grad_fn is not None:
            run_backward(outputs1, [torch.ones_like(o) for o in outputs1 if o.requires_grad])


# ========== 3. 损失函数 ==========

def criterion(outputs, labels):
    return F.mse_loss(outputs[0], labels[0])


# ========== 4. 训练脚本 ==========

def train():
    # 分布式初始化
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    torch.cuda.set_device(rank)
    
    # 配置
    hidden_size = 4096
    micro_bsz = 4
    num_chunks = world_size * 2  # 必须是偶数且 >= 2*num_ranks
    global_bsz = micro_bsz * num_chunks
    
    # 创建模型
    modules = (
        PipelineStage(hidden_size).cuda(),
        PipelineStage(hidden_size).cuda(),
    )
    model = DualPipe(modules)
    
    # 配置 P2P 通信
    set_p2p_tensor_shapes([(micro_bsz, hidden_size)])
    set_p2p_tensor_dtype(torch.bfloat16)
    
    # 优化器
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    # 训练循环
    for step in range(100):
        optimizer.zero_grad()
        
        # 生成模拟数据（仅首/尾 rank 需要数据）
        if model.is_first_rank:
            inputs = (torch.randn(global_bsz, hidden_size, dtype=torch.bfloat16).cuda(),)
            labels = [None, None]
        elif model.is_last_rank:
            inputs = (None,)
            labels = [None, torch.randn(global_bsz, hidden_size, dtype=torch.bfloat16).cuda()]
        else:
            inputs = (None,)
            labels = [None, None]
        
        # 执行一步训练
        loss, outputs = model.step(
            *inputs,
            num_chunks=num_chunks,
            criterion=criterion,
            labels=labels,
        )
        
        optimizer.step()
        
        if rank == 0 and loss is not None:
            print(f"Step {step}, Loss: {loss.item():.4f}")
    
    dist.destroy_process_group()


if __name__ == "__main__":
    train()
```

## 运行方式

```bash
torchrun --nproc_per_node=4 example_dualpipe.py
```

## 关键点说明

1. **偶数 GPU**：DualPipe 要求 world_size 为偶数，每个 GPU 持有两个 stage
2. **num_chunks**：必须为偶数且 ≥ 2×world_size，决定了流水线深度
3. **inputs/labels**：只有 is_first_rank 和 is_last_rank 需要提供实际数据，中间 rank 传 None
4. **overlapped_forward_backward**：类方法实现前后向计算重叠，是性能优化的关键
5. **WeightGradStore**：通过延迟 dW 计算到通信阶段，实现零气泡优化
6. **通信配置**：必须在 step() 前调用 set_p2p_tensor_shapes 和 set_p2p_tensor_dtype
