---
type: concept
scope: dual-pipe
name: 零气泡权重梯度优化
version: "1.0.0"
source: external/libs/ai/deepseek-ai/DualPipe/dualpipe/utils.py, examples/example_dualpipe.py
prerequisites:
  - /deepseek/dual-pipe/concepts/overview
  - /pydata/pytorch/autograd
description: 解释 WeightGradStore 如何延迟权重梯度计算以消除流水线气泡，实现零气泡（Zero-Bubble）优化
---

# 零气泡权重梯度优化

## 反向传播中的权重梯度问题

在标准反向传播中，计算顺序是：

1. 从 loss 开始反向传播，计算每个参数的输入梯度（δ）
2. 使用输入梯度和前向保存的激活值计算权重梯度（∂L/∂W）
3. 继续将输入梯度传递到前一层

权重梯度计算（dW）不需要立即执行——它只在优化器 step 时才需要。但在传统流水线中，dW 计算占用了 GPU 计算时间，而这段时间本可以用来进行其他微批次的前向/反向计算。

## WeightGradStore 的延迟策略

DualPipe 通过 `WeightGradStore` 类实现了权重梯度计算的延迟执行：

```python
class WeightGradStore:
    enabled: bool = False
    cache: List[Callable] = []
    funcs_queue = queue.Queue()
```

**三步流程：**

### 1. 缓存（put）

在自定义 autograd Function 的 backward 中，如果 `WeightGradStore.enabled` 为 True，不立即计算 dW，而是将计算函数放入 cache：

```python
@staticmethod
def backward(ctx, grad_output):
    input, weight = ctx.saved_tensors
    grad_input = grad_output @ weight
    if WeightGradStore.enabled:
        # 延迟模式：将 dW 计算函数放入缓存
        WeightGradStore.put(lambda: grad_output.t() @ input)
    else:
        # 立即模式：直接计算 dW
        grad_weight = grad_output.t() @ input
    return grad_input, grad_weight
```

### 2. 冲刷（flush）

当一个 micro-batch 的反向传播完成时（`_backward_compute_chunk` 中 `enable_zb=True`），调用 `flush()` 将 cache 中的函数移到 `funcs_queue` 队列。

### 3. 执行（pop）

在调度的 `nW` 和 `nWB0` 步骤中，`_weight_chunk()` 调用 `pop()` 从队列取出函数并执行。这些步骤与通信操作并行，因此 dW 计算不再引入额外气泡。

## 时序对比

**没有零气泡优化：**
```
时间: |--F--|--B(dX+dW)--|--comm--|
GPU:   计算   计算         空闲(气泡)
```

**有零气泡优化：**
```
时间: |--F--|--B(dX only)--|--comm+dW--|
GPU:   计算   计算          通信+计算(重叠)
```

dW 计算被推迟到与通信重叠的时间段执行，消除了等待通信期间的计算空闲。

## 如何在自定义模块中使用

要启用零气泡优化，你的模块需要：

1. 定义自定义 autograd Function，在 backward 中检查 `WeightGradStore.enabled`
2. 将权重梯度计算包装为 lambda 函数，通过 `WeightGradStore.put()` 缓存
3. DualPipe 内部在适当时机自动调用 `flush()` 和 `pop()`

参考 [examples/example_dualpipe.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/DualPipe/examples/example_dualpipe.py) 中的 `LinearFunc` 实现。
