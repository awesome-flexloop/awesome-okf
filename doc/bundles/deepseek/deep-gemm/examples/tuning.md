---
type: example
scope: deep-gemm
name: 性能调优指南
version: "2.6.1"
source: deep_gemm/testing/bench.py, csrc/jit/device_runtime.hpp, csrc/jit_kernels/heuristics/
description: DeepGEMM 性能调优最佳实践，包括 SM/TC 配置、JIT 编译优化、性能测量和常见问题排查
---

# 性能调优指南

本文档提供 DeepGEMM 核函数的性能调优最佳实践，包括运行时配置、JIT 编译优化、性能测量方法和常见性能问题排查。

---

## 一、运行时性能配置

### 1.1 SM 数量配置

在多实例共享 GPU（如 MPS、MIG）场景下，限制 SM 数量可避免核函数抢占导致的性能抖动：

```python
import deep_gemm
import torch

# 查询 GPU 总 SM 数
total_sms = torch.cuda.get_device_properties(0).multi_processor_count
print(f"Total SMs: {total_sms}")  # H100=132, H200=132, B100=176(approx)

# 限制使用的 SM 数（例如分配 50% 给当前实例）
deep_gemm.set_num_sms(total_sms // 2)
current_sms = deep_gemm.get_num_sms()
print(f"Configured SMs: {current_sms}")

# 恢复使用全部 SM
deep_gemm.set_num_sms(0)  # 0 表示使用全部
```

**调优建议**：
- 单实例独占 GPU：保持默认（全部 SM）
- 多实例 MPS 共享：按资源比例分配，如 2 实例各分 50%
- 小批量推理：适当减少 SM 数可改善 L2 cache 命中率（但收益有限，建议实际 benchmark）

### 1.2 Tensor Core 利用率

```python
# 设置 TC 利用率（0-100，0 = 100%）
deep_gemm.set_tc_util(80)  # 使用 80% TC 单元
print(f"TC util: {deep_gemm.get_tc_util()}%")

# 恢复满速
deep_gemm.set_tc_util(0)  # 0 = 100%
```

**使用场景**：主要用于功耗控制，一般训练/推理保持 100%。

### 1.3 PDL（Programmatic Dependent Launch）

```python
# 启用 PDL（默认 False）
deep_gemm.set_pdl(True)
print(f"PDL enabled: {deep_gemm.get_pdl()}")
```

**建议**：
- 连续调用多个 DeepGEMM 核函数时启用 PDL 可减少 launch overhead
- 使用 CUDA Graph 或需要精确调试时禁用
- PDL 需要 SM90+ 架构支持

---

## 二、JIT 编译优化

### 2.1 编译缓存管理

JIT 编译缓存默认位于 `~/.deep_gemm/cache/`。

**环境变量配置**：

```bash
# 自定义缓存目录
export DG_JIT_CACHE_DIR=/path/to/cache

# 使用 NVRTC（运行时编译，无需 nvcc，编译更快）
export DG_JIT_USE_NVRTC=1

# 启用调试信息（profiling 用）
export DG_JIT_WITH_LINEINFO=1

# 编译调试（输出 ptxas 详细信息）
export DG_JIT_DEBUG=1
export DG_JIT_PTXAS_VERBOSE=1
```

**预热策略**：

```python
import deep_gemm
import torch

def warmup_deepgemm():
    """预热常见尺寸的核函数，避免首次调用时编译延迟"""
    # 使用实际训练/推理中的典型尺寸预热
    common_sizes = [
        (4096, 4096, 8192),
        (8192, 8192, 4096),
        (1024, 4096, 8192),
        # ... 根据实际使用场景添加
    ]

    for M, N, K in common_sizes:
        a = torch.randn(M, K, device='cuda', dtype=torch.bfloat16)
        b = torch.randn(N, K, device='cuda', dtype=torch.bfloat16)
        d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)
        deep_gemm.bf16_gemm_nt(a, b, d)
        torch.cuda.synchronize()
        print(f"Warmed up: M={M}, N={N}, K={K}")

# 训练/推理前执行预热
warmup_deepgemm()
```

### 2.2 忽略编译维度（减少编译次数）

如果矩阵维度变化频繁导致编译开销过大，可以禁用维度特化：

```python
# 忽略编译维度特化（使用通用 kernel，减少缓存条目）
deep_gemm.set_ignore_compile_dims(True)

# 恢复维度特化（最佳性能）
deep_gemm.set_ignore_compile_dims(False)
```

**权衡**：
- `ignore_compile_dims=False`（默认）：每个 M/N/K 组合生成特化 kernel，性能最优，但首次编译可能产生大量缓存
- `ignore_compile_dims=True`：通用 kernel 覆盖不同维度，编译次数少，但性能可能下降 5-15%

### 2.3 Block 大小倍数约束

在分布式训练中，强制 block 大小对齐通信 tile：

