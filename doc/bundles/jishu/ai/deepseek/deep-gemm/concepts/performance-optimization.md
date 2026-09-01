---
type: concept
scope: deep-gemm
name: 性能优化技术
version: "2.6.1"
source: deep_gemm/include/deep_gemm/ptx/tma.cuh, deep_gemm/include/deep_gemm/ptx/wgmma.cuh, deep_gemm/include/deep_gemm/mma/sm90.cuh, deep_gemm/include/deep_gemm/mma/sm100.cuh
description: DeepGEMM 使用的关键硬件性能优化技术：TMA、WGMMA、PDL、SM 配置、数据 swizzle
---

# 性能优化技术

DeepGEMM 充分利用 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 架构的新硬件特性来实现极致的 GEMM 性能。本文档详细介绍这些硬件特性及其在 DeepGEMM 中的应用。

---

## 一、TMA（Tensor Memory Accelerator）

### 1.1 什么是 TMA

TMA 是 Hopper 架构引入的专用硬件异步拷贝引擎，替代了 Ampere 时代的 cp.async 指令。TMA 可以在不占用 SM 计算单元的情况下，将多维张量数据从 HBM 异步加载到 shared memory，支持复杂的张量布局和多播。

### 1.2 TMA 在 DeepGEMM 中的应用

- **全局内存 → Shared Memory**：A 和 B 矩阵的 tile 加载通过 TMA 异步完成
- **多播加载**：Thread Block Cluster 模式下，TMA 支持将数据一次加载广播到 cluster 内多个 SM 的 shared memory
- **多维张量描述符（Tensor Map）**：使用 `cuTensorMapEncodeTiled` 创建张量描述符，编码数据指针、维度、步长、元素类型等信息
- **异步完成通知**：TMA 操作通过 `cp.async.bulk.tensor` 指令发起，通过 mbarrier（内存屏障）通知完成

### 1.3 TMA 对齐要求

- 数据起始地址 **128 字节对齐**
- Shared memory 基地址 128 字节对齐
- 维度大小满足 tile 大小的整数倍（或通过 padding 补齐）
- K 维度的对齐粒度为 32 或 128（取决于 recipe）
- MN-major（stride(-2)==1）排列用于 SF 张量

### 1.4 TMA 描述符预分配

对于 K-grouped NT GEMM，需要在运行时预分配 tensormap buffer：

```cpp
// num_sms * 4 * sizeof(CUtensorMap) 字节
// 4 = A/B 双缓冲 × 2 operands
auto tensor_map_buffer = torch::empty(
    {num_sms * 4 * static_cast<int>(sizeof(CUtensorMap))},
    options.dtype(torch::kByte));
```

---

## 二、WGMMA（Warp Group Matrix Multiply-Accumulate）

### 2.1 什么是 WGMMA

WGMMA 是 Hopper 引入的 warp group 级矩阵乘累加指令，将 4 个 warp（128 个线程）组织为一个 warp group 协同执行矩阵乘法。相比 Ampere 的 wmma（单 warp 级），WGMMA 具有更高的计算吞吐和更大的累加器容量。

### 2.2 WGMMA 在不同架构上的支持

| 特性 | SM90 (Hopper) | SM100 (Blackwell) |
|---|---|---|
| Warp group 大小 | 4 warps (128 threads) | 4 warps (128 threads) |
| FP8 WGMMA | `wgmma.mma_async.sync.aligned.m64nNk16.f32.e4m3.e4m3` | 同左 + FP4 支持 |
| FP4 WGMMA | ❌ | `wgmma.mma_async.sync.aligned.m64nNk32.f32.e2m1.e2m1`（TCGen05） |
| BF16 WGMMA | `wgmma.mma_async.sync.aligned.m64nNk16.f32.bf16.bf16` | 同左 |
| MMA 形状 | m64 × nN × k16 | FP8: m64 × nN × k32；FP4: m64 × nN × k64 |
| Scale 支持 | 浮点 scale | UE8M0 硬件 scale（无需反量化） |
| 累加器 | FP32 寄存器 | FP32 寄存器 |

### 2.3 异步 WGMMA 流水线

WGMMA 指令是异步的——warp group 发出 WGMMA 指令后可以继续执行其他指令（如 TMA 加载、epilogue 存储），通过 `wgmma.fence` 和 `wgmma.commit_group`/`wgmma.wait_group` 管理指令流水线：

```
// 典型 WGMMA 流水线（pipeline 深度 = num_stages）
for (int k = 0; k < K; k += BLOCK_K) {
    // TMA 异步加载下一个 tile
    cpasync_bulk_tensor_2d(..., smem_A[k % num_stages], ...);
    cpasync_bulk_tensor_2d(..., smem_B[k % num_stages], ...);

    // 等待前一个 tile 加载完成
    wait_mbarrier();

    // 发出 WGMMA 指令（非阻塞）
    wgmma_m64nNk16_f32_e4m3(accumulators, smem_A, smem_B, scale_A, scale_B);
}

// 等待所有 WGMMA 完成
wgmma_wait_group(0);
```

