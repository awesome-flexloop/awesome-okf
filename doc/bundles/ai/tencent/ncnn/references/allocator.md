---
type: Reference
title: allocator.h — 内存分配器信源
description: ncnn/src/allocator.h 中 Allocator 抽象基类、PoolAllocator/UnlockedPoolAllocator、VkAllocator 层级（Blob/Weight/Staging）及 NCNN_MALLOC_ALIGN/NCNN_MALLOC_OVERREAD/NCNN_XADD 原子操作登记。
tags: [ncnn, allocator, memory, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: allocator-h
    resource: /src/allocator.h
    title: allocator.h
---

# allocator.h — 内存分配器

> 信源路径：`src/allocator.h`（442 行）。

## 对齐与越界常量

```cpp
#if NCNN_AVX512
#define NCNN_MALLOC_ALIGN 64
#elif NCNN_AVX
#define NCNN_MALLOC_ALIGN 32
#else
#define NCNN_MALLOC_ALIGN 16
#endif

#define NCNN_MALLOC_OVERREAD 64   // SIMD 循环安全余量
```

## 主机端分配器

```cpp
class NCNN_EXPORT Allocator
{
public:
    virtual ~Allocator();
    virtual void* fastMalloc(size_t size) = 0;
    virtual void fastFree(void* ptr) = 0;
};

class NCNN_EXPORT PoolAllocator : public Allocator {
    // 线程安全内存池，PIMPL
    void set_size_compare_ratio(float scr);
    void set_size_drop_threshold(size_t);
    void clear();
    virtual void* fastMalloc(size_t size);
    virtual void fastFree(void* ptr);
private:
    PoolAllocatorPrivate* const d;
};

class NCNN_EXPORT UnlockedPoolAllocator : public Allocator {
    // 单线程无锁内存池，PIMPL，接口同 PoolAllocator
    UnlockedPoolAllocatorPrivate* const d;
};
```

## 原子引用计数

```cpp
// 多平台实现：GCC __atomic_fetch_add / Clang __c11_atomic /
// MSVC _InterlockedExchangeAdd / ICC / RISC-V 无A扩展降级
#define NCNN_XADD(addr, delta) ...
```

## GPU 端分配器

```cpp
class NCNN_EXPORT VkBufferMemory {
public:
    VkBuffer buffer;
    size_t offset, capacity;
    VkDeviceMemory memory;
    void* mapped_ptr;
    uint32_t memory_type_index;
    mutable VkAccessFlags access_flags;
    mutable VkPipelineStageFlags stage_flags;
    int refcount;
};

class NCNN_EXPORT VkAllocator {
public:
    explicit VkAllocator(const VulkanDevice* _vkdev);
    virtual VkBufferMemory* fastMalloc(size_t size) = 0;
    virtual void fastFree(VkBufferMemory* ptr) = 0;
    virtual VkImageMemory* fastMalloc(int w, int h, int c, size_t elemsize, int elempack) = 0;
    virtual void fastFree(VkImageMemory* ptr) = 0;
    const VulkanDevice* vkdev;
    uint32_t buffer_memory_type_index;
    uint32_t image_memory_type_index;
    bool mappable, coherent;
};

class NCNN_EXPORT VkBlobAllocator : public VkAllocator {
    // 块大小默认 16MB，blob 数据
};
class NCNN_EXPORT VkWeightAllocator : public VkAllocator {
    // 块大小默认 8MB，权重，支持 prefer_host_memory
};
class NCNN_EXPORT VkStagingAllocator : public VkAllocator {
    // 主机可映射暂存，size_compare_ratio 默认 0.75
};
class NCNN_EXPORT VkWeightStagingAllocator : public VkAllocator {
    // 权重上传暂存
};
```

## 设计要点

- `NCNN_MALLOC_OVERREAD=64` 让 SIMD kernel 在循环尾部可安全预读取下一块数据，避免 SEGV。
- `PoolAllocator` 按尺寸比较比例（compare ratio）复用空闲块，`UnlockedPoolAllocator` 用于单线程场景省锁。
- GPU 侧分 Blob（特征图）/Weight（权重）/Staging（上传下载）三类分配器，各自独立内存池，权重可常驻主机内存。

## 相关概念

- [04 内存分配器](../concepts/04-allocator.md)
- [06 Vulkan GPU 后端](../concepts/06-vulkan-gpu.md)
