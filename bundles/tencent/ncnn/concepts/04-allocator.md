---
type: Concept
title: 内存分配器
description: Allocator 抽象基类定义 fastMalloc/fastFree 接口，PoolAllocator 线程安全内存池与 UnlockedPoolAllocator 单线程版本管理主机内存，VkAllocator 层级含 Blob/Weight/Staging 管理 GPU 缓冲，NCNN_MALLOC_ALIGN 按 AVX 级别 16/32/64 对齐。
tags: [ncnn, allocator, memory, pool]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: allocator-h
    resource: /src/allocator.h
    title: allocator.h
---

# 内存分配器

ncnn 通过 `Allocator` 抽象层统一管理主机和 GPU 内存，允许用户注入自定义分配策略（如内存池、DMA 缓冲、ION 内存）。

## 对齐与安全余量

```cpp
#if NCNN_AVX512
#define NCNN_MALLOC_ALIGN 64
#elif NCNN_AVX
#define NCNN_MALLOC_ALIGN 32
#else
#define NCNN_MALLOC_ALIGN 16
#endif

#define NCNN_MALLOC_OVERREAD 64
```

`NCNN_MALLOC_ALIGN` 根据编译的最高 SIMD 级别选择对齐：SSE/NEON 16 字节、AVX 32 字节、AVX-512 64 字节（F-063）。

`NCNN_MALLOC_OVERREAD=64` 是一个关键设计——SIMD kernel 常在循环尾部"越界"预读下一批数据以交织加载和运算，多分配 64 字节保证这种越界不会触发段错误（F-064）。

底层 `fastMalloc`/`fastFree` 跨平台封装：MSVC 用 `_aligned_malloc`、POSIX 用 `posix_memalign`、旧 Android 用 `memalign`（F-065）。

## 主机端 Allocator

### Allocator 抽象基类

```cpp
class Allocator {
public:
    virtual ~Allocator();
    virtual void* fastMalloc(size_t size) = 0;
    virtual void fastFree(void* ptr) = 0;
};
```

### PoolAllocator（线程安全）

`PoolAllocator` 维护按尺寸分组的空闲块链表，`fastFree` 时将块回收到池而非真正释放，后续 `fastMalloc` 按尺寸比较比例复用以减少系统调用（F-067）。

- `set_size_compare_ratio(float)`：尺寸匹配阈值，默认 0（精确匹配）；
- `set_size_drop_threshold(size_t)`：池容量上限，默认 10；
- `clear()`：立即释放所有缓存块；
- PIMPL 实现，内部带互斥锁。

### UnlockedPoolAllocator（单线程）

接口与 `PoolAllocator` 完全相同，但内部无锁（F-068）。用于单线程推理或外部已同步的场景，省去锁开销。

### 使用方式

```cpp
ncnn::UnlockedPoolAllocator g_blob_pool_allocator;
ncnn::PoolAllocator g_workspace_pool_allocator;

ncnn::Net net;
net.opt.blob_allocator = &g_blob_pool_allocator;
net.opt.workspace_allocator = &g_workspace_pool_allocator;
```

Net 加载后 allocator 被所有 Extractor 共享。也可在 Extractor 上单独设置以隔离会话。

## GPU 端 VkAllocator

Vulkan 后端的内存层级更复杂，区分不同用途和内存类型（F-070）：

### VkAllocator 抽象基类

```cpp
class VkAllocator {
public:
    const VulkanDevice* vkdev;
    uint32_t buffer_memory_type_index;
    uint32_t image_memory_type_index;
    bool mappable;   // 主机可映射
    bool coherent;   // 无需显式 flush

    virtual VkBufferMemory* fastMalloc(size_t size) = 0;
    virtual void fastFree(VkBufferMemory* ptr) = 0;
    virtual VkImageMemory* fastMalloc(int w, int h, int c,
                                      size_t elemsize, int elempack) = 0;
    virtual void fastFree(VkImageMemory* ptr) = 0;
};
```

### 四种内置实现

| 分配器 | 默认块大小 | 用途 | 特点 |
|---|---|---|---|
| `VkBlobAllocator` | 16 MB | 中间特征图 | 设备本地内存，子分配 |
| `VkWeightAllocator` | 8 MB | 模型权重 | 支持 `prefer_host_memory` |
| `VkStagingAllocator` | — | 主机↔GPU 传输 | mappable+coherent，compare ratio 0.75 |
| `VkWeightStagingAllocator` | — | 权重上传暂存 | 专用权重上传 |

`VkBufferMemory` 记录 `buffer`、`offset`、`capacity`、`memory`、`mapped_ptr`、`access_flags`、`stage_flags` 和 `refcount`，支持子分配和状态追踪（F-070）。

VulkanDevice 提供 `acquire_blob_allocator()/reclaim_blob_allocator()` 池化获取，避免频繁创建。

## 原子操作

`NCNN_XADD(addr, delta)` 是引用计数的原子加原语，覆盖 GCC/Clang 的 `__atomic_fetch_add`、MSVC 的 `_InterlockedExchangeAdd`、ICC、以及无原子扩展的 RISC-V 降级（F-069）。当 `NCNN_THREADS=OFF` 时降级为普通非原子加法。

## 相关概念

- [02 Mat 张量系统](02-mat-tensor-system.md)
- [05 Option 推理配置](05-option-config.md)
- [06 Vulkan GPU 后端](06-vulkan-gpu.md)
