---
type: concept
scope: tile-kernels
name: Autograd 集成模式
version: "0.1.0"
source: tile-kernels-spec-facts
description: TileKernels autograd.Function 封装模式详解——标准 forward/backward、fuse_grad_acc、main_grad、partial buffer reduce
---

# Autograd 集成模式

TileKernels 的高层 API 通过 PyTorch 的 `torch.autograd.Function` 机制将 TileLang JIT kernel 集成到 PyTorch 计算图中。每个可微算子都封装为 `autograd.Function` 的子类，在 `forward` 中调用前向 kernel，在 `backward` 中调用对应的反向 kernel。此外，TileKernels 还实现了两种梯度优化技术：fused gradient accumulation 和 main_grad 模式。

---

## 一、标准 Autograd.Function 模式

### 1.1 基本结构

所有 TileKernels 的 autograd 封装遵循统一模式：

```python
class MyOpFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input1, input2, ...):
        # 1. 获取或编译 JIT kernel
        kernel = get_my_fwd_kernel(compiled_params...)
        # 2. 分配输出 tensor
        out = torch.empty(out_shape, device=input1.device, dtype=output_dtype)
        # 3. 调用前向 kernel
        kernel(input1, input2, out, ...)
        # 4. 保存反向需要的中间结果
        ctx.save_for_backward(input1, input2, ...)
        ctx.compiled_params = compiled_params
        return out

    @staticmethod
    def backward(ctx, grad_out):
        # 1. 获取保存的中间结果
        input1, input2, ... = ctx.saved_tensors
        # 2. 获取或编译反向 kernel
        bwd_kernel = get_my_bwd_kernel(ctx.compiled_params...)
        # 3. 分配梯度 tensor
        grad_input1 = torch.empty_like(input1)
        # 4. 调用反向 kernel
        bwd_kernel(grad_out, input1, input2, grad_input1, ...)
        # 5. 返回梯度（与 forward 参数一一对应，不需要梯度的返回 None）
        return grad_input1, None, ...

# 函数式 API
my_op = MyOpFn.apply
```

### 1.2 TileKernels 中的典型封装

以 `ExpandToMHCFn` 为例：

```python
class ExpandToMHCFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, hidden, mhc_mult, out):
        ctx.mhc_mult = mhc_mult
        ctx.save_for_backward(hidden if hidden.requires_grad else torch.empty(0))
        if out is None:
            out_shape = hidden.shape[:-1] + (mhc_mult, hidden.shape[-1])
            out = hidden.new_empty(out_shape)
        kernel = expand_to_mhc_fwd_tl(hidden.shape[-1], mhc_mult)
        kernel(hidden, out)
        return out

    @staticmethod
    def backward(ctx, out_grad):
        hidden, = ctx.saved_tensors
        if hidden.numel() == 0:
            return None, None, None
        mhc_mult = ctx.mhc_mult
        grad = torch.empty_like(hidden)
        kernel = expand_to_mhc_bwd_tl(hidden.shape[-1], mhc_mult)
        kernel(out_grad, grad)
        return grad, None, None
```

### 1.3 全部 Autograd.Function 列表

| Function 类 | 模块 | 功能 |
|---|---|---|
| `ExpandToMHCFn` | modeling/mhc/ops/expand.py | (...,H)→(...,mhc,H) 复制 |
| `MHCHeadComputeMix` | modeling/mhc/ops/head_compute_mix.py | sigmoid(scale*x+base)+eps |
| `MHCPreNormFn` | modeling/mhc/ops/norm_fn.py | RMSNorm+GEMM |
| `_MHCFnNormwMerge` | modeling/mhc/ops/norm_fn.py | fn×normw 融合乘法 |
| `MHCPreSplitMixes` | modeling/mhc/ops/pre_split_mixes.py | mix 线性变换+分割 |
| `_SinkhornNormalize` | modeling/mhc/ops/sinkhorn.py | Sinkhorn 双随机归一化 |
| `MHCPreApplyMix` | modeling/mhc/ops/pre_apply_mix.py | 加权求和归约 |
| `MHCPost` | modeling/mhc/ops/post.py | residual 混合后处理 |
| `EngramGateFn` | modeling/engram/engram_gate.py | Engram 门控 |

---

## 二、Fused Gradient Accumulation

### 2.1 问题背景

在标准 PyTorch autograd 中，每个 Function 的 backward 独立分配梯度 tensor，然后通过 autograd 引擎自动累加。但在 MHC 等多算子串联的场景中，中间梯度 tensor 的反复分配和释放会带来显著的内存和调度开销。

### 2.2 Fuse Grad Acc 机制

TileKernels 通过在 tensor 的 `untyped_storage()` 上挂载 `.grad_from_mhc_post` 属性，在多个 Function 之间共享 fp32 梯度缓冲区，避免中间梯度的额外分配：

