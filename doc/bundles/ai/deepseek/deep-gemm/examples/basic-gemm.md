---
type: example
scope: deep-gemm
name: 基础 FP8/BF16 GEMM 使用示例
version: "2.6.1"
source: tests/test_fp8_fp4.py, tests/test_bf16.py
description: DeepGEMM FP8 和 BF16 GEMM 核函数的基础使用方法，包括数据准备、量化和核函数调用
---

# 基础 GEMM 使用示例

本文档展示如何使用 DeepGEMM 进行基础的 FP8 和 BF16 矩阵乘法运算。

---

## 一、BF16 GEMM 基础用法

### 1.1 标准 BF16 GEMM

```python
import torch
import deep_gemm

# 确保在 Hopper (SM90) 或 Blackwell (SM100) GPU 上
assert torch.cuda.get_device_capability()[0] >= 9

# 准备输入数据
M, N, K = 4096, 4096, 8192
a = torch.randn(M, K, device='cuda', dtype=torch.bfloat16)
b = torch.randn(N, K, device='cuda', dtype=torch.bfloat16)  # 注意：B 是 [N, K]，内部会转置
d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)

# 执行 GEMM: D = A @ B^T
# nt 表示 A 不转置 (K-major), B 转置 (即 B 原始为 [N,K])
deep_gemm.bf16_gemm_nt(a, b, d)

# 验证结果
d_ref = a @ b.T  # PyTorch 参考结果
diff = torch.norm(d - d_ref) / torch.norm(d_ref)
print(f"相对误差: {diff.item():.6f}")
```

### 1.2 带 bias 的 BF16 GEMM

```python
# 带偏置/累加: D = A @ B^T + C
c = torch.randn(M, N, device='cuda', dtype=torch.bfloat16)
d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)
deep_gemm.bf16_gemm_nt(a, b, d, c=c)
```

### 1.3 其他转置组合

```python
# NN: D = A @ B (A: [M,K], B: [K,N]，即 B 为 N-major)
b_nn = torch.randn(K, N, device='cuda', dtype=torch.bfloat16)
deep_gemm.bf16_gemm_nn(a, b_nn, d)

# TN: D = A^T @ B (A 转置: [K,M], B 转置: [N,K]^T=[K,N])
a_tn = torch.randn(K, M, device='cuda', dtype=torch.bfloat16)
b_tn = torch.randn(N, K, device='cuda', dtype=torch.bfloat16)
deep_gemm.bf16_gemm_tn(a_tn, b_tn, d)  # 注意 d 形状匹配结果

# TT: D = A^T @ B^T
deep_gemm.bf16_gemm_tt(a_tn, b_nn, d)
```

---

## 二、FP8 GEMM 基础用法

### 2.1 Per-block FP8 量化

DeepGEMM 提供 `per_block_cast_to_fp8` 工具函数进行量化：

```python
from deep_gemm import per_block_cast_to_fp8

# 准备高精度数据
M, N, K = 4096, 4096, 8192
a_fp32 = torch.randn(M, K, device='cuda', dtype=torch.float32)
b_fp32 = torch.randn(N, K, device='cuda', dtype=torch.float32)

# Per-block 量化到 FP8（SM90 默认 128x128 block）
a_fp8, a_sf = per_block_cast_to_fp8(a_fp32, use_ue8m0=False)
b_fp8, b_sf = per_block_cast_to_fp8(b_fp32, use_ue8m0=False)

# a_fp8: torch.float8_e4m3fn, shape [M, K]
# a_sf: torch.float32, shape [ceil(M/128), ceil(K/128)]
print(f"A FP8 shape: {a_fp8.shape}, SF shape: {a_sf.shape}")
```

### 2.2 Per-token FP8 量化

```python
from deep_gemm import per_token_cast_to_fp8

# Per-token（per-row）量化，每 128 个 K 元素一个 scale
a_fp8, a_sf = per_token_cast_to_fp8(a_fp32, use_ue8m0=False, gran_k=128)
b_fp8, b_sf = per_token_cast_to_fp8(b_fp32, use_ue8m0=False, gran_k=128)
```

### 2.3 FP8 GEMM 调用

```python
# 输出为 BF16
d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)

# FP8 GEMM: D = A_fp8 @ B_fp8^T（使用 per-block scale）
# 参数格式：a=(fp8_tensor, sf_tensor), b=(fp8_tensor, sf_tensor)
deep_gemm.fp8_gemm_nt(
    (a_fp8, a_sf),
    (b_fp8, b_sf),
    d
)

# 验证（需要反量化参考结果）
d_ref = a_fp32 @ b_fp32.T
diff = torch.norm(d.to(torch.float32) - d_ref) / torch.norm(d_ref)
print(f"FP8 GEMM 相对误差: {diff.item():.6f}")
```

### 2.4 指定 Recipe

```python
# 指定缩放因子粒度 (gran_m, gran_n, gran_k)
# SM90 1D1D kernel: gran_n=1, gran_k=128
deep_gemm.fp8_gemm_nt(
    (a_fp8, a_sf),
    (b_fp8, b_sf),
    d,
    recipe=(1, 1, 128)  # 1D1D kernel
)

# 分别指定 A 和 B 的 recipe（A per-1x128，B per-128x128）
deep_gemm.fp8_gemm_nt(
    (a_fp8, a_sf),
    (b_fp8, b_sf),
    d,
    recipe_a=(1, 128),     # (gran_m, gran_k) for A
    recipe_b=(128, 128),   # (gran_n, gran_k) for B
)
```

