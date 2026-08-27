---
type: Concept
title: 层注册表与自定义层
description: ncnn 通过 layer_type.h 类型枚举、CMake 构建期生成的 layer_registry 注册表、DEFINE_LAYER_CREATOR 宏和 register_custom_layer 运行时注册实现层工厂，支持自定义层扩展和内置层覆盖。
tags: [ncnn, layer, registry, factory, custom]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: layer-h
    resource: /src/layer.h
    title: layer.h
  - id: layer-type-h
    resource: /src/layer_type.h
    title: layer_type.h
  - id: cmake
    resource: /cmake/ncnn_add_layer.cmake
    title: ncnn_add_layer.cmake
---

# 层注册表与自定义层

ncnn 的层工厂结合了**编译期自动注册**和**运行时自定义注册**两种机制，使内置层零维护、自定义层可扩展。

## 类型枚举

`src/layer_type.h` 定义层类型枚举，枚举值由 `#include "layer_type_enum.h"` 引入（F-108）：

```cpp
namespace ncnn {
namespace LayerType {
enum LayerType {
#include "layer_type_enum.h"   // 构建期由 CMake 生成
    CustomBit = (1 << 8),      // 自定义层类型高位标记
};
}
}
```

`layer_type_enum.h` 不是手写文件，而是 CMake 在配置阶段扫描 `src/layer/*.cpp` 自动生成的，按字母顺序为每个内置层分配枚举值（如 `Convolution=0`、`ReLU=1` 等）。新增内置层只需放一个 `.cpp` 文件到 `src/layer/`，无需手动维护枚举表。

## 编译期注册表

类似地，`layer_registry.h`（由 `cmake/ncnn_add_layer.cmake` 生成）包含一个 `layer_registry_entry` 数组，将类型名映射到工厂函数：

```cpp
struct layer_registry_entry {
#if NCNN_STRING
    const char* name;           // 类型名字符串
#endif
    layer_creator_func creator; // 工厂函数指针
};
```

每个内置层通过 `DEFINE_LAYER_CREATOR(ClassName)` 宏生成 `ClassName_layer_creator(void*)` 工厂函数（F-047）：

```cpp
#define DEFINE_LAYER_CREATOR(name) \
    ::ncnn::Layer* name##_layer_creator(void*) { return new name; }
```

构建系统将这些工厂函数指针收集到注册表数组中，`create_layer(index)` 按下标创建层实例，`create_layer(const char* type)` 先 `layer_to_index` 查找枚举再创建。

## 工厂函数变体

```cpp
Layer* create_layer(const char* type);      // 按名创建（含 CPU+Vulkan 选择）
Layer* create_layer(int index);             // 按枚举创建
Layer* create_layer_naive(const char* type); // 强制 naive 实现
Layer* create_layer_cpu(const char* type);   // 强制 CPU 实现
Layer* create_layer_vulkan(const char* type); // 强制 Vulkan 实现
```

默认 `create_layer` 根据编译选项和 `Option` 选择最优实现；`_cpu`/`_vulkan` 变体允许强制后端。

## 运行时自定义层注册

`Net::register_custom_layer` 允许在不修改 ncnn 源码的情况下注册用户自定义层（F-004、F-005）：

```cpp
// 按类型名注册
int register_custom_layer(const char* type,
                          layer_creator_func creator,
                          layer_destroyer_func destroyer = 0,
                          void* userdata = 0);

// 按类型索引注册（>= CustomBit 避免与内置冲突）
int register_custom_layer(int index,
                          layer_creator_func creator,
                          layer_destroyer_func destroyer = 0,
                          void* userdata = 0);
```

自定义层类型索引应使用 `LayerType::CustomBit | 自定义ID`，避免与内置层枚举冲突。

### 注册流程

1. 用户继承 `Layer`，实现 `load_param`/`forward` 等；
2. 用 `DEFINE_LAYER_CREATOR(MyLayer)` 生成工厂函数；
3. 调用 `net.register_custom_layer("MyLayer", MyLayer_layer_creator)`；
4. 加载 `.param` 文件时，遇到类型名为 `"MyLayer"` 的层自动调用注册的工厂创建；
5. `userdata` 指针存入 `Layer::userdata`，可在层实例间传递上下文。

### 覆盖内置层

注册与内置层同名的自定义层会覆盖内置实现（`create_overwrite_builtin_layer` 虚函数支持更复杂的覆盖逻辑），便于替换算子行为或注入调试钩子。

## 三种注册表结构

layer.h 定义了三种注册表条目（F-049）：

```cpp
struct layer_registry_entry {                    // 内置编译期注册表
    const char* name;
    layer_creator_func creator;
};

struct custom_layer_registry_entry {             // 运行时自定义层
    const char* name;
    layer_creator_func creator;
    layer_destroyer_func destroyer;
    void* userdata;
};

struct overwrite_builtin_layer_registry_entry {  // 内置层覆盖
    int typeindex;
    layer_creator_func creator;
    layer_destroyer_func destroyer;
    void* userdata;
};
```

## C API 注册

C 接口通过函数指针表支持自定义层（c_api.h）：

```c
typedef ncnn_layer_t (*ncnn_layer_creator_t)(void* userdata);
ncnn_net_register_custom_layer_by_type(net, "MyLayer", creator, destroyer, userdata);
```

## 相关概念

- [03 Layer 抽象层](03-layer-abstraction.md)
- [01 Net 与 Extractor 推理流程](01-net-extractor.md)
- [08 ParamDict 与 ModelBin](08-paramdict-modelbin.md)
- [自定义 Layer 示例](../examples/custom-layer.md)
