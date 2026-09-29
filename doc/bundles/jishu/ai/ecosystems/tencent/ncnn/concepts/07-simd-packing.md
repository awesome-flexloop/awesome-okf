---
type: Concept
title: SIMD 打包存储与运行时 CPU 分发
description: elempack 控制张量按 NEON=4/SSE=4/AVX=8/FP16=8 打包，ruapu.h 单文件库运行时检测 CPU ISA，编译期保留 arm/x86/mips/riscv/loongarch 多套 kernel，NCNN_RUNTIME_CPU 胖二进制策略自动选择最优实现。
tags: [ncnn, simd, cpu, neon, avx, packing]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: cpu-h
    resource: /src/cpu.h
    title: cpu.h
  - id: ruapu-h
    resource: /src/ruapu.h
    title: ruapu.h
---

# SIMD 打包存储与运行时 CPU 分发

ncnn 的高性能来自两个协同设计：SIMD 友好的**打包内存布局**和编译期多套 kernel + 运行时检测的**胖二进制分发**。

## elempack 打包存储

普通张量中 `elempack=1`，一个元素就是一个标量。启用打包后，多个连续标量被打包成一个"元素"（F-022）：

| elempack | SIMD 指令集 | 一个元素的标量数 |
|---|---|---|
| 1 | scalar | 1 |
| 4 | ARM NEON / x86 SSE2 | 4 个 fp32 |
| 8 | x86 AVX / ARM FP16 | 8 个 fp32 或 fp16 |

打包后逻辑维度相应缩小：例如 64 通道的特征图在 elempack=4 时逻辑通道数变为 16，但每个"元素"含 4 个标量。这使得 kernel 可以直接对 `float32x4_t`（NEON）或 `__m128`（SSE）操作，无需在加载时解包。

打包由 [`Option::use_packing_layout`](05-option-config.md)（默认 true）控制。算子通过 `support_packing` 标志位声明是否接受打包输入；不支持时框架自动插入 `Packing` 层做打包/解包转换。

## 平台优化目录

每个支持的架构都有独立的 kernel 实现目录（F-103）：

```
src/layer/
├── arm/       NEON / VFPv4 / ASIMDHP / ASIMDDP / ASIMDFHM / I8MM / SVE / SVE2
├── x86/       SSE2 / AVX / FMA / F16C / AVX2 / AVX512 / AVX-VNNI / AVX512-BF16/FP16
├── mips/      MSA / Loongson MMI
├── riscv/     RVV (Vector) / Zfh / Zvfh / XTheadVector
├── loongarch/ LSX / LASX
└── vulkan/    SPIR-V compute shader
```

文件命名约定：`<layer>_<arch>.cpp/.h`，如 `convolution_arm.cpp`、`gemm_x86.h`、`bias_mips.cpp`、`sdpa_riscv.cpp`、`cast_loongarch.h`。

## ruapu.h 运行时 ISA 检测

`ruapu.h` 是 nihui/kernelbin 开发的单文件 CPU ISA 检测库（F-101）：

```c
void ruapu_init();                    // 检测所有 ISA
int ruapu_supports(const char* isa);  // 查询是否支持
const char* const* ruapu_rua();       // 列出所有支持的 ISA
```

其原理是尝试执行目标指令，通过捕获 SIGILL（Unix）或 SEH 异常（Windows）判断 CPU 是否支持。检测覆盖：

- ARM：neon/vfpv4/asimdhp/asimddp/asimdfhm/bf16/i8mm/sve/sve2/svebf16/svei8mm；
- x86：sse2/sse3/ssse3/sse4.1/sse4.2/avx/fma/f16c/avx2/avx512f/avx512bw/avx512dq/avx512vl/avx_vnni/avx512_bf16/avx512_fp16；
- RISC-V：v/zfh/zvfh/xtheadvector；
- LoongArch：lsx/lasx；
- MIPS：msa/mi。

`cpu.h` 在 ruapu 之上封装了 `cpu_support_arm_neon()`、`cpu_support_x86_avx2()` 等便捷函数（F-102）。

## 胖二进制策略

`NCNN_RUNTIME_CPU=ON`（默认）时，CMake 编译同一算子的多套 kernel——基线版本 + 各 ISA 优化版本——全部编入同一个二进制（F-099）。运行时初始化阶段调用 `ruapu_init()`，然后每个算子根据检测结果选择函数指针：

```cpp
// 伪代码
if (cpu_support_x86_avx512())
    forward = forward_avx512;
else if (cpu_support_x86_avx2())
    forward = forward_avx2;
else if (cpu_support_x86_avx())
    forward = forward_avx;
else
    forward = forward_sse;
```

**优势**：一份编译产物在所有同架构 CPU 上运行，自动选择最优指令集，无需为不同微架构发版。

**代价**：二进制体积增大。可设 `-DNCNN_RUNTIME_CPU=OFF` 并通过 `-DNCNN_AVX2=ON` 等只编译目标 ISA 版本来裁剪。

## ARM big.LITTLE 适配

`cpu.h` 还提供大小核感知（F-102）：

- `get_big_cpu_count()` / `get_little_cpu_count()` 查询大小核数量；
- `is_current_thread_running_on_a53_a55()` 检测是否在 A53/A55 小核上；
- `Option::use_a53_a55_optimized_kernel` 为顺序小核选择不同 kernel；
- `set_cpu_powersave()` 绑定线程到大核或小核集群。

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [03 Layer 抽象层](03-layer-abstraction.md)
- [05 Option 推理配置](05-option-config.md)
- [11 量化与低精度](11-quantization.md)
