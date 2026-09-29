# 概念文档

ncnn 核心架构概念，共 12 篇，按依赖顺序组织。

## 架构基础

* [00 ncnn 整体架构](00-overall-architecture.md) — 纯 C++ 零依赖、CPU/GPU 双后端、全架构覆盖、PIMPL 模式、五套 simple 内嵌替代。
* [01 Net 与 Extractor 推理流程](01-net-extractor.md) — Net 加载 param/bin、create_extractor、input/extract、lightmode、自定义层注册。
* [02 Mat 张量系统](02-mat-tensor-system.md) — dims/w/h/d/c、elemsize 精度、elempack 打包、cstep 对齐、refcount 引用计数、零拷贝视图、像素转换。
* [03 Layer 抽象层](03-layer-abstraction.md) — 能力标志位 bool、forward 多重重载、load_param/load_model 生命周期、one_blob_only/support_inplace。

## 核心机制

* [04 内存分配器](04-allocator.md) — Allocator 抽象、PoolAllocator 线程安全池、UnlockedPoolAllocator、NCNN_MALLOC_ALIGN/OVERREAD、VkAllocator GPU 层级。
* [05 Option 推理配置](05-option-config.md) — lightmode、num_threads、use_vulkan_compute、int8/fp16/bf16、packing_layout、winograd/sgemm、自定义 allocator。
* [06 Vulkan GPU 后端](06-vulkan-gpu.md) — VkMat/VkImageMat、VulkanDevice、Pipeline 着色器管线、VkCompute 命令录制、PipelineCache、simplevk loader。
* [07 SIMD 打包存储与运行时 CPU 分发](07-simd-packing.md) — elempack NEON=4/SSE=4/AVX=8、ruapu.h ISA 检测、胖二进制多套 kernel、ARM/x86/MIPS/RISC-V/LoongArch。

## 高级功能

* [08 ParamDict 与 ModelBin](08-paramdict-modelbin.md) — 参数 ID 字典 get<T>、权重二进制 load、param 文本格式、DataReader 文件/内存/Asset 抽象。
* [09 层注册表与自定义层](09-layer-registry.md) — layer_type_enum 构建期生成、DEFINE_LAYER_CREATOR 宏、register_custom_layer、内置层覆盖。
* [10 Python 绑定](10-python-binding.md) — pybind11、Mat↔numpy 零拷贝 buffer protocol、model_zoo 20 个预训练模型、Python 自定义层。
* [11 量化与低精度推理](11-quantization.md) — int8 量化、fp16/bf16 存储、elemsize=1/2、权重量化 int4/int6/int8、quantize/dequantize/requantize。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-net-extractor
02-mat-tensor-system
03-layer-abstraction
04-allocator
05-option-config
06-vulkan-gpu
07-simd-packing
08-paramdict-modelbin
09-layer-registry
10-python-binding
11-quantization
```