```python
# 强制 block_m 和 block_n 为指定值的倍数
deep_gemm.set_block_size_multiple_of(128)         # M/N 均对齐到 128
deep_gemm.set_block_size_multiple_of((128, 64))   # M 对齐 128，N 对齐 64
```

---

## 三、MK 对齐配置

### 3.1 连续布局对齐

```python
# 查询当前对齐值
current_align = deep_gemm.get_mk_alignment_for_contiguous_layout()
print(f"Current MK alignment: {current_align}")

# 设置对齐值（影响 M/K-grouped GEMM 的 padding 量）
deep_gemm.set_mk_alignment_for_contiguous_layout(128)

# 查询理论最优对齐值
best_align = deep_gemm.get_theoretical_mk_alignment_for_contiguous_layout()
print(f"Theoretical best alignment: {best_align}")

# 带预期 M 值的查询（SM100 动态计算）
best_align = deep_gemm.get_theoretical_mk_alignment_for_contiguous_layout(expected_m=256)
print(f"Best alignment for M=256: {best_align}")
```

**SM100 动态对齐策略**：

| expected_m | 理论最优 block_m |
|---|---|
| None/未知 | 224 |
| ≥ 192 | 224 |
| 160-191 | 192 |
| 128-159 | 160 |
| 96-127 | 128 |
| 64-95 | 96 |
| 32-63 | 64 |
| < 32 | 32 |

### 3.2 输入 Padding 建议

为获得最佳 TMA 加载效率，输入矩阵维度建议：
- K 维度对齐到 128（SM90）或 32/128（SM100，取决于 recipe）
- M 维度对齐到 `get_mk_alignment_for_contiguous_layout()` 返回值（默认 128）
- grouped GEMM 中每个 expert 的 K 值必须是 k_alignment 的倍数

```python
from deep_gemm import align, ceil_div

K = 5000
gran_k = 128
K_padded = align(K, gran_k)  # 向上对齐到 128 的倍数
print(f"K={K}, padded K={K_padded}")
```

---

## 四、性能测量

### 4.1 基础 Benchmark

```python
from deep_gemm.testing import bench
import torch
import deep_gemm

M, N, K = 8192, 8192, 8192
a = torch.randn(M, K, device='cuda', dtype=torch.bfloat16)
b = torch.randn(N, K, device='cuda', dtype=torch.bfloat16)
d = torch.empty(M, N, device='cuda', dtype=torch.bfloat16)

# 预热
for _ in range(5):
    deep_gemm.bf16_gemm_nt(a, b, d)
torch.cuda.synchronize()

# Benchmark（5 次预热，10 次测试，返回平均秒数）
t = bench(lambda: deep_gemm.bf16_gemm_nt(a, b, d), num_warmups=5, num_tests=20)
tflops = 2 * M * N * K / t / 1e12
print(f"BF16 GEMM: {t*1000:.2f} ms, {tflops:.1f} TFLOPS")

# 高精度模式（消除 CPU launch overhead 干扰）
t_hp = bench(lambda: deep_gemm.bf16_gemm_nt(a, b, d), high_precision=True)
tflops_hp = 2 * M * N * K / t_hp / 1e12
print(f"BF16 GEMM (high precision): {t_hp*1000:.2f} ms, {tflops_hp:.1f} TFLOPS")
```

**bench 函数内部操作**：
1. 使用 256MB int8 张量 flush L2 cache（模拟真实 cache 状态）
2. 执行 `num_warmups` 次预热
3. high_precision 模式：执行 8192×8192 FP32 matmul 消除 CPU 频率抖动
4. 使用 CUDA Event 精确计时 `num_tests` 次
5. 返回平均耗时

### 4.2 Kineto Profiling（单 Kernel 分析）

```python
from deep_gemm.testing import bench_kineto

kernel_time = bench_kineto(
    fn=lambda: deep_gemm.bf16_gemm_nt(a, b, d),
    kernel_names="bf16_gemm",  # 要测量的 kernel 名称（支持部分匹配）
    num_tests=30,
    suppress_kineto_output=True,
    flush_l2=True,
    # trace_path="trace.json"  # 可选：导出 Chrome trace
)
print(f"Kernel time: {kernel_time:.3f} us")
```

**注意**：使用 Nsight Compute/Systems 时设置 `DG_USE_NVIDIA_TOOLS=1` 跳过 kineto profiler。

### 4.3 理论峰值对比

| GPU | BF16 Tensor Core 峰值 | FP8 Tensor Core 峰值 | SM 数 | HBM 带宽 |
|---|---|---|---|---|
| H100 SXM | ~990 TFLOPS | ~1979 TFLOPS | 132 | ~3.35 TB/s |
| H200 SXM | ~990 TFLOPS | ~1979 TFLOPS | 132 | ~4.8 TB/s |
| B100 (预估) | ~2200 TFLOPS | ~4400 TFLOPS (含FP4) | ~176+ | ~8 TB/s |

DeepGEMM 通常可达到理论峰值的 70-90%（取决于矩阵尺寸、数据类型和布局）。

