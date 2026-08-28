---
type: Concept
title: "Arena 内存管理"
description: "C++ Arena 区域分配器的 Make/Own/DoCreateMessage 生命周期模型与 ArenaStringPtr 可变位字符串机制，Python、Rust、hpb 各运行时的 Arena 形态，以及 BM_ArenaFuse* 融合基准测试。"
tags: [protobuf, arena, memory-management, allocation]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: cpp-core
    resource: /references/cpp-core.md
    title: "protobuf C++ 运行时核心信源"
  - id: runtimes
    resource: /references/runtimes.md
    title: "protobuf 多语言运行时信源"
  - id: testing
    resource: /references/testing.md
    title: "protobuf 测试与规范体系信源"
---

protobuf 消息对象图往往深而碎——一条大消息里嵌套着成百上千个子消息、字符串与 repeated 容器。若逐个 `new`/`delete`，分配器开销与析构遍历成本都会吞噬性能。Arena（区域分配器）的答案是把整棵对象图的内存生命周期折叠为一个区域：在 Arena 上创建的一切随 Arena 一次性释放，析构仅对显式注册的对象执行。C++ 侧 `Message::New(Arena*)`（见 /concepts/01-message-model.md）即此模型的入口。本篇属于核心机制组，同时是理解 Python、Rust、hpb 运行时内存行为的公共前置——各语言绑定都对 upb/C++ 内核的 Arena 能力做了自己的封装（本束洞察 1：多语言实为多内核绑定）。

## C++ Arena：创建、接管与消息工厂

`Arena` 是 `final` 类（`class PROTOBUF_EXPORT Arena final`，F-CPP-036），核心 API 分三组。

**区域上创建**——模板成员 `Make`（F-CPP-037）：

```cpp
[[nodiscard]] PROTOBUF_NDEBUG_INLINE Ptr<T> Make(Args&&... args);
```

在 Arena 内存中构造 `T` 并返回智能指针式的 `Ptr<T>`；对象本身随 Arena 释放，无需手动析构（除非类型 `T` 的析构有副作用，那就要走 `Own`）。

**接管非平凡析构**——`Own` 与 `OwnDestructor`（F-CPP-038）：

```cpp
PROTOBUF_ALWAYS_INLINE void Own(T* object);
PROTOBUF_ALWAYS_INLINE void OwnDestructor(T* object);
```

`Own` 让 Arena 负责对象析构（针对"不随 Arena 分配但希望随 Arena 销毁"的对象）；`OwnDestructor` 只注册析构调用本身。两者区分了所有权与析构责任两个正交维度。

**消息创建链**——内部模板 `DoCreateMessage`（F-CPP-039）：

```cpp
PROTOBUF_NDEBUG_INLINE T* DoCreateMessage(Args&&... args);
```

`Create`/`DoCreateMessage` 调用链位于 arena.h 的 717、734、769 行附近——这是 `Message::New(Arena*)` 与 `MutableMessage` 反射路径（见 /concepts/03-descriptors-and-reflection.md）的底层落点，消息在 Arena 上分配后按 ClassData 的创建策略初始化（`MessageCreator`，见 01 篇）。

## ArenaStringPtr：字符串的可变位机制

字符串是 protobuf 内存行为最微妙的部分：默认值（空串）不分配、只读共享可以零拷贝、被修改才落 Arena。`arenastring.h` 的 `ArenaStringPtr` 实现了这套状态机（F-CPP-040 / F-CPP-041）：

```cpp
std::string* Mutable(Arena* arena);
std::string* Mutable(const LazyString& default_value, Arena* arena);
const std::string& Get() const;

inline bool IsMutable() const { return as_int() & kMutableBit; }
```

指针的低位被用作"可变位"（kMutableBit）：`IsMutable()` 用按位与判断当前指针是否指向专属的可变 `std::string`。未设置时指针编码的是共享默认值或 Arena 内的惰性存储，`Mutable` 才完成物化。这是 protobuf 在"零成本读、按需写"之间的经典折衷——同一位面还有 `ReflectionSchema` 偏移标记中的 `kLazyOffsetTag`/`kInlinedOffsetTag` 等（F-CPP-125，见 01 篇），共同构成字段存储属性的高位编码体系。