### 2.4 TCGen05（SM100 新指令）

Blackwell 引入了第五代 Tensor Core（TCGen05），主要增强：
- FP4 E2M1 原生支持，MMA 形状 m64×nN×k64（等效 FP8 的 2 倍 K 吞吐）
- UE8M0 缩放因子硬件解码，SF 加载后直接用于 WGMMA，无需转换
- UTCCP（Unified Tensor Core Compute Pipeline）统一计算流水线，支持更灵活的数据布局
- 更高的 Tensor Core 频率和数量

---

## 三、PDL（Programmatic Dependent Launch）

### 3.1 什么是 PDL

PDL 是 Hopper 引入的核函数依赖启动机制，允许一个核函数在 GPU 上直接启动后续核函数，无需 CPU 介入。这消除了核函数间的 CPU launch overhead，实现了核函数间的细粒度流水线。

### 3.2 DeepGEMM 中的 PDL

```cpp
// LaunchArgs 中 enable_pdl 控制是否使用 PDL
struct LaunchArgs {
    bool enable_pdl = true;  // 默认启用
};

// launch 时被 device_runtime->get_pdl() 覆盖
launch_args.enable_pdl &= device_runtime->get_pdl();
```

- 通过环境变量 `DG_ENABLE_PDL` 或 API `set_pdl(True/False)` 控制
- 启用时使用 `cudaLaunchKernelExC` / `cuLaunchKernelEx` 并设置 PDL 属性
- 对于需要 CPU 介入或调试的场景，可以禁用以获得更好的可观测性

---

## 四、Thread Block Cluster

### 4.1 什么是 Cluster

Thread Block Cluster 是 Hopper 引入的新执行层级，允许多个 thread block（最多 8 个）组成一个 cluster，在 GPU 上协同调度执行：

- Cluster 内的 block 可以访问彼此的 shared memory（distributed shared memory）
- TMA 支持 cluster 多播加载
- Cluster 内的 block 可以通过 cluster 级 barrier 同步

### 4.2 DeepGEMM 中的 Cluster 使用

- **标准 GEMM**：cluster_dim = 1（不使用 cluster）
- **MegaMoE**：cluster_dim = 2（2 个 block 组成 cluster）
- Cluster launch 通过 `cudaLaunchAttributeClusterDimension` 设置

---

## 五、SM 数量控制与 MPS 友好性

### 5.1 SM 数量动态配置

```python
deep_gemm.set_num_sms(n)  # 限制使用 n 个 SM
deep_gemm.get_num_sms()   # 查询当前 SM 数
```

应用场景：
- **MPS（Multi-Process Service）**：多个推理实例共享 GPU 时，限制每个实例使用的 SM 数
- **功耗控制**：减少活跃 SM 数可降低功耗
- **性能调优**：某些小矩阵场景下限制 SM 数可改善 L2 cache 命中率

### 5.2 Tensor Core 利用率控制

```python
deep_gemm.set_tc_util(n)  # 0-100，0=100%
```

- 控制 warp group 中活跃的 WGMMA 单元比例
- 默认 100%（全部 TC 单元活跃）
- 可用于性能/功耗权衡

---

## 六、数据布局与 Swizzle

### 6.1 Major 方向

- **K-major**（stride(-1)==1，行优先）：A 和 B 矩阵在 SM90 上必须为 K-major
- **N-major**（stride(-2)==1，列优先）：C 和 D 输出矩阵必须为 N-major
- **MN-major**（stride(-2)==1）：缩放因子 SF 要求 MN-major，便于 TMA 加载

### 6.2 Swizzle 模式

Swizzle 是一种数据重排技术，通过在 shared memory 中交错排列不同 tile 的数据来消除 bank conflict 并优化 TMA 加载模式：

- **权重 Swizzle**：`swizzle_weights_mode` 控制权重在 shared memory 中的排列方式
- **激活 Swizzle**：`swizzle_acts_mode` 控制激活值的排列方式
- Swizzle 模式由启发式配置根据 tile 大小和架构自动选择

### 6.3 缩放因子布局转换

不同架构/核函数对 SF 布局有不同要求，`layout::transform_sf_into_required_layout` 自动处理：

| 源布局 | 目标布局 | 转换操作 |
|---|---|---|
| K-major Float SF | MN-major TMA-aligned | `get_mn_major_tma_aligned_tensor`（transpose + 对齐） |
| Float SF | UE8M0 packed Int SF | `get_mn_major_tma_aligned_packed_ue8m0_tensor`（量化 + 打包 + 对齐） |
| Contiguous SF | K-grouped padded SF | `get_k_grouped_mn_major_tma_aligned_packed_ue8m0_tensor`（分组 padding） |

---

## 七、Shared Memory 与 Pipeline

### 7.1 多阶段流水线（Software Pipelining）

DeepGEMM 使用多阶段软件流水线重叠数据加载和计算：

