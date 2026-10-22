---
type: Example
title: "实战 01：稠密量化 GEMM"
description: "Humming 稠密量化 GEMM 完整实战——从最小闭环到多精度对拍、位宽与 scale 粒度扫描、MoE 前置的 Dense 基准建立，含可复制的完整脚本与判读标准"
tags: [humming, example, dense-gemm, quantization, benchmark, 对拍]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
---

# 实战 01：稠密量化 GEMM

> 场景页。目标：从「能跑」到「能判读」。本文给出可复制的完整脚本，并建立自己的量化 GEMM 判读标准。

## 一、最小闭环回顾

```python
import torch
from humming.layer import HummingLayer

layer = HummingLayer(
    shape_n=8192,
    shape_k=8192,
    weight_config={"dtype": "int6"},
    torch_dtype=torch.float16,
).cuda()

weight = torch.randn((8192, 8192), dtype=torch.float16, device="cuda:0")
inputs = torch.randn((128, 8192), dtype=torch.float16, device="cuda:0")

layer.load_from_unquantized(weight)
layer.transform()
output = layer(inputs)
```

（README.md:61-87，F-069。）

**三个必须记住的点**：

1. `from humming.layer import HummingLayer`——顶层包不导出它（F-007）。
2. `load_from_unquantized()` → `transform()` → `__call__()` 顺序不可颠倒（F-065、F-067）。
3. `int6` 是合法位宽——Humming 支持任意 ≤8 bit 整数权重（F-070）。

## 二、误差判读：不要用 assert 相等

README 的示例把量化输出与 `inputs.matmul(weight.T)` 并排打印（F-069），**没有 assert**——这是正确的。int6 权重的量化误差相当可观，逐元素相等不可能成立。

### 建立自己的判读标准

推荐三个指标而非单一的 `allclose`：

| 指标 | 含义 | 判读 |
|------|------|------|
| 相对误差中位数 | `median(\|out − ref\| / \|ref\|)` | 应随位宽提高而单调下降 |
| 归一化均方误差 | `\|\|out − ref\|\|² / \|\|ref\|\|²` | 反映能量保真度 |
| 方向性偏差 | `mean(out − ref) / mean(ref)` | **接近 0** 说明没有系统性偏差 |

**「方向性偏差接近 0」是比误差小更重要的判据**：它说明量化没有引入系统性偏移，误差是随机的。这一项若明显偏离零，说明有问题（scale 配错、零点处理错误、packing 布局错误等），而不是「精度不够」。

### 完整对拍脚本

```python
import torch
from humming.layer import HummingLayer

torch.manual_seed(0)
dev = "cuda:0"

def check(dtype: str, act_dtype: torch.dtype, shape_n=8192, shape_k=8192, m=128):
    layer = HummingLayer(
        shape_n=shape_n,
        shape_k=shape_k,
        weight_config={"dtype": dtype},
        torch_dtype=act_dtype,
    ).cuda()

    weight = torch.randn((shape_n, shape_k), dtype=act_dtype, device=dev)
    inputs = torch.randn((m, shape_k), dtype=act_dtype, device=dev)

    layer.load_from_unquantized(weight)
    layer.transform()
    out = layer(inputs)

    ref = inputs.matmul(weight.T)
    diff = out.float() - ref.float()
    # 与上文表格定义一致：逐元素相对误差的中位数
    rel = (diff.abs() / ref.float().abs().clamp_min(1e-6)).median()
    nmse = (diff.norm() ** 2) / (ref.float().norm() ** 2)
    bias = diff.mean() / ref.float().mean()

    print(f"{dtype:>6} {str(act_dtype):>16}  rel_med={rel:.4f}  nmse={nmse:.5f}  bias={bias:+.5f}")
    return rel.item(), nmse.item(), bias.item()

for w in ["int4", "int6", "int8"]:
    check(w, torch.float16)
```

### 期望的观察结果

| 位宽 | 相对误差 | 方向性偏差 |
|------|---------|-----------|
| int4 | 最大 | ≈ 0 |
| int6 | 明显小于 int4 | ≈ 0 |
| int8 | 最小 | ≈ 0 |

**如果方向性偏差明显非零**，优先排查（按可能性排序）：

1. `weight_config` 的 scale 粒度与实际权重格式不匹配（见 [02 量化模型](../concepts/02-quantization-model.md) 的 scale 粒度四态）
2. `input_config` 缺失——输入侧量化配置与权重侧不对齐
3. 零点处理：`has_zero_point` / `is_fp_zero_point` 设置与实际数据不符
4. 形状对齐：`pad_shape_n` / `pad_shape_k` 未按 kernel 要求对齐（F-054）

## 三、位宽与精度扫描

Humming 的核心价值是**位宽自由**。这个扫描是 Marlin 类内核做不到的（F-091）：

```python
# 1~8 bit 全谱扫描
for bits in range(1, 9):
    check(f"int{bits}", torch.float16)
```

**期望**：误差随位宽单调下降。**若某个位宽出现异常跳变**，说明该位宽走了不同的代码路径（Humming 会把符合条件的对称整数权重**自动转成指数位为 0 的浮点**——F-026——转换条件包含「位宽 2–8」与「权重中不含 0 值」，所以 int1 与含 0 值的权重可能走不同路径）。