```python
# mhc_post_bwd 计算 d_residual 后
if fuse_grad_acc:
    # 不直接返回 d_residual，而是挂到 storage 上
    residual.untyped_storage().grad_from_mhc_post = d_residual
    d_residual_return = None  # 由下一个 function 取用
else:
    d_residual_return = d_residual
```

下游 Function（如 `mhc_pre_apply_mix_bwd`）在执行时检查输入 tensor 的 storage 上是否已有梯度：

```python
# mhc_pre_apply_mix_bwd 中
grad_from_post = getattr(x.untyped_storage(), 'grad_from_mhc_post', None)
if grad_from_post is not None:
    # 在已有梯度缓冲区上直接累加
    accumulated_grad = my_grad + grad_from_post
    # 清理属性
    del x.untyped_storage().grad_from_mhc_post
else:
    accumulated_grad = my_grad
```

### 2.3 梯度接力流程

MHC 训练时的梯度接力链：

```
forward:  mhc_pre_norm_fn → mhc_pre_split_mixes → sinkhorn → mhc_pre_apply_mix → [Attn/FFN] → mhc_post
backward: mhc_post_bwd ──────────────────────────────────────────────────────────────────────→ mhc_pre_apply_mix_bwd → ...
              │                                                                                    │
              │ d_residual → residual.untyped_storage().grad_from_mhc_post                         │ 检测到 grad_from_mhc_post
              │                                                                                    │ 直接在该缓冲区累加
              ▼                                                                                    ▼
         不返回 d_residual                                                          减少一次内存分配和拷贝
```

这种机制的效果相当于将多个相邻 Function 的 backward 部分"融合"，减少了中间梯度的内存分配和读写。

---

## 三、Main Grad 模式

### 3.1 问题背景

混合精度训练中，模型参数通常以 BF16/FP16 存储，但梯度需要在 FP32 中累积以避免精度损失。PyTorch 的标准做法是维护一份 FP32 主权重（master weights），但这需要额外的内存和转换。

### 3.2 Main Grad 实现

TileKernels 的 `EngramGateFn` 和 `MHCPreSplitMixes` 等 Function 支持 main_grad 模式：如果权重参数上挂载了 `.main_grad` 属性（一个 FP32 tensor），梯度直接原地累积到 main_grad，backward 对该参数返回 None。

```python
# EngramGateFn.backward 中的 main_grad 处理
grad_w = grad_w_reduce(...)  # fp32 梯度

# 检查 weight_hidden 是否有 main_grad
w_h_main_grad = getattr(weight_hidden, 'main_grad', None)
if w_h_main_grad is not None:
    # 原地累加到 fp32 main_grad
    w_h_main_grad.add_(grad_w_hidden)
    grad_weight_hidden = None  # 返回 None，autograd 不做额外分配
else:
    grad_weight_hidden = grad_w_hidden.to(weight_hidden.dtype)
```

### 3.3 使用方式

```python
# 训练前，为参数挂载 main_grad
for name, param in model.named_parameters():
    if param.requires_grad:
        param.main_grad = torch.zeros_like(param, dtype=torch.float32)

# 标准反向传播
loss.backward()

# 优化器更新时使用 main_grad
for param in model.parameters():
    if hasattr(param, 'main_grad'):
        optimizer_step(param, param.main_grad)
        param.main_grad.zero_()
```

---

## 四、Partial Buffer Reduce

对于 scale、base 等 1D 参数，其梯度在 backward 中使用 partial buffer 模式高效归约：

```python
# MHCPreSplitMixes.backward 中的 scale/base 梯度计算
num_sms = get_num_sms()  # 使用配置的 SM 数量

# 分配 partial buffer：每个 SM 独立累积一份梯度
scale_grad_partial = torch.empty(num_sms, dtype=torch.float32, device=device)
base_grad_partial = torch.empty(num_sms, dtype=torch.float32, device=device)

# 反向 kernel：每个 SM 独立写自己的 partial buffer
bwd_kernel(grad_output, input_mixes, scale_grad_partial, base_grad_partial, num_sms)

# 最后 sum 归约
scale_grad = scale_grad_partial.sum(0)
base_grad = base_grad_partial.sum(0)
```

这种设计避免了在 kernel 内使用原子加（atomicAdd）导致的竞争，同时利用了 GPU 的并行度。num_sms 可以通过 `set_num_sms()` 调整以平衡并行度和 buffer 大小。

---

## 五、Save for Backward

`ctx.save_for_backward()` 用于保存反向传播需要的中间结果。TileKernels 中的使用模式：

1. **tensor 类型输入**：使用 `ctx.save_for_backward()` 保存，backward 中通过 `ctx.saved_tensors` 获取
2. **非 tensor 参数**（如 int、float、bool）：直接挂到 `ctx` 对象上（如 `ctx.mhc_mult = mhc_mult`）
3. **可选保存**：不需要梯度的输入可以不保存，或保存一个空 tensor 作为标记

