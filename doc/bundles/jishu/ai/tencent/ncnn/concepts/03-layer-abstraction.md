---
type: Concept
title: Layer 抽象层
description: Layer 是所有算子的基类，通过 bool 能力标志位声明支持的特性，虚函数 load_param/load_model/create_pipeline 管理生命周期，forward/forward_inplace 各有 CPU Mat 和 Vulkan VkMat 多重载。
tags: [ncnn, layer, operator, abstraction]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: layer-h
    resource: /src/layer.h
    title: layer.h
---

# Layer 抽象层

`Layer` 是 ncnn 中所有神经网络算子的抽象基类。它统一了 CPU 和 GPU 两种后端的算子接口，通过能力标志位而非虚继承来表达特性组合。

## 能力标志位

每个 Layer 在构造函数中设置一组 bool 标志位声明自身能力（F-038）：

| 标志位 | 含义 |
|---|---|
| `one_blob_only` | 单输入单输出（true 时框架调用单 blob forward） |
| `support_inplace` | 支持就地运算（可复用输入内存） |
| `support_vulkan` | 实现了 Vulkan compute shader |
| `support_packing` | 接受 `elempack>1` 的打包张量 |
| `support_bf16_storage` | 接受 bfloat16 存储 |
| `support_fp16_storage` | 接受 float16 存储 |
| `support_int8_storage` | 接受 int8 存储 |
| `support_tensor_storage` | 支持 shader tensor storage |
| `support_vulkan_packing` | Vulkan 路径接受打包 |
| `support_any_packing` | 接受任意 elempack |
| `support_vulkan_any_packing` | Vulkan 任意 elempack |
| `support_batch` | 支持 `n>1` 的批量输入 |

这些标志位是扁平的布尔字段而非接口继承，框架通过检查标志位决定调用哪个 forward 重载、是否需要插入 Packing/Cast 转换层。

## 生命周期

```cpp
virtual int load_param(const ParamDict& pd);   // 解析超参数
virtual int load_model(const ModelBin& mb);    // 加载权重
virtual int create_pipeline(const Option& opt); // Vulkan 管线创建
virtual int destroy_pipeline(const Option& opt);// Vulkan 管线销毁
```

1. **load_param**：从 `ParamDict` 按参数 ID 读取 kernel size、stride、num_output 等超参数。
2. **load_model**：从 `ModelBin` 加载权重数据（weight/bias），可在此做权重重排或量化预处理。
3. **create_pipeline**：Vulkan 算子编译 shader、创建 descriptor set layout（仅 `support_vulkan` 层）。
4. **destroy_pipeline**：释放 Vulkan 资源。

## forward 虚函数体系

### CPU 路径

```cpp
// 多输入多输出
virtual int forward(const std::vector<Mat>& bottom_blobs,
                    std::vector<Mat>& top_blobs, const Option& opt) const;
// 单输入单输出（one_blob_only=true 时调用）
virtual int forward(const Mat& bottom_blob, Mat& top_blob,
                    const Option& opt) const;

// 就地运算
virtual int forward_inplace(std::vector<Mat>& bottom_top_blobs,
                            const Option& opt) const;
virtual int forward_inplace(Mat& bottom_top_blob, const Option& opt) const;
```

### Vulkan 路径（NCNN_VULKAN）

```cpp
virtual int forward(const std::vector<VkMat>& bottom_blobs,
                    std::vector<VkMat>& top_blobs,
                    VkCompute& cmd, const Option& opt) const;
virtual int forward(const VkMat& bottom_blob, VkMat& top_blob,
                    VkCompute& cmd, const Option& opt) const;
virtual int forward_inplace(std::vector<VkMat>& bottom_top_blobs,
                            VkCompute& cmd, const Option& opt) const;
virtual int forward_inplace(VkMat& bottom_top_blob,
                            VkCompute& cmd, const Option& opt) const;
virtual int upload_model(VkTransfer& cmd, const Option& opt);
```

Vulkan forward 额外接收 `VkCompute& cmd` 用于录制 compute 命令，不立即执行。

### 分派逻辑

框架根据以下条件选择调用：
1. `Option::use_vulkan_compute && support_vulkan` → Vulkan forward；
2. 否则 → CPU forward；
3. `one_blob_only` → 单 blob 版本；否则 vector 版本；
4. `support_inplace` 且内存可复用 → forward_inplace。

## 索引与形状

```cpp
int typeindex;                   // 层类型枚举值
std::string type;                // 类型名（如 "Convolution"）
std::string name;                // 实例名
std::vector<int> bottoms;        // 输入 blob 索引
std::vector<int> tops;           // 输出 blob 索引
std::vector<Mat> bottom_shapes;  // 输入形状提示
std::vector<Mat> top_shapes;     // 输出形状提示
void* userdata;                  // 自定义层用户数据
const VulkanDevice* vkdev;       // Vulkan 设备指针
```

`bottoms`/`tops` 存储的是 blob 在 `Net::blobs()` 数组中的索引，层通过这些索引读写数据，实现计算图的连接。

## 自定义层

```cpp
class MyLayer : public ncnn::Layer {
public:
    MyLayer() { one_blob_only = true; support_inplace = true; }
    int load_param(const ncnn::ParamDict& pd) override { ... }
    int forward(const ncnn::Mat& bottom, ncnn::Mat& top,
                const ncnn::Option& opt) const override { ... }
};
DEFINE_LAYER_CREATOR(MyLayer)

// 注册
net.register_custom_layer("MyLayer", MyLayer_layer_creator);
```

`DEFINE_LAYER_CREATOR` 宏生成工厂函数 `MyLayer_layer_creator(void*)` 返回 `new MyLayer`（F-047）。

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [05 Option 推理配置](05-option-config.md)
- [06 Vulkan GPU 后端](06-vulkan-gpu.md)
- [08 ParamDict 与 ModelBin](08-paramdict-modelbin.md)
- [09 层注册表与自定义层](09-layer-registry.md)
- [自定义 Layer 示例](../examples/custom-layer.md)
