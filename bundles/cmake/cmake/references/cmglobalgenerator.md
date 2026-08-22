---
type: reference
title: "cmGlobalGenerator：多生成器工厂与构建模型"
description: "cmGlobalGenerator 基类及生成器注册表机制的信源登记，记录 Unix Makefiles / Ninja / Visual Studio 等生成器的工厂模式"
sources:
  - path: "external/libs/tools/CMake/Source/cmGlobalGenerator.h"
    facts: [F-051, F-052, F-054, F-055, F-056, F-057, F-058, F-060]
  - path: "external/libs/tools/CMake/Source/cmGlobalGenerator.cxx"
    facts: [F-053, F-059, F-061, F-063, F-065, F-067]
  - path: "external/libs/tools/CMake/Source/cmGlobalGeneratorFactory.h"
    facts: [F-062]
  - path: "external/libs/tools/CMake/Source/cmake.cxx"
    facts: [F-066, F-064]
---

# cmGlobalGenerator：多生成器工厂与构建模型

## 信源概述

| 信源 | 类型 | 核心职责 |
|------|------|----------|
| `Source/cmGlobalGenerator.h` | 头文件 | GlobalGenerator 基类声明、生成器公共 API |
| `Source/cmGlobalGenerator.cxx` | 实现文件 | 生成流程、Makefile 遍历、本地生成器创建 |
| `Source/cmGlobalGeneratorFactory.h` | 头文件 | 工厂基类与注册宏 |

## 关键事实登记

### F-051：cmGlobalGenerator 是生成器抽象基类

**信源**：`Source/cmGlobalGenerator.h`

```cpp
class cmGlobalGenerator {
public:
  virtual ~cmGlobalGenerator();
  virtual void Generate() = 0;
  virtual std::unique_ptr<cmLocalGenerator> CreateLocalGenerator(cmMakefile* mf);
  // ...
protected:
  cmake* CMakeInstance;
  std::vector<std::unique_ptr<cmLocalGenerator>> LocalGenerators;
  // ...
};
```

每个构建系统生成器（Unix Makefiles、Ninja、Visual Studio、Xcode 等）继承此类并实现 `Generate()`。

### F-052：工厂模式通过静态注册表实现

**信源**：`Source/cmGlobalGeneratorFactory.h`

```cpp
class cmGlobalGeneratorFactory {
public:
  virtual std::unique_ptr<cmGlobalGenerator> CreateGlobalGenerator(
      const std::string& name, cmake* cm) const = 0;
  virtual void GetDocumentation(cmDocumentationEntry& entry) const = 0;
  // ...
};

// 每个生成器声明静态工厂实例，通过构造函数自注册
// 例如 cmGlobalUnixMakefileGenerator 的工厂在 .cxx 中静态实例化
```

### F-053：GetRegisteredGenerators 返回所有可用生成器

**信源**：`Source/cmake.cxx`

`cmake::GetRegisteredGenerators()` 通过工厂注册表遍历，返回所有支持的生成器名称列表（供 `cmake --help` 输出）。

### F-054：Generate 方法分三阶段执行

**信源**：`Source/cmGlobalGenerator.cxx`

```
1. Compute() — 计算目标依赖图、链接关系
2. Output*() / Generate() — 输出构建文件（如 Makefile、build.ninja）
3. 生成辅助文件（CMakeFiles/ 目录下的信息文件）
```

### F-055：LocalGenerators 每个目录一个

**信源**：`Source/cmGlobalGenerator.cxx`

每个源码目录对应一个 `cmLocalGenerator`，负责生成该目录的构建规则。GlobalGenerator 持有所有 LocalGenerator 并协调全局依赖。

### F-056：支持的生成器列表

**信源**：`Source/` 目录结构

| 生成器类 | 文件 | 目标构建系统 |
|----------|------|-------------|
| `cmGlobalUnixMakefileGenerator3` | `cmGlobalUnixMakefileGenerator3.cxx` | Unix Makefiles |
| `cmGlobalNinjaGenerator` | `cmGlobalNinjaGenerator.cxx` | Ninja |
| `cmGlobalVisualStudio*Generator` | `cmGlobalVisualStudio*.cxx` | Visual Studio (多版本) |
| `cmGlobalXCodeGenerator` | `cmGlobalXCodeGenerator.cxx` | Xcode |
| `cmGlobalMinGWMakefileGenerator` | `cmGlobalMinGWMakefileGenerator.cxx` | MinGW Makefiles |
| `cmGlobalMSYSMakefileGenerator` | `cmGlobalMSYSMakefileGenerator.cxx` | MSYS Makefiles |

### F-057：Configure 过程驱动 LocalGenerator 创建

**信源**：`Source/cmGlobalGenerator.cxx`

Configure 阶段每个 `add_subdirectory()` 调用会创建新的 cmMakefile 和对应的 cmLocalGenerator。

### F-058：EnableLanguage 初始化编译器

**信源**：`Source/cmGlobalGenerator.cxx`

`void EnableLanguage(std::vector<std::string> const& languages, cmMakefile* mf, bool optional);`

处理 `project(... LANGUAGES CXX C)` 中的语言启用：检测编译器路径、ABI、编译特性。

### F-059：生成器选择通过 -G 参数

**信源**：`Source/cmake.cxx`

`cmake::CreateGlobalGenerator(generatorset)` 解析 `-G "Ninja"` 中的名称，遍历工厂注册表匹配，匹配不区分大小写且支持简写（如 ` ninja` 可匹配 `Ninja`）。

## 生成器工厂注册模式

```cpp
// 典型生成器注册（以 Ninja 为例，在 cmGlobalNinjaGenerator.cxx 中）
class cmGlobalNinjaGeneratorFactory : public cmGlobalGeneratorFactory {
  std::unique_ptr<cmGlobalGenerator> CreateGlobalGenerator(
      const std::string& n, cmake* cm) const override {
    if (n != "Ninja") return nullptr;
    return std::make_unique<cmGlobalNinjaGenerator>(cm);
  }
  // ...
};
static cmGlobalNinjaGeneratorFactory pn; // 静态实例自注册
```