### 4.4 多 Kernel 性能分析

```python
# 测量多个 kernel 的时间
times = bench_kineto(
    fn=lambda: (deep_gemm.bf16_gemm_nt(a, b, d1),
                deep_gemm.bf16_gemm_nt(d1, w2, d2)),
    kernel_names=("gemm1", "gemm2"),
    num_tests=10,
    with_multiple_kernels=True,
)
print(f"GEMM1: {times[0]:.2f} us, GEMM2: {times[1]:.2f} us")
```

---

## 五、cuBLASLt 性能对比

```python
# 对比 DeepGEMM 和 cuBLASLt 性能
import deep_gemm

def bench_deepgemm():
    deep_gemm.bf16_gemm_nt(a, b, d)

def bench_cublaslt():
    deep_gemm.cublaslt_gemm_nt(a, b, d)

t_dg = bench(bench_deepgemm)
t_cublas = bench(bench_cublaslt)
print(f"DeepGEMM: {t_dg*1000:.2f} ms")
print(f"cuBLASLt: {t_cublas*1000:.2f} ms")
print(f"Speedup: {t_cublas/t_dg:.2f}x")
```

通常 DeepGEMM 在 grouped GEMM 场景和大矩阵 FP8 场景显著优于 cuBLASLt；标准 BF16 GEMM 性能与 cuBLASLt 相当或略优。

---

## 六、常见性能问题排查

### 6.1 首次调用慢

**症状**：第一次调用核函数耗时数十秒。
**原因**：JIT 编译和内核加载。
**解决方案**：
- 训练/推理开始前执行预热（参见 2.2 节）
- 使用 `DG_JIT_USE_NVRTC=1` 加速编译（部分场景）
- 持久化缓存目录到共享存储（多节点/多容器环境）

### 6.2 性能低于预期

**排查清单**：
1. **检查输入布局**：确保 A/B 是 K-major（contiguous 或正确的 transpose）
2. **检查维度对齐**：K 是否对齐到 128？M 是否对齐到 MK alignment？
3. **检查 SM 配置**：是否被意外设置了 `set_num_sms` 或 `set_tc_util`？
4. **检查 PDL 状态**：连续 kernel 场景启用 PDL 可能提升性能
5. **检查是否使用了正确的精度**：FP8 比 BF16 快约 2 倍
6. **使用 Nsight Compute 分析**：设置 `DG_JIT_WITH_LINEINFO=1` 获取源级 profiling
7. **检查 cuBLASLt 对比**：如果 cuBLASLt 更快，可能是特殊尺寸未被启发式覆盖

### 6.3 显存使用异常

**可能原因**：
- JIT 缓存过大：定期清理 `~/.deep_gemm/cache/`（注意这会导致重新编译）
- cuBLASLt workspace：32MB 固定分配
- K-grouped GEMM 的 tensormap buffer：`num_sms * 4 * sizeof(CUtensorMap)`，通常很小

### 6.4 多进程性能问题

**建议**：
- 使用 `DG_JIT_CACHE_DIR` 设置共享缓存目录，避免多进程重复编译
- 使用 MPS（Multi-Process Service）减少上下文切换开销
- 每个进程设置合理的 `set_num_sms` 避免 SM 争抢

---

## 七、环境变量速查表

| 环境变量 | 默认值 | 性能调优建议 |
|---|---|---|
| `DG_JIT_USE_NVRTC` | 0 | 开发环境设为 1 加速编译；生产环境用 NVCC |
| `DG_JIT_CACHE_DIR` | `~/.deep_gemm` | 设置到高速本地存储 |
| `DG_JIT_WITH_LINEINFO` | 0 | Profiling 时设为 1 |
| `DG_JIT_PTXAS_CHECK` | 0 | 调试时设为 1 检查 local memory |
| `DG_USE_PYTORCH_CUBLASLT_HANDLE` | 0 | 与 PyTorch 共享 handle 可减少显存 |
| `DG_USE_TEMP_CUBLASLT_WORKSPACE` | 0 | 多流并发时设为 1 避免 workspace 竞争 |
| `DG_COMM_KERNEL_DEBUG` | 0 | 仅调试 MegaMoE 时使用 |
| `DG_USE_NVIDIA_TOOLS` | 0 | 使用 NSys/NCU 时设为 1 |

---

## 八、相关链接

- [/deepseek/deep-gemm/references/runtime-config](/deepseek/deep-gemm/references/runtime-config) — 完整运行时配置 API
- [/deepseek/deep-gemm/concepts/performance-optimization](/deepseek/deep-gemm/concepts/performance-optimization) — 硬件优化技术详解
- [/deepseek/deep-gemm/concepts/jit-kernel-compilation](/deepseek/deep-gemm/concepts/jit-kernel-compilation) — JIT 编译系统
- [/deepseek/deep-gemm/examples/basic-gemm](/deepseek/deep-gemm/examples/basic-gemm) — 基础 GEMM 示例
