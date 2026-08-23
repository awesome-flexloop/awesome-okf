---
type: Example
title: 启用 Vulkan GPU 推理
description: 通过 create_gpu_instance 初始化 Vulkan 后端，配置 Option::use_vulkan_compute 和 VkAllocator，使用 VkMat 进行全 GPU 推理，含 PipelineCache 持久化和 CPU/GPU 混合执行。
tags: [ncnn, vulkan, gpu, example]
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

# 启用 Vulkan GPU 推理

本例演示如何在 ncnn 中启用 Vulkan GPU 加速，包括实例管理、Option 配置、VkMat 推理和管线缓存。

## 完整 C++ 代码

```cpp
#include <net.h>
#include <gpu.h>
#include <simpleocv.h>

int main()
{
    // 1. 创建 Vulkan 实例（全局，只需一次）
    ncnn::create_gpu_instance();

    {
        // 2. 查询 GPU 信息
        int gpu_count = ncnn::get_gpu_count();
        printf("GPU count: %d\n", gpu_count);
        for (int i = 0; i < gpu_count; i++) {
            const ncnn::GpuInfo& info = ncnn::get_gpu_info(i);
            printf("  GPU %d: %s, type=%d, score=%u\n",
                   i, info.device_name(), info.type(), info.rough_score());
        }

        // 3. 配置 Option
        ncnn::Option opt;
        opt.use_vulkan_compute = true;          // 启用 GPU
        opt.use_fp16_storage = true;            // fp16 存储省带宽
        opt.use_fp16_packed = true;             // fp16 打包
        opt.use_shader_local_memory = true;     // shader 本地内存
        opt.use_packing_layout = true;
        opt.num_threads = 4;

        // 可选：指定 GPU 设备（默认 get_default_gpu_index()）
        // opt.vulkan_device_index = 0;

        // 可选：持久化管线缓存（加速二次启动）
        ncnn::PipelineCache* pipeline_cache = nullptr;
        // ncnn::PipelineCache cache(ncnn::get_gpu_device(0));
        // cache.load_cache("pipeline.cache");
        // opt.pipeline_cache = &cache;
        // pipeline_cache = &cache;

        // 4. 加载模型
        ncnn::Net net;
        net.opt = opt;
        net.set_vulkan_device(0);               // 指定 GPU
        net.load_param("model.param");
        net.load_model("model.bin");

        // 5. 预处理（CPU 端 Mat）
        cv::Mat bgr = cv::imread("image.jpg");
        ncnn::Mat in = ncnn::Mat::from_pixels_resize(
            bgr.data, ncnn::Mat::PIXEL_BGR2RGB,
            bgr.cols, bgr.rows, 640, 640);
        in.substract_mean_normalize(mean_vals, norm_vals);

        // 6. 创建 Extractor
        ncnn::Extractor ex = net.create_extractor();

        // 方式 A：输入 CPU Mat，框架自动上传 GPU
        ex.input("images", in);

        // 7. 提取 GPU 输出
        ncnn::VkMat vk_out;
        {
            ncnn::VkCompute cmd(ncnn::get_gpu_device(0));
            ex.extract("output", vk_out, cmd);
            cmd.submit_and_wait();
        }

        // 8. 下载到 CPU
        ncnn::Mat out = vk_out.mapped();

        // 9. 后处理 out ...
        printf("output dims: %d, shape: %dx%dx%d\n",
               out.dims, out.w, out.h, out.c);

        // 可选：保存管线缓存
        // if (pipeline_cache) pipeline_cache->save_cache("pipeline.cache");
    }

    // 10. 销毁 Vulkan 实例（程序退出前）
    ncnn::destroy_gpu_instance();
    return 0;
}
```

## 全 GPU 零拷贝路径（VkMat 输入）

对于已经在 GPU 上的数据（如相机采集纹理），可直接使用 VkMat 避免上传：

```cpp
ncnn::VkMat vk_in;
vk_in.create(640, 640, 3, 4u, 1, blob_vkallocator);  // 640x640x3 fp32

ncnn::Extractor ex = net.create_extractor();
ex.input("images", vk_in);

ncnn::VkMat vk_out;
ncnn::VkCompute cmd(ncnn::get_gpu_device(0));
ex.extract("output", vk_out, cmd);
cmd.submit_and_wait();

ncnn::Mat out = vk_out.mapped();
```

## CPU/GPU 混合执行

不需要将所有层都放 GPU。框架自动处理：
- `support_vulkan=true` 的层在 GPU 执行；
- 不支持 Vulkan 的层自动回退 CPU；
- 层间自动插入 upload/download；
- 也可通过 `create_layer_cpu`/`create_layer_vulkan` 强制后端。

## PipelineCache 持久化

Vulkan shader 管线创建开销较大。`PipelineCache` 将编译结果序列化：

```cpp
ncnn::PipelineCache cache(vkdev);
cache.load_cache("pipeline.cache");  // 启动时加载
net.opt.pipeline_cache = &cache;
// ... 推理 ...
cache.save_cache("pipeline.cache");  // 退出时保存
```

首次运行创建管线并保存，后续启动直接加载，大幅减少初始化时间。

## GPU 内存分配器

Option 中可注入 GPU 分配器：

```cpp
ncnn::VkAllocator* blob_vkallocator = vkdev->acquire_blob_allocator();
ncnn::VkAllocator* staging_vkallocator = vkdev->acquire_staging_allocator();

ex.set_blob_vkallocator(blob_vkallocator);
ex.set_staging_vkallocator(staging_vkallocator);

// 推理完成后回收
vkdev->reclaim_blob_allocator(blob_vkallocator);
vkdev->reclaim_staging_allocator(staging_vkallocator);
```

- `VkBlobAllocator`（默认 16MB 块）：中间特征图；
- `VkWeightAllocator`（默认 8MB 块）：权重，可常驻主机；
- `VkStagingAllocator`（mappable）：CPU↔GPU 传输。

## 注意事项

- `create_gpu_instance`/`destroy_gpu_instance` 必须配对，覆盖所有 GPU 使用周期；
- `VkCompute` 的 `submit_and_wait` 阻塞等待 GPU 完成；
- `VkMat::mapped()` 隐式下载并映射，数据在 `VkMat` 释放前有效；
- 无 Vulkan 设备时 `get_gpu_count()` 返回 0，应回退 CPU。

## 相关概念

- [06 Vulkan GPU 后端](/concepts/06-vulkan-gpu.md)
- [01 Net 与 Extractor 推理流程](/concepts/01-net-extractor.md)
- [02 Mat 张量系统](/concepts/02-mat-tensor-system.md)
- [04 内存分配器](/concepts/04-allocator.md)
- [05 Option 推理配置](/concepts/05-option-config.md)
