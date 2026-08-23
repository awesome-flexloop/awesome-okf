---
type: Reference
title: net.h — Net 与 Extractor API 信源
description: ncnn/src/net.h 中 Net 网络容器与 Extractor 推理执行器的完整类定义、加载 API、自定义层注册、input/extract 签名登记。
tags: [ncnn, net, extractor, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: net-h
    resource: /src/net.h
    title: net.h
---

# net.h — Net 与 Extractor

> 信源路径：`src/net.h`（260 行）。BSD-3-Clause，Copyright 2017 Tencent。

## Net 类

```cpp
class NCNN_EXPORT Net
{
public:
    Net();
    virtual ~Net();

public:
    Option opt;                          // F-003 加载前可改

#if NCNN_VULKAN
    void set_vulkan_device(int device_index);
    void set_vulkan_device(const VulkanDevice* vkdev);
    const VulkanDevice* vulkan_device() const;
#endif

#if NCNN_STRING
    int register_custom_layer(const char* type, layer_creator_func creator,
                              layer_destroyer_func destroyer = 0, void* userdata = 0);
    virtual int custom_layer_to_index(const char* type);
#endif
    int register_custom_layer(int index, layer_creator_func creator,
                              layer_destroyer_func destroyer = 0, void* userdata = 0);

    // 加载：DataReader / FILE* / 路径 / wchar_t* / 内存 / AAsset
#if NCNN_STRING
    int load_param(const DataReader& dr);
    int load_param(FILE* fp);
    int load_param(const char* protopath);
    int load_param_mem(const char* mem);
#endif
    int load_param_bin(const DataReader& dr);
    int load_param_bin(FILE* fp);
    int load_model(const DataReader& dr);
    int load_model(FILE* fp);
    int load_model(const char* modelpath);
    size_t load_param(const unsigned char* mem);   // F-007 32位对齐,返回字节数
    size_t load_model(const unsigned char* mem);   // F-008 引用不拷贝

    void clear();
    Extractor create_extractor() const;            // F-009

    const std::vector<int>& input_indexes() const;
    const std::vector<int>& output_indexes() const;
    const std::vector<Blob>& blobs() const;
    const std::vector<Layer*>& layers() const;

protected:
    friend class Extractor;
    virtual Layer* create_custom_layer(const char* type);
    virtual Layer* create_custom_layer(int index);

private:
    Net(const Net&);                               // F-017 禁止拷贝
    Net& operator=(const Net&);
private:
    NetPrivate* const d;                           // F-001 PIMPL
};
```

## Extractor 类

```cpp
class NCNN_EXPORT Extractor
{
public:
    virtual ~Extractor();
    Extractor(const Extractor&);
    Extractor& operator=(const Extractor&);

    void clear();
    void set_light_mode(bool enable);              // F-010 默认 true

    void set_blob_allocator(Allocator* allocator);
    void set_workspace_allocator(Allocator* allocator);
    void set_kvcache_allocator(Allocator* allocator);

#if NCNN_VULKAN
    void set_blob_vkallocator(VkAllocator* allocator);
    void set_workspace_vkallocator(VkAllocator* allocator);
    void set_staging_vkallocator(VkAllocator* allocator);
    void set_kvcache_vkallocator(VkAllocator* allocator);
#endif

#if NCNN_STRING
    int input(const char* blob_name, const Mat& in);
    int extract(const char* blob_name, Mat& feat, int type = 0);  // F-014 type=1保留fp16/packing
#endif
    int input(int blob_index, const Mat& in);
    int extract(int blob_index, Mat& feat, int type = 0);

#if NCNN_VULKAN
    int input(const char* blob_name, const VkMat& in);
    int extract(const char* blob_name, VkMat& feat, VkCompute& cmd);
    int input(int blob_index, const VkMat& in);
    int extract(int blob_index, VkMat& feat, VkCompute& cmd);
#endif

protected:
    friend Extractor Net::create_extractor() const;
    Extractor(const Net* net, size_t blob_count);
private:
    ExtractorPrivate* const d;                     // F-002 PIMPL
};
```

## 要点

- `opt` 是公开成员，必须在 `load_param/load_model` **之前**设置 `use_winograd_convolution`、`use_int8_inference`、`use_packing_layout` 等影响层创建的选项。
- `load_param(const unsigned char*)` / `load_model(const unsigned char*)` 实现内存零拷贝加载，模型数据须 32 位对齐且在推理期间保持存活。
- `Extractor` 可拷贝（引用同一 Net 的 blob 槽位），但 `Net` 不可拷贝。
- `extract(..., int type=0)` 的 `type=1` 用于 LLM KV cache 场景，禁止 fp16/bf16/packing 自动转换。

## 相关概念

- [01 Net 与 Extractor 推理流程](/concepts/01-net-extractor.md)
- [05 Option 推理配置](/concepts/05-option-config.md)
