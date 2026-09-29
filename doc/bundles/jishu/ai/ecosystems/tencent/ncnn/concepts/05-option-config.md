---
type: Concept
title: Option 推理配置
description: Option 集中控制推理行为，含 lightmode 中间 blob 回收、num_threads 线程数、use_vulkan_compute GPU 开关、use_int8_inference 量化、use_fp16/bf16_storage 低精度、use_packing_layout SIMD 打包、winograd/sgemm 卷积优化及自定义 allocator。
tags: [ncnn, option, config, performance]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: option-h
    resource: /src/option.h
    title: option.h
---

# Option 推理配置

`Option` 类集中控制 ncnn 的推理行为，涵盖线程、内存、精度、计算后端和算子优化。它是 `Net::opt` 和 `Extractor` 的公开成员，**影响层创建的选项必须在 `load_param` 之前设置**。

## 内存与模式

```cpp
bool lightmode;     // 默认 true，中间 blob 用完即回收
int num_threads;    // 默认 get_cpu_count()
int openmp_blocktime; // 默认 20ms，OpenMP 自旋等待
```

- **lightmode**：启用后 Extractor 在每个 blob 被所有消费者读取后立即释放其内存（F-051）。关闭可保留中间结果供多次 extract，但增加峰值内存。
- **openmp_blocktime**：OpenMP 线程在自旋等待新任务多少毫秒后休眠。默认 20ms 平衡延迟和功耗（F-054）。

## 计算后端

```cpp
bool use_vulkan_compute;   // 默认 false，启用 Vulkan GPU
int vulkan_device_index;   // GPU 设备索引
```

启用后框架自动将 `support_vulkan=true` 的层分派到 GPU，不支持的层回退 CPU。CPU/GPU 之间的传输由 `VkStagingAllocator` 管理。

## 低精度推理

```cpp
bool use_bf16_storage;       // bfloat16 存储
bool use_fp16_packed;        // fp16 打包
bool use_fp16_storage;       // fp16 存储
bool use_fp16_arithmetic;    // fp16 计算
bool use_int8_packed;
bool use_int8_storage;
bool use_int8_arithmetic;
bool use_int16_packed;
bool use_int16_storage;
bool use_int8_inference;     // 默认 true，int8 量化推理
```

- **use_int8_inference**（默认 true）：对量化模型启用 int8 低精度路径（F-056）。
- **use_fp16_storage / use_bf16_storage**：以 fp16/bf16 存储中间特征图，减半内存带宽，在 ARM 设备上显著提速。
- packed/storage/arithmetic 三级控制：打包是 SIMD 布局、storage 是存储精度、arithmetic 是计算精度，可独立组合。

## 卷积优化

```cpp
bool use_winograd_convolution;  // 默认 true，3x3 卷积
bool use_sgemm_convolution;     // 默认 true，1x1 卷积
bool use_winograd23_convolution;
bool use_winograd43_convolution;
bool use_winograd63_convolution;
```

- Winograd 优化 3×3 stride=1 卷积，通过变换减少乘法次数；
- SGEMM 将卷积展开为矩阵乘法，适合 1×1；
- 更细粒度的 23/43/63 控制不同 Winograd 变体。

## SIMD 打包布局

```cpp
bool use_packing_layout;  // 默认 true
```

启用后 ncnn 将张量按 SIMD 宽度打包存储（NEON/SSE=4，AVX/FP16=8），使每个元素直接对应一个 SIMD 寄存器槽位，避免加载时的解包开销（F-059）。代价是内存占用略增（通道维度向上取整）。

## 分配器注入

```cpp
Allocator* blob_allocator;       // 特征图
Allocator* workspace_allocator;  // 工作区
Allocator* kvcache_allocator;    // LLM KV cache
// Vulkan:
VkAllocator* blob_vkallocator;
VkAllocator* workspace_vkallocator;
VkAllocator* staging_vkallocator;
VkAllocator* kvcache_vkallocator;
PipelineCache* pipeline_cache;
```

用户可注入自定义分配器（如 [PoolAllocator](04-allocator.md)）来复用内存、使用 DMA 缓冲或追踪内存使用。

## 其他重要选项

```cpp
unsigned char flush_denormals;  // 默认 3 (DAZ ON + FTZ ON)
bool use_shader_local_memory;   // GPU shader 本地内存
bool use_cooperative_matrix;    // GPU 协作矩阵（张量核心）
bool use_a53_a55_optimized_kernel; // ARM 小核优化
bool use_local_pool_allocator;  // Extractor 局部池
bool use_weights_in_host_memory; // 权重常驻主机
```

`flush_denormals` 默认 3 启用 Denormals-Are-Zero 和 Flush-To-Zero，避免非规格化浮点数导致的性能惩罚（F-060）。

## 典型配置

```cpp
ncnn::Option opt;
opt.lightmode = true;
opt.num_threads = 4;
opt.use_packing_layout = true;
opt.use_winograd_convolution = true;
opt.use_sgemm_convolution = true;
opt.use_vulkan_compute = true;        // 启用 GPU
opt.use_fp16_storage = true;          // fp16 存储
opt.use_int8_inference = true;        // int8 量化

ncnn::Net net;
net.opt = opt;                        // 必须在 load 前设置
net.load_param("model.param");
net.load_model("model.bin");
```

## 相关概念

- [01 Net 与 Extractor 推理流程](01-net-extractor.md)
- [04 内存分配器](04-allocator.md)
- [06 Vulkan GPU 后端](06-vulkan-gpu.md)
- [07 SIMD 打包存储](07-simd-packing.md)
- [11 量化与低精度](11-quantization.md)
