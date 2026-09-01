---
type: Concept
title: Net 与 Extractor 推理流程
description: Net 负责加载 param/bin 模型并管理层与 blob，Extractor 由 Net 创建，设置 allocator 后通过 input/extract 按名称或索引喂入数据并获取结果，lightmode 自动回收中间 blob。
tags: [ncnn, net, extractor, inference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: net-h
    resource: /src/net.h
    title: net.h
---

# Net 与 Extractor 推理流程

## 两阶段模型

ncnn 将"模型"与"推理会话"分离为两个类：

- **`Net`**：加载并持有网络结构（层、blob）和权重，是不可变的模型容器。
- **`Extractor`**：由 `Net::create_extractor()` 创建，持有一次推理的中间 blob 数据和 allocator，可多次创建、并发使用。

```cpp
ncnn::Net net;
net.load_param("model.param");
net.load_model("model.bin");

ncnn::Extractor ex = net.create_extractor();
ex.input("data", in);
ncnn::Mat out;
ex.extract("output", out);
```

## Net：模型加载

### 加载 API 矩阵

| 来源 | param 文本 | param 二进制 | model 权重 |
|---|---|---|---|
| 文件路径 | `load_param(path)` | `load_param_bin(path)` | `load_model(path)` |
| FILE* | `load_param(FILE*)` | `load_param_bin(FILE*)` | `load_model(FILE*)` |
| 内存 | `load_param_mem(str)` | `load_param(mem*)` | `load_model(mem*)` |
| DataReader | `load_param(dr)` | `load_param_bin(dr)` | `load_model(dr)` |
| Android Asset | `load_param(AAsset*)` | `load_param_bin(AAsset*)` | `load_model(AAsset*)` |

### 内存零拷贝加载

`load_param(const unsigned char* mem)` 和 `load_model(const unsigned char* mem)` 返回消费的字节数（F-007、F-008）。权重数据**不被拷贝而是直接引用**，因此外部内存必须：

1. 32 位对齐；
2. 在整个推理期间保持有效。

这使得 ncnn 可以直接 mmap 模型文件而不复制权重。

### 选项必须在加载前设置

`net.opt` 是公开成员，但影响层创建的选项（`use_winograd_convolution`、`use_int8_inference`、`use_packing_layout`、`use_vulkan_compute` 等）必须在 `load_param` **之前**设置，因为层的能力标志位和权重预处理在加载阶段确定。

### 自定义层注册

```cpp
net.register_custom_layer("MyLayer", MyLayer_layer_creator,
                          MyLayer_layer_destroyer, nullptr);
```

支持按类型名（`const char*`）或类型索引（`int`）注册，可覆盖内置层（F-004、F-005）。自定义层需用 `DEFINE_LAYER_CREATOR(MyLayer)` 宏生成工厂函数。

## Extractor：推理执行

### Allocator 配置

Extractor 允许为不同用途设置独立分配器（F-011、F-012）：

- `set_blob_allocator`：中间特征图
- `set_workspace_allocator`：层内临时工作区
- `set_kvcache_allocator`：LLM KV cache

Vulkan 下额外有 blob/workspace/staging/kvcache 四种 `VkAllocator`。

### Light Mode

`set_light_mode(true)`（默认启用）使中间 blob 在被所有消费者读取后立即回收内存（F-010）。对于多输出或需要复用中间结果的场景可关闭，但会增加峰值内存。

### input/extract

```cpp
ex.input("data", in);          // 按名称
ex.input(0, in);               // 按索引

ncnn::Mat out;
ex.extract("output", out, 0);  // type=0 默认，自动转换精度/packing
```

`extract` 的 `type` 参数：
- `0`（默认）：必要时自动将 fp16/bf16/packed 结果转换回 fp32 scalar；
- `1`：不转换，保留原始存储格式（用于 KV cache 等需要原样传递的场景）。

### Vulkan 推理

启用 `net.opt.use_vulkan_compute = true` 后，Extractor 的 input/extract 可接受 `VkMat`：

```cpp
ex.input("data", vk_in);
ncnn::VkMat vk_out;
ex.extract("output", vk_out, cmd);
cmd.submit_and_wait();
ncnn::Mat out = vk_out.mapped();  // 下载回主机
```

### 并发推理

`Net` 加载后不可变，因此可安全地从多个线程调用 `create_extractor()`。每个 `Extractor` 是独立的推理会话，持有自己的 blob 数据，可在不同线程上并行执行。`Net` 本身禁止拷贝（拷贝构造和赋值运算符为 private）。

## 模型自省

```cpp
const std::vector<int>& in_idx = net.input_indexes();
const std::vector<int>& out_idx = net.output_indexes();
const std::vector<ncnn::Blob>& blobs = net.blobs();
const std::vector<ncnn::Layer*>& layers = net.layers();
```

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [03 Layer 抽象层](03-layer-abstraction.md)
- [04 内存分配器](04-allocator.md)
- [05 Option 推理配置](05-option-config.md)
- [C++ 完整推理示例](../examples/first-inference.md)
