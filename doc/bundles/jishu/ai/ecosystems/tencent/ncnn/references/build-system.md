---
type: Reference
title: CMakeLists.txt — 构建系统信源
description: ncnn/CMakeLists.txt 版本定义、核心构建选项（NCNN_VULKAN/OPENMP/INT8/PYTHON/BF16/WEIGHT_QUANT/BATCH/PIXEL/RUNTIME_CPU/SIMPLEVK/SIMPLESTL）及平台分支登记。
tags: [ncnn, cmake, build, reference]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: cmake
    resource: /CMakeLists.txt
    title: CMakeLists.txt
---

# CMakeLists.txt — 构建系统

> 信源路径：`CMakeLists.txt`。版本 1.0.20260526。

## 版本定义

```cmake
if(NOT DEFINED NCNN_VERSION)
    string(TIMESTAMP NCNN_VERSION "%Y%m%d")
endif()
set(NCNN_VERSION_MAJOR 1)
set(NCNN_VERSION_MINOR 0)
set(NCNN_VERSION_PATCH ${NCNN_VERSION})
set(NCNN_VERSION_STRING ${NCNN_VERSION_MAJOR}.${NCNN_VERSION_MINOR}.${NCNN_VERSION_PATCH})
```

## 核心构建选项

| 选项 | 默认 | 说明 |
|---|---|---|
| `NCNN_SHARED_LIB` | OFF | 动态库 |
| `NCNN_OPENMP` | ON | OpenMP 多线程 |
| `NCNN_STDIO` | ON | 从文件加载模型 |
| `NCNN_STRING` | ON | 字符串名/明文 param |
| `NCNN_THREADS` | ON | 线程支持 |
| `NCNN_BENCHMARK` | OFF | 逐层耗时打印 |
| `NCNN_C_API` | ON | C 语言 API |
| `NCNN_PLATFORM_API` | ON | 平台糖果 API（Android Asset 等） |
| `NCNN_BATCH` | ON | batch 推理（n>1） |
| `NCNN_PIXEL` | ON | 图像像素转换/缩放 |
| `NCNN_VULKAN` | OFF | Vulkan GPU 计算 |
| `NCNN_SIMPLEVK` | ON | 内置极简 Vulkan loader |
| `NCNN_SYSTEM_GLSLANG` | OFF | 使用系统 glslang |
| `NCNN_RUNTIME_CPU` | ON | 运行时 CPU 特性分发 |
| `NCNN_PYTHON` | OFF | Python pybind11 绑定 |
| `NCNN_INT8` | ON | int8 量化推理 |
| `NCNN_WEIGHT_QUANT` | ON | 权重量化推理 |
| `NCNN_BF16` | ON | bfloat16 推理 |
| `NCNN_SIMPLEOCV` | OFF | 内嵌最小 OpenCV 模拟 |
| `NCNN_SIMPLEOMP` | OFF | 内嵌最小 OpenMP 运行时 |
| `NCNN_SIMPLESTL` | OFF | 内嵌最小 C++ STL |
| `NCNN_SIMPLEMATH` | OFF | 内嵌最小 cmath |
| `NCNN_ENABLE_LTO` | OFF | 链接时优化 |
| `NCNN_BUILD_TESTS` | OFF | 构建测试 |
| `NCNN_BUILD_BENCHMARK` | ON | 构建 benchmark |

## 平台分支

```cmake
# ANDROID / IOS / SIMPLESTL 时禁用 RTTI 和异常
if(ANDROID OR IOS OR NCNN_SIMPLESTL)
    option(NCNN_DISABLE_RTTI "disable rtti" ON)
    option(NCNN_DISABLE_EXCEPTION "disable exception" ON)
endif()

# 交叉编译或 SIMPLESTL 时不构建 tools/examples
if(ANDROID OR IOS OR NCNN_SIMPLESTL OR CMAKE_CROSSCOMPILING)
    option(NCNN_BUILD_TOOLS "build tools" OFF)
    option(NCNN_BUILD_EXAMPLES "build examples" OFF)
endif()

# NCNN_STDIO 或 NCNN_STRING 关闭时，tools/examples/benchmark/tests 强制关闭
```

## 架构检测

CMake 通过 `check_cxx_source_compiles` 检测目标架构 SIMD 支持：

- ARM：NEON、VFPv4、FP16
- x86：SSE2/AVX/AVX2/AVX512/FMA/F16C/XOP
- 架构标识 `NCNN_TARGET_ARCH` 设为 `arm`/`x86`/`mips`/`riscv`/`loongarch`

## 层注册机制

`cmake/ncnn_add_layer.cmake` 在构建期扫描 `src/layer/*.cpp`，自动生成 `layer_type_enum.h`（枚举值）和 `layer_registry.h`（创建函数表），无需手动维护注册表。

## 相关概念

- [00 整体架构](../concepts/00-overall-architecture.md)
- [09 层注册表与自定义层](../concepts/09-layer-registry.md)
- [10 Python 绑定](../concepts/10-python-binding.md)
