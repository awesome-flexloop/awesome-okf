---
type: bundle
title: ncnn 高性能神经网络推理框架
okf_version: "0.2"
---

# ncnn 知识库

本知识包是腾讯优图实验室开源的高性能神经网络推理框架 [ncnn](https://github.com/Tencent/ncnn)（BSD-3-Clause 许可证）的系统化中文源码教程，基于 ncnn 源码（`external/libs/ai/Tencent/ncnn/` 目录，版本 1.0.20260526）深度阅读生成。覆盖从 Net/Extractor 推理流程到 Mat 引用计数张量、从 Layer 双后端抽象到 Vulkan GPU 计算、从 SIMD 打包存储到 int8/fp16 量化的完整知识体系。所有内容均溯源至 ncnn C++ 头文件与 CMake 构建系统，遵循 [OKF v0.2 规范](concepts/00-overall-architecture.md)。

## 架构基础篇（concepts/）

* [ncnn 整体架构](concepts/00-overall-architecture.md) — 纯 C++ 零第三方依赖、CPU/GPU 双后端、全架构覆盖（x86/ARM/MIPS/RISC-V/LoongArch）、simplestl/simpleomp/simpleocv/simplemath/simplevk 五套内嵌替代、PIMPL 编译防火墙。
* [Net 与 Extractor 推理流程](concepts/01-net-extractor.md) — Net 加载 param/bin、create_extractor、input/extract 按名称或索引、lightmode 自动回收中间 blob、内存零拷贝加载、自定义层注册。
* [Mat 张量系统](concepts/02-mat-tensor-system.md) — dims 0-4 秩与 w/h/d/c 维度、elemsize 4/2/1 精度、elempack 1/4/8 SIMD 打包、cstep 16 字节对齐、refcount+NCNN_XADD 原子引用计数、channel/row/range 零拷贝视图、from_pixels 像素转换。
* [Layer 抽象层](concepts/03-layer-abstraction.md) — 12 个 bool 能力标志位、forward/forward_inplace 各 4 个虚函数重载（CPU Mat + Vulkan VkMat）、load_param/load_model/create_pipeline 生命周期、bottoms/tops 索引连接。

## 核心机制篇（concepts/）

* [内存分配器](concepts/04-allocator.md) — Allocator 抽象基类、PoolAllocator 线程安全内存池、UnlockedPoolAllocator 单线程、NCNN_MALLOC_ALIGN 16/32/64、NCNN_MALLOC_OVERREAD 64、VkBlobAllocator/VkWeightAllocator/VkStagingAllocator GPU 层级。
* [Option 推理配置](concepts/05-option-config.md) — lightmode 默认 true、num_threads、use_vulkan_compute、use_int8_inference、use_fp16/bf16_storage、use_packing_layout、use_winograd/sgemm_convolution、blob/workspace_allocator 自定义。
* [Vulkan GPU 后端](concepts/06-vulkan-gpu.md) — VkMat/VkImageMat 设备端张量、VulkanDevice/GpuInfo 设备管理、Pipeline SPIR-V 着色器管线、VkCompute 命令录制、PipelineCache 管线缓存、simplevk 内置 loader 零 SDK 依赖。
* [SIMD 打包存储与运行时 CPU 分发](concepts/07-simd-packing.md) — elempack NEON=4/SSE=4/AVX=8/FP16=8、ruapu.h 单文件 ISA 检测、编译期保留多套 kernel 胖二进制策略、arm/x86/mips/riscv/loongarch 平台优化目录。

## 高级功能篇（concepts/）

* [ParamDict 与 ModelBin](concepts/08-paramdict-modelbin.md) — 参数 ID 字典 get<T> 四类型重载、每层最多 32 参数、ModelBin 权重加载 type 0-8（fp32/fp16/int8/int4/int6 块量化）、DataReader 文件/内存/Android Asset 数据源抽象。
* [层注册表与自定义层](concepts/09-layer-registry.md) — layer_type_enum.h 构建期 CMake 自动生成、DEFINE_LAYER_CREATOR/DESTROYER 宏、register_custom_layer 运行时注册、按名称或类型索引、内置层覆盖。
* [Python 绑定](concepts/10-python-binding.md) — pybind11 绑定、pybind11_mat.h Mat↔numpy 零拷贝 buffer protocol、model_zoo 20 个预训练模型（YOLO/FasterRCNN/RetinaFace/SqueezeNet 等）、Python 自定义层。
* [量化与低精度推理](concepts/11-quantization.md) — int8 量化推理、fp16/bf16 存储、quantize_to_int8/dequantize_from_int32/requantize_from_int32_to_int8 算子、NCNN_WEIGHT_QUANT int4/int6/int8 块量化、float8 前瞻支持。

## 实战示例（examples/）

* [C++ 完整推理示例](examples/first-inference.md) — Option 配置→Net 加载→from_pixels_resize 预处理→substract_mean_normalize→Extractor input/extract→后处理，含 PoolAllocator 内存池。
* [Python YOLO 目标检测](examples/python-yolo.md) — model_zoo get_model 加载 YOLOv8s、numpy 零拷贝输入、直接使用 Net/Extractor、检测结果解析与可视化。
* [自定义 Layer 注册与实现](examples/custom-layer.md) — 继承 Layer 设置 one_blob_only/support_inplace/support_packing、实现 load_param/forward/forward_inplace、DEFINE_LAYER_CREATOR 宏、C++ 与 Python 双版本。
* [启用 Vulkan GPU 推理](examples/vulkan-inference.md) — create_gpu_instance/destroy_gpu_instance、use_vulkan_compute、VkMat 全 GPU 路径、PipelineCache 持久化、VkAllocator 配置、CPU/GPU 混合执行。

## 信源登记簿（references/）

* [net.h — Net 与 Extractor](references/net-extractor.md) — Net/Extractor 类完整定义、加载 API 矩阵、input/extract 签名、Vulkan 重载。
* [mat.h — Mat 张量系统](references/mat-tensor.md) — Mat/VkMat/VkImageMat 字段、构造函数族、create/clone/reshape、视图、像素转换、精度转换。
* [layer.h — Layer 基类](references/layer-base.md) — 能力标志位、生命周期虚函数、forward 多重载、工厂宏与注册表结构。
* [allocator.h — 内存分配器](references/allocator.md) — 对齐常量、fastMalloc/fastFree、PoolAllocator、VkAllocator 层级。
* [gpu.h/pipeline.h/command.h/pipelinecache.h — Vulkan 后端](references/vulkan-backend.md) — 实例管理、GpuInfo/VulkanDevice、Pipeline、VkCompute/VkTransfer、PipelineCache。
* [CMakeLists.txt — 构建系统](references/build-system.md) — 版本定义、20+ 构建选项、平台分支、架构检测、层自动注册。

## 信任与生命周期说明

* **status 判定依据**：全部 22 个内容文档（12 个概念 + 4 个示例 + 6 个信源登记）均 `status: stable`。内容基于对 ncnn 源码（`src/` 目录 14 个核心头文件 + CMakeLists.txt + python/ 绑定）的逐文件阅读与事实提取（108 条源码事实 F-001~F-108），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。ncnn 核心架构（Net/Extractor PIMPL、Mat 引用计数、Layer 双后端、Allocator 池化、ruapu 运行时分发）自 2017 年开源以来极其稳定，新算子和平台优化不断添加但核心设计不变；该日期作为针对未来大版本（如 2.x 引入破坏性 API 变更）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（类名/虚函数签名/字段/CMake 选项逐一比对源码），两者分离、可追溯。

本知识包共收录 22 个内容文档（12 个概念 + 4 个示例 + 6 个信源登记），另含 3 个子目录 index.md、2 个 spec 文档（facts/insights）与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
