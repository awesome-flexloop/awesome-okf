---
type: Reference
title: layer.h — Layer 基类信源
description: ncnn/src/layer.h 中 Layer 抽象基类的能力标志位、生命周期虚函数、CPU/Vulkan forward 多重载、bottoms/tops 索引及层工厂注册表结构登记。
tags: [ncnn, layer, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: layer-h
    resource: /src/layer.h
    title: layer.h
---

# layer.h — Layer 基类

> 信源路径：`src/layer.h`（213 行）。

## Layer 类定义

```cpp
class NCNN_EXPORT Layer
{
public:
    Layer();
    virtual ~Layer();

    // 生命周期
    virtual int load_param(const ParamDict& pd);
    virtual int load_model(const ModelBin& mb);
    virtual int create_pipeline(const Option& opt);
    virtual int destroy_pipeline(const Option& opt);

public:
    // 能力标志位
    bool one_blob_only;            // 单输入单输出
    bool support_inplace;          // 支持就地运算
    bool support_vulkan;           // 支持 Vulkan
    bool support_packing;          // 接受打包存储
    bool support_bf16_storage;
    bool support_fp16_storage;
    bool support_int8_storage;
    bool support_tensor_storage;
    bool support_vulkan_packing;
    bool support_any_packing;
    bool support_vulkan_any_packing;
    bool support_batch;
    int featmask;

public:
    // CPU forward
    virtual int forward(const std::vector<Mat>& bottom_blobs,
                        std::vector<Mat>& top_blobs, const Option& opt) const;
    virtual int forward(const Mat& bottom_blob, Mat& top_blob,
                        const Option& opt) const;
    // CPU inplace
    virtual int forward_inplace(std::vector<Mat>& bottom_top_blobs,
                                const Option& opt) const;
    virtual int forward_inplace(Mat& bottom_top_blob, const Option& opt) const;

#if NCNN_VULKAN
    virtual int upload_model(VkTransfer& cmd, const Option& opt);
    // Vulkan forward
    virtual int forward(const std::vector<VkMat>& bottom_blobs,
                        std::vector<VkMat>& top_blobs,
                        VkCompute& cmd, const Option& opt) const;
    virtual int forward(const VkMat& bottom_blob, VkMat& top_blob,
                        VkCompute& cmd, const Option& opt) const;
    // Vulkan inplace
    virtual int forward_inplace(std::vector<VkMat>& bottom_top_blobs,
                                VkCompute& cmd, const Option& opt) const;
    virtual int forward_inplace(VkMat& bottom_top_blob,
                                VkCompute& cmd, const Option& opt) const;
    const VulkanDevice* vkdev;
#endif

public:
    void* userdata;
    int typeindex;
#if NCNN_STRING
    std::string type;
    std::string name;
#endif
    std::vector<int> bottoms;      // 输入 blob 索引
    std::vector<int> tops;         // 输出 blob 索引
    std::vector<Mat> bottom_shapes;
    std::vector<Mat> top_shapes;
};
```

## 工厂类型与宏

```cpp
typedef Layer* (*layer_creator_func)(void*);
typedef void (*layer_destroyer_func)(Layer*, void*);

struct layer_registry_entry {
#if NCNN_STRING
    const char* name;
#endif
    layer_creator_func creator;
};

#define DEFINE_LAYER_CREATOR(name) \
    ::ncnn::Layer* name##_layer_creator(void*) { return new name; }

#define DEFINE_LAYER_DESTROYER(name) \
    void name##_layer_destroyer(::ncnn::Layer* layer, void*) { delete layer; }

NCNN_EXPORT int layer_to_index(const char* type);
NCNN_EXPORT Layer* create_layer(const char* type);
NCNN_EXPORT Layer* create_layer(int index);
NCNN_EXPORT Layer* create_layer_cpu(int index);
#if NCNN_VULKAN
NCNN_EXPORT Layer* create_layer_vulkan(int index);
#endif
```

## 分派规则

- `one_blob_only=true` 时框架调用单 blob 版本 `forward(const Mat&, Mat&, ...)`；否则调用 vector 版本。
- `support_inplace=true` 时框架可调用 `forward_inplace` 直接复用输入内存。
- `Option::use_vulkan_compute && support_vulkan` 时选择 VkMat forward；否则回退 Mat forward。
- `support_packing` 决定算子是否接受 `elempack>1` 的打包张量；不支持时框架自动插入 `Packing` 层解包。

## 相关概念

- [03 Layer 抽象层](/concepts/03-layer-abstraction.md)
- [09 层注册表与自定义层](/concepts/09-layer-registry.md)
- [06 Vulkan GPU 后端](/concepts/06-vulkan-gpu.md)
