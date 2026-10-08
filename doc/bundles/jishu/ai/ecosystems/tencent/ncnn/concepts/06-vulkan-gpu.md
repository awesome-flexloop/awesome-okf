---
type: Concept
title: Vulkan GPU 后端
description: ncnn Vulkan 后端由 VkMat/VkImageMat 设备张量、VulkanDevice 设备管理、Pipeline SPIR-V 着色器管线、VkCompute 命令录制、PipelineCache 管线缓存和 simplevk 内置 loader 组成，CPU/GPU 输入输出自动转换。
tags: [ncnn, vulkan, gpu, pipeline]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: gpu-h
    resource: /src/gpu.h
    title: gpu.h
  - id: command-h
    resource: /src/command.h
    title: command.h
---

# Vulkan GPU 后端

ncnn 的 Vulkan 后端允许同一套网络在 GPU 上执行，无需为 GPU 重写模型代码。启用 `Option::use_vulkan_compute=true` 后，框架自动将 `support_vulkan` 标志的层分派到 GPU。

## 设备管理

### 全局实例

```cpp
ncnn::create_gpu_instance();          // 创建 VkInstance，解析所有 vk* 函数
int count = ncnn::get_gpu_count();
ncnn::VulkanDevice* vkdev = ncnn::get_gpu_device(0);
// ... 推理 ...
ncnn::destroy_gpu_instance();         // 确保所有设备 idle 后销毁
```

`create_gpu_instance` 枚举物理设备、检查扩展支持、初始化验证层（F-082）。gpu.h 声明约 90 个 `PFN_vk*` 全局函数指针，由 simplevk 内置 loader 在运行时动态解析——这意味着 ncnn 不链接系统 Vulkan SDK，编译时无需 Vulkan 头文件之外的依赖（F-083、F-093）。

### GpuInfo

`GpuInfo` 提供详尽的设备信息查询（F-084）：

- 设备类型（独显/集显/虚拟/CPU）和性能评分 `rough_score()`；
- 硬件限制：max_workgroup_size、max_shared_memory_size、subgroup_size；
- 特性：fp16/int8/bf16 storage 和 arithmetic、cooperative matrix、image storage；
- 扩展支持：VK_KHR_8bit_storage、shader_float16_int8、cooperative_matrix 等；
- Bug 标志：如 `bug_storage_buffer_no_l1`（某些 Adreno 的 L1 缓存 bug）。

### VulkanDevice

`VulkanDevice` 封装逻辑设备，提供 shader 编译、管线创建、内存类型查询、队列管理和分配器池（F-085、F-086）。

## 设备端张量

### VkMat

`VkMat` 是 GPU 版的 Mat，字段与 Mat 平行，但 `data` 类型为 `VkBufferMemory*`（F-033）：

```cpp
VkBufferMemory* data;
int* refcount;
size_t elemsize; int elempack;
VkAllocator* allocator;
int dims, w, h, d, c; size_t cstep;
```

通过 `mapped()` 将设备缓冲映射回主机 Mat（隐式下载），通过 `VkCompute::record_upload` 从 Mat 上传。

### VkImageMat

`VkImageMat` 基于 `VkImage`/`VkImageView`，适用于需要纹理采样或 storage image 的 shader（F-034）。

## Pipeline（着色器管线）

`Pipeline` 封装一个 compute shader 的完整管线状态（F-087）：

```cpp
ncnn::Pipeline pipeline(vkdev);
pipeline.set_optimal_local_size_xyz(4, 4, 4);  // 默认 workgroup size
pipeline.create(spv_data, spv_size, specializations);
```

每个 Layer 的 `create_pipeline` 创建一个或多个 Pipeline（对应不同 elempack/精度变体）。shader 以预编译 SPIR-V 内嵌，运行时无需 glslang（除非在线编译）。

`vk_specialization_type`（int/float/uint32 union）用于 specialization constant，在不重新编译 shader 的情况下特化工作组大小等参数。

## 命令录制（VkCompute）

GPU 推理不是逐层立即执行，而是录制到命令缓冲后批量提交（F-090）：

```cpp
ncnn::VkCompute cmd(vkdev);
cmd.record_upload(mat_in, vk_in, opt);          // 上传
// ... Layer::forward 内部录制 cmd.record_pipeline(...) ...
cmd.record_download(vk_out, mat_out, opt);       // 下载
cmd.submit_and_wait();                           // 提交并等待
```

`record_pipeline` 绑定 descriptor set、push constants，然后 `vkCmdDispatch`。`VkCompute` 自动插入 pipeline barrier 处理读写依赖。

`VkTransfer` 是轻量版本，仅用于 `Layer::upload_model` 上传权重（F-091）。

## PipelineCache

`PipelineCache` 缓存已创建的 VkPipeline 对象，避免相同 shader 重复创建（F-089）。支持序列化为内存或文件：

```cpp
ncnn::PipelineCache cache(vkdev);
cache.load_cache("pipeline.cache");
// ... 推理 ...
cache.save_cache("pipeline.cache");
```

首次运行编译 SPIR-V 并创建管线，后续运行从缓存加载，显著减少启动时间。

## GPU/CPU 混合执行

- 输入 Mat 由 Extractor 自动上传为 VkMat；
- 不支持 Vulkan 的层自动回退 CPU，框架在层间插入上传/下载；
- 输出通过 `mapped()` 或 `record_download` 取回主机；
- 可混合使用：部分层 CPU、部分层 GPU。

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [03 Layer 抽象层](03-layer-abstraction.md)
- [04 内存分配器](04-allocator.md)
- [05 Option 推理配置](05-option-config.md)
- [Vulkan GPU 推理示例](../examples/vulkan-inference.md)