> 这是**正常现象**而非 bug，但**必须知道**：int1 与 int2 的行为可能与其他位宽不同，因为自动转换的条件不满足时会走原始整数路径。

## 四、激活类型扫描

```python
for act in [torch.float16, torch.bfloat16]:
    check("int8", act)
```

**架构门槛约束**（F-013）：

| 激活 | 门槛 | 不满足时的表现 |
|------|------|--------------|
| float16 | SM75+ | 断言失败 |
| bfloat16 | SM80+ | 断言失败 |

> **Turing（SM75）上只能用 float16**。如果你的部署目标包含 T4 / V100，注意 BF16 会直接失败。

## 五、Shape 对齐

kernel 有硬性 assert（F-054 上下文）：

```python
assert padded_shape_n % 64 == 0
assert padded_shape_k % (512 / kNumBitsA) == 0
```

**实操**：如果 `shape_k` 不是 `512 / num_bits_a` 的整数倍，需要用 `pad_k_to_multiple`：

```python
layer = HummingLayer(
    shape_n=8192,
    shape_k=4096,           # 需检查是否满足对齐
    pad_k_to_multiple=16,   # 按需调整
    weight_config={"dtype": "int8"},
    torch_dtype=torch.float16,
).cuda()
```

**对齐参数不是优化选项，是前置条件**——不满足会直接失败。

> **注**：上面 `padded_shape_n` / `padded_shape_k` 是 kernel 内部的补齐后维度（`humming/include/humming/kernel/process.cuh` 的 assert 条件），**不是 `LayerConfig` 的公开字段名**——公开字段是 `pad_shape_n` / `pad_shape_k` / `pad_n_to_multiple` / `pad_k_to_multiple`（F-032、F-063）。

## 六、性能基线建立

功能对了之后建立自己的性能基线（官方数据的条件见 [08 性能与基准](../concepts/08-performance.md)）：

```python
import time

def bench(dtype: str, m_values=[1, 8, 128, 1024, 8192], shape_n=8192, shape_k=8192):
    layer = HummingLayer(
        shape_n=shape_n, shape_k=shape_k,
        weight_config={"dtype": dtype},
        torch_dtype=torch.float16,
    ).cuda()
    weight = torch.randn((shape_n, shape_k), dtype=torch.float16, device=dev)
    layer.load_from_unquantized(weight)
    layer.transform()

    for m in m_values:
        inputs = torch.randn((m, shape_k), dtype=torch.float16, device=dev)
        # warmup（编译 + kernel 选择）
        for _ in range(5):
            layer(inputs)
        torch.cuda.synchronize()

        t0 = time.perf_counter()
        for _ in range(50):
            layer(inputs)
        torch.cuda.synchronize()
        dt = (time.perf_counter() - t0) / 50 * 1e3

        # 有效 TFLOPS = 2 * N * K * M / 时间
        tflops = 2 * shape_n * shape_k * m / (dt * 1e-3) / 1e12
        print(f"{dtype} m={m:>5}  {dt:8.3f} ms  {tflops:8.1f} TFLOPS")
```

**M 档位很重要**：Humming 为不同 M 预编译不同 tile 配置（F-057），所以 M=1 与 M=8192 的性能形态完全不同——小 M 是访存受限，大 M 是计算受限（见 [05 调优与启发式](../concepts/05-tuning.md) 的瓶颈判定）。

**务必把 warmup 放在计时之外**：前几次调用包含 JIT 编译（1.82–1.88 秒/ kernel，F-080），不预热会把编译时间算进延迟。

## 七、与 PyTorch 对照

```python
# PyTorch 原生 BF16 GEMM 作为参考上限
inputs = torch.randn((4096, 8192), dtype=torch.bfloat16, device=dev)
weight = torch.randn((8192, 8192), dtype=torch.bfloat16, device=dev)

for _ in range(10):
    ref = inputs.matmul(weight.T)
torch.cuda.synchronize()
```

官方数据给了个参照点：SM120 上最低位配置超过 BF16 cuBLAS 的 **5×**（F-088），大 batch 下 H20 上多个位宽维持接近 BF16 cuBLAS 的计算效率。

**但这是官方条件下的数字**。你自己的机器、shape、位宽组合需要自己测。

## 八、排查清单

| 症状 | 优先排查 |
|------|---------|
| 方向性偏差明显非零 | scale 粒度 / input_config / 零点设置 |
| 断言失败（类型） | 权重位宽 > 激活位宽、整数权重+浮点激活时权重未设无符号、架构门槛（F-015、F-016、F-013） |
| 断言失败（对齐） | `pad_shape_n` / `pad_shape_k`（F-054） |
| illegal instruction | 用了未文档化浮点格式且架构不在白名单（F-029） |
| 首次调用极慢 | 正常——JIT 编译 1.82–1.88 秒/ kernel（F-080）；检查缓存目录可写 |
| 多次调用仍极慢 | 缓存未命中——检查 `HUMMING_CACHE_DIR` 与签名变化（F-042、F-043） |
| 编译失败 | `RuntimeError` 消息给出缓存目录，看 `stderr.log` 与 `kernel.cu`（F-046） |

## 九、下一步

- [02 MoE GEMM](02-moe-gemm.md)：grouped 形态的实战
- [04 基准对拍](04-benchmarking.md)：与 Marlin / CUTLASS / Torch 横向比
- [03 架构总览](../concepts/03-architecture.md)：想自定义 kernel 时看这里