```
Stage 0: TMA load tile 0
Stage 1: TMA load tile 1 + WGMMA tile 0
Stage 2: TMA load tile 2 + WGMMA tile 1
...
Stage K: WGMMA tile K-1
Epilogue: store result
```

- `num_stages` 由启发式根据 BLOCK_K、smem_size、寄存器数量自动选择
- 典型值为 2-4 个阶段
- SM90 支持最多 228KB dynamic shared memory per block
- SM100 支持更大的 shared memory（具体取决于 SKU）

### 7.2 寄存器分块

WGMMA 指令在 warp group 内将 accumulator 分布到 128 个线程的寄存器中：

- M 方向：64 行（一个 WGMMA 指令的固定 M 大小）
- N 方向：通常分成 8/16/32 的组（wgmma N 参数，如 8/16/32/64/128/256）
- 每个线程持有部分 accumulator 寄存器

---

## 八、启发式调优

### 8.1 Block 大小选择

`csrc/jit_kernels/heuristics/` 目录包含各架构的启发式配置：

- **sm90.hpp**：Hopper 的 block_m/n/k、num_stages、cluster_dim 选择
- **sm100.hpp**：Blackwell 的配置
- **mega_moe.hpp**：MegaMoE 的 block 配置
- **config.hpp**：通用配置参数

启发式根据以下因素选择最优 tile 大小：
- M/N/K 维度大小
- 数据类型（FP8/FP4/BF16）
- GEMM 类型（Normal/Grouped/MegaMoE）
- SM 数量和 shared memory 容量

### 8.2 编译维度特化

```python
# compiled_dims 参数控制 JIT 特化维度
fp8_gemm_nt(..., compiled_dims="nk")  # 按 N、K 特化
bf16_gemm_tn(..., compiled_dims="mn") # 按 M、N 特化
```

- "nk"：生成的核函数对 N 和 K 维度硬编码（编译期常量），M 为运行时参数
- "mn"：对 M 和 N 硬编码，K 为运行时参数
- 硬编码维度允许编译器进行更激进的循环展开和指令调度
- `set_ignore_compile_dims(True)` 禁用维度特化，使用通用 kernel（减少编译次数）

### 8.3 Block 大小倍数约束

```python
# 强制 block 大小为指定倍数
deep_gemm.set_block_size_multiple_of((128, 64))  # block_m=128倍数, block_n=64倍数
```

在分布式场景中，强制 block 大小对齐通信 tile 大小可避免边界处理开销。

---

## 九、cuBLASLt 回退路径

DeepGEMM 在以下场景使用 cuBLASLt 作为回退：
- 不支持的架构或配置
- `cublaslt_gemm_*` 系列 API 直接调用
- Einsum 中 `use_cublaslt=True` 时的 BF16 path

cuBLASLt workspace 大小固定为 32MB，支持 PyTorch 管理或自管理两种模式。

---

## 十、性能调试工具

### 10.1 Benchmark 工具

```python
from deep_gemm.testing import bench

# 基础计时
time_per_call = bench(fn, num_warmups=5, num_tests=10)

# 高精度模式（消除 CPU launch overhead）
time_per_call = bench(fn, high_precision=True)
```

bench 函数：
- 使用 256MB int8 张量 flush L2 cache
- CUDA Event 精确计时
- high_precision 模式先执行一次 8192×8192 FP32 matmul 消除 CPU launch 抖动

### 10.2 Kineto Profiling

```python
from deep_gemm.testing import bench_kineto

kernel_time = bench_kineto(
    fn, kernel_names="sm90_fp8_gemm",
    num_tests=30, suppress_kineto_output=True,
    flush_l2=True
)
```

- 使用 `torch.profiler` 进行 CUDA activity profiling
- 支持多 kernel 计时
- 可导出 Chrome trace（`trace_path` 参数）
- 设置 `DG_USE_NVIDIA_TOOLS=1` 跳过 profiler（使用 Nsight Systems/Compute 时）

### 10.3 JIT 调试

| 环境变量 | 功能 |
|---|---|
| `DG_JIT_DEBUG=1` | ptxas verbose 输出 + lineinfo |
| `DG_JIT_PTXAS_VERBOSE=1` | ptxas 详细输出（寄存器使用等） |
| `DG_JIT_PTXAS_CHECK=1` | 断言无 local memory 使用 |
| `DG_JIT_WITH_LINEINFO=1` | 生成 lineinfo（NCU profiling 需要） |
| `DG_JIT_PRINT_LOAD_TIME=1` | 打印 kernel 加载耗时 |
| `DG_COMM_KERNEL_DEBUG=1` | MegaMoE 执行后清零 sym_buffer |

---

## 十一、相关链接

- /deepseek/deep-gemm/concepts/jit-kernel-compilation — JIT 编译系统（维度特化、启发式）
- /deepseek/deep-gemm/concepts/fp8-gemm — FP8/FP4 精度与 WGMMA scale
- /deepseek/deep-gemm/references/runtime-config — SM/TC/PDL 配置 API
- /deepseek/deep-gemm/examples/tuning — 性能调优示例
