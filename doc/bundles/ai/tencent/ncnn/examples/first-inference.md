---
type: Example
title: C++ 完整推理示例
description: 使用 ncnn C++ API 从零完成模型加载、图像预处理、Extractor 推理和结果后处理的完整可运行示例，含 Option 配置和内存池使用。
tags: [ncnn, cpp, inference, example]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: net-h
    resource: /src/net.h
    title: net.h
---

# C++ 完整推理示例

本例演示使用 ncnn C++ API 完成一个图像分类模型的完整推理流程。

## 完整代码

```cpp
#include <net.h>
#include <simpleocv.h>   // 或使用 OpenCV

int main(int argc, char** argv)
{
    // 1. 配置 Option（必须在 load_param 前设置）
    ncnn::Option opt;
    opt.lightmode = true;
    opt.num_threads = 4;
    opt.use_packing_layout = true;
    opt.use_winograd_convolution = true;
    opt.use_sgemm_convolution = true;

    // 可选：使用内存池减少分配开销
    ncnn::UnlockedPoolAllocator g_blob_pool;
    ncnn::PoolAllocator g_workspace_pool;
    opt.blob_allocator = &g_blob_pool;
    opt.workspace_allocator = &g_workspace_pool;

    // 2. 加载模型
    ncnn::Net net;
    net.opt = opt;
    if (net.load_param("squeezenet.param") != 0) {
        fprintf(stderr, "load_param failed\n");
        return -1;
    }
    if (net.load_model("squeezenet.bin") != 0) {
        fprintf(stderr, "load_model failed\n");
        return -1;
    }

    // 3. 读取并预处理图像
    cv::Mat bgr = cv::imread("cat.jpg");
    ncnn::Mat in = ncnn::Mat::from_pixels_resize(
        bgr.data, ncnn::Mat::PIXEL_BGR2RGB,
        bgr.cols, bgr.rows, 227, 227);

    // 减均值 / 归一化（ImageNet 统计量）
    const float mean_vals[3] = {104.f, 117.f, 123.f};
    const float norm_vals[3] = {1.0f / 255.0f, 1.0f / 255.0f, 1.0f / 255.0f};
    in.substract_mean_normalize(mean_vals, norm_vals);

    // 4. 创建 Extractor 并喂入数据
    ncnn::Extractor ex = net.create_extractor();
    ex.input("data", in);

    // 5. 提取输出
    ncnn::Mat out;
    if (ex.extract("prob", out) != 0) {
        fprintf(stderr, "extract failed\n");
        return -1;
    }

    // 6. 后处理：找最大概率类别
    float max_prob = 0.f;
    int max_idx = 0;
    for (int i = 0; i < out.w; i++) {
        float prob = out[i];
        if (prob > max_prob) {
            max_prob = prob;
            max_idx = i;
        }
    }
    printf("class = %d, prob = %.4f\n", max_idx, max_prob);

    return 0;
}
```

## 关键步骤说明

### Option 配置时机

影响层创建的选项（`use_packing_layout`、`use_int8_inference`、`use_winograd_convolution` 等）必须在 `load_param` **之前**赋给 `net.opt`，因为层的能力标志位在加载阶段确定。

### 图像预处理

`Mat::from_pixels_resize` 一步完成颜色转换和缩放：
- `PIXEL_BGR2RGB` 同时处理通道顺序转换；
- 输出为 `227×227×3` 的 float32 Mat，像素值已归一化到 `[0,255]`；
- `substract_mean_normalize` 逐通道减均值再乘归一化系数。

### Extractor 生命周期

- `create_extractor()` 返回一个独立的推理会话，可多次创建并发执行；
- `input` 可多次调用喂入多个输入 blob；
- `extract` 触发按需计算（lightmode 下只计算依赖链上的层）；
- `Net` 不可拷贝，但 `Extractor` 可拷贝（共享同一 Net）。

### 内存池

`UnlockedPoolAllocator` 用于 blob（单推理线程无锁），`PoolAllocator` 用于 workspace（多线程安全）。Net 的 opt 中设置后，所有 Extractor 共享。

## CMake 集成

```cmake
find_package(ncnn REQUIRED)
add_executable(inference main.cpp)
target_link_libraries(inference ncnn)
```

## 相关概念

- [01 Net 与 Extractor 推理流程](/concepts/01-net-extractor.md)
- [02 Mat 张量系统](/concepts/02-mat-tensor-system.md)
- [04 内存分配器](/concepts/04-allocator.md)
- [05 Option 推理配置](/concepts/05-option-config.md)
