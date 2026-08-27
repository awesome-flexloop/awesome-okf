---
type: Reference
title: mat.h — Mat 张量系统信源
description: ncnn/src/mat.h 中 Mat/VkMat/VkImageMat 类的公共字段、构造函数、create/clone/reshape、视图方法、像素转换与精度转换 API 登记。
tags: [ncnn, mat, tensor, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mat-h
    resource: /src/mat.h
    title: mat.h
---

# mat.h — Mat 张量系统

> 信源路径：`src/mat.h`（893 行）。

## Mat 公共字段

```cpp
void* data;              // 数据指针
int* refcount;           // 引用计数；外部数据时为 NULL
size_t elemsize;         // 4=fp32/int32, 2=fp16/bf16, 1=int8/uint8, 0=empty
int elempack;            // 1=scalar, 4=neon/sse, 8=avx/fp16
Allocator* allocator;    // 分配器
int dims;                // 维度秩 0/1/2/3/4
int w, h, d, c;          // 宽/高/深/通道
size_t cstep;            // 通道步长（按元素，16字节对齐）
#if NCNN_BATCH
int n;                   // batch 数，默认 1
size_t nstep;            // batch 步长
#else
static const int n = 1;
#endif
```

## 构造函数族（节选）

每个维度（1d vec / 2d image / 3d dim / 4d cube）均有四种变体：

```cpp
Mat();
Mat(int w, size_t elemsize = 4u, Allocator* allocator = 0);
Mat(int w, int h, size_t elemsize = 4u, Allocator* allocator = 0);
Mat(int w, int h, int c, size_t elemsize = 4u, Allocator* allocator = 0);
Mat(int w, int h, int d, int c, size_t elemsize = 4u, Allocator* allocator = 0);
// packed：带 elempack 参数
Mat(int w, size_t elemsize, int elempack, Allocator* allocator = 0);
// ...（其余维度同理）
// external：包装外部数据，refcount=NULL
Mat(int w, void* data, size_t elemsize = 4u, Allocator* allocator = 0);
// ...（其余维度同理）
```

## 关键方法

```cpp
void addref();
void release();
bool empty() const;
size_t total() const;
int elembits() const;
Mat shape() const;

Mat clone(Allocator* allocator = 0) const;
void clone_from(const Mat& mat, Allocator* allocator = 0);
Mat reshape(int w, Allocator* = 0) const;
Mat reshape(int w, int h, Allocator* = 0) const;
Mat reshape(int w, int h, int c, Allocator* = 0) const;
Mat reshape(int w, int h, int d, int c, Allocator* = 0) const;

void create(int w, ...);
void create_like(const Mat& m, Allocator* = 0);

// 视图（零拷贝，共享 data）
Mat channel(int c);
Mat depth(int z);
float* row(int y);
Mat channel_range(int c, int channels);
Mat row_range(int y, int rows);
Mat range(int x, int n);
Mat batch(int b);
```

## 像素与预处理

```cpp
enum PixelType { PIXEL_RGB=1, PIXEL_BGR=2, PIXEL_GRAY=3, PIXEL_RGBA=4, PIXEL_BGRA=5,
                 PIXEL_RGB2BGR=..., ... };  // 转换用 16 位移位编码

static Mat from_pixels(const unsigned char* pixels, int type, int w, int h, Allocator* = 0);
static Mat from_pixels_resize(...);
static Mat from_pixels_roi(...);
void to_pixels(unsigned char* pixels, int type) const;
void substract_mean_normalize(const float* mean_vals, const float* norm_vals);
```

## VkMat / VkImageMat 字段

```cpp
// VkMat
VkBufferMemory* data;
int* refcount;
size_t elemsize; int elempack;
VkAllocator* allocator;
int dims, w, h, d, c; size_t cstep;
Mat mapped() const;             // 映射回主机
VkBuffer buffer() const;

// VkImageMat
VkImageMemory* data;
VkImage image() const;
VkImageView imageview() const;
```

## 精度转换全局函数

```cpp
NCNN_EXPORT unsigned short float32_to_float16(float);
NCNN_EXPORT float float16_to_float32(unsigned short);
NCNN_EXPORT unsigned short float32_to_bfloat16(float);  // 直接取高16位
NCNN_EXPORT float bfloat16_to_float32(unsigned short);
NCNN_EXPORT void cast_float32_to_float16(const Mat&, Mat&, const Option&);
NCNN_EXPORT void quantize_to_int8(const Mat&, Mat&, const Mat& scale, const Option&);
NCNN_EXPORT void convert_packing(const Mat&, Mat&, int elempack, const Option&);
```

## 相关概念

- [02 Mat 张量系统](../concepts/02-mat-tensor-system.md)
- [07 SIMD 打包存储](../concepts/07-simd-packing.md)
- [11 量化与低精度](../concepts/11-quantization.md)
