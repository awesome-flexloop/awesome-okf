---
type: example
scope: dual-pipe
name: DualPipeV 推理示例
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/examples/example_dualpipev.py
description: 使用 DualPipeV 进行 V 型双向流水线推理的示例
---

# DualPipeV 推理示例

DualPipeV 采用 V 型调度，适合自回归模型的推理场景（一端输入，一端输出 loss/logits）。

## 完整代码

```python
import torch
import torch.nn as nn
import torch.distributed as dist
from dualpipe import DualPipeV, set_p2p_tensor_shapes, set_p2p_tensor_dtype


class PipelineStage(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.linear = nn.Linear(hidden_size, hidden_size, bias=False)
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(self.linear(x))


def inference():
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    torch.cuda.set_device(rank)
    
    hidden_size = 4096
    micro_bsz = 4
    num_chunks = world_size * 2  # DualPipeV 不要求偶数
    global_bsz = micro_bsz * num_chunks
    
    # DualPipeV：每个 rank 持有两个 stage
    modules = (
        PipelineStage(hidden_size).cuda(),
        PipelineStage(hidden_size).cuda(),
    )
    model = DualPipeV(modules)
    
    # 配置通信
    set_p2p_tensor_shapes([(micro_bsz, hidden_size)])
    set_p2p_tensor_dtype(torch.bfloat16)
    
    # 推理（no_grad 模式自动检测）
    with torch.no_grad():
        if model.is_first_rank:
            inputs = (torch.randn(global_bsz, hidden_size, dtype=torch.bfloat16).cuda(),)
        else:
            inputs = (None,)
        
        _, outputs = model.step(
            *inputs,
            num_chunks=num_chunks,
            return_outputs=True,
        )
    
    if model.is_first_rank and outputs is not None:
        print(f"Output shape: {outputs[0].shape}")
    
    dist.destroy_process_group()


if __name__ == "__main__":
    inference()
```

## 运行方式

```bash
torchrun --nproc_per_node=4 example_dualpipev.py
```

## DualPipeV 推理注意事项

1. **自动检测推理模式**：`torch.no_grad()` 上下文自动设置 `self.forward_only = True`，跳过反向计算
2. **V 型连接**：数据从 first rank 流入，经过所有 stage 后在 last rank 折返，最终在 first rank 输出
3. **return_outputs=True**：需要返回输出时设置此参数
4. **无需 criterion/labels**：推理时不需要损失函数和标签
5. **num_chunks 灵活**：DualPipeV 不要求 num_chunks 为偶数，可根据实际 batch size 调整