```python
# 示例：只在需要梯度时保存输入
@staticmethod
def forward(ctx, hidden, mhc_mult, out):
    ctx.mhc_mult = mhc_mult
    # 只有 hidden 需要梯度时才保存
    ctx.save_for_backward(hidden if hidden.requires_grad else torch.empty(0))
    ...

@staticmethod
def backward(ctx, out_grad):
    hidden, = ctx.saved_tensors
    if hidden.numel() == 0:
        return None, None, None  # 不需要计算 hidden 的梯度
    ...
```

---

## 六、高层 Functional API

在 autograd.Function 之上，TileKernels 提供了 functional 风格的高层 API，封装了完整的子层处理逻辑：

```python
def mhc_pre(residual, fn, scale, base, *, norm_weight=None, norm_eps=1e-6,
            mhc_mult=4, post_mult_value=1.0, pre_eps=1e-6,
            sinkhorn_eps=1e-6, sinkhorn_repeat=10, n_splits=16):
    """MHC 子层预处理一站式 API"""
    if not torch.is_grad_enabled():
        # 推理模式：使用大融合 kernel
        return mhc_pre_big_fuse(residual, fn, scale, base, ...)
    else:
        # 训练模式：分步执行 autograd.Function 链
        normed = mhc_pre_norm_fn(residual, mhc_fn, norm_weight, norm_eps)
        pre_mix, post_mix, comb_mix = mhc_pre_split_mixes(normed, scale, base, ...)
        comb_mix = sinkhorn_normalize(comb_mix, sinkhorn_repeat, sinkhorn_eps)
        layer_input = mhc_pre_apply_mix(normed, pre_mix)
        return layer_input, (post_mix, comb_mix)
```

这种设计让用户无需了解内部的 autograd.Function 细节，同时自动选择最优的训练/推理路径。

---

## 七、EngramGateFn 完整示例

EngramGateFn 是最复杂的 autograd.Function 之一，整合了 fused_weight、前向/反向 kernel、grad_w_reduce 和 main_grad 模式：

```python
class EngramGateFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, hidden_states, k, v, weight_hidden, weight_embed, clamp_value, eps):
        # 1. 融合权重（bf16×bf16→fp32）
        weight_fused = fused_weight(weight_hidden, weight_embed)
        # 2. 调用前向 kernel
        output, dot, gate_score, rstd_x, rstd_k = engram_gate_fwd(
            hidden_states, k, v, weight_fused, eps, clamp_value,
            save_for_backward=True,
        )
        # 3. 保存中间结果
        ctx.save_for_backward(hidden_states, k, v, weight_fused, dot, gate_score, rstd_x, rstd_k)
        ctx.clamp_value = clamp_value
        ctx.has_w_h_grad = weight_hidden.requires_grad
        ctx.has_w_e_grad = weight_embed.requires_grad
        # 4. main_grad 检测
        ctx.w_h_main_grad = getattr(weight_hidden, 'main_grad', None)
        ctx.w_e_main_grad = getattr(weight_embed, 'main_grad', None)
        return output

    @staticmethod
    def backward(ctx, grad_output):
        hidden_states, k, v, weight_fused, dot, gate_score, rstd_x, rstd_k = ctx.saved_tensors
        # 1. 调用反向 kernel
        grad_x, grad_k, grad_v, grad_w_partial = engram_gate_bwd(
            grad_output, hidden_states, k, v, weight_fused,
            dot, gate_score, rstd_x, rstd_k, ctx.clamp_value,
        )
        # 2. 归约权重梯度
        grad_w_h = torch.zeros_like(weight_fused)
        grad_w_e = torch.zeros_like(weight_fused)
        grad_w_reduce(grad_w_partial, weight_fused, grad_w_h, grad_w_e)
        # 3. main_grad 处理
        if ctx.w_h_main_grad is not None:
            ctx.w_h_main_grad.add_(grad_w_h)
            grad_w_h = None
        if ctx.w_e_main_grad is not None:
            ctx.w_e_main_grad.add_(grad_w_e)
            grad_w_e = None
        return grad_x, grad_k, grad_v, grad_w_h, grad_w_e, None, None
```

---

## 八、设计总结

TileKernels 的 autograd 集成有三个层次的优化：

1. **基础层**：标准 `torch.autograd.Function` 封装前向/反向 kernel，保证正确性和自动微分
2. **性能层**：fused_grad_acc 通过 storage 属性共享梯度缓冲区，减少中间张量分配；partial buffer reduce 避免原子操作竞争
3. **训练优化层**：main_grad 模式支持 FP32 主梯度原地累积，适配混合精度训练

这些模式使得 TileKernels 的算子既能无缝融入 PyTorch 训练流水线，又能达到接近手写 CUDA 的性能。
