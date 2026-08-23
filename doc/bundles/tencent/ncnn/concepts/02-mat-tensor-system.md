---
type: Concept
title: Mat 张量系统
description: Mat 是 ncnn 的核心张量结构，dims 0-4 维秩与 w/h/d/c 维度、elemsize 精度、elempack SIMD 打包、cstep 对齐通道步长、refcount 引用计数实现浅拷贝零拷贝，channel/row/range 视图共享数据。
tags: [ncnn, mat, tensor, memory]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mat-h
    resource: /src/mat.h
    title: mat.h
---

# Mat 张量系统

`Mat` 是 ncnn 中所有数据的载体，设计灵感来自 OpenCV 的 `cv::Mat`，但针对神经网络推理和 SIMD 优化做了专门设计。

## 维度模型

Mat 使用 `dims`（维度秩）+ 四个维度字段描述形状：

| dims | 含义 | 字段 |
|---|---|---|
| 0 | 空 | — |
| 1 | 向量 | `w` |
| 2 | 矩阵/图像 | `w`, `h` |
| 3 | 多通道图像/特征图 | `w`, `h`, `c` |
| 4 | 立方体/3D卷积 | `w`, `h`, `d`, `c` |

`NCNN_BATCH=ON` 时额外有 `n`（batch 数，默认 1）和 `nstep`。注意 ncnn 没有把 batch 作为 dims=5，而是作为独立字段，与 w/h/d/c 正交。

## 精度与打包

### elemsize（元素字节数）

| elemsize | 类型 |
|---|---|
| 4 | float32 / int32 |
| 2 | float16 / bfloat16 |
| 1 | int8 / uint8 |
| 0 | empty |

### elempack（元素打包数）

`elempack` 控制一个"元素"内打包多少个标量，直接对应 SIMD 寄存器宽度（F-022）：

| elempack | 平台 |
|---|---|
| 1 | scalar（默认） |
| 4 | NEON / SSE |
| 8 | AVX / FP16 |

打包后逻辑形状的 w/h/c 会相应缩小（如 c=64 打包为 c/4=16 个 elempack=4 的元素），这是 [`use_packing_layout`](05-option-config.md) 的基础。

### cstep（通道步长）

`cstep` 是相邻两个通道之间的元素距离，按 16 字节对齐计算（F-027）：

```
cstep = alignSize(w * h * elemsize, 16) / elemsize
```

这保证每个通道起始地址 16 字节对齐，满足 NEON/SSE 的对齐加载要求，并为越界预读保留填充。

## 引用计数与零拷贝

### 公共字段

```cpp
void* data;          // 数据指针
int* refcount;       // 引用计数；外部数据时为 NULL
size_t elemsize;
int elempack;
Allocator* allocator;
int dims, w, h, d, c;
size_t cstep;
```

### 浅拷贝是默认语义

Mat 的拷贝构造和赋值运算符执行浅拷贝——复制所有字段指针后调用 `addref()`（F-026）：

```cpp
Mat(const Mat& m) : data(m.data), refcount(m.refcount), ... {
    addref();
}
```

`addref()` 通过 `NCNN_XADD(refcount, 1)` 原子增加引用计数；析构时 `release()` 原子递减，归零时通过 `allocator->fastFree(data)` 释放。这使得在层间传递 Mat 零拷贝。

### 外部数据引用

使用 external 构造函数包装用户数据时，`refcount=NULL`，ncnn 不管理该内存（F-025）：

```cpp
float buffer[1000];
ncnn::Mat m(1000, buffer);  // refcount=NULL，析构时不释放
```

这避免了"栈内存被 delete"的风险，但用户需保证缓冲区生命周期长于 Mat。

### 视图（View）

`channel(c)`、`depth(z)`、`row(y)`、`range(x,n)`、`channel_range`、`batch(b)` 等方法返回共享同一块 `data` 的新 Mat，仅调整指针偏移和形状字段（F-029）。在 `Layer::forward` 中返回视图可避免不必要的内存分配。

深拷贝用 `clone()`，原地深拷贝用 `clone_from()`。

## 内存分配

- `create(w, h, c, elemsize, elempack, allocator)` 分配新内存；
- `create_like(m)` 按另一个 Mat 的形状/精度/打包分配；
- 分配大小 = `cstep * c * elemsize + NCNN_MALLOC_OVERREAD`，带 64 字节越界余量；
- 可传入自定义 `Allocator*`，传 NULL 使用默认 `fastMalloc`。

## 像素转换

`from_pixels` 系列静态方法将 `unsigned char*` 像素数据转为 float Mat，支持：

- 格式：RGB/BGR/GRAY/RGBA/BGRA；
- 操作：直接转换、resize、roi、roi+resize；
- stride 参数支持行填充。

`to_pixels` 反向导出。`substract_mean_normalize(mean, norm)` 执行通道级减均值乘归一化预处理。

## GPU 张量

Vulkan 下有对应的 `VkMat`（缓冲区）和 `VkImageMat`（图像），字段结构与 Mat 平行，但 `data` 类型为 `VkBufferMemory*`/`VkImageMemory*`，allocator 为 `VkAllocator*`。通过 `mapped()` 可映射回主机 Mat。

## 相关概念

- [03 Layer 抽象层](03-layer-abstraction.md)
- [04 内存分配器](04-allocator.md)
- [07 SIMD 打包存储](07-simd-packing.md)
- [06 Vulkan GPU 后端](06-vulkan-gpu.md)
- [11 量化与低精度](11-quantization.md)
