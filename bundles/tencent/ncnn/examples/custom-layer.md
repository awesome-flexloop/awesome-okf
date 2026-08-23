---
type: Example
title: 自定义 Layer 注册与实现
description: 继承 ncnn::Layer 实现自定义算子，设置能力标志位，实现 load_param/forward，用 DEFINE_LAYER_CREATOR 宏生成工厂函数，通过 register_custom_layer 注册到 Net。
tags: [ncnn, custom-layer, extension, example]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: layer-h
    resource: /src/layer.h
    title: layer.h
---

# 自定义 Layer 注册与实现

本例演示如何为 ncnn 添加一个自定义算子，并在模型中使用。

## C++ 自定义层

### 1. 实现 Layer 子类

```cpp
#include <layer.h>

namespace ncnn {

class MyScale : public Layer
{
public:
    MyScale()
    {
        one_blob_only = true;       // 单输入单输出
        support_inplace = true;      // 支持就地运算
        support_packing = true;      // 支持 SIMD 打包
    }

    // 从 ParamDict 读取超参数
    virtual int load_param(const ParamDict& pd)
    {
        scale = pd.get(0, 1.0f);    // 参数 ID 0，默认 1.0
        bias = pd.get(1, 0.0f);     // 参数 ID 1，默认 0.0
        return 0;
    }

    // 从 ModelBin 加载权重（如有）
    virtual int load_model(const ModelBin& mb)
    {
        // 如无需权重可直接返回 0
        return 0;
    }

    // 单 blob forward（分配输出）
    virtual int forward(const Mat& bottom_blob, Mat& top_blob,
                        const Option& opt) const
    {
        top_blob.create_like(bottom_blob, opt.blob_allocator);
        if (top_blob.empty()) return -100;

        int w = bottom_blob.w;
        int h = bottom_blob.h;
        int c = bottom_blob.c;
        size_t elemsize = bottom_blob.elemsize;
        int size = w * h;

        // 支持打包存储
        if (bottom_blob.elempack == 1) {
            for (int q = 0; q < c; q++) {
                const float* ptr = bottom_blob.channel(q);
                float* outptr = top_blob.channel(q);
                for (int i = 0; i < size; i++) {
                    outptr[i] = ptr[i] * scale + bias;
                }
            }
        }

        return 0;
    }

    // 就地 forward（复用输入内存）
    virtual int forward_inplace(Mat& bottom_top_blob,
                                const Option& opt) const
    {
        int w = bottom_top_blob.w;
        int h = bottom_top_blob.h;
        int c = bottom_top_blob.c;
        int size = w * h;

        for (int q = 0; q < c; q++) {
            float* ptr = bottom_top_blob.channel(q);
            for (int i = 0; i < size; i++) {
                ptr[i] = ptr[i] * scale + bias;
            }
        }
        return 0;
    }

private:
    float scale;
    float bias;
};

DEFINE_LAYER_CREATOR(MyScale)

} // namespace ncnn
```

### 2. 注册到 Net

```cpp
ncnn::Net net;

// 必须在 load_param 之前注册
net.register_custom_layer("MyScale",
                          ncnn::MyScale_layer_creator,
                          nullptr, nullptr);

net.load_param("model.param");
net.load_model("model.bin");
```

### 3. param 文件中使用

在 `.param` 文件中将层类型设为注册的名称：

```
7767517
2 2
Input      data   0 1 data 0=3 1=224 2=224
MyScale    scale1 1 1 data output 0=2.0 1=0.5
```

## 能力标志位设置指南

| 场景 | one_blob_only | support_inplace | support_packing | support_vulkan |
|---|---|---|---|---|
| 简单逐元素运算 | true | true | true | 可选 |
| 多输入融合（Eltwise） | false | true | true | 可选 |
| 变形/裁剪（Reshape/Crop） | true | false | true | 可选 |
| 卷积 | true | false | true | 需实现 shader |

- 不设 `support_packing` 时框架自动插入解包层，功能正确但略慢；
- `support_inplace` 仅在输入可安全覆写时启用；
- Vulkan 算子需额外实现 `forward(VkMat...)` 并设 `support_vulkan=true`。

## 带权重的自定义层

```cpp
int load_model(const ModelBin& mb) {
    // 按 param 中声明的顺序读取权重
    weight = mb.load(num_output, 0);  // fp32 权重
    if (bias_term)
        bias = mb.load(num_output, 0);
    return 0;
}
```

`mb.load(size, type)` 的 type 参数：0=auto/fp32，2=fp16，3=int8。

## Python 自定义层

```python
import ncnn

class MyScale(ncnn.Layer):
    def __init__(self):
        super().__init__()
        self.one_blob_only = True
        self.support_inplace = True
        self.scale = 1.0
        self.bias = 0.0

    def load_param(self, pd):
        self.scale = pd.get(0, 1.0)
        self.bias = pd.get(1, 0.0)
        return 0

    def forward(self, bottom, opt):
        top = bottom.clone()
        # numpy 运算（bottom/top 通过 buffer protocol 共享内存）
        import numpy as np
        top_np = np.array(top)
        top_np *= self.scale
        top_np += self.bias
        return 0, top

    def forward_inplace(self, bottom_top, opt):
        import numpy as np
        arr = np.array(bottom_top)
        arr *= self.scale
        arr += self.bias
        return 0

net = ncnn.Net()
net.register_custom_layer("MyScale", MyScale)
net.load_param("model.param")
net.load_model("model.bin")
```

## 相关概念

- [03 Layer 抽象层](/concepts/03-layer-abstraction.md)
- [09 层注册表与自定义层](/concepts/09-layer-registry.md)
- [08 ParamDict 与 ModelBin](/concepts/08-paramdict-modelbin.md)
- [01 Net 与 Extractor 推理流程](/concepts/01-net-extractor.md)
