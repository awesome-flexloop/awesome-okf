---
type: Reference
title: gpu.h / pipeline.h / command.h / pipelinecache.h — Vulkan 后端信源
description: ncnn Vulkan 后端四大头文件中 VulkanDevice/GpuInfo、Pipeline 着色器管线、VkCompute 命令录制、PipelineCache 管线缓存的类定义与关键 API 登记。
tags: [ncnn, vulkan, gpu, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: gpu-h
    resource: /src/gpu.h
    title: gpu.h
  - id: pipeline-h
    resource: /src/pipeline.h
    title: pipeline.h
  - id: command-h
    resource: /src/command.h
    title: command.h
  - id: pipelinecache-h
    resource: /src/pipelinecache.h
    title: pipelinecache.h
---

# Vulkan 后端四头文件

> 信源路径：`src/gpu.h`、`src/pipeline.h`、`src/command.h`、`src/pipelinecache.h`。

## gpu.h：实例与设备

```cpp
// 全局实例生命周期
NCNN_EXPORT int create_gpu_instance(const char* driver_path = 0);
NCNN_EXPORT VkInstance get_gpu_instance();
NCNN_EXPORT void destroy_gpu_instance();

// 约 90 个 PFN_vk* 函数指针全局声明，由 simplevk 运行时加载
extern PFN_vkAllocateCommandBuffers vkAllocateCommandBuffers;
// ... vkCreateBuffer / vkCmdDispatch / vkQueueSubmit 等

NCNN_EXPORT int get_gpu_count();
NCNN_EXPORT int get_default_gpu_index();
NCNN_EXPORT const GpuInfo& get_gpu_info(int device_index = ...);
NCNN_EXPORT VulkanDevice* get_gpu_device(int device_index = ...);
```

### GpuInfo（查询）

```cpp
class NCNN_EXPORT GpuInfo {
    int device_index() const;
    VkPhysicalDevice physicalDevice() const;
    const VkPhysicalDeviceProperties& physicalDeviceProperties() const;
    uint32_t api_version() const;
    const char* device_name() const;
    int type() const;                 // 0=独显 1=集显 2=虚拟 3=cpu
    uint32_t rough_score() const;     // 性能评分
    // subgroup / fp16 / int8 / bf16 / cooperative matrix 特性查询
    bool support_fp16_storage() const;
    bool support_int8_storage() const;
    bool support_bf16_storage() const;
    bool support_cooperative_matrix() const;
    uint32_t subgroup_size() const;
};
```

### VulkanDevice（设备封装）

```cpp
class NCNN_EXPORT VulkanDevice {
public:
    VulkanDevice(int device_index = get_default_gpu_index());
    const GpuInfo& info;
    VkDevice vkdevice() const;

    VkShaderModule compile_shader_module(const uint32_t* spv, size_t size) const;
    int create_descriptorset_layout(int binding_count, const int* binding_types,
                                    VkDescriptorSetLayout*) const;
    int create_pipeline_layout(int push_constant_count,
                               VkDescriptorSetLayout, VkPipelineLayout*) const;
    int create_pipeline(VkShaderModule, VkPipelineLayout,
                        const std::vector<vk_specialization_type>&,
                        uint32_t subgroup_size, VkPipeline*) const;
    uint32_t find_memory_index(uint32_t type_bits, VkFlags required,
                               VkFlags preferred, VkFlags preferred_not) const;
    VkQueue acquire_queue(uint32_t queue_family_index) const;

    VkAllocator* acquire_blob_allocator() const;
    VkAllocator* acquire_staging_allocator() const;
    const PipelineCache* get_pipeline_cache() const;
    uint32_t get_heap_budget() const;
private:
    VulkanDevicePrivate* const d;
};
```

## pipeline.h：着色器管线

```cpp
class NCNN_EXPORT Pipeline {
public:
    explicit Pipeline(const VulkanDevice* vkdev);
    void set_optimal_local_size_xyz(int w = 4, int h = 4, int c = 4);
    void set_local_size_xyz(int w, int h, int c);
    void set_subgroup_size(uint32_t subgroup_size);

    int create(const uint32_t* spv_data, size_t spv_data_size,
               const std::vector<vk_specialization_type>& specializations);
    int create(int shader_type_index, const Option& opt,
               const std::vector<vk_specialization_type>& specializations);

    VkShaderModule shader_module() const;
    VkDescriptorSetLayout descriptorset_layout() const;
    VkPipelineLayout pipeline_layout() const;
    VkPipeline pipeline() const;
    const ShaderInfo& shader_info() const;
private:
    PipelinePrivate* const d;
};
```

## command.h：命令录制

```cpp
class NCNN_EXPORT VkCompute {
public:
    explicit VkCompute(const VulkanDevice* vkdev);
    void record_upload(const Mat& src, VkMat& dst, const Option& opt);
    void record_download(const VkMat& src, Mat& dst, const Option& opt);
    void record_clone(const Mat& src, VkMat& dst, const Option& opt);
    void record_pipeline(const Pipeline* pipeline,
                         const std::vector<VkMat>& bindings,
                         const std::vector<vk_constant_type>& constants,
                         const VkMat& dispatcher);
    int submit_and_wait();
    int reset();
private:
    VkComputePrivate* const d;
};

class NCNN_EXPORT VkTransfer {
    // 仅权重上传：record_upload + submit_and_wait
};
```

## pipelinecache.h：管线缓存

```cpp
class NCNN_EXPORT PipelineCache {
public:
    explicit PipelineCache(const VulkanDevice* _vkdev);
    void clear();
    size_t size() const;
    int save_cache(std::vector<unsigned char>& data) const;
    int load_cache(const unsigned char* data, size_t size) const;
    int save_cache(FILE* fp) const;
    int load_cache(FILE* fp) const;

    int get_pipeline(const uint32_t* spv_data, size_t spv_data_size,
                     const std::vector<vk_specialization_type>& specializations,
                     uint32_t lsx, uint32_t lsy, uint32_t lsz,
                     uint32_t subgroup_size,
                     VkShaderModule*, VkDescriptorSetLayout*,
                     VkPipelineLayout*, VkPipeline*,
                     VkDescriptorUpdateTemplateKHR*, ShaderInfo&) const;
private:
    PipelineCachePrivate* const d;
};
```

## 相关概念

- [06 Vulkan GPU 后端](../concepts/06-vulkan-gpu.md)
- [04 内存分配器](../concepts/04-allocator.md)