## 跨语言 Arena 形态

**Python（PyUpb_Arena）**：`python/protobuf.c` 定义 `PyUpb_Arena` 类型（`PyType_Spec` 名为 `PYUPB_MODULE_NAME ".Arena"`，即 `"google._upb._message.Arena"`）与函数 `PyUpb_Arena_New/Get/IsFrozen/SetFrozen`（F-RT-007）。它还是 Python 消息对象图的宿主——upb 消息在 Arena 上分配，Python 包装对象与 Arena 绑定。值得一提的细节：该文件含 `upb_trim_allocfunc` 分配器，GLIBC 下周期调用 `malloc_trim` 归还操作系统内存；`IsFrozen`/`SetFrozen` 提供冻结语义（冻结的消息不可变更）。

**Rust（upb::Arena）**：`rust/upb/lib.rs` 声明 `mod arena` 并 `pub use arena::Arena`（F-RT-034），`rust/upb/arena.rs` 定义 `pub struct Arena`（F-RT-036）；同层的 `owned_arena_box` 模块导出 `OwnedArenaBox`——把对象与其 Arena 打包为一个 Rust 所有权单元，RAII 释放。Rust 绑定全貌详见 /concepts/12-upb-and-rust-runtime.md。

**hpb（多后端 Arena）**：`hpb/arena.h` 定义 `class Arena`（F-RT-057）：构造函数 `Arena()`、`Arena(char* initial_block, size_t size)`（外部初始块模式）、`explicit Arena(size_t size_hint)`；upb 后端下额外提供 `Fuse(Arena&)`、`IsFused(Arena&)`、`RefArena(const Arena&)`。内部成员 `backend::Arena arena_` 按编译期后端选择（`HPB_INTERNAL_BACKEND`，见 /concepts/13-hpb.md）路由到 upb 或 C++ 实现——同一头文件接口，两种内核行为。

## Arena 融合与基准测试

`Fuse`/`IsFused` 的语义是 Arena 融合（arena fusion）：当两条消息（各自持有 Arena）需要发生合并/复制时，把两个 Arena 熔接为同一生存域，使后续的子消息指针交换无需深拷贝。这不是微优化——benchmarks 的 `benchmark.cc` 专门注册了两个对照基准（F-TST-039）：

- `BM_ArenaFuseUnbalanced`——非平衡融合（两条大小悬殊的对象图互熔）；
- `BM_ArenaFuseBalanced`——平衡融合；

两者都配 `->Range(2, 128)` 做规模扫描。同文件还有 `BM_ArenaOneAlloc`、`BM_ArenaInitialBlockOneAlloc` 等基线，以及大量 `UseArena`/`InitBlock`/`NoArena` 变体的解析基准——Arena 的"初始块模式"（对应 hpb 的 `Arena(char*, size_t)` 构造）允许调用方预置一块栈/静态内存作为第一分配区，进一步消灭热路径 malloc。基准体系全貌见 /concepts/16-wkt-conformance-benchmarks.md。

## 相关概念

- [/concepts/01-message-model.md](/concepts/01-message-model.md)——`New(Arena*)`、`MessageCreator` 与 `UnsafeArenaReleaseMessage` 的上层语境。
- [/concepts/03-descriptors-and-reflection.md](/concepts/03-descriptors-and-reflection.md)——反射写路径如何在 Arena 上创建子消息。
- [/concepts/12-upb-and-rust-runtime.md](/concepts/12-upb-and-rust-runtime.md)——upb C 内核 Arena 与 Rust 绑定的深潜。
- [/concepts/13-hpb.md](/concepts/13-hpb.md)——hpb 双后端 Arena 与 `OwnedArenaBox` 等所有权封装。
