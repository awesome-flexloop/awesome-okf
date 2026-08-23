---
type: Concept
title: 量化与低精度推理
description: ncnn 支持 int8 量化推理（use_int8_inference）、fp16/bf16 存储（elemsize=2）、int8 存储（elemsize=1）和权重量化（NCNN_WEIGHT_QUANT，int4/int6/int8 块量化），通过 quantize/dequantize/requantize 算子和 cast 转换层在运行时混合精度。
tags: [ncnn, quantization, int8, fp16, bf16]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mat-h
    resource: /src/mat.h
    title: mat.h
  - id: modelbin-h
    resource: /src/modelbin.h
    title: modelbin.h
  - id: cmake
    resource: /CMakeLists.txt
    title: CMakeLists.txt
---

# 量化与低精度推理

ncnn 提供多层次的低精度支持，从权重量化到运行时 int8 计算，再到 fp16/bf16 存储和打包，可独立或组合使用。

## 精度与 elemsize

Mat 的 `elemsize` 字段直接标识存储精度（F-021）：

| elemsize | 精度 | 典型用途 |
|---|---|---|
| 4 | float32 / int32 | 默认精度、量化缩放因子 |
| 2 | float16 / bfloat16 | 半精度存储、中间特征图 |
| 1 | int8 / uint8 | 量化权重、int8 推理 |

## int8 量化推理

### 启用

```cpp
ncnn::Option opt;
opt.use_int8_inference = true;  // 默认 true（F-056）
net.opt = opt;
```

启用后，加载量化模型时 ncnn 自动选择 int8 kernel。量化模型的权重在 `.bin` 中以 int8 存储（`ModelBin::load(..., 3)`），附带每层的 scale 量化参数。

### 量化算子

三个核心算子处理量化数据流（mat.h:890-892）：

```cpp
// fp32 -> int8
void quantize_to_int8(const Mat& src, Mat& dst,
                      const Mat& scale_data, const Option& opt);

// int32 accumulator -> fp32（带 scale 和 bias）
void dequantize_from_int32(const Mat& src, Mat& dst,
                           const Mat& scale_data,
                           const Mat& bias_data, const Option& opt);

// int32 -> int8（层间融合，带激活）
void requantize_from_int32_to_int8(const Mat& src, Mat& dst,
                                   const Mat& scale_in_data,
                                   const Mat& scale_out_data,
                                   const Mat& bias_data,
                                   int activation_type,
                                   const Mat& activation_params,
                                   const Option& opt);
```

卷积/GEMM 等算子内部：int8 乘法 → int32 累加 → requantize 回 int8，避免层间反复精度转换。

### Layer 能力标志

```cpp
bool support_int8_storage;    // 接受 int8 输入
bool support_int8_packed;     // int8 + SIMD 打包
// Option 三级控制
bool use_int8_packed;
bool use_int8_storage;
bool use_int8_arithmetic;
```

## fp16 / bf16 半精度

### fp16

- `Option::use_fp16_storage`：中间特征图以 fp16 存储，减半内存带宽；
- `use_fp16_packed`：fp16 + elempack=8（NEON FP16/AVX 可一次处理 8 个 fp16）；
- `use_fp16_arithmetic`：GPU shader 中使用 fp16 计算；
- ARM 的 `__ARM_FEATURE_FP16_VECTOR_ARITHMETIC` 和 x86 的 F16C/AVX512-FP16 提供硬件加速。

### bf16

- `Option::use_bf16_storage`：bfloat16 存储；
- bf16 与 fp32 的转换极其简单——直接取高/低 16 位（F-036）：

```cpp
NCNN_FORCEINLINE unsigned short float32_to_bfloat16(float value) {
    union { unsigned int u; float f; } tmp;
    tmp.f = value;
    return tmp.u >> 16;  // 直接截断
}
```

无需复杂的舍入逻辑，在支持 bf16 的硬件（AVX512-BF16、ARM SVE-BF16、Google TPU）上可直接计算。bf16 动态范围与 fp32 相同（8 位指数），适合深度学习；fp16 精度更高（10 位尾数）但动态范围较小。

## 权重量化（Weight Quantization）

`NCNN_WEIGHT_QUANT=ON`（默认）启用块量化权重格式，`ModelBin` 支持三种块量化类型（F-079）：

| load type | 格式 | 说明 |
|---|---|---|
| 4 | int4 块量化 | 每块 4-bit，极致压缩 |
| 6 | int6 块量化 | 每块 6-bit |
| 8 | int8 块量化 | 每块 8-bit |

块量化将权重分块，每块有独立的 scale，相比逐张量量化精度更高。加载时 `ModelBin` 反量化为 fp32（或在 int8 推理路径中直接保留）。

## 精度转换算子

`cast` 层和全局函数处理精度间转换（mat.h:885-889）：

```cpp
cast_float32_to_float16 / cast_float16_to_float32
cast_float32_to_bfloat16 / cast_bfloat16_to_float32
cast_int8_to_float32
```

框架根据 `Option` 和 Layer 的 `support_*_storage` 标志自动在不支持低精度的层边界插入 cast 层。

## float8 支持

mat.h 还包含 float8（e4m3 和 e5m2）转换函数：

```cpp
unsigned char float16_to_float8(unsigned short);  // fp16 -> fp8 e4m3
unsigned short float8_to_float16(unsigned char);  // fp8 e4m3 -> fp16
unsigned char float16_to_bfloat8(unsigned short); // fp16 -> bf8 e5m2
unsigned short bfloat8_to_float16(unsigned char);
```

这是面向新兴硬件（如 NVIDIA Hopper/Blackwell 的 FP8 tensor core）的前瞻支持。

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [03 Layer 抽象层](03-layer-abstraction.md)
- [05 Option 推理配置](05-option-config.md)
- [07 SIMD 打包存储](07-simd-packing.md)
