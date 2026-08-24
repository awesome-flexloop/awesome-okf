# 信源登记簿

* [net.h — Net 与 Extractor](net-extractor.md) — Net 类（PIMPL、加载 API、register_custom_layer、create_extractor）与 Extractor 类（lightmode、allocator、input/extract、Vulkan 重载）完整类定义。
* [mat.h — Mat 张量系统](mat-tensor.md) — Mat/VkMat/VkImageMat 公共字段、构造函数族、create/clone/reshape、视图方法、像素转换、精度转换函数。
* [layer.h — Layer 基类](layer-base.md) — 能力标志位、生命周期虚函数、CPU/Vulkan forward 多重载、bottoms/tops 索引、工厂宏与注册表结构。
* [allocator.h — 内存分配器](allocator.md) — NCNN_MALLOC_ALIGN/OVERREAD、fastMalloc 跨平台实现、PoolAllocator/UnlockedPoolAllocator、VkAllocator 层级（Blob/Weight/Staging）。
* [gpu.h/pipeline.h/command.h/pipelinecache.h — Vulkan 后端](vulkan-backend.md) — create_gpu_instance、GpuInfo/VulkanDevice、Pipeline 管线、VkCompute/VkTransfer 命令录制、PipelineCache 缓存。
* [CMakeLists.txt — 构建系统](build-system.md) — 版本定义、NCNN_VULKAN/OPENMP/INT8/PYTHON/BF16/WEIGHT_QUANT/BATCH/PIXEL/RUNTIME_CPU/SIMPLEVK 等构建选项、平台分支。

```{toctree}
:hidden:

allocator
build-system
layer-base
mat-tensor
net-extractor
vulkan-backend
```
