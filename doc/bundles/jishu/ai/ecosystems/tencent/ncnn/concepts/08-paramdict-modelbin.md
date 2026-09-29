---
type: Concept
title: ParamDict 与 ModelBin
description: ParamDict 解析 .param 文本或二进制参数字典，get<T> 按 ID 读取 int/float/Mat/string，每层最多 32 参数；ModelBin 从 .bin 加载权重，load 按 type 支持 fp32/fp16/int8/int4/int6 分块量化；DataReader 抽象文件/内存/Asset 数据源。
tags: [ncnn, paramdict, modelbin, datareader, model-format]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: paramdict-h
    resource: /src/paramdict.h
    title: paramdict.h
  - id: modelbin-h
    resource: /src/modelbin.h
    title: modelbin.h
  - id: datareader-h
    resource: /src/datareader.h
    title: datareader.h
---

# ParamDict 与 ModelBin

ncnn 模型由两个文件组成：`.param`（网络结构和超参数）和 `.bin`（权重数据）。`ParamDict` 和 `ModelBin` 分别负责这两部分的解析，`DataReader` 抽象底层数据源。

## ParamDict：参数字典

每层最多 32 个参数（`NCNN_MAX_PARAM_COUNT=32`，F-076），参数以数字 ID 索引而非名称，ID 在层的 `load_param` 中硬编码。

### 类型安全的 get/set

```cpp
class ParamDict {
public:
    int get(int id, int def) const;           // 整型
    float get(int id, float def) const;        // 浮点
    Mat get(int id, const Mat& def) const;     // 数组
    std::string get(int id, const std::string& def) const;

    void set(int id, int i);
    void set(int id, float f);
    void set(int id, const Mat& v);
    void set(int id, const std::string& s);
};
```

四个 `get` 重载通过参数类型区分返回类型，未设置时返回默认值（F-077）。

### param 文本格式

典型 `.param` 文件：

```
7767517
3 2
Input            data             0 1 data 0=4 1=3 2=224 3=224
Convolution      conv1            1 1 data conv1 0=64 1=3 2=1 3=1 4=0 5=1 6=512
ReLU             relu1            1 1 conv1 conv1 0=0.0
```

- 第一行 magic number `7767517`；
- 第二行 `层数 blob数`；
- 每行：层类型、层名、bottom数、top数、bottom名、top名、`ID=值` 参数列表；
- 数组参数用 `ID=值1,值2,...` 逗号分隔。

二进制 param（`.param.bin`）是文本格式的紧凑二进制编码，用于减少解析开销。

### 加载流程

`Net::load_param` 通过 `DataReader` 读取：
1. 解析 magic number 和层计数；
2. 逐层读取类型名、名称、bottom/top 连接；
3. 构造 `ParamDict`，调用 `ParamDict::load_param(dr)` 解析键值对；
4. 调用该层的 `Layer::load_param(pd)`，层内用 `pd.get(id, default)` 提取自己的参数。

## ModelBin：权重加载

`ModelBin` 按顺序从 `.bin` 文件读取权重张量（F-079）：

```cpp
class ModelBin {
public:
    // type: 0=auto, 1=fp32, 2=fp16, 3=int8,
    //       4=int4 block quant, 6=int6, 8=int8 block quant
    virtual Mat load(int w, int type) const;
    virtual Mat load(int w, int h, int type) const;
    virtual Mat load(int w, int h, int c, int type) const;
    virtual Mat load(int w, int h, int d, int c, int type) const;
};
```

### 权重类型

| type | 格式 | 说明 |
|---|---|---|
| 0 | auto | 自动判断（通常 fp32） |
| 1 | float32 | 单精度浮点 |
| 2 | float16 | 半精度浮点 |
| 3 | int8 | 对称量化 int8 |
| 4 | int4 | 块量化 4-bit |
| 6 | int6 | 块量化 6-bit |
| 8 | int8 | 块量化 8-bit |

`load` 返回的 Mat 已经是反量化/转换后的 fp32（除非用 int8 storage 直接保留）。层在 `load_model` 中按**声明顺序**调用 `mb.load(...)` 读取权重。

### 两种来源

```cpp
ModelBinFromDataReader(const DataReader& dr);  // 从 .bin 文件/内存流
ModelBinFromMatArray(const Mat* weights);      // 从内存 Mat 数组
```

`ModelBinFromMatArray` 用于从内存数组加载权重（如 PNNX 转换后的内存模型），按数组顺序逐个返回（F-080）。

## DataReader：数据源抽象

`DataReader` 屏蔽不同存储介质（F-081）：

```cpp
class DataReader {
public:
    virtual int scan(const char* format, void* p) const;   // 文本解析
    virtual size_t read(void* buf, size_t size) const;      // 二进制读取
    virtual size_t reference(size_t size, const void** buf) const; // 零拷贝引用
};
```

| 子类 | 数据源 |
|---|---|
| `DataReaderFromStdio` | FILE* 文件指针 |
| `DataReaderFromMemory` | 内存字节流（支持零拷贝 reference） |
| `DataReaderFromAndroidAsset` | Android AAsset |

`DataReaderFromMemory::reference` 直接返回内存指针而不拷贝，这是 `Net::load_model(const unsigned char*)` 零拷贝权重的基础。

## 层中的典型用法

```cpp
int MyLayer::load_param(const ncnn::ParamDict& pd) {
    num_output = pd.get(0, 0);
    kernel_w = pd.get(1, 3);
    stride_w = pd.get(2, 1);
    bias_term = pd.get(3, 0);
    weight_data_size = pd.get(6, 0);
    return 0;
}

int MyLayer::load_model(const ncnn::ModelBin& mb) {
    weight_data = mb.load(weight_data_size, 0);  // fp32
    if (bias_term)
        bias_data = mb.load(num_output, 0);
    return 0;
}
```

参数 ID 和权重读取顺序必须与 `.param`/`.bin` 生成端一致。

## 相关概念

- [03 Layer 抽象层](03-layer-abstraction.md)
- [01 Net 与 Extractor 推理流程](01-net-extractor.md)
- [09 层注册表与自定义层](09-layer-registry.md)
- [11 量化与低精度](11-quantization.md)
