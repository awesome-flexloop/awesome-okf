---
type: concept
scope: dual-pipe
name: 自定义模块集成
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/examples/example_dualpipe.py, dualpipe/dualpipe.py
prerequisites:
  - /deepseek/dual-pipe/concepts/overview
  - /deepseek/dual-pipe/concepts/zero-bubble
  - /pydata/pytorch/module-development
description: 说明如何将自定义 PyTorch 模块集成到 DualPipe 流水线中，包括模块编写规范、overlapped_forward_backward 接口和 WeightGradStore 使用
---

# 自定义模块集成

## 模块基本要求

DualPipe 接受 `Tuple[nn.Module, nn.Module]` 作为 modules 参数，两个模块分别对应两个方向。大多数情况下，两个模块类型相同（都是你的 PipelineStage 类）。

### Stage 模块基本结构

```python
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
```

## overlapped_forward_backward 接口

如果模块实现了类方法 `overlapped_forward_backward`，DualPipe 会在 `_forward_backward_compute_chunk` 中调用它来实现自定义的前后向重叠策略。

```python
@classmethod
def overlapped_forward_backward(cls, module0, phase0, inputs0, module1, phase1, inputs1):
    """
    参数:
        module0: 第一个方向的模块实例
        phase0: 第一个方向的 phase（0 或 1）
        inputs0: 第一个方向的输入 tensor 元组
        module1: 第二个方向的模块实例
        phase1: 第二个方向的 phase
        inputs1: 第二个方向的输入 tensor 元组
    
    返回:
        无返回值。方法负责执行前向计算、保存中间结果、执行反向传播
    """
```

示例实现（来自 example_dualpipe.py）：

```python
@classmethod
def overlapped_forward_backward(cls, module0, phase0, inputs0, module1, phase1, inputs1):
    # Phase 0 前向
    x0 = inputs0[0]
    x0 = module0.linear1(x0)
    x0_for_act = x0
    x0 = module0.act(x0)
    x0 = module0.linear2(x0)
    
    # Phase 1 前向
    x1 = inputs1[0]
    x1 = module1.linear1(x1)
    x1_for_act = x1
    x1 = module1.act(x1)
    x1 = module1.linear2(x1)
    
    # 保存输入给反向
    module0.inputs = (x0_for_act,)
    module1.inputs = (x1_for_act,)
    
    # 设置输出
    outputs0 = (x0,)
    outputs1 = (x1,)
    
    # 立即执行两个方向的反向
    # 这里直接调用反向，与前向计算重叠
    if outputs0[0].grad_fn is not None:
        run_backward(outputs0, ...)
    if outputs1[0].grad_fn is not None:
        run_backward(outputs1, ...)
```

**注意**：当两个模块类型相同时，DualPipe 自动检测 `hasattr(type(modules[0]), "overlapped_forward_backward")` 并启用重叠。如果两个模块类型不同，则不会使用重叠模式。

## 集成 WeightGradStore 零气泡优化

为了让自定义线性层支持零气泡优化，需要：

### 1. 自定义 autograd Function

```python
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
            # 零气泡模式：延迟 dW 计算
            WeightGradStore.put(lambda: grad_output.t() @ input)
            grad_weight = None
        else:
            # 立即计算 dW
            grad_weight = grad_output.t() @ input
        
        return grad_input, grad_weight
```

### 2. 使用自定义 Function 的模块

```python
class MyLinear(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.bias = None
    
    def forward(self, x):
        output = LinearFunc.apply(x, self.weight)
        if self.bias is not None:
            output = output + self.bias
        return output
```

## 配置 P2P 通信

在训练前必须配置通信 tensor 的形状和 dtype：

```python
from dualpipe import set_p2p_tensor_shapes, set_p2p_tensor_dtype

# 配置：hidden_size 维的激活 tensor + labels tensor（如果有）
set_p2p_tensor_shapes([
    (global_bsz // pp_size // num_chunks, hidden_size),  # hidden states
    # 如有多个 tensor 需要通信，按顺序添加
])
set_p2p_tensor_dtype(torch.bfloat16)
```

**重要**：shapes 列表中的 tensor 顺序必须与模块 forward() 的输入顺序一致。

## 损失函数

损失函数签名：

```python
def criterion(outputs: Tuple[Tensor, ...], labels: Tuple[Tensor, ...]) -> Tensor:
    """
    参数:
        outputs: 模型输出 tensor 元组
        labels: 标签 tensor 元组
    返回:
        标量 loss tensor
    """
    return F.cross_entropy(outputs[0], labels[0])
```

## 完整训练步骤

```python
# 1. 初始化分布式
dist.init_process_group("nccl")
rank = dist.get_rank()
world_size = dist.get_world_size()
torch.cuda.set_device(rank)

# 2. 创建模块
pp_size = world_size // 2  # DualPipe 需要偶数 GPU
modules = (
    PipelineStage(hidden_size).cuda(),
    PipelineStage(hidden_size).cuda(),
)
model = DualPipe(modules)

# 3. 配置通信
set_p2p_tensor_shapes([(micro_bsz, hidden_size)])
set_p2p_tensor_dtype(torch.bfloat16)

# 4. 训练循环
for batch in dataloader:
    optimizer.zero_grad()
    
    # 第一/最后 rank 提供输入和标签
    inputs = (batch.inputs,) if model.is_first_rank else (None,)
    labels = [batch.labels] if model.is_last_rank else [None]
    
    loss, _ = model.step(
        *inputs,
        num_chunks=num_micro_batches,
        criterion=criterion,
        labels=labels,
    )
    
    optimizer.step()
```