### 2.5 FP32 输出

```python
# 输出为 FP32
d_fp32 = torch.empty(M, N, device='cuda', dtype=torch.float32)
deep_gemm.fp8_gemm_nt(
    (a_fp8, a_sf),
    (b_fp8, b_sf),
    d_fp32
)
```

---

## 三、cuBLASLt 回退

对于不被 DeepGEMM JIT 核函数支持的场景，可以使用 cuBLASLt 路径：

```python
# cuBLASLt BF16 GEMM（无需 Hopper/Blackwell）
deep_gemm.cublaslt_gemm_nt(a, b, d)
deep_gemm.cublaslt_gemm_nt(a, b, d, c=c)  # 带 bias
```

---

## 四、性能基准测试

使用 DeepGEMM 内置的 benchmark 工具：

```python
from deep_gemm.testing import bench
import time

def run_fp8_gemm():
    deep_gemm.fp8_gemm_nt((a_fp8, a_sf), (b_fp8, b_sf), d)

# 预热 5 次，测试 10 次，返回平均耗时（秒）
avg_time = bench(run_fp8_gemm, num_warmups=5, num_tests=10)
flops = 2 * M * N * K / avg_time / 1e12  # TFLOPS
print(f"FP8 GEMM: {avg_time*1e3:.2f} ms, {flops:.1f} TFLOPS")

def run_bf16_gemm():
    deep_gemm.bf16_gemm_nt(a, b, d_bf16)

d_bf16 = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)
avg_time_bf16 = bench(run_bf16_gemm, num_warmups=5, num_tests=10)
flops_bf16 = 2 * M * N * K / avg_time_bf16 / 1e12
print(f"BF16 GEMM: {avg_time_bf16*1e3:.2f} ms, {flops_bf16:.1f} TFLOPS")
```

---

## 五、完整 FP8 GEMM 示例（含 FP8 输出精度对比）

```python
import torch
import deep_gemm
from deep_gemm import per_block_cast_to_fp8, bench

def basic_fp8_gemm_demo():
    assert torch.cuda.get_device_capability()[0] >= 9, "Requires Hopper or Blackwell"

    M, N, K = 8192, 8192, 8192
    print(f"FP8 GEMM: [{M}, {K}] @ [{N}, {K}]^T = [{M}, {N}]")

    # 生成随机数据
    a_hp = torch.randn(M, K, device='cuda', dtype=torch.bfloat16)
    b_hp = torch.randn(N, K, device='cuda', dtype=torch.bfloat16)

    # Per-block FP8 量化
    a_fp8, a_sf = per_block_cast_to_fp8(a_hp.float(), use_ue8m0=False)
    b_fp8, b_sf = per_block_cast_to_fp8(b_hp.float(), use_ue8m0=False)

    # DeepGEMM FP8 GEMM
    d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)
    deep_gemm.fp8_gemm_nt((a_fp8, a_sf), (b_fp8, b_sf), d)

    # BF16 参考
    d_ref = a_hp @ b_hp.T

    # 精度检查
    cos_sim = torch.nn.functional.cosine_similarity(
        d.float().flatten().unsqueeze(0),
        d_ref.float().flatten().unsqueeze(0)
    ).item()
    print(f"余弦相似度: {cos_sim:.6f}")

    # 性能测试
    t = bench(lambda: deep_gemm.fp8_gemm_nt((a_fp8, a_sf), (b_fp8, b_sf), d))
    tflops = 2 * M * N * K / t / 1e12
    print(f"性能: {t*1e3:.2f} ms, {tflops:.1f} TFLOPS")

if __name__ == '__main__':
    basic_fp8_gemm_demo()
```

---

## 六、注意事项

1. **架构要求**：FP8/BF16 JIT 核函数需要 CUDA Driver ≥ 12.1 且 GPU SM ≥ 90（Hopper/Blackwell）
2. **K-major 要求（SM90）**：SM90 上 A 和 B 必须是 K-major（即最后一维 stride=1）；SM100 支持 K-major 和 MN-major
3. **N-major 输出**：D 必须是 N-major（行优先）
4. **首次编译**：首次调用会触发 JIT 编译，耗时几秒到几十秒；后续调用使用缓存
5. **K 对齐**：K 维度应对齐到 128（或 recipe 中的 gran_k）
6. **缓存目录**：编译缓存在 `~/.deep_gemm/cache/`，可通过 `DG_JIT_CACHE_DIR` 环境变量修改
7. **NVRTC 模式**：设置 `DG_JIT_USE_NVRTC=1` 使用运行时编译，避免 nvcc 依赖

---

## 七、相关链接

- /deepseek/deep-gemm/concepts/fp8-gemm — FP8/FP4 量化原理
- /deepseek/deep-gemm/references/api — GEMM API 完整参考
- /deepseek/deep-gemm/examples/moe-forward — MoE 分组 GEMM 示例
- /deepseek/deep-gemm/examples/tuning — 性能调优指南
